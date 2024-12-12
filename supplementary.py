import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

import clients
from bs4 import BeautifulSoup
from models import Book


@dataclass(slots=True)
class DigitalAccess:
  platform: Optional[str]
  url: str

@dataclass(kw_only=True, slots=True)
class SupplementaryBookInfo:
  digital_accesses: list[DigitalAccess] = field(default_factory=list)
  oclc_number: Optional[str] = None
  isbns: set[str] = field(default_factory=set)


def to_isbn10(raw_isbn: str, /):
  return raw_isbn[3:] if len(raw_isbn) == 13 else raw_isbn


async def query_supplementary(book: Book):
  # Query the Google Books API

  if book.isbn is not None:
    query = f'isbn:{book.isbn}'
  else:
    query = f'intitle:{book.title}'

  response = await clients.google_books_api.get(f'https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote_plus(query)}')
  data = response.json()

  if not data.get('items'):
    return SupplementaryBookInfo()

  book_id = data['items'][0]['id']


  # Scrape Google Books

  response = await clients.google_books_reg.get(f'https://books.google.fr/books?id={book_id}&sitesec=buy')
  soup = BeautifulSoup(response.text, 'html.parser')

  link = soup.select_one('#summary_content > span > a')

  if link is None:
    return SupplementaryBookInfo()

  href = link.attrs['href'] # type: ignore

  marker = 'http://worldcat.org/oclc/'
  marker_index = href.find(marker)

  if marker_index < 0:
    return SupplementaryBookInfo()

  start_index = marker_index + len(marker)
  end_index = href.index('&', start_index)

  oclc_number = href[start_index:end_index]


  # Scrape WorldCat

  response = await clients.worldcat.get(f'https://search.worldcat.org/api/search-item/{oclc_number}')

  data = response.json()

  return SupplementaryBookInfo(
    digital_accesses=[DigitalAccess(platform=access.get('materialSpecified'), url=access['uri']) for access in (data['digitalAccessAndLocations'] or [])],
    oclc_number=oclc_number,
    isbns={to_isbn10(isbn) for isbn in data.get('isbns') or []},
  )
