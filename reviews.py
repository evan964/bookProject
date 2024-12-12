import functools
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Sequence

import clients


def get_legacy_id_from_url(url: str):
    target = url[len('www.goodreads.com/book/show/'):]
    match = re.match(r'\d+', target)
    assert match is not None
    return match.group(0)


async def fetch_reviews(urls: Sequence[str]):
    print('->', urls)

    response = await clients.goodreads_api.get(dict(
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
    ''' + '\n'.join([f'a{index}: getBookByLegacyId(legacyId: {get_legacy_id_from_url(url)}) {{ ...X }}' for index, url in enumerate(urls)]) + '\n}'
    ))

    print(response)

    data = response.json()['data']

    def get_review(index: int):
        book_data = data[f'a{index}']
        # average_rating = book_data['stats']['averageRating']
        return [process_review(review_data['node']) for review_data in book_data['work']['reviews']['edges']]

    return [get_review(index) for index in range(len(urls))]


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
