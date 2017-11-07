#!/usr/bin/env python3
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from model.Restaurant import Restaurant
from model.Base import Base


class MenuItem(Base):
    __tablename__ = 'menu_item'
    name = Column(
        String(80),
        nullable=False
    )

    id = Column(
        Integer,
        primary_key=True
    )

    description = Column(String(250))

    course = Column(String(250))

    price = Column(String(8))

    restaurant_id = Column(
        Integer,
        ForeignKey('restaurant.id')
    )

    restaurant = relationship(Restaurant)


