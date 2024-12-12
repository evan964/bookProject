# main.py
import asyncio
from contextlib import AsyncExitStack
from pprint import pprint

import clients
import pandas as pd
from async_util import BatchQueue
from database import create_tables, insert_book
from exceptions import GoodreadsScraperException
from reviews import BookReview, fetch_reviews
from scraper import GoodreadsScraper
from supplementary import query_supplementary
from tqdm import tqdm


async def main():
    # create_tables()  # Create the database tables

    async with AsyncExitStack() as stack:
        for client in clients.clients:
            await stack.enter_async_context(client)

        await run_scraping()


scraper = GoodreadsScraper()

async def run_scraping():
    # Read the CSV file
    df = pd.read_csv('books_list.csv', sep=';')

    # Take only the first 3 rows from the DataFrame
    df = df.head(3)

    semaphore = asyncio.Semaphore(15)


    async def fetch_book(row):
        book_url = "https://" + row['link']

        try:
            book_data = await scraper.scrape_book(book_url)
            # book_data.reviews = reviews_by_url[row['link']]

            print(book_data)

            # Insert book data into the database
            # pprint(await query_supplementary(book_data))
            print(await review_queue.push(row['link']))
            print()

            # insert_book(book_data)
        except GoodreadsScraperException as e:
            print(f"Scraping Error for {book_url}: {e}")
            # Continue with next book if current one fails


    async with BatchQueue[str, list[BookReview]](fetch_reviews) as review_queue:
        async with asyncio.TaskGroup() as group:
            # Iterate through each row in the DataFrame
            for _, row in tqdm(df.iterrows(), total=len(df)):
                async with semaphore:
                    group.create_task(fetch_book(row))


if __name__ == "__main__":
    asyncio.run(main())
