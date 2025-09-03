
# PieQL — JMESPath Filtering Middleware for FastAPI

**PieQL** is a lightweight FastAPI middleware that allows clients to filter JSON responses from your endpoints using JMESPath queries.  

With PieQL, clients can request only the data they need without changing your endpoint logic.

---

## Features

- Works with any HTTP method (`GET`, `POST`, etc.)
- Supports `JSONResponse` and Pydantic models (via `JSONResponse`)
- Automatically ignores non-JSON responses (HTML, files, streaming responses)
- Simple integration with FastAPI via one line of code
- Fully supports nested JSON structures and JMESPath functions like `sum`, `max`, `min`, etc.

---

## Installation

Install via pip:

```bash
pip install pieql jmespath fastapi
````

---

## Integration

```python
from fastapi import FastAPI
from pieql import PieQL

app = FastAPI()
PieQL(app)  # default query parameter: "__schema"
```

You can customize the query parameter name:

```python
PieQL(app, param_name="filter")
```

---

## Usage Example

```python
from fastapi import FastAPI
from pieql import PieQL

app = FastAPI()
PieQL(app)

@app.get("/items")
def items():
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Carol"}
        ]
    }
```

### Sample Requests

1. Get all user names:

```
GET /items?__schema=users[*].name
```

Response:

```json
["Alice", "Bob", "Carol"]
```

2. Sum of user IDs:

```
GET /items?__schema=sum(users[*].id)
```

Response:

```json
6
```

3. Get user with `id=2`:

```
GET /items?__schema=users[?id==`2`]
```

Response:

```json
[{"id": 2, "name": "Bob"}]
```

---

## Error Handling

If the JMESPath query is invalid, PieQL returns HTTP 400:

```json
{
  "error": "Invalid JMESPath users[??].name for query: SyntaxError..."
}
```

---

## Notes

* Middleware only processes `JSONResponse` objects. All other response types are returned unchanged.
* Works seamlessly with nested JSON structures and Pydantic models.

---

## License

MIT


