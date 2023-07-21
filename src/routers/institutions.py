from fastapi import Depends, Request
from oauth2 import oauth2_admin
from util import Router
from typing import List, Tuple
from db import (
    get_session,
    FinancialInstitutionDto,
    FinancialInstitutionWithDomainsDto,
    FinancialInsitutionDomainDto,
    FinancialInsitutionDomainCreate,
    institutions_repo as repo,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import requires

router = Router()


@router.get("/", response_model=List[FinancialInstitutionWithDomainsDto])
@requires("authenticated")
async def get_institutions(
    request: Request,
    domain: str = "",
    page: int = 0,
    count: int = 100,
    session: AsyncSession = Depends(get_session),
):
    return await repo.get_institutions(session, domain, page, count)


@router.post("/", response_model=Tuple[str, FinancialInstitutionDto])
@requires(["query-groups", "manage-users"])
async def create_institution(
    request: Request,
    fi: FinancialInstitutionDto,
    session: AsyncSession = Depends(get_session),
):
    db_fi = await repo.upsert_institution(session, fi)
    kc_id = oauth2_admin.upsert_group(fi.lei, fi.name)
    return kc_id, db_fi


@router.get("/{lei}", response_model=FinancialInstitutionWithDomainsDto)
@requires("authenticated")
async def get_institution(
    request: Request, lei: str, session: AsyncSession = Depends(get_session)
):
    return await repo.get_institution(session, lei)


@router.post("/{lei}/domains/", response_model=List[FinancialInsitutionDomainDto])
@requires(["query-groups", "manage-users"])
async def add_domains(
    request: Request,
    lei: str,
    domains: List[FinancialInsitutionDomainCreate],
    session: AsyncSession = Depends(get_session),
):
    return await repo.add_domains(session, lei, domains)
