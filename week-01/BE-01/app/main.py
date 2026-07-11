from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "Hello, World!"
    }

@app.get("/about")
def about():
    return {
        "name": "John Elvin",
        "role": "Backend AI Engineering Intern"
    }