from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

def read_data(file: str):
    data_list: list[dict] = []
    with open(file, "r") as file:
        data_list: list[dict] = json.load(file)
    return data_list

posts = read_data("snippets.json")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
def home():
    return f"<h1>{posts[0]['title']}</h1>"

@app.get("/api/posts")
def get_posts():
    return posts
