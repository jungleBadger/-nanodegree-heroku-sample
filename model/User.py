#!/usr/bin/env python3
from sqlalchemy import Column, String

from model.Base import Base


class User(Base):
    __tablename__ = 'user'
    name = Column(
        String(30),
        nullable=False
    )

    picture = Column(
        String(150),
        nullable=True
    )

    email = Column(
        String(40),
        primary_key=True
    )

    token = Column(
        String(40),
        primary_key=True
    )
