import re
import json
from dataclasses import dataclass, field


@dataclass
class DagRunEventMessage:
    dag_id: str
    dag_run_id: str | None = None
    logical_date: str | None = None
    conf: dict = field(default_factory=dict)
    note: str | None = None


TIME_UNITS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
}


@dataclass
class DagSlaConfig:
    """
    `sla_period` string could be defined as "12h", "3 days", "120 minutes" etc. strings
    """
    sla_period: str

    @staticmethod
    def parse_sla(sla_period_str):
        sla_period = re.findall(r"(\d+)\s*([a-zA-Z]+)", sla_period_str)
        if sla_period:
            sla_value, sla_unit = sla_period[0]
            sla_value = int(sla_value)
            sla_unit = sla_unit[0].lower()

            return sla_value * TIME_UNITS[sla_unit]

        raise ValueError(f"Incorrect SLA period definition '{sla_period_str}'")

    def to_json(self):
        copy = self.__dict__.copy()
        copy["sla_period"] = self.parse_sla(self.sla_period)
        return json.dumps(copy, default=str)
