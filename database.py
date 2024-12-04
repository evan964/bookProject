import sqlite3

def create_tables():
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Create Books table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        rating REAL,
        ratings_count INTEGER,
        reviews_count INTEGER,
        description TEXT,
        publication_date TEXT,
        isbn TEXT,
        language TEXT,
        book_url TEXT
    )
    ''')

    # Create Authors table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        url TEXT
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
        name TEXT UNIQUE
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
        rating INTEGER,
        text TEXT,
        FOREIGN KEY (book_id) REFERENCES Books (id)
    )
    ''')

    conn.commit()
    conn.close()

def insert_book(book_data):
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO Books (title, rating, ratings_count, reviews_count, description, publication_date, isbn, language, book_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (book_data.title, book_data.rating, book_data.ratings_count, book_data.reviews_count,
          book_data.description, book_data.publication_date, book_data.isbn, book_data.language, book_data.book_url))

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

    conn.commit()
    conn.close() 