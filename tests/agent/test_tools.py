from unittest.mock import MagicMock, patch

from app.agent.tools import get_stardew_info


def test_get_stardew_info_returns_string() -> None:
    with patch("app.agent.tools.GetStardewInfoUseCase") as MockUseCase:
        MockUseCase.return_value.execute.return_value = "[PERSONAGEM] Penny: Mora em Pelican Town."
        result = get_stardew_info.invoke({"query": "Penny"})
    assert isinstance(result, str)
    assert "Penny" in result


def test_get_stardew_info_calls_use_case_with_query() -> None:
    mock_execute = MagicMock(return_value="[PESCA] Legend: Peixe raro.")
    with patch("app.agent.tools.GetStardewInfoUseCase") as MockUseCase:
        MockUseCase.return_value.execute = mock_execute
        get_stardew_info.invoke({"query": "peixe lendário"})
    mock_execute.assert_called_once_with("peixe lendário")


def test_get_stardew_info_is_langchain_tool() -> None:
    from langchain_core.tools import BaseTool
    assert isinstance(get_stardew_info, BaseTool)


def test_get_stardew_info_tool_name() -> None:
    assert get_stardew_info.name == "get_stardew_info"
