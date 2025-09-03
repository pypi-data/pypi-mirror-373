
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from ocpi_pydantic.v221.base import OcpiBaseResponse
from ocpi_pydantic.v221.enum import OcpiPartyRoleEnum
from ocpi_pydantic.v221.locations import OcpiBusinessDetails



class OcpiCredentialsRole(BaseModel):
    '''
    OCPI 7.4.1 CredentialsRole class
    '''
    role: OcpiPartyRoleEnum = Field(description='Type of role.')
    business_details: OcpiBusinessDetails = Field(description='Details of this party.')
    party_id: str = Field(
        description='CPO, eMSP (or other role) ID of this party (following the ISO-15118 standard).',
        min_length=3, max_length=3,
    )
    country_code: str = Field(
        description='ISO-3166 alpha-2 country code of the country this party is operating in.',
        min_length=2, max_length=2,
    )

    _example: ClassVar[dict] = {
        'role': OcpiPartyRoleEnum.CPO,
        'party_id': 'WNC',
        'country_code': 'TW',
        'business_details': OcpiBusinessDetails._example,
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})




class OcpiCredentials(BaseModel):
    '''
    OCPI 7.3.1 Credentials object

    甲、乙兩系統要認證，甲為 Sender、乙為 Receiver，實務上誰是 Sender 誰是 Receiver 雙方自行協調。

    1. Receiver 乙生成給 Sender 甲的 token_A，以郵件或其他方式交給 Sender 甲。
    2. Sender 甲開始註冊流程，Sender 甲生成一組 token_B，POST 打給 Receiver 乙的 credential 端點，請求 HTTP 附上 token_A 作為身份識別用。
    3. Receiver 乙收到 Sender 甲打過來的資訊，利用 HTTP 標頭的 token_A 確認身份，把收到的 token_B 存下來。
    4. Receiver 乙還要回應 Sender 甲的請求，Receiver 乙生成一組 token_C 回應給 Sender 甲。
    5. 至此完成 token 交換：
            - Receiver 乙持有 Sender 甲發來的 token_B，往後 Receiver 乙發給 Sender 甲的請求，都附上此 token_B。
            - Sender 甲持有 Receiver 乙回覆的 token_C，往後 Sender 甲發給 Receiver 乙的請求，都附上此 token_C。
            - Token_A 已無用，可割可棄。

    ---

    OCPI 建議 token 每個月更換一次。

    ---

    如果我是 Receiver：

    - 我生成 token_A 交給 Sender。
    - Sender 註冊時打 token_B 給我。
    - 我再生成 token_C 回覆給 Sender。
    - 往後我打給 Sender 的請求都帶上 token_B 給它識別身份。
    - 往後 Sender 打給我的請求都帶上 token_C 給我識別身份。

    此情況下 token_A 與 token_C 都由我生成，我用 JWT 再算成 Base64 給它。我可以直接以 JWT 驗證請求方身份。

    ---
    
    如果我是 Sender：

    - Receiver 生成 token_A 交給我。
    - 我生成 token_B 打給 Receiver 註冊。
    - Receiver 再生成 token_C 回覆給我。
    - 往後我打給 Receiver 的請求都帶上 token_C 給它識別身份。
    - 往後 Receiver 打給我的請求都帶上 token_B 給我識別身份。

    此情況下 token_B 由我生成，我用 JWT 再算成 Base64 給它。我可以直接以 JWT 驗證請求方身份。
    '''
    token: str = Field(description='The credentials token for the other party to authenticate in your system.')
    url: HttpUrl = Field(description='The URL to your API versions endpoint.')
    roles: list[OcpiCredentialsRole] = Field(description='List of the roles this party provides.')

    _example: ClassVar[dict] = {
        'token': '01JM2S75MMNRXX4M5FPGA9P1AP', # ULID
        'url': 'https://example.com/ocpi/versions',
        'roles': [OcpiCredentialsRole._example],
    }
    model_config = ConfigDict(json_schema_extra={'examples': [_example]})




class OcpiCredentialsResponse(OcpiBaseResponse):
    data: OcpiCredentials = ...

    _examples: ClassVar[dict] = [{ # Version details response (one object)
        'data': OcpiCredentials._example, 'status_code': 1000, 'timestamp': '2015-06-30T21:59:59Z',
    }]
    model_config = ConfigDict(json_schema_extra={'examples': _examples})
