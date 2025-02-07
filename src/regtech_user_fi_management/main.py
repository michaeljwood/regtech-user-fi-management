from contextlib import asynccontextmanager
import os
import logging
from fastapi import FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from alembic.config import Config
from alembic import command

from regtech_api_commons.oauth2.oauth2_backend import BearerTokenAuthBackend
from regtech_api_commons.oauth2.oauth2_admin import OAuth2Admin
from regtech_api_commons.api.fastapi_wrapper import RegtechApp

from regtech_user_fi_management.config import kc_settings
from regtech_user_fi_management.entities.listeners import setup_dao_listeners
from regtech_user_fi_management.routers import admin_router, institutions_router


log = logging.getLogger()


def run_migrations():
    file_dir = os.path.dirname(os.path.realpath(__file__))
    alembic_cfg = Config(f"{file_dir}/../../alembic.ini")
    alembic_cfg.set_main_option("script_location", f"{file_dir}/../../db_revisions")
    alembic_cfg.set_main_option("prepend_sys_path", f"{file_dir}/../../")
    command.upgrade(alembic_cfg, "head")


@asynccontextmanager
async def lifespan(app_: FastAPI):
    log.info("Starting up...")
    log.info("run alembic upgrade head...")
    run_migrations()
    setup_dao_listeners()
    yield
    log.info("Shutting down...")


app = RegtechApp(lifespan=lifespan)


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=kc_settings.auth_url.unicode_string(), tokenUrl=kc_settings.token_url.unicode_string()
)

app.add_middleware(AuthenticationMiddleware, backend=BearerTokenAuthBackend(oauth2_scheme, OAuth2Admin(kc_settings)))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/v1/admin")
app.include_router(institutions_router, prefix="/v1/institutions")
