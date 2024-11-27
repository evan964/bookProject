# main.py
import pandas as pd
from exceptions import GoodreadsScraperException
from scraper import GoodreadsScraper

from reviews import fetch_reviews


def main():
    scraper = GoodreadsScraper()

    try:
        # Read the CSV file
        df = pd.read_csv('books_list.csv', sep=';')
        # Take only the first 3 rows from the DataFrame
        df = df.head(3)

        reviews_by_url = dict(zip(df['link'], fetch_reviews(list(df['link']))))

        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            try:
                # Assuming your CSV has a column named 'link' containing Goodreads URLs
                book_url = "https://" + row['link']
                print(f"\nScraping book {index + 1}: {book_url}")

                book_data = scraper.scrape_book(book_url)
                book_data.reviews = reviews_by_url[row['link']]

                print("\nExtracted Book Data:")
                print(f"Title: {book_data.title}")
                print(f"Authors: {book_data.authors}")
                print(f"Rating: {book_data.rating}")
                print(f"Ratings Count: {book_data.ratings_count}")
                print(f"Description: {book_data.description[:200]}...")
                print(f"Genres: {book_data.genres}")
                print(f"Pages: {book_data.pages}")
                print(f"Publication Date: {book_data.publication_date}")
                print(f"ISBN: {book_data.isbn}")
                print(f"Language: {book_data.language}")
                print(f"Review ratings: {[review.rating for review in book_data.reviews]}")

            except GoodreadsScraperException as e:
                print(f"Scraping Error for {book_url}: {e}")
                continue  # Continue with next book if current one fails

    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
