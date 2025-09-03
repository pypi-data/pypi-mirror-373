from datetime import datetime, timezone

from pydantic import ValidationError
from pytest import raises

from ocpi_pydantic.v221.commands import OcpiStartSession
from ocpi_pydantic.v221.enum import OcpiTokenTypeEnum, OcpiWhitelistTypeEnum
from ocpi_pydantic.v221.tokens import OcpiToken


class TestCommands:
    ocpi_token = OcpiToken(
            country_code='TW',
            party_id='PID',
            uid='uid1',
            type=OcpiTokenTypeEnum.AD_HOC_USER,
            contract_id='cid1',
            issuer='i1',
            valid=True,
            whitelist=OcpiWhitelistTypeEnum.ALLOWED,
            last_updated=datetime.now(timezone.utc),
        )
    

    def test_start_session_model_with_fill_all_fields(self):
        assert OcpiStartSession(
            response_url='https://example.com/response',
            token=TestCommands.ocpi_token,
            location_id='lid1',
            evse_uid='puid1',
            connector_id='cid1',
            authorization_reference=None,
        )


    def test_start_session_model_with_conector_id_but_missing_evse_uid(self):
        with raises(ValidationError, match='`evse_uid` is required when connector_id is set.') as e:
            OcpiStartSession(
                response_url='https://example.com/response',
                token=TestCommands.ocpi_token,
                location_id='lid1',
                evse_uid=None,
                connector_id='cid1',
                authorization_reference=None,
            )