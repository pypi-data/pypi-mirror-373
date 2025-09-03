from typing import Annotated, ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, HttpUrl

from ocpi_pydantic.v221.base import OcpiBaseResponse
from ocpi_pydantic.v221.enum import OcpiConnectorFormatEnum, OcpiConnectorTypeEnum, OcpiPowerTypeEnum



class OcpiConnector(BaseModel):
    '''
    OCPI 8.3.3. Connector Object

    A _Connector_ is the _socket_ or _cable and plug_ available for the EV to use. A single EVSE may provide multiple Connectors but only
    one of them can be in use at the same time. A Connector always belongs to an EVSE object.

    - `max_voltage`:
        Maximum voltage of the connector (line to neutral for AC_3_PHASE), in
        volt [V]. For example: DC Chargers might vary the voltage during
        charging when battery almost full.
    - `max_electric_power`:
        Maximum electric power that can be delivered by this connector, in
        Watts (W). When the maximum electric power is lower than the
        calculated value from `voltage` and `amperage`, this value should be
        set.
        For example: A DC Charge Point which can delivers up to 920V and up
        to 400A can be limited to a maximum of 150kW (max_electric_power =
        150000). Depending on the car, it may supply max voltage or current,
        but not both at the same time.
        For AC Charge Points, the amount of phases used can also have
        influence on the maximum power.
    - `tariff_ids`:
        Identifiers of the currently valid charging tariffs. Multiple tariffs are
        possible, but only one of each Tariff.type can be active at the same time.
        Tariffs with the same type are only allowed if they are not active at the
        same time: start_date_time and end_date_time period not overlapping.
        When preference-based smart charging is supported, one tariff for
        every possible ProfileType should be provided. These tell the user about
        the options they have at this Connector, and what the tariff is for every
        option.
        For a "free of charge" tariff, this field should be set and point to a
        defined "free of charge" tariff.
    '''
    id: str = Field(
        max_length=36,
        description='''
        Identifier of the Connector within the EVSE. Two Connectors may have
        the same id as long as they do not belong to the same _EVSE_ object.
        ''',
    )
    standard: OcpiConnectorTypeEnum = Field(description='The standard of the installed connector.')
    format: OcpiConnectorFormatEnum = Field(description='The format (socket/cable) of the installed connector.')
    power_type: OcpiPowerTypeEnum
    max_voltage: int = Field(description='Maximum voltage of the connector (line to neutral for AC_3_PHASE), in volt [V].', gt=0)
    max_amperage: int = Field(description='Maximum amperage of the connector, in ampere [A].', gt=0)
    max_electric_power: Annotated[int | None, Field(description='Maximum electric power that can be delivered by this connector, in Watts (W).', gt=0)] = None
    tariff_ids: Annotated[list[str], Field(description='Identifiers of the currently valid charging tariffs.')] = []
    terms_and_conditions: HttpUrl | None = Field(None, description='URL to the operator’s terms and conditions.')
    last_updated: AwareDatetime = Field(description='Timestamp when this Connector was last updated (or created).')

    _example: ClassVar[dict] = {
        "id": "1",
        "standard": OcpiConnectorTypeEnum.IEC_62196_T2,
        "format": OcpiConnectorFormatEnum.SOCKET,
        "tariff_ids": ["14"],
        
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})


class OcpiConnectorResponse(OcpiBaseResponse):
    data: OcpiConnector = ...

    _examples: ClassVar[dict] = [{ # Version details response (one object)
        'data': OcpiConnector._example, 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})