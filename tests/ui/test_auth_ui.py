import os
import pytest
from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.login_modal_page import LoginModalPage

TEST_USER = os.getenv("TEST_USER", "userXX")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "password")


def test_abertura_e_fechamento_modal_login(page: Page, base_url: str, navbar: NavbarComponent, login_modal: LoginModalPage):
    """Valida o ciclo de abertura e fechamento do LoginModal na UI."""
    page.goto(base_url)

    navbar.clicar_entrar()
    expect(login_modal.container_modal).to_be_visible()

    login_modal.fechar_modal()
    expect(login_modal.container_modal).not_to_be_visible()


def test_login_ui_com_sucesso(page: Page, base_url: str, navbar: NavbarComponent, login_modal: LoginModalPage):
    """Valida o fluxo completo de autenticação com credenciais corretas."""
    page.goto(base_url)

    navbar.clicar_entrar()
    login_modal.realizar_login(TEST_USER, TEST_PASSWORD)

    expect(navbar.botao_sair).to_be_visible(timeout=8000)
    expect(navbar.link_carteira).to_be_visible()


def test_login_ui_credenciais_invalidas(page: Page, base_url: str, navbar: NavbarComponent, login_modal: LoginModalPage):
    """Valida a exibição de aviso na UI ao fornecer senha incorreta."""
    page.goto(base_url)

    navbar.clicar_entrar()
    login_modal.realizar_login(TEST_USER, "senha_completamente_errada_xyz")

    expect(login_modal.mensagem_erro).to_be_visible(timeout=5000)
    expect(navbar.botao_sair).not_to_be_visible()
