import os
from pathlib import Path
import streamlit
import streamlit.components.v1 as components

_COMPONENT_NAME = "st_orgChart"

def _declare_component():
    if os.getenv("DEV_MODE", "").lower() == "true":
        host = os.getenv("FRONTEND_HOST_ORG", "http://localhost:5173")
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

def st_orgChart(data, key=None):
    """
    Função que exibe o Org Chart.

    Args:
        data (list|dict): Dados hierárquicos.
        key (str): Chave do componente.
    Returns:
        any: Valor retornado pelo front-end (se houver).
    """
    component_value = _component_func(data=data, key=key, default=None)
    return component_value
