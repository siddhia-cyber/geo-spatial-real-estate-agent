from services.query_parser import parse_query


def test_parse_bhk_and_price_lakh():
    q = "2 bhk flat under 80 lakh with gym"
    result = parse_query(q)

    assert result["bhk"] == 2
    assert result["max_price"] == 8000000
    assert result["require_gym"] is True


def test_parse_crore_price():
    q = "3 bhk apartment under 1.5 crore"
    result = parse_query(q)

    assert result["bhk"] == 3
    assert result["max_price"] == 15000000


def test_parse_no_filters():
    q = "flat near metro station"
    result = parse_query(q)

    assert result["bhk"] is None
    assert result["max_price"] is None
    assert result["require_gym"] is False
