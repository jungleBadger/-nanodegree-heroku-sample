#!/usr/bin/env python3
from sqlalchemy import Column, Integer, String
from model.Base import Base


class Category(Base):
    __tablename__ = 'category'
    name = Column(
        String(30),
        nullable=False
    )

    description = Column(
        String(150),
        nullable=True
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
