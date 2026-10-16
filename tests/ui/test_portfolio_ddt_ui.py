import csv
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


def carregar_dados_investimentos_csv():
    """Le a massa CSV com resolucao de caminho dinamica."""
    caminho = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "dados_investimentos_ui.csv"
    )

    if not caminho.exists():
        raise FileNotFoundError(f"CSV nao localizado em: {caminho}")

    cenarios = []
    with open(caminho, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            cenarios.append(
                (
                    linha["asset_name"],
                    linha["amount"],
                    linha["purchase_price"],
                    linha["days_invested"],
                    linha["planned_days"],
                    linha["deve_ter_sucesso"].strip().lower() == "true",
                )
            )
    return cenarios


@pytest.mark.parametrize(
    "asset, amount, price, days, planned, deve_sucesso",
    carregar_dados_investimentos_csv(),
)
def test_cadastro_aporte_ddt_pom(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
    asset,
    amount,
    price,
    days,
    planned,
    deve_sucesso,
):
    """Executa varios cadastros na UI delegando a interacao ao Page Object."""
    navbar.navegar_para_carteira()
    portfolio_page.aguardar_carteira_carregada()

    portfolio_page.cadastrar_aporte(
        ativo=asset,
        quantidade=amount,
        preco=price,
        dias_inv=days,
        dias_plan=planned,
    )

    if deve_sucesso:
        linha = portfolio_page.obter_linha_por_ativo_e_prazo(
            asset, days, planned
        )
        expect(linha).to_be_visible(timeout=5000)
        # Limpeza: remove o aporte criado para nao acumular dados na conta
        portfolio_page.excluir_linha(linha)
    else:
        expect(portfolio_page.alerta_erro).to_be_visible()