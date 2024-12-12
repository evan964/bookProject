from dataclasses import dataclass
from pprint import pprint

import requests
from bs4 import BeautifulSoup


@dataclass(slots=True)
class DigitalAccess:
  platform: str
  url: str

@dataclass(slots=True)
class SupplementaryBookInfo:
  digital_access: list[DigitalAccess]
  oclc_number: str
  isbns: list[str]


def to_isbn10(raw_isbn: str, /):
  return raw_isbn[3:] if len(raw_isbn) == 13 else raw_isbn


def query_supplementary(isbn: str):
  # Query the Google Books API

  response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
  data = response.json()

  if not data['items']:
    return None

  book_id = data['items'][0]['id']
  # return GoogleBooksInfo(id=data['items'][0]['id'])


  # Scrape Google Books

  response = requests.get(f'https://books.google.fr/books?id={book_id}&sitesec=buy')
  soup = BeautifulSoup(response.text, 'html.parser')

  link = soup.select_one('#summary_content > span > a')
  href = link.attrs['href'] # type: ignore

  marker = 'http://worldcat.org/oclc/'
  start_index = href.index(marker) + len(marker)
  end_index = href.index('&', start_index)

  oclc_number = href[start_index:end_index]


  # Scrape WorldCat

  response = requests.get(f'https://search.worldcat.org/api/search-item/{oclc_number}', headers={
    # Necessary
    "Referer": "https://search.worldcat.org",
  })

  data = response.json()

  return SupplementaryBookInfo(
    digital_access=[DigitalAccess(platform=access['materialSpecified'], url=access['uri']) for access in data['digitalAccessAndLocations']],
    oclc_number=oclc_number,
    isbns=[to_isbn10(isbn) for isbn in data['isbns']],
  )


if __name__ == '__main__':
  pprint(query_supplementary('9781429522823'))
