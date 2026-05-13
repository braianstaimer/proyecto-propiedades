from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Enum, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Property(Base):
    __tablename__ = "propiedades"
    __table_args__ = (
        Index("idx_tipo", "tipo"),
        Index("idx_precio", "precio"),
        Index("idx_ubicacion", "ubicacion"),
        Index("idx_fecha_publicacion", "fecha_publicacion"),
        Index("idx_habitaciones_banos", "habitaciones", "banos"),
        Index("idx_tipo_precio", "tipo", "precio"),
        CheckConstraint("precio >= 0", name="chk_precio_positivo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(180), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(
        Enum("casa", "departamento", "terreno", "oficina", "local", name="tipo_propiedad"),
        nullable=False,
    )
    precio: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    habitaciones: Mapped[int | None] = mapped_column(Integer, nullable=True)
    banos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    area_m2: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    ubicacion: Mapped[str] = mapped_column(String(160), nullable=False)
    fecha_publicacion: Mapped[date] = mapped_column(Date, nullable=False)
