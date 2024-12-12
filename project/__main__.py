# main.py
import asyncio
import contextlib
import json
import sqlite3
from contextlib import AsyncExitStack
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from . import clients
from .async_util import BatchQueue
from .database import create_tables, insert_book
from .reviews import fetch_reviews
from .scraper import GoodreadsScraper
from .supplementary import query_supplementary


async def main():
    create_tables()  # Create the database tables

    async with AsyncExitStack() as stack:
        for client in clients.clients:
            await stack.enter_async_context(client)

        await run_scraping()


scraper = GoodreadsScraper()

async def run_scraping():
    # Read the CSV file
    df = pd.read_csv('books_list.csv', sep=';')

    # Take only the first 3 rows from the DataFrame
    df = df.head(75)

    conn = sqlite3.connect('books.db')
    semaphore = asyncio.Semaphore(15)

    completed_urls_path = Path('completed_urls.txt')

    if completed_urls_path.exists():
        with completed_urls_path.open('r') as file:
            completed_urls = set(json.load(file))
    else:
        completed_urls = set[str]()

    all_urls = set(df['link'])
    target_urls = all_urls - completed_urls

    try:
        with tqdm(initial=len(completed_urls), total=len(all_urls)) as progress:
            with contextlib.closing(conn):
                async def fetch_book(target_url):
                    book_url = "https://" + target_url

                    try:
                        book_data = await scraper.scrape_book(book_url)
                        book_data.reviews = await review_queue.push(target_url)
                        supplementary = await query_supplementary(book_data)

                        # Insert book data into the database
                        insert_book(conn, book_data, supplementary)

                        completed_urls.add(target_url)

                        progress.update(1)
                        # print(f"Scraped {book_data.title}")
                    except Exception as e:
                        print(f"Scraping Error for {book_url}: {e}")
                        # Continue with next book if current one fails


                async with BatchQueue(fetch_reviews) as review_queue:
                    async with asyncio.TaskGroup() as group:
                        # Iterate through each row in the DataFrame
                        for target_url in target_urls:
                            async with semaphore:
                                group.create_task(fetch_book(target_url))
    finally:
        with completed_urls_path.open('w') as file:
            json.dump(list(completed_urls), file, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
