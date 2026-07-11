"""
Week 1 Backend Engineering Assignment

Goal:
Build the smallest possible backend server with two JSON endpoints,
test them using both a web browser and curl, and publish the project
to a public GitHub repository.

Objectives:
- Understand the HTTP request → response cycle.
- Create a simple backend service.
- Return JSON responses from API endpoints.
- Verify the API using a browser and curl.
- Practice version control by publishing the project to GitHub.

Endpoints:
GET /
    Returns a welcome message.

GET /about
    Returns basic information about the application.

Author: John Elvin Endrenal
"""

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