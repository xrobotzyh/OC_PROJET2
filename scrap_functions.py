
def next_page_url(page) :
    next_page_link = None
    next_page_link_tag = page.html.find('li.next a', first='True')
    if next_page_link is not None :
        next_page_link = next_page_link.absolute_links[0]
    return next_page_link
    
def get_links_in_page(page_url: str) -> Tuple[List[str], Optional[str]]:
    # For Tuple, List, Optional objects, look at the module 'typings' in the standard library
    # Load page
    page = session.get(page_url)
    
    # Find book links in the page
    books_a_tags = page.html.find('div.image_container a')
    book_links_in_page = []

    for a_tag in books_a_tags:
        book_links_in_page.append(a_tag.absolute_links)

    # Find the "next" page url. next_page_link = ''
    next_page_link = next_page_url(page)

    return (book_links_in_page, next_page_link)


def get_all_books_links() -> List[str]:
    all_books_links = []
    next_page_link = 'http://books.toscrape.com/catalogue/page-1.html'
    while next_page_link is not None:
        book_links, next_page_link = get_links_in_page(url)
        all_books_links = all_books_links + book_links
    return all_books_links







