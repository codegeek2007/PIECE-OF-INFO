from flask import Flask, render_template, request
import requests

app = Flask(__name__)

HEADERS = {"User-Agent": "WikiQA/1.0 (student project)"}
API = "https://en.wikipedia.org/w/api.php"
SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"

def get_answer(question):
    # 1. search for the best matching article
    params = {
        "action": "query", "list": "search",
        "srsearch": question, "format": "json", "srlimit": 1,
    }
    r = requests.get(API, params=params, headers=HEADERS, timeout=10).json()
    results = r["query"]["search"]
    if not results:
        return None, None

    title = results[0]["title"]

    # 2. get the summary of that article
    s = requests.get(SUMMARY + title.replace(" ", "_"),
                     headers=HEADERS, timeout=10).json()
    extract = s.get("extract", "")

    # 3. keep it short: first 2 sentences
    short = ". ".join(extract.split(". ")[:2]).strip()
    if short and not short.endswith("."):
        short += "."
    return title, short

@app.route("/", methods=["GET", "POST"])
def index():
    title = answer = None
    if request.method == "POST":
        question = request.form["question"]
        title, answer = get_answer(question)
        if not answer:
            answer = "Sorry, I couldn't find an answer."
    return render_template("index.html", title=title, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)