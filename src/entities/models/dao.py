from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class AuditMixin(object):
    event_time: Mapped[datetime] = mapped_column(server_default=func.now())


class FinancialInstitutionDao(AuditMixin, Base):
    __tablename__ = "financial_institutions"
    lei: Mapped[str] = mapped_column(unique=True, index=True, primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    domains: Mapped[List["FinancialInstitutionDomainDao"]] = relationship(
        "FinancialInstitutionDomainDao", back_populates="fi"
    )
    tax_id: Mapped[str] = mapped_column(String(9), unique=True)
    rssd_id: Mapped[int] = mapped_column(unique=True)
    primary_federal_regulator_id: Mapped[str] = mapped_column(ForeignKey("federal_regulator.id"))
    primary_federal_regulator: Mapped["FederalRegulatorDao"] = relationship(lazy="selectin")
    hmda_institution_type_id: Mapped[str] = mapped_column(ForeignKey("hmda_institution_type.id"))
    hmda_institution_type: Mapped["HMDAInstitutionTypeDao"] = relationship(lazy="selectin")
    sbl_institution_type_id: Mapped[str] = mapped_column(ForeignKey("sbl_institution_type.id"))
    sbl_institution_type: Mapped["SBLInstitutionTypeDao"] = relationship(lazy="selectin")
    hq_address_street_1: Mapped[str] = mapped_column(nullable=False)
    hq_address_street_2: Mapped[str]
    hq_address_city: Mapped[str]
    hq_address_state_code: Mapped[str] = mapped_column(ForeignKey("address_state.code"))
    hq_address_state: Mapped["AddressStateDao"] = relationship(lazy="selectin")
    hq_address_zip: Mapped[str] = mapped_column(String(5), nullable=False)
    parent_lei: Mapped[str] = mapped_column(String(20))
    parent_legal_name: Mapped[str]
    parent_rssd_id: Mapped[int]
    top_holder_lei: Mapped[str] = mapped_column(String(20))
    top_holder_legal_name: Mapped[str]
    top_holder_rssd_id: Mapped[int]


class FinancialInstitutionDomainDao(AuditMixin, Base):
    __tablename__ = "financial_institution_domains"
    domain: Mapped[str] = mapped_column(index=True, primary_key=True)
    lei: Mapped[str] = mapped_column(ForeignKey("financial_institutions.lei"), index=True, primary_key=True)
    fi: Mapped["FinancialInstitutionDao"] = relationship("FinancialInstitutionDao", back_populates="domains")


class DeniedDomainDao(AuditMixin, Base):
    __tablename__ = "denied_domains"
    domain: Mapped[str] = mapped_column(index=True, primary_key=True)


class FederalRegulatorDao(AuditMixin, Base):
    __tablename__ = "federal_regulator"
    id: Mapped[str] = mapped_column(String(4), index=True, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)


class HMDAInstitutionTypeDao(AuditMixin, Base):
    __tablename__ = "hmda_institution_type"
    id: Mapped[str] = mapped_column(index=True, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)


class SBLInstitutionTypeDao(AuditMixin, Base):
    __tablename__ = "sbl_institution_type"
    id: Mapped[str] = mapped_column(index=True, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)


class AddressStateDao(AuditMixin, Base):
    __tablename__ = "address_state"
    code: Mapped[str] = mapped_column(String(2), index=True, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
