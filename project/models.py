from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Author:
    """Represents an author of a book"""
    name: str
    url: str

class Book:
    """Represents a book with its details"""
    def __init__(
        self,
        title: str,
        authors: list,
        book_url: str,
        rating: float = None,
        ratings_count: int = None,
        reviews_count: int = None,
        description: str = None,
        genres: list = None,
        pages: int = None,
        publication_date: str = None,
        isbn: Optional[str] = None,
        language: Optional[str] = None,
        reviews: list = None
    ):
        self.title = title
        self.authors = authors
        self.book_url = book_url
        self.rating = rating
        self.ratings_count = ratings_count
        self.reviews_count = reviews_count
        self.description = description
        self.genres = genres or []
        self.pages = pages
        self.publication_date = publication_date
        self.isbn = isbn
        self.language = language
        self.reviews = reviews or []

    def __repr__(self):
        return f"Book(title='{self.title}', authors={self.authors})"
