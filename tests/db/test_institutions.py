import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.models import FinancialInstitutionDao
from src.entities.repo import institutions_repo as repo


class TestInstitutions:
    @pytest.fixture(scope="function", autouse=True)
    async def setup(
        request: pytest.FixtureRequest,
        session: AsyncSession,
    ):
        fi_dao = FinancialInstitutionDao(name="name123", lei="lei123")
        session.add(fi_dao)
        await session.commit()

    async def test_normal_dao_count(self, session: AsyncSession):
        res = await session.scalar(
            select(func.count()).select_from(FinancialInstitutionDao)
        )
        assert res == 1

    async def test_repo_get_institutions(self, session: AsyncSession):
        res = await repo.get_institutions(session)
        assert len(res) == 1

    async def test_repo_upsert_institution(self, session: AsyncSession):
        await repo.upsert_institution(
            session, FinancialInstitutionDao(name="asdf", lei="asdf")
        )
        res = await repo.get_institutions(session)
        assert len(res) == 2
