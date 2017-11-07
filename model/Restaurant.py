#!/usr/bin/env python3
from sqlalchemy import Column, Integer, String

from model.Base import Base


class Restaurant(Base):
    __tablename__ = 'restaurant'
    name = Column(
        String(80),
        nullable=False
    )

    id = Column(
        Integer,
        primary_key=True
    )
