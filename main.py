# main.py
import asyncio
from contextlib import AsyncExitStack
from pprint import pprint

from tqdm import tqdm

import clients
import pandas as pd
from database import create_tables, insert_book
from exceptions import GoodreadsScraperException
from reviews import fetch_reviews
from scraper import GoodreadsScraper
from supplementary import query_supplementary


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

    # reviews_by_url = dict(zip(df['link'], fetch_reviews(list(df['link']))))

    semaphore = asyncio.Semaphore(15)

    async with asyncio.TaskGroup() as group:
        # Iterate through each row in the DataFrame
        for _, row in tqdm(df.iterrows(), total=len(df)):
            async with semaphore:
                group.create_task(fetch_book(row))


async def fetch_book(row):
    book_url = "https://" + row['link']

    try:
        book_data = await scraper.scrape_book(book_url)
        # book_data.reviews = reviews_by_url[row['link']]

        # Insert book data into the database
        pprint(await query_supplementary(book_data))

        # insert_book(book_data)
        # print(f"Book {index + 1} inserted into the database.")

        # print("\nExtracted Book Data:")
        # print(f"Title: {book_data.title}")
        # print(f"Authors: {book_data.authors}")
        # print(f"Rating: {book_data.rating}")
        # print(f"Ratings Count: {book_data.ratings_count}")
        # print(f"Description: {book_data.description[:200]}...")
        # print(f"Genres: {book_data.genres}")
        # print(f"Pages: {book_data.pages}")
        # print(f"Publication Date: {book_data.publication_date}")
        # print(f"ISBN: {book_data.isbn}")
        # print(f"Language: {book_data.language}")
        # print(f"Review ratings: {[review.rating for review in book_data.reviews]}")
    except GoodreadsScraperException as e:
        print(f"Scraping Error for {book_url}: {e}")
        # Continue with next book if current one fails

if __name__ == "__main__":
    asyncio.run(main())
