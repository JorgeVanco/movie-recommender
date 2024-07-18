from flask import Flask, request
import json
import random
import flask
import numpy as np

app = Flask(__name__)

with open("movies.json") as f:
    raw_movies = json.load(f)

embeddings = []
movies = []
for idx, movie in enumerate(raw_movies):
    movies.append(
        {
            "title": movie["title"],
            "year": movie["year"],
            "img": movie["img"],
            "url": movie["url"],
            "idx": idx,
        }
    )
    embeddings.append(movie["embeddings"])
embeddings = np.array(embeddings)


@app.route("/")
def hello_world():
    response = flask.jsonify(random.choices(movies, k=40))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/similar")
def get_similar():
    idx = request.args.get("idx")
    idx = int(idx)
    query = embeddings[idx]
    scores = np.dot(embeddings, query)
    top_40 = np.argsort(-scores)[:40]
    response = flask.jsonify([movies[i] for i in top_40])
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/search")
def search():
    query = request.args.get("title")
    query = query.lower()
    results = []
    for movie in movies:
        if query in movie["title"].lower():
            results.append(movie)

    response = flask.jsonify(results)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(debug=True)
