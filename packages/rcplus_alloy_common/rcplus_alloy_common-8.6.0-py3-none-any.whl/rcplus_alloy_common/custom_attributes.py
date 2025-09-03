"""
Custom attributes related functions

NOTE: S3 related utils implemented here to avoid dependency on `aws` extra which requires
      such heavy dependencies as `pandas` and `awswrangler`.
"""
import os
import re
import math
import logging
from typing import Tuple
from urllib.parse import urlparse

import yaml
import boto3

logger = logging.getLogger(__name__)

REPOSITORY_TAG = os.environ.get("REPOSITORY_TAG")
PROJECT_VERSION = os.environ.get("PROJECT_VERSION")
PROFILES_TAXONOMY_TABLE = "profiles_taxonomy"


class CustomDumper(yaml.SafeDumper):
    # A hackish way to deal with PyYAML formatting, at least to make tables definitions visually separated
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()

        if len(self.indents) == 4:
            super().write_line_break()


def parse_s3_url(s3_url) -> Tuple[str, str]:
    """
    Parse S3 URL and return (S3 bucket, S3 path) tuple pair on success or raise ValueError exception
    """
    url_parts = urlparse(s3_url)
    if url_parts.scheme != "s3" or url_parts.netloc is None or url_parts.path is None:
        raise ValueError(f"Failed to parse malformed S3 URL {s3_url}")

    return url_parts.netloc, url_parts.path.lstrip("/")


def read_s3_file_content(s3_url, decode=True):
    """
    Read S3 file content into memory
    """
    s3 = boto3.client("s3")
    s3_bucket, s3_path = parse_s3_url(s3_url)

    logger.debug(f"Read S3 file content from {s3_url}")
    if decode:
        return s3.get_object(Bucket=s3_bucket, Key=s3_path)["Body"].read().decode("utf-8")

    return s3.get_object(Bucket=s3_bucket, Key=s3_path)["Body"].read()


def copy_file_from_s3(src_s3_url, dst_local_path, decode=True):
    """
    Copy file from S3 URL to local file
    """
    logger.debug(f"Copy file from {src_s3_url} to {dst_local_path}")
    with open(dst_local_path, "wb") as dst:
        content = read_s3_file_content(src_s3_url, decode=decode)
        if decode:
            dst.write(content.encode())
        else:
            dst.write(content)


def normalize_label(label_name: str, attribute_name: str) -> str:
    """
    Some arbitrary rules based on our current experience:
    - a label can't start with a digit, so prefix it with its attribute name
    - a label can't have `-` (hyphen), so replace it with `_` (underscore)
    - a label can't have `+`, so replace it with `_plus` text
    Probably some more rules will be applied in the future
    """
    if re.match(r"^\d", label_name):
        label_name = f"{attribute_name}_{label_name}"

    if "-" in label_name:
        label_name = label_name.replace("-", "_")

    if "+" in label_name:
        label_name = label_name.replace("+", "_plus")

    return label_name


def generate_custom_attributes_sources(predictions: list[dict]) -> dict | None:
    """
    Generate custom attributes sources definitions based on the `predictions` section from
    the tenants configs file as YAML string.

    NOTE: The "param_path" in the "predictions" section has the reference to the folder on S3 which contains all
          predictions related files.
    """
    if not predictions:
        logger.debug("No custom attributes sources were generated because predictions are empty")
        return None

    tables = []
    for prediction in predictions:
        params_s3_url = os.path.join(prediction["params_path"], "inference.yaml")
        params = yaml.safe_load(read_s3_file_content(params_s3_url))
        attr_name = params["task"]
        logger.debug(f"Generate custom attributes sources for {attr_name} based on params from {params_s3_url}")
        labels_str = ",".join([f"{normalize_label(label, attr_name)}:float" for label in params["labels"]])
        table_name = f"predictions_{attr_name}"

        # The main custom attribute table definition
        tables.append({
            "name": table_name,
            "description": f"{attr_name} predictions".capitalize(),
            "columns": [
                {
                    "name": "fp_id",
                    "type": "string",
                    "description": "First party id",
                    "meta": {
                        "pii": True
                    }
                },
                {
                    "name": "predictions",
                    "type": f"struct<{labels_str}>",
                    "description": f"{attr_name} predictions".capitalize(),
                }
            ],
            "external": {
                "partitions": [
                    {
                        "name": "p_timestamp",
                        "type": "timestamp",
                        "description": "Timestamp truncated to an hour when data were processed"
                    },
                ]
            },
            "meta": {
                "repo": REPOSITORY_TAG,
                "source": REPOSITORY_TAG,
                "version": PROJECT_VERSION,
                "depends_on": [f"{table_name}_tmp"]
            },
        })

        # The tmp custom attribute table definition (the same as a main table)
        tables.append({
            "name": f"{table_name}_tmp",
            "description": f"{attr_name} predictions".capitalize(),
            "columns": [
                {
                    "name": "fp_id",
                    "type": "string",
                    "description": "First party id",
                    "meta": {
                        "pii": True
                    }
                },
                {
                    "name": "predictions",
                    "type": f"struct<{labels_str}>",
                    "description": f"{attr_name} predictions".capitalize(),
                }
            ],
            "external": {
                "partitions": [
                    {
                        "name": "p_timestamp",
                        "type": "timestamp",
                        "description": "Timestamp truncated to an hour when data were processed"
                    },
                ]
            },
            "meta": {
                "repo": REPOSITORY_TAG,
                "source": REPOSITORY_TAG,
                "version": PROJECT_VERSION,
                "depends_on": [PROFILES_TAXONOMY_TABLE, f"{table_name}_columns"]
            },
        })

        # The columns custom attribute table definition
        tables.append({
            "name": f"predictions_{attr_name}_columns",
            "description": f"{attr_name} predictions columns".capitalize(),
            "columns": [
                {
                    "name": "index",
                    "type": "string",
                    "description": "",
                },
                {
                    "name": "taxonomy",
                    "type": "string",
                    "description": "",
                },
                {
                    "name": "col",
                    "type": "bigint",
                    "description": "",
                },
            ],
            "meta": {
                "repo": REPOSITORY_TAG,
                "source": REPOSITORY_TAG,
                "version": PROJECT_VERSION,
            },
        })

    sources = {
        "version": 2,
        "sources": [{
            "name": "attribute_predictions",
            "description": "Attribute Predictions",
            "schema": '{{ env_var("TENANT", "riad") }}',
            "tables": tables,
        }]
    }

    return sources


# NOTE-ab: new function for generation of source file.
# generate_custom_attributes_sources will be removed soon after migration to custom_attributes
def generate_custom_attributes_sources_file_content(custom_attributes: list[dict]) -> dict | None:
    """
    Generate custom attributes sources definitions based on the `custom_attributes` section from
    the tenants configs file as YAML string.
    """

    custom_attributes = [
        custom_attribute
        for custom_attribute in custom_attributes
        if custom_attribute["active"]
        and custom_attribute["type"] in {"direct", "training", "external_id", "audience_segment"}
    ]

    if not custom_attributes:
        logger.debug("No custom attributes sources were generated because custom_attributes are empty")
        return None

    tables = [{
        "name": "custom_attributes_metadata",
        "description": "Custom attributes metadata",
        "columns": [
            {
                "name": "attr_name",
                "type": "string",
                "description": "Attribute name",
            },
            {
                "name": "previous_import_timestamp",
                "type": "timestamp",
                "description": "Previous import timestamp.",
            },
            {
                "name": "last_import_timestamp",
                "type": "timestamp",
                "description": "Last import timestamp"
            },
        ],
        "external": {
            "partitions": [
                {
                    "name": "p_timestamp",
                    "type": "timestamp",
                    "description": "Timestamp when data were processed"
                },
            ]
        },
        "meta": {
            "repo": REPOSITORY_TAG,
            "source": REPOSITORY_TAG,
            "version": PROJECT_VERSION,
        },
    }]

    for custom_attribute in custom_attributes:
        attr_name = custom_attribute["name"]
        logger.debug(f"Generate custom attributes sources for {attr_name}")

        tables.append({
            "name": f"custom_attribute_{attr_name}_stg",
            "description": f"Custom attribute {attr_name} stg".capitalize(),
            "columns": [
                {
                    "name": "id",
                    "type": "string",
                    "description": "User identifier",
                    "meta": {
                        "pii": custom_attribute.get("id_pii", False)
                    }
                },
                {
                    "name": "value",
                    "type": "map<string,float>",
                    "description": f"{attr_name} values".capitalize(),
                    "meta": {
                        "pii": custom_attribute.get("value_pii", False)
                    }
                },
                {
                    "name": "upload_timestamp",
                    "type": "timestamp",
                    "description": "When raw data was uploaded"
                },
            ],
            "meta": {
                "repo": REPOSITORY_TAG,
                "source": REPOSITORY_TAG,
                "version": PROJECT_VERSION,
            },
        })

        tables.append({
            "name": f"custom_attribute_{attr_name}_snapshot",
            "description": f"Custom attribute {attr_name} snapshot".capitalize(),
            "columns": [
                {
                    "name": "id",
                    "type": "string",
                    "description": "User identifier",
                    "meta": {
                        "pii": custom_attribute.get("id_pii", False)
                    }
                },
                {
                    "name": "value",
                    "type": "map<string,float>",
                    "description": f"{attr_name} values".capitalize(),
                    "meta": {
                        "pii": custom_attribute.get("value_pii", False)
                    }
                },
                {
                    "name": "upload_timestamp",
                    "type": "timestamp",
                    "description": (
                        "When raw data was uploaded. It is used for merging new data from STG to SNAPSHOT table"
                    )
                },
                {
                    "name": "last_user_update_timestamp",
                    "type": "timestamp",
                    "description": (
                        "Last user update timestamp. It is used for merging SNAPSHOT data to profiles_cache"
                    )
                },
            ],
            "meta": {
                "repo": REPOSITORY_TAG,
                "source": REPOSITORY_TAG,
                "version": PROJECT_VERSION,
                "depends_on": [
                    f"custom_attribute_{attr_name}_stg",
                ]
            },
        })

        if custom_attribute["type"] == "training":
            tables.append({
                "name": f"custom_attribute_{attr_name}_predictions",
                "description": f"Custom attribute {attr_name} predictions".capitalize(),
                "columns": [
                    {
                        "name": "fp_id",
                        "type": "string",
                        "description": "First party id",
                        "meta": {
                            "pii": True
                        }
                    },
                    {
                        "name": "predictions",
                        "type": "map<string,float>",
                        "description": f"Custom attribute {attr_name} predictions".capitalize(),
                    }
                ],
                "external": {
                    "partitions": [
                        {
                            "name": "p_timestamp",
                            "type": "timestamp",
                            "description": "Timestamp truncated to an hour when data were processed"
                        },
                    ]
                },
                "meta": {
                    "repo": REPOSITORY_TAG,
                    "source": REPOSITORY_TAG,
                    "version": PROJECT_VERSION,
                    "depends_on": [
                        f"custom_attribute_{attr_name}_predictions_tmp",
                    ]
                },
            })

            tables.append({
                "name": f"custom_attribute_{attr_name}_predictions_tmp",
                "description": f"{attr_name} predictions".capitalize(),
                "columns": [
                    {
                        "name": "fp_id",
                        "type": "string",
                        "description": "First party id",
                        "meta": {
                            "pii": True
                        }
                    },
                    {
                        "name": "predictions",
                        "type": "map<string,float>",
                        "description": f"Custom attribute {attr_name} predictions".capitalize(),
                    }
                ],
                "external": {
                    "partitions": [
                        {
                            "name": "p_timestamp",
                            "type": "timestamp",
                            "description": "Timestamp truncated to an hour when data were processed"
                        },
                    ]
                },
                "meta": {
                    "repo": REPOSITORY_TAG,
                    "source": REPOSITORY_TAG,
                    "version": PROJECT_VERSION,
                    "depends_on": [
                        f"custom_attribute_{attr_name}_snapshot",
                        f"custom_attribute_{attr_name}_predictions_columns",
                        PROFILES_TAXONOMY_TABLE,
                    ]
                },
            })

            tables.append({
                "name": f"custom_attribute_{attr_name}_predictions_columns",
                "description": f"Custom attribute {attr_name} predictions columns".capitalize(),
                "columns": [
                    {
                        "name": "index",
                        "type": "string",
                        "description": "",
                    },
                    {
                        "name": "taxonomy",
                        "type": "string",
                        "description": "",
                    },
                    {
                        "name": "col",
                        "type": "bigint",
                        "description": "",
                    },
                ],
                "meta": {
                    "repo": REPOSITORY_TAG,
                    "source": REPOSITORY_TAG,
                    "version": PROJECT_VERSION,
                },
            })

    sources = {
        "version": 2,
        "sources": [{
            "name": "custom_attributes",
            "description": "Custom attributes",
            "schema": '{{ env_var("TENANT", "riad") }}',
            "tables": tables,
        }]
    }

    return sources


def to_yaml(sources):
    return yaml.dump(
        sources, sort_keys=False, indent=2, explicit_start=True,
        default_flow_style=False, width=math.inf, Dumper=CustomDumper,
    )
