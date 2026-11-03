# -*- coding: utf-8 -*-
"""
Smart Library - Console-Based
Combines 3 ideas:
  1) Library System: display / search / borrow / return       (list of dicts)
  2) Booking System: reserve a borrowed book + cancel reservation (dict + set)
  3) Quiz Game: a game that learns the user's interests and recommends books (list of dicts + random)

Applied bonus:
  - Save data in a JSON file
  - Use Classes (Book, Library, InterestQuiz)
  - Handle errors with try/except
  - Additional features: loan duration + late fee + maximum loan limit
                        + reservation queue (first reserved, first served) + statistics
"""

import json
import os
import random
from datetime import date, timedelta

# ------------------------- Settings (constants) -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "library.json")   # works from any folder
LOAN_DAYS = 14        # Loan duration in days
MAX_LOANS = 3         # Maximum number of books one person can borrow
FINE_PER_DAY = 5      # Delay fine per day (currency unit)

# Available categories
TECH = "Technology and Programming"
FANTASY = "Fantasy"
HISTORY = "History"
SELF = "Self-Development"
MYSTERY = "Mystery and Crime"

# ------------------------- Default books (list of dicts) -------------------------
DEFAULT_BOOKS = [
    # --- Technology and Programming ---
    {"id": 1, "title": "Python Crash Course", "author": "Eric Matthes", "category": TECH},
    {"id": 2, "title": "Clean Code", "author": "Robert C. Martin", "category": TECH},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "category": TECH},
    {"id": 4, "title": "Automate the Boring Stuff with Python", "author": "Al Sweigart", "category": TECH},
    {"id": 5, "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "category": TECH},
    {"id": 6, "title": "Code: The Hidden Language of Computer Hardware and Software", "author": "Charles Petzold", "category": TECH},
    # --- Fantasy ---
    {"id": 7, "title": "The Hobbit", "author": "J.R.R. Tolkien", "category": FANTASY},
    {"id": 8, "title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "category": FANTASY},
    {"id": 9, "title": "Dune", "author": "Frank Herbert", "category": FANTASY},
    {"id": 10, "title": "The Name of the Wind", "author": "Patrick Rothfuss", "category": FANTASY},
    {"id": 11, "title": "The Lion, the Witch and the Wardrobe", "author": "C.S. Lewis", "category": FANTASY},
    {"id": 12, "title": "A Game of Thrones", "author": "George R.R. Martin", "category": FANTASY},
    # --- History ---
    {"id": 13, "title": "Sapiens", "author": "Yuval Noah Harari", "category": HISTORY},
    {"id": 14, "title": "Guns, Germs, and Steel", "author": "Jared Diamond", "category": HISTORY},
    {"id": 15, "title": "The Silk Roads", "author": "Peter Frankopan", "category": HISTORY},
    {"id": 16, "title": "SPQR: A History of Ancient Rome", "author": "Mary Beard", "category": HISTORY},
    {"id": 17, "title": "The Guns of August", "author": "Barbara W. Tuchman", "category": HISTORY},
    {"id": 18, "title": "The History of the Ancient World", "author": "Susan Wise Bauer", "category": HISTORY},
    # --- Self-Development ---
    {"id": 19, "title": "Atomic Habits", "author": "James Clear", "category": SELF},
    {"id": 20, "title": "Deep Work", "author": "Cal Newport", "category": SELF},
    {"id": 21, "title": "Man's Search for Meaning", "author": "Viktor Frankl", "category": SELF},
    {"id": 22, "title": "The 7 Habits of Highly Effective People", "author": "Stephen R. Covey", "category": SELF},
    {"id": 23, "title": "Mindset", "author": "Carol S. Dweck", "category": SELF},
    {"id": 24, "title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "category": SELF},
    # --- Mystery and Crime ---
    {"id": 25, "title": "And Then There Were None", "author": "Agatha Christie", "category": MYSTERY},
    {"id": 26, "title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "category": MYSTERY},
    {"id": 27, "title": "The Adventures of Sherlock Holmes", "author": "Arthur Conan Doyle", "category": MYSTERY},
    {"id": 28, "title": "Murder on the Orient Express", "author": "Agatha Christie", "category": MYSTERY},
    {"id": 29, "title": "Gone Girl", "author": "Gillian Flynn", "category": MYSTERY},
    {"id": 30, "title": "The Big Sleep", "author": "Raymond Chandler", "category": MYSTERY},
]

# ------------------------- Interest quiz questions (list of dicts) -------------------------
# Each choice = (choice text, category that gets a point)
INTEREST_QUESTIONS = [
    {"q": "What is the best plan for a weekend getaway?",
     "options": [("Build a small project on my laptop", TECH), ("Enter a fantasy movie world", FANTASY),
                 ("Visit a museum or historical site", HISTORY), ("Solve a puzzle or brain game", MYSTERY)]},
    {"q": "If you had a superpower, what would you choose?",
     "options": [("Travel through time", HISTORY), ("Read people's thoughts", MYSTERY),
                 ("Fly and enchant things", FANTASY), ("Learn any skill in seconds", SELF)]},
    {"q": "What type of content do you prefer on YouTube?",
     "options": [("Technology tutorials", TECH), ("Historical documentaries", HISTORY),
                 ("Motivational and productivity videos", SELF), ("Mysterious crime stories", MYSTERY)]},
    {"q": "What quality do you love to have?",
     "options": [("Discipline and good habits", SELF), ("Intelligence in uncovering the truth", MYSTERY),
                 ("A wide imagination", FANTASY), ("Deep understanding of technology", TECH)]},
    {"q": "If you were to visit a place, which would you choose?",
     "options": [("Pyramids and the Silk Road", HISTORY), ("A magical castle from a story", FANTASY),
                 ("Silicon Valley", TECH), ("An old house full of secrets", MYSTERY)]},
    {"q": "What most attracts you in any story?",
     "options": [("The surprise at the end", MYSTERY), ("The new worlds", FANTASY),
                 ("The lessons learned", SELF), ("The real events", HISTORY)]},
    {"q": "How do you spend your free time?",
     "options": [("Learn programming or a new tool", TECH), ("Improve myself and organize my goals", SELF),
                 ("Play story-driven fantasy games", FANTASY), ("Follow investigative series", MYSTERY)]},
    {"q": "If you could learn something new today?",
     "options": [("A programming language", TECH), ("The origin of an ancient civilization", HISTORY),
                 ("Time management and focus", SELF), ("Detective tricks", MYSTERY)]},
    {"q": "What is the best companion on a journey?",
     "options": [("A friendly dragon", FANTASY), ("A smart robot", TECH),
                 ("A historian who tells stories of every place", HISTORY), ("A coach who motivates you", SELF)]},
    {"q": "Which title grabs your attention the most?",
     "options": [("Small habits that change your life", SELF), ("A crime on the express train", MYSTERY),
                 ("Clean code in 30 days", TECH), ("Journey to the land of monsters", FANTASY)]},
]


# ======================= Class: Book =======================
class Book:
    """One book: its data + its status (borrowed? reserved?)"""

    def __init__(self, book_id, title, author, category,
                 borrowed_by=None, due_date=None, reservations=None, hold_for=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.category = category
        self.borrowed_by = borrowed_by          # Current borrower's name or None
        self.due_date = due_date                # Return date (ISO text)
        self.reservations = reservations or []  # Reservation queue (list of names)
        self.hold_for = hold_for                # Book temporarily reserved for this person after return

    def is_available(self):
        """Available means not currently borrowed"""
        return self.borrowed_by is None

    def can_borrow(self, name):
        """Can borrow if available and not reserved for someone else"""
        return self.is_available() and self.hold_for in (None, name)

    def status_text(self):
        if not self.is_available():
            return f"❌ Borrowed ({self.borrowed_by}) until {self.due_date}"
        if self.hold_for:
            return f"⏳ Reserved for {self.hold_for}"
        return "✅ Available"

    def to_dict(self):
        return {"id": self.book_id, "title": self.title, "author": self.author,
                "category": self.category, "borrowed_by": self.borrowed_by,
                "due_date": self.due_date, "reservations": self.reservations,
                "hold_for": self.hold_for}

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["title"], d["author"], d["category"],
                   d.get("borrowed_by"), d.get("due_date"),
                   d.get("reservations", []), d.get("hold_for"))


# ======================= Class: Library =======================
class Library:
    """Book management: display, search, borrow, return, reserve, save, and load"""

    def __init__(self):
        self.books = []
        self.load_data()

    # ---------- Save and load (JSON + try/except) ----------
    def load_data(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.books = [Book.from_dict(item) for item in raw]
        except FileNotFoundError:
            # First run: no file exists, so use default books
            self.books = [Book.from_dict(item) for item in DEFAULT_BOOKS]
            self.save_data()
        except (json.JSONDecodeError, KeyError):
            # File is corrupted: keep a backup and start with fresh data
            print("⚠️ The data file is corrupted; a backup was created and new data started.")
            try:
                os.replace(DATA_FILE, DATA_FILE + ".bak")
            except OSError:
                pass
            self.books = [Book.from_dict(item) for item in DEFAULT_BOOKS]
            self.save_data()

    def save_data(self):
        try:
            os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self.books], f, ensure_ascii=False, indent=2)
        except OSError as error:
            print(f"⚠️ Could not save data: {error}")

    # ---------- Search and display ----------
    def find_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                return book
        return None  # Not found

    def search(self, keyword):
        keyword = keyword.strip().lower()
        return [b for b in self.books
                if keyword in b.title.lower() or keyword in b.author.lower()]

    def available_books(self):
        return [b for b in self.books if b.is_available()]

    def books_by_category(self, category):
        return [b for b in self.books if b.category == category]

    # ---------- Borrowing ----------
    def books_borrowed_by(self, name):
        return [b for b in self.books if b.borrowed_by == name]

    def borrow(self, book_id, name):
        """Returns (success?, message)"""
        book = self.find_book(book_id)
        if book is None:
            return False, "❌ Book number does not exist."
        if len(self.books_borrowed_by(name)) >= MAX_LOANS:
            return False, f"❌ You reached the maximum ({MAX_LOANS} books). Return one first."
        if not book.is_available():
            return False, (f"❌ The book is currently borrowed by {book.borrowed_by}.\n"
                           "   You can reserve it from the reservation list and wait for your turn.")
        if not book.can_borrow(name):
            return False, f"⏳ The book is reserved for {book.hold_for} (your turn in the queue)."
        # Execute the loan
        book.borrowed_by = name
        book.due_date = (date.today() + timedelta(days=LOAN_DAYS)).isoformat()
        book.hold_for = None
        if name in book.reservations:
            book.reservations.remove(name)  # Leave the reservation queue
        self.save_data()
        return True, f"✅ The book was borrowed successfully. Return date: {book.due_date}"

    def return_book(self, book_id, name):
        book = self.find_book(book_id)
        if book is None:
            return False, "❌ Book number does not exist."
        if book.borrowed_by != name:
            return False, "❌ This book is not borrowed under your name."
        # Calculate the fine if overdue
        late_days = (date.today() - date.fromisoformat(book.due_date)).days
        fine = max(0, late_days) * FINE_PER_DAY
        book.borrowed_by = None
        book.due_date = None
        message = "✅ The book was returned."
        if fine > 0:
            message += f"\n💸 You were late by {late_days} day(s), fine: {fine} currency units."
        # If someone is in the reservation queue, the book is held for them
        if book.reservations:
            book.hold_for = book.reservations[0]
            message += f"\n🔔 The book is now reserved for {book.hold_for} (first in the queue)."
        self.save_data()
        return True, message

    # ---------- Reservation ----------
    def reserve(self, book_id, name):
        book = self.find_book(book_id)
        if book is None:
            return False, "❌ Book number does not exist."
        if book.is_available() and book.hold_for in (None, name):
            return False, "ℹ️ The book is available now; borrow it directly instead of reserving it."
        if book.borrowed_by == name:
            return False, "❌ You already borrowed this book."
        if name in book.reservations:           # Prevent duplicate reservations
            return False, "❌ You already reserved this book before."
        book.reservations.append(name)
        self.save_data()
        position = book.reservations.index(name) + 1
        return True, f"✅ Reservation successful. Your queue position: {position}"

    def cancel_reservation(self, book_id, name):
        book = self.find_book(book_id)
        if book is None:
            return False, "❌ Book number does not exist."
        if name not in book.reservations:
            return False, "❌ You do not have a reservation for this book."
        book.reservations.remove(name)
        if book.hold_for == name:  # If the book was reserved for them, pass it to the next person
            book.hold_for = book.reservations[0] if book.reservations else None
        self.save_data()
        return True, "✅ Reservation cancelled."

    def reservations_of(self, name):
        return [b for b in self.books if name in b.reservations]

    # ---------- Statistics ----------
    def statistics(self):
        total = len(self.books)
        borrowed = len([b for b in self.books if not b.is_available()])
        waiting = sum(len(b.reservations) for b in self.books)
        per_category = {}                       # dict: category -> number of books
        for b in self.books:
            per_category[b.category] = per_category.get(b.category, 0) + 1
        borrowers = {b.borrowed_by for b in self.books if b.borrowed_by}  # set: distinct borrowers
        return total, borrowed, waiting, per_category, borrowers


# ======================= Class: InterestQuiz =======================
class InterestQuiz:
    """Short game that identifies the category closest to the user's interests"""

    def __init__(self, questions):
        self.questions = questions

    def play(self):
        """Returns (winning category, score dictionary)"""
        scores = {}                              # dict: category -> points
        questions = self.questions[:]
        random.shuffle(questions)                # Randomize the question order
        for number, item in enumerate(questions, start=1):
            options = item["options"][:]
            random.shuffle(options)              # Randomize the answer order
            print(f"\nQuestion {number}/{len(questions)}: {item['q']}")
            for i, (text, _) in enumerate(options, start=1):
                print(f"  {i}. {text}")
            choice = read_int("Your choice: ", 1, len(options))
            category = options[choice - 1][1]
            scores[category] = scores.get(category, 0) + 1   # Point counter
        best_score = max(scores.values())
        winners = [c for c, s in scores.items() if s == best_score]
        return random.choice(winners), scores    # If tied, choose randomly

    @staticmethod
    def feedback(category, scores):
        percent = scores[category] * 100 // sum(scores.values())
        if percent >= 60:
            return f"🎯 Your interest is clearly strongest in the field of «{category}» ({percent}%)!"
        if percent >= 40:
            return f"👍 Your strongest inclination is in the field of «{category}» ({percent}%)."
        return f"🌈 Your interests are varied, and the closest field to you is «{category}» ({percent}%)."


    @staticmethod
    def runner_up(category, scores):
        """Returns the second-best category (or None) so we can recommend more books"""
        others = {c: s for c, s in scores.items() if c != category}
        if not others:
            return None
        return max(others, key=others.get)


# ======================= Helper functions (Input Validation) =======================
def read_int(prompt, low, high):
    """Reads a valid integer within a range and repeats until the user enters a correct value"""
    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:                       # If letters were entered instead of a number
            print("⚠️ Please enter a valid number.")
            continue
        if low <= value <= high:
            return value
        print(f"⚠️ The value must be between {low} and {high}.")


def read_name():
    """Reads a name. It must be text (letters only): numbers or symbols give an error"""
    while True:
        name = " ".join(input("Enter your name: ").split())   # remove extra spaces
        if not name:
            print("⚠️ The name cannot be empty.")
        elif not name.replace(" ", "").isalpha():
            print("❌ Error: the name must be text (letters only), not numbers or symbols.")
        else:
            return name.title()                                # "ali" -> "Ali"


def print_books(books, title):
    """Displays a list of books in an organized way"""
    print(f"\n===== {title} =====")
    if not books:
        print("There are no books to display.")
        return
    for b in books:
        print(f"[{b.book_id}] {b.title} - {b.author} | {b.category} | {b.status_text()}")


def pick_option(options):
    """Prints ONLY the given next steps (+ Back) and returns the chosen one (or None for Back)"""
    print("\nWhat would you like to do next?")
    for number, (label, _, _) in enumerate(options, start=1):
        print(f"{number}. {label}")
    print("0. Back to the main menu")
    choice = read_int("Your choice: ", 0, len(options))
    return None if choice == 0 else options[choice - 1]


def run_book_action(action, allowed_books, name):
    """Asks for a book number, accepts only numbers from the shown list, then runs the action"""
    allowed_ids = {b.book_id for b in allowed_books}          # set of valid choices
    book_id = read_int("Enter the book number: ", 1, 10 ** 6)
    if book_id not in allowed_ids:
        print("❌ That number is not one of the choices shown to you.")
        return
    success, message = action(book_id, name)
    print(message)


def book_actions_menu(library, name, books, title):
    """The user picks a book NUMBER from the shown list to borrow it.
    If the chosen book is not available, we say so and offer: reserve it, or choose another book."""
    shown_ids = {b.book_id for b in books}                     # only numbers from the list are accepted
    while True:
        print("\nEnter the number of the book you want to borrow (0 = back to the main menu).")
        book_id = read_int("Book number: ", 0, 10 ** 6)
        if book_id == 0:
            return
        if book_id not in shown_ids:
            print("❌ That number is not one of the books shown in the list.")
            continue

        book = library.find_book(book_id)
        if book.can_borrow(name):                              # available -> borrow it
            success, message = library.borrow(book_id, name)
            print(message)
        elif book.borrowed_by == name:
            print("ℹ️ You already borrowed this book.")
        else:                                                  # not available -> reserve or choose another
            print(f"\n⚠️ «{book.title}» is not available right now.")
            print(f"   Status: {book.status_text()}")
            if name in book.reservations:
                print("ℹ️ You already reserved this book. Choose another book to borrow.")
            else:
                print("1. Reserve this book (you will get your turn when it is returned)")
                print("2. Choose another book")
                print("0. Back to the main menu")
                choice = read_int("Your choice: ", 0, 2)
                if choice == 0:
                    return
                if choice == 1:
                    success, message = library.reserve(book_id, name)
                    print(message)
        print_books(books, title)                              # show the updated statuses


def browse_books(library, name, books, title):
    """Shows a list, then moves on to the next steps (borrow / reserve)"""
    print_books(books, title)
    if books:
        book_actions_menu(library, name, books, title)


def my_books_menu(library, name):
    """Shows the user's books and reservations, then offers only return / cancel if they apply"""
    while True:
        borrowed = library.books_borrowed_by(name)
        reserved = library.reservations_of(name)
        print_books(borrowed, f"Your borrowed books ({name})")
        print_books(reserved, "Your reservations")
        options = []
        if borrowed:
            options.append(("Return a book", library.return_book, borrowed))
        if reserved:
            options.append(("Cancel a reservation", library.cancel_reservation, reserved))
        if not options:
            print("\nYou have no borrowed books or reservations yet.")
            return
        chosen = pick_option(options)
        if chosen is None:
            return
        _, action, allowed_books = chosen
        run_book_action(action, allowed_books, name)


def run_quiz_and_recommend(library, name):
    """Plays the game (with repeat option), shows several suitable books, then lets the user pick"""
    quiz = InterestQuiz(INTEREST_QUESTIONS)
    while True:
        print("\n🎮 Interest Game: answer the questions and we will recommend suitable books for you.")
        category, scores = quiz.play()
        print("\n" + quiz.feedback(category, scores))

        recommended = library.books_by_category(category)
        print_books(recommended, f"Books recommended for you in «{category}»")
        second = quiz.runner_up(category, scores)              # more choices from the 2nd interest
        if second:
            extra = library.books_by_category(second)
            print_books(extra, f"You may also like «{second}»")
            recommended = recommended + extra

        book_actions_menu(library, name, recommended, "Your recommended books")
        again = input("\nWould you like to play again? (y/n): ").strip().lower()
        if again != "y":
            break


def show_statistics(library):
    total, borrowed, waiting, per_category, borrowers = library.statistics()
    print("\n===== Library Statistics =====")
    print(f"Total books: {total} | Available: {total - borrowed} | Borrowed: {borrowed}")
    print(f"Number of reservations waiting: {waiting}")
    print(f"Current number of borrowers: {len(borrowers)}")
    for category, count in per_category.items():
        print(f"  - {category}: {count} books")


# ======================= Menus =======================
def start_screen(library, name):
    """First screen: choose a book directly or play the interest game"""
    print("\nHow would you like to start?")
    print("1. Choose my book right away")
    print("2. Play a simple game to learn my interests")
    if read_int("Your choice: ", 1, 2) == 2:
        run_quiz_and_recommend(library, name)
    else:
        browse_books(library, name, library.books, "All books")


def main_menu(library, name):
    """Main menu inside the while loop: the program ends only when the exit option is chosen.
    Borrow / reserve / return / cancel appear as NEXT STEPS after the user views books,
    so the old options are not repeated every time."""
    while True:
        print(f"\n===== Main Menu | {name} =====")
        print("1. View all books")
        print("2. View available books only")
        print("3. Search by title or author")
        print("4. Interest game (book recommendations)")
        print("5. My books and reservations")
        print("6. Library statistics")
        print("0. Exit")
        choice = read_int("Your choice: ", 0, 6)

        if choice == 1:
            browse_books(library, name, library.books, "All books")
        elif choice == 2:
            browse_books(library, name, library.available_books(), "Available books")
        elif choice == 3:
            keyword = input("Enter a search word: ").strip()
            if keyword == "":
                print("⚠️ You must enter a search word.")
            else:
                browse_books(library, name, library.search(keyword), "Search results")
        elif choice == 4:
            run_quiz_and_recommend(library, name)
        elif choice == 5:
            my_books_menu(library, name)
        elif choice == 6:
            show_statistics(library)
        else:
            print("👋 Data saved. Goodbye!")
            library.save_data()
            break


def main():
    print("📚 Welcome to the Smart Library")
    library = Library()
    try:
        name = read_name()
        start_screen(library, name)
        main_menu(library, name)
    except (KeyboardInterrupt, EOFError):
        # If the user exits the program suddenly (Ctrl+C), save the data
        print("\n⚠️ The program was stopped. Saving data...")
        library.save_data()


if __name__ == "__main__":
    main()
