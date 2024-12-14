The website "https://www.goodreads.com/list?ref=nav_brws_lists" includes genres. Each genre includes lists associated with those genres. Each list contains many books throughout many pages. There are approximately 100 pages for each list and 100 books in each page.

1. Change "max_page" and "max_list" variables in "books_list.py" as needed.

max_page: How many pages to scrape for each list.
 
max_list: How many lists to scrape for each genre. If a list is present in two genres, the spider does not choose it when encountered for the second time. It chooses another list to get to this max number.

2. Start crawling with spider "books_list".

3. Use csv_duplicate_deleter to delete duplicate books according to their links, not names.