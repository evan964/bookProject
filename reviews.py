import functools
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Sequence

import requests


def get_legacy_id_from_url(url: str):
    target = url[len('www.goodreads.com/book/show/'):]
    match = re.match(r'\d+', target)
    assert match is not None
    return match.group(0)


def fetch_reviews(urls: Sequence[str]):
    # Request books 5 at a time
    cluster_size = 5

    book_reviews = list[list[BookReview]]()

    for first_book_index in range(0, len(urls), cluster_size):
        cluster_urls = urls[first_book_index:(first_book_index + cluster_size)]

        response = requests.post('https://kxbwmqov6jgg3daaamb744ycu4.appsync-api.us-east-1.amazonaws.com/graphql', headers={
            'x-api-key': 'da2-xpgsdydkbregjhpr6ejzqdhuwy'
        }, json=dict(
            query='''
    fragment X on Book {
        id
        title
        stats {
            averageRating
            ratingsCount
        }
        work {
            reviews(pagination:  { limit: 10 }) {
                edges {
                    node {
                        text
                        rating
                    }
                }
                totalCount
            }
        }
    }

    query {
        ''' + '\n'.join([f'a{index}: getBookByLegacyId(legacyId: {get_legacy_id_from_url(url)}) {{ ...X }}' for index, url in enumerate(cluster_urls)]) + '\n}',
            variables={}
        ))

        data = response.json()['data']

        for rel_book_index in range(len(cluster_urls)):
            book_data = data[f'a{rel_book_index}']
            # average_rating = book_data['stats']['averageRating']
            reviews = [process_review(review_data['node']) for review_data in book_data['work']['reviews']['edges']]

            book_reviews.append(reviews)

    return book_reviews


@dataclass(slots=True)
class BookReview:
    rating: int
    text: str

def process_review(data: dict):
    review_text = get_review_parser().run(data['text'])
    review_text = re.sub(r'\n+', '\n', review_text.strip())

    return BookReview(
        rating=data['rating'],
        text=review_text,
    )


class ReviewParser(HTMLParser):
    def run(self, html: str, /):
        self.output = ''
        self.feed(html)
        return self.output

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.output += '\n'

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        self.output += data

@functools.cache
def get_review_parser():
    return ReviewParser()
