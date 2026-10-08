from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )
    additional_info: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Internal fields used to request weather data.
    latitude: Mapped[float]
    longitude: Mapped[float]

    temperatures: Mapped[list["Temperature"]] = relationship(
        back_populates="city",
        passive_deletes=True,
    )


class Temperature(Base):
    __tablename__ = "temperatures"

    id: Mapped[int] = mapped_column(primary_key=True)

    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    temperature: Mapped[float] = mapped_column(
        nullable=False,
    )

    city: Mapped[City] = relationship(
        back_populates="temperatures",
    )
