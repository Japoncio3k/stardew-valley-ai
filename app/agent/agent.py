from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from app.agent.tools import get_stardew_info
from common.utils.open_router_manager import OpenRouterManager

SYSTEM_PROMPT = """Você é um assistente especialista em Stardew Valley, o jogo de fazenda e aventura.
Seu objetivo é responder perguntas dos jogadores sobre o jogo de forma clara, simpática e detalhada.

Você pode ajudar com:
- Informações sobre personagens e como aumentar a amizade com eles
- Cultivos, temporadas e estratégias de fazenda
- Pesca: peixes, locais e épocas
- Minas: andares, minérios e inimigos
- Mecânicas gerais do jogo

Sempre que precisar de informações sobre o jogo, use a ferramenta disponível para buscar dados.
Responda sempre em português do Brasil."""

_TOOLS = [get_stardew_info]


class StardewAgent:
    _graph: CompiledStateGraph[Any, Any, Any, Any]

    def __init__(self) -> None:
        llm = OpenRouterManager().llm
        self._graph = create_agent(llm, tools=_TOOLS, system_prompt=SYSTEM_PROMPT)

    def chat(self, message: str) -> str:
        result = self._graph.invoke({"messages": [HumanMessage(content=message)]})
        return result["messages"][-1].content  # type:ignore
