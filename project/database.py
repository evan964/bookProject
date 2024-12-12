import sqlite3

from .models import Book
from .supplementary import SupplementaryBookInfo


def create_tables():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Create Books table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        rating REAL NOT NULL,
        ratings_count INTEGER NOT NULL,
        review_count INTEGER NOT NULL,
        description TEXT NOT NULL,
        publication_date TEXT NOT NULL,
        language TEXT NOT NULL,
        url TEXT NOT NULL,
        oclc_number TEXT
    )
    ''')

    # Create Authors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL
    )
    ''')

    # Create BookAuthors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BookAuthors (
        book_id INTEGER,
        author_id INTEGER,
        FOREIGN KEY (book_id) REFERENCES Books (id),
        FOREIGN KEY (author_id) REFERENCES Authors (id),
        PRIMARY KEY (book_id, author_id)
    )
    ''')

    # Create Genres table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Create BookGenres table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BookGenres (
        book_id INTEGER,
        genre_id INTEGER,
        FOREIGN KEY (book_id) REFERENCES Books (id),
        FOREIGN KEY (genre_id) REFERENCES Genres (id),
        PRIMARY KEY (book_id, genre_id)
    )
    ''')

    # Create Reviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        rating INTEGER NOT NULL,
        text TEXT,
        FOREIGN KEY (book_id) REFERENCES Books (id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DigitalAccess (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        platform TEXT,
        url TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Isbn (
        id TEXT PRIMARY KEY,
        book_id INTEGER NOT NULL,
        FOREIGN KEY (book_id) REFERENCES Books (id)
    )
    ''')

    conn.commit()
    conn.close()

def insert_book(conn: sqlite3.Connection, book_data: Book, supplementary: SupplementaryBookInfo):
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO Books (title, rating, ratings_count, review_count, description, publication_date, language, url, oclc_number)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (book_data.title, book_data.rating, book_data.ratings_count, book_data.reviews_count,
          book_data.description, book_data.publication_date, book_data.language, book_data.book_url, supplementary.oclc_number))

    book_id = cursor.lastrowid

    for author in book_data.authors:
        cursor.execute('INSERT OR IGNORE INTO Authors (name, url) VALUES (?, ?)', (author.name, author.url))
        cursor.execute('SELECT id FROM Authors WHERE name = ?', (author.name,))
        author_id = cursor.fetchone()[0]
        cursor.execute('INSERT INTO BookAuthors (book_id, author_id) VALUES (?, ?)', (book_id, author_id))

    for genre in book_data.genres:
        cursor.execute('INSERT OR IGNORE INTO Genres (name) VALUES (?)', (genre,))
        cursor.execute('SELECT id FROM Genres WHERE name = ?', (genre,))
        genre_id = cursor.fetchone()[0]
        cursor.execute('INSERT INTO BookGenres (book_id, genre_id) VALUES (?, ?)', (book_id, genre_id))

    for review in book_data.reviews:
        cursor.execute('''
        INSERT INTO Reviews (book_id, rating, text)
        VALUES (?, ?, ?)
        ''', (book_id, review.rating, review.text))

    for digital_access in supplementary.digital_accesses:
        cursor.execute('INSERT INTO DigitalAccess (book_id, platform, url) VALUES (?, ?, ?)', (book_id, digital_access.platform, digital_access.url))

    for isbn in supplementary.isbns:
        cursor.execute('INSERT INTO Isbn (id, book_id) VALUES (?, ?)', (isbn, book_id))

    conn.commit()
