<!-- PROJECT: streamlit-rtr-components -->
<!-- BADGES: start -->
<p align="center">
  <!-- Substitua o href se já estiver no PyPI -->
  <a href="https://pypi.org/project/streamlit-rtr-components/"><img alt="PyPI" src="https://img.shields.io/pypi/v/streamlit-rtr-components.svg"></a>
  <img alt="Python" src="https://img.shields.io/pypi/pyversions/streamlit-rtr-components.svg">
  <img alt="Streamlit" src="https://img.shields.io/badge/streamlit-%E2%89%A51.24-FF4B4B">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>
<!-- BADGES: end -->

<h1 align="center">streamlit-rtr-components</h1>
<p align="center">Componentes customizados para <b>Streamlit</b>: organograma e grid hierárquico.</p>

<!-- TOC: start -->
## Sumário
- [Visão geral](#visão-geral)
- [Instalação](#instalação)
- [Exemplo rápido](#exemplo-rápido)
- [API](#api)
- [Formato de dados](#formato-de-dados)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Desenvolvimento (Vite + Tailwind v4)](#desenvolvimento-vite--tailwind-v4)
- [Build de produção (frontend)](#build-de-produção-frontend)
- [Empacotamento Python](#empacotamento-python)
- [Solução de problemas](#solução-de-problemas)
- [Changelog](#changelog)
- [Contribuição](#contribuição)
- [Licença](#licença)
<!-- TOC: end -->

## Visão geral
Dois componentes prontos para uso em Streamlit:
- `st_orgChart` — organograma (árvore hierárquica).
- `st_hierarchicalGrid` — grid hierárquico com colunas configuráveis e suporte a imagens (PNG/SVG via data URL).

> **Stack**: Python (Streamlit) + React/TypeScript (Vite) + Tailwind v4.  
> **Artefatos**: cada frontend gera `frontend/dist` e é empacotado junto ao wheel.

## Instalação
```bash
pip install streamlit-rtr-components


<!-- USAGE: start -->

## Exemplo rápido

import streamlit as st
from rtr_componentes import st_orgChart, st_hierarchicalGrid

st.title("Demo • RTR Components")

st.subheader("Org Chart")
st_orgChart(
    data={
        "id": "CEO",
        "children": [{"id": "CTO"}, {"id": "CFO"}]
    }
)

st.subheader("Hierarchical Grid")
data = [
    {
        "estrutura": "Presidência",
        "avatar": "data:image/png;base64,....",   # PNG opcional (data URL)
        "quantidade_funcionarios": 2167,
        "salario_total": "R$ 5.239.551,21",
        "salario_medio": "R$ 2.417,88",
        "children": [
            {
                "estrutura": "Assessoria Financeira",
                "avatar": "data:image/svg+xml;base64,....",  # SVG opcional (data URL)
                "quantidade_funcionarios": 1,
                "salario_total": "R$ 5.184,00",
                "salario_medio": "R$ 5.184,00",
                "children": []
            }
        ]
    }
]
columns = [
    {"label": "Estrutura", "field": "estrutura"},
    {"label": "Quantidade Funcionarios", "field": "quantidade_funcionarios"},
    {"label": "Salario Total", "field": "salario_total", "secret": True},
    {"label": "Salario Medio", "field": "salario_medio"}
]

st_hierarchicalGrid(data=data, columns=columns, expanded=True)

<!-- USAGE: end -->

## API

from rtr_componentes import st_orgChart, st_hierarchicalGrid

st_orgChart(
    data: dict | list | None = None,
    key: str | None = None,
    **kwargs
) -> Any


st_hierarchicalGrid(
    data: dict | list | None = None,
    columns: list[dict] | None = None,
    expanded: bool = False,
    key: str | None = None,
    **kwargs
) -> Any

# data
# Org: objeto/array hierárquico com id, children, etc.
# Grid: nós com campos livres e children: [].
# columns (Grid): {"label": str, "field": str, "secret"?: bool, "type"?: "text"|"number"|"currency"|...}.
# expanded (Grid): expande nós por padrão.
# Retorno: se o frontend chamar Streamlit.setComponentValue(...), o valor retorna via função Python.


<!-- DATA-FORMAT: start -->

Formato de dados
Imagens: envie como data URL

PNG → data:image/png;base64,<...>

SVG → data:image/svg+xml;base64,<...>

Perfomance: prefira miniaturas (ex.: 64–128 px) para reduzir payload.

Grid: garanta que os nomes em columns[].field existam em cada nó.

<!-- DATA-FORMAT: end -->


## Estrutura do repositório

.
├─ st_orgChart/
│  ├─ __init__.py                 # wrapper Python (usa frontend/dist)
│  └─ frontend/                   # Vite/React/TS
│     ├─ index.html
│     ├─ src/
│     │  ├─ main.tsx
│     │  ├─ StOrgChart.tsx
│     │  └─ index.css             # @import "tailwindcss";
│     └─ dist/                    # gerado por vite build
├─ st_hierarchicalGrid/
│  ├─ __init__.py
│  └─ frontend/
│     ├─ index.html
│     ├─ src/
│     │  ├─ main.tsx
│     │  ├─ RtrHierarchicalGrid.tsx
│     │  └─ index.css
│     └─ dist/
├─ rtr_componentes/
│  └─ __init__.py                 # reexporta os dois componentes
├─ pyproject.toml
├─ MANIFEST.in
├─ README.md
└─ LICENSE


## Desenvolvimento (Vite + Tailwind v4)
# Em cada frontend:

npm i
npm run dev

## No seu app Streamlit (dev hot-reload):

# Windows PowerShell
$env:DEV_MODE="true"
$env:FRONTEND_HOST="http://localhost:5173"   # altere a porta conforme o componente
streamlit run seu_app.py

# Em dev, o wrapper usa DEV_MODE/FRONTEND_HOST. Em produção (sem envs), ele lê frontend/dist.


<!-- BUILD-FRONTEND: start -->

## Build de produção (frontend)

cd st_orgChart/frontend && npm run build
cd ../../st_hierarchicalGrid/frontend && npm run build


# vite.config.ts (recomendado nos dois):

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";

export default defineConfig(({ command }) => ({
  base: command === "build" ? "./" : "/",
  plugins: [react(), tailwind()],
  build: { outDir: "dist" }
}));

<!-- BUILD-FRONTEND: end --> <!-- PACKAGING: start -->


## Empacotamento Python

# MANIFEST.in

recursive-include st_orgChart/frontend/dist *
recursive-include st_hierarchicalGrid/frontend/dist *
include README.md
include LICENSE


# pyproject.toml (trechos)

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["."]
include = ["st_orgChart*", "st_hierarchicalGrid*", "rtr_componentes*"]

[tool.setuptools.package-data]
"st_orgChart" = ["frontend/dist/**"]
"st_hierarchicalGrid" = ["frontend/dist/**"]


# Build & teste:

python -m build
pip install -e .

<!-- PACKAGING: end --> <!-- TROUBLESHOOT: start -->

# Solução de problemas
# Tela branca/404 em produção → confirme base: "./" no Vite e que frontend/dist existe e foi incluído no wheel.

# RuntimeError: Build não encontrado → rode npm run build em cada frontend antes de instalar.

# Erros de JSX/TS no editor → use TS 5, moduleResolution: "bundler", jsx: "react-jsx", types: ["vite/client"].

# Conflitos NPM (ERESOLVE) → se migrou de CRA, remova react-scripts, apague node_modules/package-lock.json e reinstale.

# Bundle grande (Grid) → faça import dinâmico de html2canvas/jspdf somente na ação de exportar.

# <!-- TROUBLESHOOT: end -->
# Changelog
# <!-- CHANGELOG: start -->
# 1.0.0 — release inicial com st_orgChart e st_hierarchicalGrid.

# <!-- CHANGELOG: end -->
# Contribuição
# Issues e PRs são bem-vindos. Antes de abrir PR:

# Rode npm run build em ambos os frontends.

# Rode npm run lint (se estiver usando ESLint).

# Adicione/atualize exemplos no README quando necessário.


## Licença
# MIT — veja LICENSE.
