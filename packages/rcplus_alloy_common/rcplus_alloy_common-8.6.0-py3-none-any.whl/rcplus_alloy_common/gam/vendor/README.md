## GAM vendor models

GAM vendor models were generated with semi-automatic approach using WSDL definitions.
All definitions can be found in the official documentation https://developers.google.com/ad-manager/api/rel_notes
Select the appropriate version there (for example, `v202502`) and related service (for example, `OrderService`).
Its URL will be https://developers.google.com/ad-manager/api/reference/v202502/OrderService . On this page there
is references to the WSDL definition (see, `Production WSDL` section), for the `OrderService` it is
https://ads.google.com/apis/ads/publisher/v202502/OrderService?wsdl . Also here there is reference for some related
objects such as `Order` (as well as `LineItem` etc.).

From the WSDL links the whole schema definition is copied into appropriate model file (in this case `orders.py`).
The `Copilot` from `GitHub` is used to generate appropriate models based on the definitions copied from the full WSDL definition.
For example, for the `Order` object it would be definition in `<complexType name="Order">..</complexType name="Order">`.

Please note, that many definitions have nested definitions and additional types as well. For example, for the `Order` case
it also has the `OrderStatus` type which is defined in `<simpleType name="OrderStatus">..</simpleType name="OrderStatus">`.
In the code such types can be represented as literals (using Python's `Literal[str]`, this is older approach) or as `Enum`
(see example in `creatives.py`, this is newer approach).

Also please note that some common additional types already defined in the `common.py`, these are types such as 
`Date`, `DateTime`, `Money` etc. Probably most used is the `DateTime` and it must be used instead of `datetime` type.
`Copilot` always provides `datetime` type for time related fields because it is unaware of existing `DateTime`. Also
`Copilot` provides `str` for many nested types so such things also must be carefully checked.
Also all models must be derived from `common.GAMSOAPBaseModel` model and not from bare Pydantic `BaseModel`.

The possible prompts for `Copilot` are following:

    Generate me Python Pydantic model Placement based on this WSDL definition
    ```
    PUT WSDL DEFINITION XML HERE
    ```

    Generate me enumeration model in Python for this WSDL definition
    ```
    PUT WSDL DEFINITION XML HERE
    ```
