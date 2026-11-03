# 📚 Smart Library

A small library system built with **Python + Flask**.

## Features
- Browse, search, and filter books
- Borrow / return books (14-day loan, max 3 books, late fine)
- Reservation queue (first reserved, first served)
- Interest quiz that recommends books
- Library statistics
- Data saved in `data/library.json`
- The original console version still works: `python library.py`

## Project structure
```
smart-library/
├── app.py            # Flask server (API)
├── library.py        # Classes and logic (Book, Library, InterestQuiz)
├── data/library.json # Saved data
├── templates/index.html
├── static/style.css
├── static/script.js
├── static/img/       # hawk logo, favicon, hero watermark (SVG)
├── requirements.txt
└── README.md
```

## Run
```bash
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000
