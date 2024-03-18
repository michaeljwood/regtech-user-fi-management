from typing import Tuple
from fastapi import Request
import pytest

from pytest_mock import MockerFixture
from starlette.authentication import AuthCredentials
from regtech_api_commons.models import AuthenticatedUser, RegTechUser


@pytest.fixture(autouse=True)
def setup(mocker: MockerFixture):
    mocked_engine = mocker.patch("sqlalchemy.ext.asyncio.create_async_engine")
    MockedEngine = mocker.patch("sqlalchemy.ext.asyncio.AsyncEngine")
    mocked_engine.return_value = MockedEngine.return_value
    mocker.patch("fastapi.security.OAuth2AuthorizationCodeBearer")
    mocker.patch("entities.engine.get_session")


@pytest.fixture
def mock_auth() -> Tuple[AuthCredentials, RegTechUser]:
    creds = AuthCredentials(["manage-account", "authenticated"])
    user = AuthenticatedUser.from_claim(
        {
            "name": "test",
            "preferred_username": "test_user",
            "email": "test@local.host",
            "sub": "testuser123",
            "institutions": ["TESTBANK123"],
        }
    )
    return creds, user


@pytest.fixture
def mock_request(mocker: MockerFixture, mock_auth: Tuple[AuthCredentials, RegTechUser]) -> Request:
    request: Request = mocker.patch("fastapi.Request").return_value
    request.auth = mock_auth[0]
    request.user = mock_auth[1]
    return request
