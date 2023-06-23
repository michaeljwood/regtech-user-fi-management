from fastapi import Depends, Request
from oauth2 import oauth2_admin
from util import Router
from typing import List, Tuple
from db import *
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import requires

router = Router()

@router.get("/", response_model=List[FinancialInstitutionWithDomainsDto])
@requires("authenticated")
async def get_groups(request: Request, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        stmt = select(FinancialInstitutionDao).options(selectinload(FinancialInstitutionDao.domains))
        res = await session.execute(stmt)
        return res.scalars().all()
    
@router.post("/", response_model=Tuple[str, FinancialInstitutionDto])
@requires(["query-groups", "manage-users"])
async def create_group(request: Request, fi: FinancialInstitutionDto, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        stmt = select(FinancialInstitutionDao).filter(FinancialInstitutionDao.lei == fi.lei)
        res = await session.execute(stmt)
        existing_fi = res.scalar_one_or_none()
        if existing_fi is None:
            existing_fi = FinancialInstitutionDao(lei=fi.lei, name=fi.name)
            session.add(existing_fi)
        else:
            existing_fi.name = fi.name
        await session.commit()
        kc_id = oauth2_admin.upsert_group(fi.lei, fi.name)
        return kc_id, existing_fi
    
@router.post("/{lei}/domains/", response_model=List[FinancialInsitutionDomainDto])
@requires(["query-groups", "manage-users"])
async def add_domain(request: Request, lei: str, domains: List[FinancialInsitutionDomainCreate], session: AsyncSession = Depends(get_session)):
    async with session.begin():
        daos = set(map(lambda dto: FinancialInstitutionDomainDao(domain=dto.domain, lei=lei), domains))
        session.add_all(daos)
        await session.commit()
        return daos