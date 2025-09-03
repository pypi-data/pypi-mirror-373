from datetime import datetime, timezone

from ocpi_pydantic.v221.locations.location import OcpiExceptionalPeriod


class TestLocations:
    def test_exceptional_period_model_with_datetime_string(self):
        p = OcpiExceptionalPeriod.model_validate({
            'period_begin': '2018-12-25T03:00:00Z', 'period_end': '2018-12-25T05:00:00Z',
        })
        assert p


    def test_exceptioal_period_model_with_datetime_instance(self):
        p_no_tz = OcpiExceptionalPeriod.model_validate({
            'period_begin': datetime(2018, 12, 25, 3, 0, 0, 0),
            'period_end': datetime(2018, 12,25, 5, 0, 0, 0),
        })
        assert p_no_tz

        p_tz = OcpiExceptionalPeriod.model_validate({
            'period_begin': datetime(2018, 12, 25, 3, 0, 0, 0, timezone.utc),
            'period_end': datetime(2018, 12,25, 5, 0, 0, 0, timezone.utc),
        })