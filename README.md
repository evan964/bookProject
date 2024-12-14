# Books Scraper

A Python scraper for extracting book information.

## Installation

1. Clone this repository
2. Create a virtual environment:

```sh
$ python -m venv venv
$ source venv/bin/activate # On Windows: venv\Scripts\activate
$ pip install -r requirements.txt
```

To recompute the books_list.csv file, run:
```sh
#Create the books_list.csv file
python3 -m scrapy crawl books_list -a max_lists=2 -a max_pages=2 -o books_list.csv
python3 csv_duplicate_deleter.py --filename books_list.csv
```

To build the sql database (books.db), from the books_list.csv file, we need to run:
```sh
#Create the books.db
python3 -m project
```


## Requirements

- Python 3.11
