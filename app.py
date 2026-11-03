# -*- coding: utf-8 -*-
"""Flask server for Smart Library. Run:  python app.py  then open http://127.0.0.1:5000"""
from flask import Flask, jsonify, render_template, request

from library import INTEREST_QUESTIONS, InterestQuiz, Library

app = Flask(__name__)
app.json.ensure_ascii = False
library = Library()


def clean_name(raw):
    """Same rule as the console version: letters only."""
    name = " ".join((raw or "").split())
    if not name or not name.replace(" ", "").isalpha():
        return None
    return name.title()


def book_json(b):
    return {**b.to_dict(), "status": b.status_text()}


def action(fn):
    """Runs a library action (borrow / return / reserve / cancel) from a JSON body."""
    data = request.get_json(silent=True) or {}
    name = clean_name(data.get("name"))
    if name is None:
        return jsonify(ok=False, message="❌ Name must be letters only."), 400
    try:
        book_id = int(data.get("book_id"))
    except (TypeError, ValueError):
        return jsonify(ok=False, message="❌ Invalid book number."), 400
    ok, message = fn(book_id, name)
    return jsonify(ok=ok, message=message)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/books")
def books():
    q = request.args.get("q", "").strip()
    result = library.search(q) if q else library.books
    if request.args.get("available") == "1":
        result = [b for b in result if b.is_available()]
    return jsonify([book_json(b) for b in result])


@app.route("/api/borrow", methods=["POST"])
def borrow():
    return action(library.borrow)


@app.route("/api/return", methods=["POST"])
def return_book():
    return action(library.return_book)


@app.route("/api/reserve", methods=["POST"])
def reserve():
    return action(library.reserve)


@app.route("/api/cancel", methods=["POST"])
def cancel():
    return action(library.cancel_reservation)


@app.route("/api/my")
def my_books():
    name = clean_name(request.args.get("name"))
    if name is None:
        return jsonify(error="Invalid name"), 400
    return jsonify(borrowed=[book_json(b) for b in library.books_borrowed_by(name)],
                   reserved=[book_json(b) for b in library.reservations_of(name)])


@app.route("/api/stats")
def stats():
    total, borrowed, waiting, per_category, borrowers = library.statistics()
    return jsonify(total=total, borrowed=borrowed, available=total - borrowed,
                   waiting=waiting, borrowers=len(borrowers), per_category=per_category)


@app.route("/api/quiz")
def quiz_questions():
    return jsonify([{"q": item["q"], "options": [text for text, _ in item["options"]]}
                    for item in INTEREST_QUESTIONS])


@app.route("/api/quiz", methods=["POST"])
def quiz_result():
    """Body: {"answers": [option index for each question, in order]}"""
    answers = (request.get_json(silent=True) or {}).get("answers", [])
    if len(answers) != len(INTEREST_QUESTIONS):
        return jsonify(error="Answer all questions."), 400
    scores = {}
    try:
        for item, i in zip(INTEREST_QUESTIONS, answers):
            category = item["options"][int(i)][1]
            scores[category] = scores.get(category, 0) + 1
    except (ValueError, IndexError, TypeError):
        return jsonify(error="Invalid answers."), 400
    best = max(scores.values())
    category = next(c for c, s in scores.items() if s == best)
    second = InterestQuiz.runner_up(category, scores)
    recommended = library.books_by_category(category)
    if second:
        recommended += library.books_by_category(second)
    return jsonify(feedback=InterestQuiz.feedback(category, scores),
                   category=category, second=second,
                   books=[book_json(b) for b in recommended])


if __name__ == "__main__":
    app.run(debug=True)
