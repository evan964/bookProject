import scrapy
from urllib.parse import urljoin

class BooksSpider(scrapy.Spider):
    name = "books_list" 
    start_urls = [
        'https://goodreads.com/list?ref=nav_brws_lists'  # Initial URL to scrape
    ]
    def __init__(self, max_lists = 2, max_pages = 2, *args, **kwargs):
        super(BooksSpider, self).__init__(*args, **kwargs)
        self.max_lists = int(max_lists)
        self.max_pages = int(max_pages)
    
    
    already_looked_lists = []
    def parse(self, response):
        for genre in response.css('ul.CollapsableList a'):
            genre_url = urljoin("www.goodreads.com", genre.css("::attr(href)").get())
            yield response.follow(genre_url, callback=self.parse_genre)

    def parse_genre(self, response):
        current_list = 1
        for link in response.css("a.listTitle::attr(href)").getall():
            if self.max_lists < current_list:
                break
            if (link not in self.already_looked_lists) and current_list <= self.max_lists:
                current_list += 1
                self.already_looked_lists.append(link)
                yield response.follow(link, callback=lambda r: self.parse_list(r, 1))

    def parse_list(self, response, current_page):
        for book in response.css('table.tableList tr td:nth-of-type(3)'):
            yield {
                "title" : book.css("a.bookTitle span::text").get(),
                "link" : f"www.goodreads.com{book.css("a.bookTitle::attr(href)").get()}"
            }
        next_page = response.css('div.pagination a.next_page::attr(href)').extract_first()
        if next_page and current_page < self.max_pages:
            yield response.follow(next_page, callback=lambda r: self.parse_list(r, current_page + 1))