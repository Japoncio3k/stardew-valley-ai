from unittest.mock import MagicMock, patch

import pytest

from app.domain.get_stardew_info_use_case import GetStardewInfoUseCase


@pytest.fixture
def use_case() -> GetStardewInfoUseCase:
    return GetStardewInfoUseCase()


def test_execute_returns_string(use_case: GetStardewInfoUseCase) -> None:
    result = use_case.execute("Penny")
    assert isinstance(result, str)
    assert result  # non-empty


def test_execute_includes_category_and_name(use_case: GetStardewInfoUseCase) -> None:
    with patch.object(
        use_case._datasource,
        "get",
        return_value={"category": "personagem", "name": "Abigail", "description": "Aventureira."},
    ):
        result = use_case.execute("Abigail")
    assert "PERSONAGEM" in result
    assert "Abigail" in result
    assert "Aventureira" in result


def test_execute_formats_output_correctly(use_case: GetStardewInfoUseCase) -> None:
    mock_data = {"category": "cultivo", "name": "Morango", "description": "Cresce em 8 dias."}
    with patch.object(use_case._datasource, "get", return_value=mock_data):
        result = use_case.execute("morango")
    assert result == "[CULTIVO] Morango: Cresce em 8 dias."


def test_execute_calls_datasource_with_query(use_case: GetStardewInfoUseCase) -> None:
    mock_get = MagicMock(return_value={"category": "pesca", "name": "Legend", "description": "Raro."})
    with patch.object(use_case._datasource, "get", mock_get):
        use_case.execute("peixe lendário")
    mock_get.assert_called_once_with("peixe lendário")
