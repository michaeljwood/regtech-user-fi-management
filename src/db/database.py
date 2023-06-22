import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DB_URL = os.getenv("INST_CONN")
DB_SCHEMA = os.getenv("INST_DB_SCHEMA", "public")

engine = create_async_engine(DB_URL, echo=True).execution_options(schema_translate_map={None: DB_SCHEMA})

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()

class Base(AsyncAttrs, DeclarativeBase):
    pass
