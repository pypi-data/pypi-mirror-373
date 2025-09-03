from qolab.hardware.scpi import response2numStr


def test_separator_and_unit():
    assert response2numStr("TDIV 2.00E-08S", firstSeparator=" ", unit="Z") == (
        "TDIV",
        "2.00E-08S",
        None,
    )  # incorrect unit was specified
    assert response2numStr("TDIV 2.00E-08S", firstSeparator=" ", unit="S") == (
        "TDIV",
        "2.00E-08",
        "S",
    )
    assert response2numStr("TDIV,2.00E-08S", firstSeparator=",", unit="S") == (
        "TDIV",
        "2.00E-08",
        "S",
    )


def test_separator_and_empty_unit():
    assert response2numStr("TDIV,2.00E-08", firstSeparator=",", unit=None) == (
        "TDIV",
        "2.00E-08",
        None,
    )
    assert response2numStr("TDIV,2.00E-08", firstSeparator=",", unit="") == (
        "TDIV",
        "2.00E-08",
        "",
    )


def test_no_separator_with_unit():
    assert response2numStr("2.00E-08S", firstSeparator=None, unit="S") == (
        None,
        "2.00E-08",
        "S",
    )
    assert response2numStr("2.00E-08S", firstSeparator="", unit="S") == (
        None,
        "2.00E-08",
        "S",
    )


def test_no_separator_and_no_unit():
    assert response2numStr("2.00E-08", firstSeparator=None, unit=None) == (
        None,
        "2.00E-08",
        None,
    )
    assert response2numStr("2.00E-08", firstSeparator="", unit="") == (
        None,
        "2.00E-08",
        "",
    )
