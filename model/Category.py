#!/usr/bin/env python3
from sqlalchemy import Column, Integer, String
from model.Base import Base


class Category(Base):
    __tablename__ = 'category'
    name = Column(
        String(80),
        nullable=False
    )

    id = Column(
        Integer,
        primary_key=True
    )
