# main.py
from scraper import GoodreadsScraper
from exceptions import GoodreadsScraperException


def main():
    # Example usage
    scraper = GoodreadsScraper()
    try:
        book_data = scraper.scrape_book('https://www.goodreads.com/book/show/173754979-james')
        print("\nExtracted Book Data:")
        print(f"Title: {book_data.title}")
        print(f"Authors: {book_data.authors}")
        print(f"Rating: {book_data.rating}")
        print(f"Ratings Count: {book_data.ratings_count}")
        print(f"Description: {book_data.description[:200]}...")  # Print first 200 chars
        print(f"Genres: {book_data.genres}")
        print(f"Pages: {book_data.pages}")
        print(f"Publication Date: {book_data.publication_date}")
        print(f"ISBN: {book_data.isbn}")
        print(f"Language: {book_data.language}")
    except GoodreadsScraperException as e:
        print(f"Scraping Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()