from typing import Annotated, ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from ocpi_pydantic.v221.base import OcpiBaseResponse, OcpiDisplayText
from ocpi_pydantic.v221.enum import OcpiCapabilityEnum, OcpiParkingRestrictionEnum, OcpiStatusEnum
from ocpi_pydantic.v221.locations import OcpiGeoLocation, OcpiImage
from ocpi_pydantic.v221.locations.connector import OcpiConnector



class OcpiStatusSchedule(BaseModel):
    '''
    OCPI 8.4.23. StatusSchedule class

    即使有狀態排程，還是要即時更新實際的狀態。
    '''
    period_begin: AwareDatetime = Field(description='Begin of the scheduled period.')
    period_end: Annotated[AwareDatetime | None, Field(description='End of the scheduled period, if known.')] = None
    status: OcpiStatusEnum = Field(description='Status value during the scheduled period.')



class OcpiEvse(BaseModel):
    '''
    OCPI 8.3.2. EVSE Object
    '''
    uid: str = Field(description='Uniquely identifies the EVSE within the CPOs platform (and suboperator platforms).', max_length=36)
    evse_id: Annotated[str | None, Field(
        max_length=48,
        description='''
        Compliant with the following specification for EVSE ID from "eMI3 standard version V1.0" (http://emi3group.com/documents-links/) "Part 2: business objects."
        ''',
    )] = None
    status: OcpiStatusEnum = Field(description='Indicates the current status of the EVSE.')
    status_schedule: Annotated[list[OcpiStatusSchedule], Field(description='Indicates a planned status update of the EVSE.')] = []
    capabilities: list[OcpiCapabilityEnum] = Field([], description='List of functionalities that the EVSE is capable of.')
    connectors: list[OcpiConnector] = Field(description='List of available connectors on the EVSE.', min_length=1)
    floor_level: str | None = Field(None, description='Level on which the Charge Point is located (in garage buildings) in the locally displayed numbering scheme.', max_length=4)
    coordinates: OcpiGeoLocation | None = Field(None, description='Coordinates of the EVSE.')
    physical_reference: str | None = Field(None, description='A number/string printed on the outside of the EVSE for visual identification.', max_length=16)
    directions: list[OcpiDisplayText] = Field([], description='Multi-language human-readable directions when more detailed information on how to reach the EVSE from the Location is required.')
    parking_restrictions: list[OcpiParkingRestrictionEnum] | None = Field(None, description='The restrictions that apply to the parking spot.')
    images: list[OcpiImage] = Field([], description='Links to images related to the EVSE such as photos or logos.')
    last_updated: AwareDatetime = Field(description='Timestamp when this EVSE or one of its Connectors was last updated (or created).')

    _example: ClassVar[dict] = {
        "uid": "3256",
        "evse_id": "BE*BEC*E041503003",
        "status": OcpiStatusEnum.AVAILABLE,
        "capabilities": [OcpiCapabilityEnum.RESERVABLE],
        "connectors": [OcpiConnector._example],
        "floor": '-1',
        "physical_reference": '3',
        "last_updated": "2019-06-24T12:39:09Z",
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiEvseListResponse(OcpiBaseResponse):
    data: list[OcpiEvse] = ...

    _examples: ClassVar[dict] = [{
        'data': [OcpiEvse._example], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiEvseResponse(OcpiBaseResponse):
    data: OcpiEvse = ...

    _examples: ClassVar[dict] = [{
        'data': OcpiEvse._example, 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})