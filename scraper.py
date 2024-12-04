import requests
import re
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union

from exceptions import GoodreadsScraperException
from models import Author, Book
from utils import extract_text, extract_number

class GoodreadsScraper:
    BASE_URL = "https://www.goodreads.com"

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
        }

    def _make_request(self, url: str) -> BeautifulSoup:
        """Make HTTP request and return BeautifulSoup object"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            raise GoodreadsScraperException(f"Failed to fetch page: {str(e)}")

    def _extract_authors(self, soup: BeautifulSoup) -> List[Author]:
        """Extract book authors"""
        authors = []
        contributors_section = soup.find('div', class_='BookPageMetadataSection__contributor')
        if contributors_section:
            for contributor in contributors_section.find_all('a', class_='ContributorLink'):
                name = extract_text(contributor.find('span', class_='ContributorLink__name'))
                url = f"{self.BASE_URL}{contributor['href']}"
                authors.append(Author(name=name, url=url))
        return authors

    def _extract_rating_info(self, soup: BeautifulSoup) -> Dict[str, Union[float, int]]:
        """Extract rating information"""
        rating = None
        ratings_count = None
        reviews_count = None

        rating_section = soup.find('div', class_='RatingStatistics__rating')
        if rating_section:
            rating = float(extract_text(rating_section))

        meta_section = soup.find('div', class_='RatingStatistics__meta')
        if meta_section:
            ratings_count_elem = meta_section.find('span', {'data-testid': 'ratingsCount'})
            reviews_count_elem = meta_section.find('span', {'data-testid': 'reviewsCount'})
            
            if ratings_count_elem:
                ratings_count = extract_number(extract_text(ratings_count_elem))
            
            if reviews_count_elem:
                reviews_count = extract_number(extract_text(reviews_count_elem))

        return {
            'rating': rating,
            'ratings_count': ratings_count,
            'reviews_count': reviews_count
        }

    def _extract_genres(self, soup: BeautifulSoup) -> List[str]:
        """Extract book genres"""
        genres = []
        genres_div = soup.find('div', {'data-testid': 'genresList'})
        if genres_div:
            for button in genres_div.find_all('a', class_='Button--tag'):
                genre_name = extract_text(button.find('span', class_='Button__labelItem'))
                genres.append(genre_name)
        return genres

    def _extract_publication_info(self, soup: BeautifulSoup) -> Dict[str, Union[int, str]]:
        """Extract publication information"""
        pages = None
        publication_date = 'N/A'

        featured_details = soup.find('div', class_='FeaturedDetails')
        if featured_details:
            pages_format = featured_details.find('p', {'data-testid': 'pagesFormat'})
            if pages_format:
                pages = extract_number(extract_text(pages_format))

            publication_info = featured_details.find('p', {'data-testid': 'publicationInfo'})
            if publication_info:
                pub_date = extract_text(publication_info)
                publication_date = re.sub(r'First published ', '', pub_date)

        return {
            'pages': pages,
            'publication_date': publication_date
        }

    def _extract_isbn_and_language(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract ISBN and language from JSON-LD metadata"""
        isbn = 'N/A'
        language = 'N/A'
        
        json_ld_script = soup.find('script', type='application/ld+json')
        if json_ld_script:
            try:
                json_data = json.loads(json_ld_script.string)
                isbn = json_data.get('isbn', 'N/A')
                language = json_data.get('inLanguage', 'N/A')
            except json.JSONDecodeError:
                raise GoodreadsScraperException("Failed to parse JSON-LD data")

        return {
            'isbn': isbn, 
            'language': language
        }

    def scrape_book(self, book_url: str) -> Book:
        """Main method to scrape book information"""
        soup = self._make_request(book_url)
        
        title = extract_text(soup.find('h1', {'data-testid': 'bookTitle'}))
        description = self._extract_description(soup)
        
        # Combine all extracted information
        book_data = {
            'title': title,
            'authors': self._extract_authors(soup),
            'book_url': book_url,
            'description': description,
            'genres': self._extract_genres(soup),
            **self._extract_rating_info(soup),
            **self._extract_publication_info(soup),
            **self._extract_isbn_and_language(soup)
        }
        
        return Book(**book_data)

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract book description"""
        description_div = soup.find('div', {'data-testid': 'description'})
        if description_div:
            description_span = description_div.find('span', class_='Formatted')
            return extract_text(description_span)
        return 'N/A'