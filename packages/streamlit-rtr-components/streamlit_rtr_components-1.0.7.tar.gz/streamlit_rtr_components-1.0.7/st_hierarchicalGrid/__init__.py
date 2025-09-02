import os
from pathlib import Path
import streamlit
import streamlit.components.v1 as components

_COMPONENT_NAME = "st_hierarchicalGrid"

def _declare_component():
    if os.getenv("DEV_MODE", "").lower() == "true":
        host = os.getenv("FRONTEND_HOST_GRID", "http://localhost:3001")
        return components.declare_component(_COMPONENT_NAME, url=host)

    base = Path(__file__).parent / "frontend"
    dist = base / "dist" # Vite
    if dist.exists():
        return components.declare_component(_COMPONENT_NAME, path=str(dist))

    build = base / "build" # fallback se algum ainda for CRA
    if build.exists():
        return components.declare_component(_COMPONENT_NAME, path=str(build))

    raise RuntimeError(f"Nenhum build encontrado em {dist} ou {build}. Rode `npm run build`.")

_component_func = _declare_component()

def st_hierarchicalGrid(data, columns, expanded, key=None):
    """
    Função que exibe o Grid Hierárquico.

    Args:
        data (list|dict): Dados hierárquicos.
        columns (list|dict): Definição de colunas.
        expanded (bool): Expandir nós por padrão.
        key (str): Chave do componente.
    Returns:
        any: Valor retornado pelo front-end (se houver).
    """
    component_value = _component_func(data=data,columns=columns,expanded=expanded, key=key, default=0)  
    return component_value
