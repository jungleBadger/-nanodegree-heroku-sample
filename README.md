# App developed to meet Udacity Nanodegree requirements.

- Basic CRUD with Authorization / Authentication service

### TECHNOLOGIES:
- Python3
- aclhemySQL
- Google OAUth 2 provider

### Setup
clone repo
from root folder `pip3 install -r requirements.txt`
all data are loaded on 'store.db' file. You can delete this file to start fresh if you want to.

### To Run
from root folder `python3 final.py`

The database includes three tables:
- Users table
- CatalogItem table
- Category table

To execute the program, run `python3 final.py` from the command line or from your preferred IDE.
After running go to http://localhost:5000/

### JSON ENDPOINTS
* `/item/<int:item_id>/v1/JSON'`
* `'/items/v1/JSON'`
* `'/category/<int:category_id>/v1/JSON'`
* `/categories/v1/JSON'`