from datetime import datetime, timezone
from typing import Annotated, ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from ocpi_pydantic.v221.base import OcpiBaseResponse, OcpiDisplayText
from ocpi_pydantic.v221.enum import OcpiEnergySourceCategoryEnum, OcpiEnvironmentalImpactCategoryEnum, OcpiFacilityEnum, OcpiParkingTypeEnum, OcpiTokenTypeEnum
from ocpi_pydantic.v221.locations import OcpiBusinessDetails, OcpiGeoLocation, OcpiImage
from ocpi_pydantic.v221.locations.evse import OcpiEvse



class OcpiPublishTokenType(BaseModel):
    '''
    OCPI 8.4.20. PublishTokenType class

    - uid、visual_number、group_id 至少要填一欄位。
    - 如果有 uid，type 也應該要有。
    - 如果有 visual_number，issuer 也應該要有。
    '''
    uid: Annotated[str | None, Field(description='Unique ID by which this Token can be identified.', max_length=36)] = None
    type: OcpiTokenTypeEnum | None = Field(None, description='Type of the token.')
    visual_number: str | None = Field(None, description='Visual readable number/identification as printed on the Token (RFID card).', max_length=64)
    issuer: str | None = Field(None, description='Issuing company, most of the times the name of the company printed on the token (RFID card), not necessarily the eMSP.', max_length=64)
    group_id: str | None = Field(None, description='This ID groups a couple of tokens.')

    @model_validator(mode='after')
    def validate_uid_visual_number_group_id(self):
        if not self.uid and not self.visual_number and not self.group_id:
            raise ValueError('At least one of the following fields SHALL be set: `uid`, `visual_number`, or `group_id`.')
        if self.uid and not self.type:
            raise ValueError('When `uid` is set, `type` SHALL also be set.')
        if self.visual_number and not self.issuer:
            raise ValueError('When `visual_number` is set, `issuer` SHALL also be set.')
        return self



class OcpiRegularHours(BaseModel):
    '''
    OCPI 8.4.21. REgularHours class

    Regular recurring operation or access hours.

    - `period_begin`:
        Begin of the regular period, in local time, given in hours and minutes. Must be in
        24h format with leading zeros. Example: "18:15". Hour/Minute separator: ":"
        Regex: `([0-1][0-9]|2[0-3]):[0-5][0-9]`.
    - `period_end`:
        End of the regular period, in local time, syntax as for `period_begin`. Must be
        later than `period_begin`.
    '''
    weekday: int = Field(description='Number of day in the week, from Monday (1) till Sunday (7)', ge=1, le=7)
    period_begin: str = Field(description='Begin of the regular period, in local time, given in hours and minutes.')
    period_end: str = Field(description='End of the regular period, in local time, syntax as for period_begin.')

    _example: ClassVar[dict] = {"weekday": 1, "period_begin": "08:00", "period_end": "20:00"}
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiExceptionalPeriod(BaseModel):
    '''
    OCPI 8.4.11. ExceptionalPeriod class
    '''
    period_begin: AwareDatetime = Field(description='Begin of the exception. In UTC, time_zone field can be used to convert to local time.')
    period_end: AwareDatetime = Field(description='End of the exception. In UTC, time_zone field can be used to convert to local time.')

    @field_validator('period_begin', 'period_end', mode='before')
    @classmethod
    def validate_datetime(cls, value: str | datetime, info: ValidationInfo):
        match type(value).__name__:
            case 'datetime': dt = value
            case 'str':
                try: dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z') # '2024-06-11T16:00:00Z' to datetime
                except ValueError: dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f%z') # '2024-06-11T16:00:00.123Z' to datetime
        dt = dt.replace(second=0, microsecond=0)
        if not dt.tzinfo: dt = dt.replace(tzinfo=timezone.utc)
        return dt
    
    _examples: ClassVar[list[dict]] = [{'period_begin': '2018-12-25T03:00:00Z', 'period_end': '2018-12-25T05:00:00Z'}]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiHours(BaseModel):
    '''
    OCPI 8.4.14. Hours class
    '''
    twentyfourseven: bool = Field(description='True to represent 24 hours a day and 7 days a week, except the given exceptions.')
    regular_hours: Annotated[list[OcpiRegularHours], Field(description='Regular hours, weekday-based.')] = []
    exceptional_openings: list[OcpiExceptionalPeriod] = Field([], description='Exceptions for specified calendar dates, time-range based.')
    exceptional_closings: list[OcpiExceptionalPeriod] = Field([], description='Exceptions for specified calendar dates, time-range based.')

    _examples: ClassVar[list[dict]] = [
        # 8.4.14.1. Example: 24/7 open with exceptional closing.
        {"twentyfourseven": True, "exceptional_closings": [{"period_begin": "2018-12-25T03:00:00Z", "period_end": "2018-12-25T05:00:00Z"}]},
        # 8.4.14.2. Example: Opening Hours with exceptional closing.
        {
            "twentyfourseven": False,
            "regular_hours": [
                {"weekday": 1, "period_begin": "01:00", "period_end": "06:00"},
                {"weekday": 2, "period_begin": "01:00", "period_end": "06:00"},
            ],
            "exceptional_closings": [{'period_begin': '2018-12-25T03:00:00Z', 'period_end': '2018-12-25T05:00:00Z'}],
        },
        # 8.4.14.3. Example: Opening Hours with exceptional opening.
        {
            "twentyfourseven": False,
            "regular_hours": [
                {"weekday": 1, "period_begin": "00:00", "period_end": "04:00"},
                {"weekday": 2, "period_begin": "00:00", "period_end": "04:00"}
            ],
            "exceptional_openings": [{'period_begin': '2018-12-25T03:00:00Z', 'period_end': '2018-12-25T05:00:00Z'}],
        },
    ]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class AdditionalGeoLocation(BaseModel):
    r'''
    OCPI 8.4.1. AdditionalGeoLoation class

    This class defines an additional geo location that is relevant for the Charge Point. The geodetic system to be used is WGS 84.

    - `latitude`:
        Latitude of the point in decimal degree. Example: 50.770774. Decimal
        separator: "`.`" Regex: `-?[0-9]{1,2}\.[0-9]{5,7}`
    - `longitude`:
        Longitude of the point in decimal degree. Example: -126.104965. Decimal
        separator: "`.`" Regex: `-?[0-9]{1,3}\.[0-9]{5,7}`
    - `name`:
        Name of the point in local language or as written at the location. For example
        the street name of a parking lot entrance or it’s number.
    '''
    latitude: str = Field(description='Latitude of the point in decimal degree.', max_length=10)
    longitude: str = Field(description='Longitude of the point in decimal degree.', max_length=11)
    name: OcpiDisplayText | None = Field(None, description='Name of the point in local language or as written at the location.')

    _example: ClassVar[dict] = {"latitude": "51.047599", "longitude": "3.729944"}
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiEnergySource(BaseModel): 
    '''
    OCPI 8.4.7. EnergySource class

    Key-value pairs (enum + percentage) of energy sources. All given values of all categories should add up to 100 percent.
    '''
    source: OcpiEnergySourceCategoryEnum = Field(description='The type of energy source.')
    percentage: float = Field(description='Percentage of this source (0-100) in the mix.', gt=0, le=100)



class OcpiEnvironmentalImpact(BaseModel):
    '''
    OCPI 8.4.9. EnvironmentalImpact class
    '''
    category: OcpiEnvironmentalImpactCategoryEnum = Field(description='The environmental impact category of this value.')
    amount: float = Field(description='Amount of this portion in g/kWh.', gt=0)



class OcpiEnergyMix(BaseModel):
    '''
    OCPI 8.4.6. EnergyMix class
    '''
    is_green_energy: bool = Field(description='True if 100% from regenerative sources. (CO2 and nuclear waste is zero)')
    energy_sources: list[OcpiEnergySource] = Field([], description='Key-value pairs (enum + percentage) of energy sources of this location’s tariff.')
    environ_impact: list[OcpiEnvironmentalImpact] = Field([], description='Key-value pairs (enum + percentage) of nuclear waste and CO2 exhaust of this location’s tariff.')
    supplier_name: str | None = Field(None, description='Name of the energy supplier, delivering the energy for this location or tariff.', max_length=64)
    evergy_product_name: str | None = Field(None, description='Name of the energy suppliers product/tariff plan used at this location.', max_length=64)

    _examples: ClassVar[list[dict]] = [
        # Simple
        {"is_green_energy": True},
        # Tariff energy provider name
        {"is_green_energy": True, "supplier_name": "Greenpeace Energy eG", "energy_product_name": "eco-power"},
        # Complete
        {
            "is_green_energy": False,
            "energy_sources": [
                { "source": "GENERAL_GREEN", "percentage": 35.9 },
                { "source": "GAS", "percentage": 6.3 },
                { "source": "COAL", "percentage": 33.2 },
                { "source": "GENERAL_FOSSIL", "percentage": 2.9 },
                { "source": "NUCLEAR", "percentage": 21.7 },
            ],
            "environ_impact": [
                { "category": "NUCLEAR_WASTE", "amount": 0.0006 },
                { "category": "CARBON_DIOXIDE", "amount": 372 },
            ],
            "supplier_name": "E.ON Energy Deutschland",
            "energy_product_name": "E.ON DirektStrom eco",
        },
    ]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiLocation(BaseModel):
    '''
    OCPI 8.3.1. Location Object
    
    The _Location_ object describes the location and its properties where a group of EVSEs that belong together are installed. Typically,
    the _Location_ object is the exact location of the group of EVSEs, but it can also be the entrance of a parking garage which contains
    these EVSEs. The exact way to reach each EVSE can be further specified by its own properties.

    Locations may be shown in apps or on websites etc. when the flag: `publish` is set to `true`. Locations that have this flag set to
    `false` SHALL not be shown in an app or on a website etc. unless it is to the owner of a Token in the `publish_allowed_to` list.
    Even parties like NSP or eMSP that do not 'own' this Token MAY show this location on an app or website, but only to the owner of
    that Token. If the user of their app/website has provided information about his/her Token, And that information matches all the fields
    of one of the PublishToken tokens in the list, then they are allowed to show this location to their user. It is not allowed in OCPI to
    use a Token that is not 'owned' by the eMSP itself to start a charging session.

    Private Charge Points, home or business that do not need to be published on apps, and do not require remote control via OCPI,
    SHOULD not be PUT via the OCPI Locations module. Reimbursement via eMSP is still possible by sending CDRs to eMSP, the
    Locations module is not needed for this..
    '''

    country_code: str = Field(description="ISO-3166 alpha-2 country code of the CPO that 'owns' this Location.", min_length=2, max_length=2)
    party_id: str = Field(description="ID of the CPO that 'owns' this Location (following the ISO-15118 standard).", min_length=3, max_length=3)
    id: str = Field(description='Uniquely identifies the location within the CPOs platform (and suboperator platforms).', max_length=36)
    name: Annotated[str | None, Field(description='Display name of the location.')] = None

    publish: bool = Field(description='Defines if a Location may be published on an website or app etc.')
    publish_allowed_to: list[OcpiPublishTokenType] = Field([], description='This field may only be used when the publish field is set to false.')

    time_zone: str = Field(description='One of IANA tzdata’s TZ-values representing the time zone of the location.')
    coordinates: OcpiGeoLocation = Field(description='Coordinates of the location.')
    postal_code: Annotated[str | None, Field(
        max_length=10,
        description='''
        Postal code of the location, may only be omitted when the location has no postal
        code.
        ''',
    )] = None
    country: str = Field(max_length=3, description='ISO 3166-1 alpha-3 code for the country of this location.')
    state: Annotated[str | None, Field(max_length=20, description='State or province of the location, only to be used when relevant.')] = None
    city: str = Field(max_length=45, description='City or town.')
    address: str = Field(max_length=45, description='Street/block name and house number if available.')
    opening_times: OcpiHours | None = Field(None, description='The times when the EVSEs at the location can be accessed for charging.')
    charging_when_closed: Annotated[bool | None, Field(description='Indicates if the EVSEs are still charging outside the opening hours of the location. Default: true')] = True

    related_locations: list[AdditionalGeoLocation] = Field([], description='Geographical location of related points relevant to the user.')
    parking_type: OcpiParkingTypeEnum | None = Field(None, description='The general type of parking at the charge point location.')
    evses: list[OcpiEvse] = Field([], description='List of EVSEs that belong to this Location.')
    directions: list[OcpiDisplayText] = Field([], description='Human-readable directions on how to reach the location.')
    operator: OcpiBusinessDetails | None = Field(None, description='Information of the operator.')
    suboperator: OcpiBusinessDetails | None = Field(None, description='Information of the suboperator if available.')
    owner: OcpiBusinessDetails | None = Field(None, description='Information of the owner if available.')
    facilities: list[OcpiFacilityEnum] | None = Field(None, description='Optional list of facilities this charging location directly belongs to.')
    images: list[OcpiImage] = Field([], description='Links to images related to the location such as photos or logos.')
    energy_mix: Annotated[OcpiEnergyMix | None, Field(description='Details on the energy supplied at this location.')] = None
    last_updated: AwareDatetime = Field(description='Timestamp when this Location or one of its EVSEs or Connectors were last updated (or created).')

    _examples: ClassVar[list[dict]] = [
        { # 8.3.1.1. Example public charging location
            "country_code": "BE",
            "party_id": "BEC",
            "id": "LOC1",
            "name": "Gent Zuid",

            "publish": True,

            "time_zone": "Europe/Brussels",
            "coordinates": {"latitude": "51.047599", "longitude": "3.729944"},
            "postal_code": "9000",
            "country": "BEL",
            "city": "Gent",
            "address": "F.Rooseveltlaan 3A",

            "parking_type": "ON_STREET",
            "evses": [
                {
                    "uid": "3256",
                    "evse_id": "BE*BEC*E041503001",
                    "status": "AVAILABLE",
                    "capabilities": ["RESERVABLE"],
                    "connectors": [
                        {
                            "id": "1",
                            "standard": "IEC_62196_T2",
                            "format": "CABLE",
                            "power_type": "AC_3_PHASE",
                            "max_voltage": 220,
                            "max_amperage": 16,
                            "tariff_ids": ["11"],
                            "last_updated": "2015-03-16T10:10:02Z"
                        },
                        {
                            "id": "2",
                            "standard": "IEC_62196_T2",
                            "format": "SOCKET",
                            "power_type": "AC_3_PHASE",
                            "max_voltage": 220,
                            "max_amperage": 16,
                            "tariff_ids": ["13"],
                            "last_updated": "2015-03-18T08:12:01Z"
                        }
                    ],
                        "physical_reference": "1",
                        "floor_level": "-1",
                        "last_updated": "2015-06-28T08:12:01Z"
                    },
                {
                    "uid": "3257",
                    "evse_id": "BE*BEC*E041503002",
                    "status": "RESERVED",
                    "capabilities": [
                        "RESERVABLE"
                    ],
                    "connectors": [{
                        "id": "1",
                        "standard": "IEC_62196_T2",
                        "format": "SOCKET",
                        "power_type": "AC_3_PHASE",
                        "max_voltage": 220,
                        "max_amperage": 16,
                        "tariff_ids": ["12"],
                        "last_updated": "2015-06-29T20:39:09Z"
                    }],
                    "physical_reference": "2",
                    "floor_level": "-2",
                    "last_updated": "2015-06-29T20:39:09Z"
                }
            ],
            "operator": {"name": "BeCharged"},
            "last_updated": "2015-06-29T20:39:09Z"
        },
        { # 8.3.1.2. Example destination charging location
            "country_code": "NL",
            "party_id": "ALF",
            "id": "3e7b39c2-10d0-4138-a8b3-8509a25f9920",
            "name": "ihomer",

            "publish": True,

            "time_zone": "Europe/Amsterdam",
            "coordinates": {"latitude": "51.562787", "longitude": "4.638975"},
            "postal_code": "4876 BS",
            "country": "NLD",
            "city": "Etten-Leur",
            "address": "Tamboerijn 7",

            "parking_type": "PARKING_LOT",
            "evses": [{
                "uid": "fd855359-bc81-47bb-bb89-849ae3dac89e",
                "evse_id": "NL*ALF*E000000001",
                "status": "AVAILABLE",
                "connectors": [{
                    "id": "1",
                    "standard": "IEC_62196_T2",
                    "format": "SOCKET",
                    "power_type": "AC_3_PHASE",
                    "max_voltage": 220,
                    "max_amperage": 16,
                    "last_updated": "2019-07-01T12:12:11Z"
                }],
                "parking_restrictions": [ "CUSTOMERS" ],
                "last_updated": "2019-07-01T12:12:11Z",
            }],
            "last_updated": "2019-07-01T12:12:11Z",
        },
        { # 8.3.1.3. Example destination charging location not published, but paid guest usage possible
            "country_code": "NL",
            "party_id": "ALF",
            "id": "3e7b39c2-10d0-4138-a8b3-8509a25f9920",
            "name": "ihomer",

            "publish": False,

            "time_zone": "Europe/Amsterdam",
            "coordinates": {"latitude": "51.562787","longitude": "4.638975"},
            "postal_code": "4876 BS",
            "country": "NLD",
            "city": "Etten-Leur",
            "address": "Tamboerijn 7",

            "evses": [{
                "uid": "fd855359-bc81-47bb-bb89-849ae3dac89e",
                "evse_id": "NL*ALF*E000000001",
                "status": "AVAILABLE",
                "connectors": [{
                    "id": "1",
                    "standard": "IEC_62196_T2",
                    "format": "SOCKET",
                    "power_type": "AC_3_PHASE",
                    "max_voltage": 220,
                    "max_amperage": 16,
                    "last_updated": "2019-07-01T12:12:11Z",
                }],
                "parking_restrictions": [ "CUSTOMERS" ],
                "last_updated": "2019-07-01T12:12:11Z",
            }],
            "last_updated": "2019-07-01T12:12:11Z"
        },
        { # 8.3.1.4. Example charging location with limited visibility
            "country_code": "NL",
            "party_id": "ALL",
            "id": "f76c2e0c-a6ef-4f67-bf23-6a187e5ca0e0",
            "name": "Water State",

            "publish": False,
            "publish_allowed_to": [
                {"visual_number": "12345-67", "issuer": "NewMotion"},
                {"visual_number": "0055375624", "issuer": "ANWB"},
                {"uid": "12345678905880", "type": "RFID"},
            ],

            "time_zone": "Europe/Amsterdam",
            "coordinates": {"latitude": "53.213763", "longitude": "5.804638"},
            "postal_code": "8923 EM",
            "country": "NLD",
            "city": "Leeuwarden",
            "address": "Taco van der Veenplein 12",

            "parking_type": "UNDERGROUND_GARAGE",
            "evses": [{
                "uid": "8c1b3487-61ac-40a7-a367-21eee99dbd90",
                "evse_id": "NL*ALL*EGO0000013",
                "status": "AVAILABLE",
                "connectors": [{
                    "id": "1",
                    "standard": "IEC_62196_T2",
                    "format": "SOCKET",
                    "power_type": "AC_3_PHASE",
                    "max_voltage": 230,
                    "max_amperage": 16,
                    "last_updated": "2019-09-27T00:19:45Z",
                }],
                "last_updated": "2019-09-27T00:19:45Z"
            }],
            "last_updated": "2019-09-27T00:19:45Z",
        },
        { # 8.3.1.5. Example private charge point with eMSP app control
            "country_code": "DE",
            "party_id": "ALL",
            "id": "a5295927-09b9-4a71-b4b9-a5fffdfa0b77",

            "publish": False,
            "publish_allowed_to": [{"visual_number": "0123456-99", "issuer": "MoveMove"}],

            "time_zone": "Europe/Berlin",
            "coordinates": {"latitude": "50.931826", "longitude": "6.964043"},
            "postal_code": "50931",
            "country": "DEU",
            "city": "Köln",
            "address": "Krautwigstraße 283A",

            "parking_type": "ON_DRIVEWAY",
            "evses": [{
                "uid": "4534ad5f-45be-428b-bfd0-fa489dda932d",
                "evse_id": "DE*ALL*EGO0000001",
                "status": "AVAILABLE",
                "connectors": [{
                    "id": "1",
                    "standard": "IEC_62196_T2",
                    "format": "SOCKET",
                    "power_type": "AC_1_PHASE",
                    "max_voltage": 230,
                    "max_amperage": 8,
                    "last_updated": "2019-04-05T17:17:56Z"
                }],
                "last_updated": "2019-04-05T17:17:56Z",
            }],
            "last_updated": "2019-04-05T17:17:56Z"
        },
        { # 8.3.1.6. Example charge point in a parking garage with opening hours
            "country_code": "SE",
            "party_id": "EVC",
            "id": "cbb0df21-d17d-40ba-a4aa-dc588c8f98cb",
            "name": "P-Huset Leonard",

            "publish": True,

            "time_zone": "Europe/Stockholm",
            "coordinates": {"latitude": "55.590325", "longitude": "13.008307"},
            "postal_code": "214 26",
            "country": "SWE",
            "city": "Malmö",
            "address": "Claesgatan 6",
            "opening_times": {
                "twentyfourseven": False,
                "regular_hours": [
                    {"weekday": 1, "period_begin": "07:00", "period_end": "18:00"},
                    {"weekday": 2, "period_begin": "07:00", "period_end": "18:00"},
                    {"weekday": 3, "period_begin": "07:00", "period_end": "18:00"},
                    {"weekday": 4, "period_begin": "07:00", "period_end": "18:00"},
                    {"weekday": 5, "period_begin": "07:00", "period_end": "18:00"},
                    {"weekday": 6, "period_begin": "07:00", "period_end": "18:00"},
                    {"weekday": 7, "period_begin": "07:00", "period_end": "18:00"},
                ],
            },
            "charging_when_closed": True,

            "parking_type": "PARKING_GARAGE",
            "evses": [{
                "uid": "eccb8dd9-4189-433e-b100-cc0945dd17dc",
                "evse_id": "SE*EVC*E000000123",
                "status": "AVAILABLE",
                "connectors": [{
                    "id": "1",
                    "standard": "IEC_62196_T2",
                    "format": "SOCKET",
                    "power_type": "AC_3_PHASE",
                    "max_voltage": 230,
                    "max_amperage": 32,
                    "last_updated": "2017-03-07T02:21:22Z",
                }],
                "last_updated": "2017-03-07T02:21:22Z"
            }],
            "last_updated": "2017-03-07T02:21:22Z"
        },
    ]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})




class OcpiLocationListResponse(OcpiBaseResponse):
    data: list[OcpiLocation] = ...

    _examples: ClassVar[dict] = [{
        'data': [OcpiLocation._examples[0]], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiLocationResponse(OcpiBaseResponse):
    data: OcpiLocation = ...

    _examples: ClassVar[dict] = [{
        'data': OcpiLocation._examples[0], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})