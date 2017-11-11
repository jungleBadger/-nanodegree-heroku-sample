#!/usr/bin/env python3
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from model.Category import Category
from model.Base import Base


class CatalogItem(Base):
    __tablename__ = 'catalog_item'
    name = Column(
        String(80),
        nullable=False
    )

    id = Column(
        Integer,
        primary_key=True
    )

    description = Column(String(250))

    price = Column(String(8))

    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    category_id = Column(
        Integer,
        ForeignKey('category.id')
    )

    category = relationship(Category)


