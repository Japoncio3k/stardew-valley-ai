import pytest

from app.data.stardew_info_data_source import StardewDatasource


@pytest.fixture
def datasource() -> StardewDatasource:
    return StardewDatasource()


def test_get_returns_dict(datasource: StardewDatasource) -> None:
    result = datasource.get("any query")
    assert isinstance(result, dict)
    assert result  # non-empty


def test_get_has_required_fields(datasource: StardewDatasource) -> None:
    result = datasource.get("anything")
    assert "category" in result
    assert "name" in result
    assert "description" in result


def test_get_matches_by_name(datasource: StardewDatasource) -> None:
    result = datasource.get("Penny")
    assert result["name"] == "Penny"


def test_get_matches_by_category(datasource: StardewDatasource) -> None:
    result = datasource.get("pesca")
    assert result["category"] == "pesca"


def test_get_fallback_for_unknown_query(datasource: StardewDatasource) -> None:
    result = datasource.get("xyzzy_unknown_topic_12345")
    assert isinstance(result, dict)
    assert result


def test_get_multiple_calls_return_valid_data(datasource: StardewDatasource) -> None:
    for _ in range(10):
        result = datasource.get("cultivo")
        assert result["category"] in {"cultivo", "personagem", "pesca", "minas", "fazenda"}
