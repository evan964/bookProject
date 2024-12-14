# Goodreads Scraper

A Python scraper for extracting book information from Goodreads.

## Installation

1. Clone this repository
2. Create a virtual environment:

```sh
$ python -m venv venv
$ source venv/bin/activate # On Windows: venv\Scripts\activate
$ pip install -r requirements.txt
```
To build the sql database (books.db), we need to run:
```sh
python3 -m scrapy crawl books_list -a max_lists=2 -a max_pages=2 -o books_list.csv
python3 csv_duplicate_deleter.py --filename books_list.csv
python3 -m project
```


## Requirements

- Python 3.11
