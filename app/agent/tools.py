from langchain_core.tools import tool

from app.domain.get_stardew_info_use_case import GetStardewInfoUseCase


@tool
def get_stardew_info(query: str) -> str:
    """Busca informações sobre o conteúdo do jogo Stardew Valley.

    Use esta ferramenta quando o usuário perguntar sobre personagens, cultivos, pesca,
    minas, mecânicas de fazenda ou qualquer outro tema do Stardew Valley.

    Args:
        query: Descrição do tema do Stardew Valley a ser consultado.

    Returns:
        Uma string com informações relevantes sobre o Stardew Valley.
    """
    use_case = GetStardewInfoUseCase()
    return use_case.execute(query)
