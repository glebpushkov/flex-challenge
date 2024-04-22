### How to start the app:

`docker build -t webapi . && docker run -p 127.0.0.1:8000:8000 webapi`

access docs http://localhost:8000/docs  

available endpoints\
GET http://localhost:8000/trades \
POST http://localhost:8000/trades

username: **webapi** \
password: **secret**

### Description

The idea was to structure app on 3 layers: API, Service(domain, core), Persistence(database).\
For such a simple app it feels like overkill, but as it's a coding challenge I selected a 'nice' decoupled structure.
Disclaimer: I'm not very familiar with FastAPI best practices, so I would be glad to hear a feedback what could be done better. 

NOTE: sqlite is used as a database, so each time you restart container - 
you have to start from scratch 

---
not covered / todos:
- api has no versioning
- api has no pagination
- more validation should be enforced on openapi level
- domain level validation is missing (core/entities.py)
- more tests
- no db migrations
- no db indexes for trader_id & delivery_day
- didn't used async
- poetry / black / linters / .dockerignore / logger
- ...
