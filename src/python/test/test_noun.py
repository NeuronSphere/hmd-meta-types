from datetime import date, time, datetime, timezone, timedelta

import re
import pytest
from dateutil.parser import isoparse


class TestNoun:
    def test_namespace_name(self, anoun):
        assert anoun.get_namespace_name() == "name.space.a_noun"

    def test_okay(self, anoun):
        datetime_value = datetime.now().astimezone()
        noun1 = anoun(
            **{
                "field1": "hello",
                "field2": 5,
                "field3": "b",
                "timestampfield": datetime_value,
            }
        )
        assert noun1.field1 == "hello"
        assert noun1.field2 == 5
        assert noun1.field3 == "b"
        assert noun1.timestampfield == datetime_value

        assert noun1.serialize() == {
            "field1": "hello",
            "field2": 5,
            "field3": "b",
            "timestampfield": datetime_value.astimezone(timezone.utc).isoformat(
                timespec="milliseconds"
            ),
        }

    def test_instance_type(self, anoun):
        noun1 = anoun(**{"field1": "hello", "field2": 5})

        assert noun1.instance_type == anoun

    def test_bad_type(self, anoun):
        with pytest.raises(
            Exception,
            match='For field, field1, expected a value of one of the types: "str", was "int"',
        ) as exc:
            noun1 = anoun(**{"field1": 5, "field2": 5})

    def test_missing_required_field(self, anoun):
        with pytest.raises(
            Exception, match="Missing required fields: {'field1'}"
        ) as exc:
            noun1 = anoun(**{"field2": 5})

    def test_bad_enum_type(self, anoun):
        with pytest.raises(
            Exception,
            match=re.escape("For field, field3, expected one of ['a', 'b'], was \"c\""),
        ) as exc:
            noun1 = anoun(**{"field1": "hello", "field2": 5, "field3": "c"})

    def test_bad_date_type(self, anoun):
        with pytest.raises(
            Exception,
            match='For field, timestampfield, expected a value of one of the types: "datetime", "str", was "int"',
        ) as exc:
            noun1 = anoun(**{"field1": "hello", "timestampfield": 5})

    def test_invalid_date_string(self, anoun):
        with pytest.raises(
            Exception,
            match='Invalid value for field, "timestampfield": 1985-13-01T00:00:00. Error: month must be in 1..12',
        ) as exc:
            noun1 = anoun(
                **{"field1": "hello", "timestampfield": "1985-13-01T00:00:00"}
            )

    def test_timestamp_as_string_string(self, anoun):
        time_string = "1985-12-01T00:00:00Z"
        noun1 = anoun(**{"field1": "hello", "timestampfield": time_string})

        assert isinstance(noun1.timestampfield, datetime)
        assert noun1.timestampfield == isoparse(time_string)

        assert noun1.serialize() == {
            "field1": "hello",
            "timestampfield": isoparse(time_string).isoformat(timespec="milliseconds"),
        }

        # a datetime in the local timezone
        a_datetime = datetime.now().astimezone()
        noun1.timestampfield = a_datetime

        # confirm the offset from utc is non-zero
        assert a_datetime.tzinfo.utcoffset(noun1.timestampfield).seconds > 0
        # confirm the datetime object in noun1 has a zero offset (because it's in utc)
        assert noun1.timestampfield.tzinfo.utcoffset(noun1.timestampfield) == timedelta(
            0
        )
        # confirm the two dates are equal
        assert a_datetime == noun1.timestampfield

        assert noun1.timestampfield.isoformat(
            timespec="milliseconds"
        ) != a_datetime.isoformat(timespec="milliseconds")
        assert noun1.timestampfield.isoformat(
            timespec="milliseconds"
        ) == a_datetime.astimezone(timezone.utc).isoformat(timespec="milliseconds")
