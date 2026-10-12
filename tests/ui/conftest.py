import os
import pytest
from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.login_modal_page import LoginModalPage
from pages.portfolio_page import PortfolioPage

UI_BASE_URL = os.getenv("UI_BASE_URL", "http://investapp-frontend.s3-website-us-east-1.amazonaws.com")
TEST_USER = os.getenv("TEST_USER", "userXX")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "password")


@pytest.fixture(scope="session")
def base_url():
    return UI_BASE_URL


@pytest.fixture
def navbar(page: Page) -> NavbarComponent:
    return NavbarComponent(page)


@pytest.fixture
def login_modal(page: Page) -> LoginModalPage:
    return LoginModalPage(page)


@pytest.fixture
def portfolio_page(page: Page) -> PortfolioPage:
    return PortfolioPage(page)


@pytest.fixture
def logged_page(page: Page, base_url: str, navbar: NavbarComponent, login_modal: LoginModalPage) -> Page:
    """
    Fixture que entrega o navegador logado via POM.
    Abre o sistema, clica em Entrar na Navbar, executa o login e aguarda a sessão ativa.
    """
    page.goto(base_url)
    navbar.clicar_entrar()
    expect(login_modal.container_modal).to_be_visible()

    login_modal.realizar_login(TEST_USER, TEST_PASSWORD)
    expect(navbar.botao_sair).to_be_visible(timeout=10000)

    return page
