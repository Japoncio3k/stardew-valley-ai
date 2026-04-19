from langchain_core.tools import tool

from app.domain.get_stardew_info_use_case import GetStardewInfoUseCase


@tool
def get_stardew_info(query: str) -> str:
    """Retrieve information about Stardew Valley game content.

    Use this tool when the user asks about characters, crops, fishing,
    mines, farming mechanics, or any other Stardew Valley topic.

    Args:
        query: A description of the Stardew Valley topic to look up.

    Returns:
        A string with relevant Stardew Valley information.
    """
    use_case = GetStardewInfoUseCase()
    return use_case.execute(query)
