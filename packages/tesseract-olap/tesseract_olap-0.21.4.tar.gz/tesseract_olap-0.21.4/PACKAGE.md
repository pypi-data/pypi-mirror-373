## Installation

Besides the main contents of the package, you can install the optional dependencies for the backend driver of your choice:

* `tesseract-olap[clickhouse]`  
  Installs the dependency needed to enable the use of the `tesseract_olap.backend.clickhouse` module.

## Getting started

In its most basic form, the tesseract-olap package provides you with a way to translate OLAP-type queries into request statements that a data backend can understand and execute safely. The results obtained through the execution of server methods are python objects, and as such, can be used in any way the language allows.

```python
# example.py

from tesseract_olap.backend.clickhouse import ClickhouseBackend
from tesseract_olap import OlapServer

backend = ClickhouseBackend("clickhouse://user:pass@localhost:9000/database")
server = OlapServer(backend=backend, schema="./path/to/schema.xml")

def get_data():
    # First you create an ordered representation of the intent for data
    request = DataRequest.new("cube_name", {
      "drilldowns": ["Time", "Country"],
      "measures": ["Units", "Price"],
    })

    # This step performs the validation of the request against the schema
    query = DataQuery.from_request(server.schema, request)

    # The context manager establishes the connection with the backend
    with server.session() as session:
        # .fetch() methods perform the request against the server.
        # There are three methods depending on the shape you want the data:
        # result = session.fetch(query)
        # result = session.fetch_dataframe(query)
        result = session.fetch_records(query)
    
    return result.data

if __name__ == "__main__":
    get_data()
```

The server instance can then be used in other programs as the data provider, for simple (like data exploration) and complex (like data processing) operations.

---
&copy; 2022 [Datawheel, LLC.](https://www.datawheel.us/)
