from http import HTTPStatus
from typing import List
from fastapi import HTTPException, Request
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import lei_association_check, fi_search_association_check
from starlette.authentication import AuthCredentials

import pytest


@pytest.fixture
def mock_session(mocker: MockerFixture) -> AsyncSession:
    return mocker.patch("sqlalchemy.ext.asyncio.AsyncSession").return_value


async def test_domain_denied(mocker: MockerFixture, mock_session: AsyncSession):
    domain_allowed_mock = mocker.patch("entities.repos.institutions_repo.is_domain_allowed")
    domain_allowed_mock.return_value = False
    from dependencies import email_domain_denied

    denied_domain = "denied.domain"

    assert await email_domain_denied(mock_session, denied_domain) is True
    domain_allowed_mock.assert_called_once_with(mock_session, denied_domain)


async def test_domain_allowed(mocker: MockerFixture, mock_session: AsyncSession):
    domain_allowed_mock = mocker.patch("entities.repos.institutions_repo.is_domain_allowed")
    domain_allowed_mock.return_value = True
    from dependencies import email_domain_denied

    allowed_domain = "allowed.domain"

    assert await email_domain_denied(mock_session, allowed_domain) is False
    domain_allowed_mock.assert_called_once_with(mock_session, allowed_domain)


async def test_lei_association_check_matching_lei(mock_request: Request):
    @lei_association_check
    async def method_to_wrap(request: Request, lei: str):
        pass

    await method_to_wrap(mock_request, lei="TESTBANK123")


async def test_lei_association_check_is_admin(mock_request: Request):
    mock_request.auth = AuthCredentials(["manage-account", "query-groups", "manage-users", "authenticated"])

    @lei_association_check
    async def method_to_wrap(request: Request, lei: str):
        pass

    await method_to_wrap(mock_request, lei="TESTBANK1234")


async def test_lei_association_check_not_matching(mock_request: Request):
    @lei_association_check
    async def method_to_wrap(request: Request, lei: str):
        pass

    with pytest.raises(HTTPException) as e:
        await method_to_wrap(mock_request, lei="NOTMYBANK")
    assert e.value.status_code == HTTPStatus.FORBIDDEN
    assert "not associated" in e.value.detail


async def test_fi_search_association_check_matching_lei(mock_request: Request):
    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    await method_to_wrap(mock_request, leis=["TESTBANK123"])


async def test_fi_search_association_check_invalid_lei(mock_request: Request):
    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    with pytest.raises(HTTPException) as e:
        await method_to_wrap(mock_request, leis=["NOTMYBANK"])
    assert e.value.status_code == HTTPStatus.FORBIDDEN
    assert "not associated" in e.value.detail


async def test_fi_search_association_check_matching_domain(mock_request: Request):
    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    await method_to_wrap(mock_request, domain="local.host")


async def test_fi_search_association_check_invalid_domain(mock_request: Request):
    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    with pytest.raises(HTTPException) as e:
        await method_to_wrap(mock_request, domain="not.myhost")
    assert e.value.status_code == HTTPStatus.FORBIDDEN
    assert "not associated" in e.value.detail


async def test_fi_search_association_check_no_filter(mock_request: Request):
    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    with pytest.raises(HTTPException) as e:
        await method_to_wrap(mock_request)
    assert e.value.status_code == HTTPStatus.FORBIDDEN
    assert "without filter" in e.value.detail


async def test_fi_search_association_check_lei_admin(mock_request: Request):
    mock_request.auth = AuthCredentials(["manage-account", "query-groups", "manage-users", "authenticated"])

    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    await method_to_wrap(mock_request, leis=["TESTBANK123", "ANOTHERBANK", "NOTMYBANK"])


async def test_fi_search_association_check_domain_admin(mock_request: Request):
    mock_request.auth = AuthCredentials(["manage-account", "query-groups", "manage-users", "authenticated"])

    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    await method_to_wrap(mock_request, domain="not.myhost")


async def test_fi_search_association_check_no_filter_admin(mock_request: Request):
    mock_request.auth = AuthCredentials(["manage-account", "query-groups", "manage-users", "authenticated"])

    @fi_search_association_check
    async def method_to_wrap(request: Request, leis: List[str] = [], domain: str = ""):
        pass

    await method_to_wrap(mock_request)
