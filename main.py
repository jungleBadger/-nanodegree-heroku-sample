#!/usr/bin/env python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.Base import Base
from model.Restaurant import Restaurant
from model.MenuItem import MenuItem
# import insertscript
engine = create_engine('sqlite:///restaurantmenu.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()


myFirstRestaurant = Restaurant(name="Daniel x")
# session.add(myFirstRestaurant)
# session.commit()


cheesepizza = MenuItem(
    name="pizza",
    description="xx",
    course="Entree",
    price="$8.99",
    restaurant=myFirstRestaurant
)

# session.add(cheesepizza)
# session.commit()

result = session.query(Restaurant).all()
result2 = session.query(MenuItem).all()

for restaurant in result:
   print(restaurant.name)


for item in result2:
   print(item.name)


pizzaItems = session.query(MenuItem).filter_by(name = "new pizza")
for pizza in pizzaItems:
    print("before update")
    print(pizza.id)
    print(pizza.name)
    pizza.name = "new new pizza"
    session.add(pizza)
    session.commit()



print("updated")
pizzaItems = session.query(MenuItem).filter_by(name = "new new pizza")
for pizza in pizzaItems:
    print("after update")
    print(pizza.id)
    print(pizza.name)

pizzaItems = session.query(MenuItem).filter_by(name="new new pizza")
for pizza in pizzaItems:
    session.delete(pizza)
    session.commit()


