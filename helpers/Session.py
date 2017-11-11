from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model.Base import Base
from model.Category import Category
from model.CatalogItem import CatalogItem
from model.User import User

engine = create_engine('sqlite:///store.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)


# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

#
# category1 = Category(name="Surf")
#
# session.add(category1)
# session.commit()
#
# catalogItem1 = CatalogItem(name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
#                      price="$7.50", category=category1)
#
# session.add(catalogItem1)
# session.commit()

