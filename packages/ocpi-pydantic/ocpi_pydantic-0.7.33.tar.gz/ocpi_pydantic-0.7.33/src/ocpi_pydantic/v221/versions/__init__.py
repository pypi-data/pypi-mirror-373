from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ocpi_pydantic.v221.base import OcpiBaseResponse
from ocpi_pydantic.v221.enum import OcpiInterfaceRoleEnum, OcpiModuleIdEnum, OcpiVersionNumberEnum



class OcpiEndpoint(BaseModel):
    '''
    OCPI 6.2.2. Endpoint class

    NOTE: for the `credentials` module, the role is not relevant as this module is the same for all roles.
    '''
    identifier: OcpiModuleIdEnum = Field(description='Endpoint identifier.')
    role: OcpiInterfaceRoleEnum = Field(description='Interface role this endpoint implements.')
    url: HttpUrl = Field(description='URL to the endpoint.')

    _examples: ClassVar[list[dict]] = [
        {
            'identifier': OcpiModuleIdEnum.credentials,
            'role': OcpiInterfaceRoleEnum.RECEIVER,
            'url': 'https://example.com/ocpi/cpo/2.2/credentials',
        },
        {
            'identifier': OcpiModuleIdEnum.locations,
            'role': OcpiInterfaceRoleEnum.SENDER,
            'url': 'https://example.com/ocpi/cpo/2.2/locations',
        },
        {
            'identifier': OcpiModuleIdEnum.tokens,
            'role': OcpiInterfaceRoleEnum.RECEIVER,
            'url': 'https://example.com/ocpi/cpo/2.2/tokens',
        },
        {
            'identifier': OcpiModuleIdEnum.locations,
            'role': OcpiInterfaceRoleEnum.RECEIVER,
            'url': 'https://example.com/ocpi/emsp/2.2/locations',
        },
        {
            'identifier': OcpiModuleIdEnum.tokens,
            'role': OcpiInterfaceRoleEnum.SENDER,
            'url': 'https://example.com/ocpi/emsp/2.2/tokens',
        },
    ]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiVersion(BaseModel):
    version: OcpiVersionNumberEnum
    url: HttpUrl

    _example: ClassVar[dict] = {
        'version': OcpiVersionNumberEnum.v221, 'url': 'https://example.com/ocpi/cpo/2.2/',
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiVersionDetail(BaseModel):
    version: OcpiVersionNumberEnum = Field(description='The version number.')
    endpoints: list[OcpiEndpoint] = Field(description='A list of supported endpoints for this version.')

    _example: ClassVar[dict] = {
        'version': OcpiVersionNumberEnum.v221,
        'endpoints': OcpiEndpoint._examples,
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})



class OcpiVersionsResponse(OcpiBaseResponse):
    data: list[OcpiVersion] = []

    _examples: ClassVar[dict] = [{ # Version information response (list of objects)
        'data': [OcpiVersion._example], 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})



class OcpiVersionDetailsResponse(OcpiBaseResponse):
    data: OcpiVersionDetail = ...

    _examples: ClassVar[dict] = [{ # Version details response (one object)
        'data': OcpiVersionDetail._example, 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})