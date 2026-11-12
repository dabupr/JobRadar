import pytest

from jobradar.dates import to_date


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-11-03T10:20:30Z", "2026-11-03"),
        ("2026-11-03T10:20:30.123+01:00", "2026-11-03"),
        ("2026-11-03", "2026-11-03"),
        ("2026-11-03 10:20:30 UTC", "2026-11-03"),
        ("Tue, 03 Nov 2026 10:20:30 +0000", "2026-11-03"),
        ("1793701230000", "2026-11-03"),
        (1793701230, "2026-11-03"),
        (None, None),
        ("", None),
        ("not a date", None),
    ],
)
def test_to_date(value, expected):
    assert to_date(value) == expected
