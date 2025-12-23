from fastapi import FastAPI

app = FastAPI(title="My First FastAPI App")

@app.get("/")
def home():
    return {"message": "Hello FastAPI 🚀"}

@app.get("/users")
def get_users():
    return [
        {"id": 1, "name": "Ali"},
        {"id": 2, "name": "Ahmed"}
    ]
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}