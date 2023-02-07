import csv
import os
from requests_html import HTMLSession


# find if there is a next button in the page
def next_page_url(page):
    next_page_link_a_tag = page.html.find('li.next a', first='True')
    if next_page_link_a_tag is not None:
        next_page_link = list(next_page_link_a_tag.absolute_links)
        return next_page_link[0]
    else:
        nex_page_link = None
        return nex_page_link


# find all the category links in the first page except category:"book"
def get_links_of_category_in_first_page(first_page_url):
    page = session.get(first_page_url)
    category_links = []
    all_category_content = page.html.find('ul.nav-list a')
    for category_content in all_category_content:
        category_links = category_links + list(category_content.absolute_links)
    category_links.pop(0)
    return category_links


# get all the links in a single detail page of category
def get_links_of_books_in_page(page):
    # For Tuple, List, Optional objects, look at the module 'typings' in the standard library

    # Find book links in the page
    books_a_tags = page.html.find('div.image_container a')
    book_links_in_page = []

    for a_tag in books_a_tags:
        book_links_in_page = book_links_in_page + list(a_tag.absolute_links)

    return book_links_in_page


# get all the book's links of the site
def get_all_books_links_of_one_category(category_link):
    all_books_links = []
    book_links = []
    next_page_link = category_link
    while next_page_link is not None:
        page = session.get(next_page_link)
        book_links = get_links_of_books_in_page(page)
        next_page_link = next_page_url(page)
        all_books_links = all_books_links + book_links

    return all_books_links


# get diver information from a single book in detail page
def get_data_in_book_page(url):
    page = session.get(url)
    download_links_of_images = []
    title = page.html.find('div.product_main h1', first='true').text
    category = page.html.find('.breadcrumb > li:nth-child(3) > a:nth-child(1)')[0].text
    production_descripton_p_tag = page.html.find('article.product_page p')
    production_descripton = production_descripton_p_tag[3].text
    code_upc = page.html.find('table.table-striped tr td', first='true').text
    star_rating_information = page.html.find('p.star-rating', first='true')

    # using the arguments attrs to get the star rating informations
    star_rating = star_rating_information.attrs.get('class')[1]

    price_without_tax = page.html.find('table.table-striped tr td')[2].text
    price_with_tax = page.html.find('table.table tr td')[3].text
    inventory = page.html.find('table.table tr td')[5].text

    # image links to absolute links by re write the link
    image_link = str(page.html.find('div.active img')[0].attrs.get('src'))
    image_absolute_link = 'http://books.toscrape.com' + image_link.replace('../..', '')

    # Use dictionary to write to the csv
    data = {'Titre :': title, 'Catégorie:': category, 'Descripton :': production_descripton, 'UPC Code :': code_upc,
             'Etoile :':star_rating, 'Prix hors taxe :': price_without_tax, 'Prix taxe compris :': price_with_tax,
             'Stock :': inventory}

    return (data,image_absolute_link)


url = 'http://books.toscrape.com/catalogue/category/books/mystery_3/index.html'
session = HTMLSession()
all_books_url = []
data_all_books = {}
links_all_images = []
all_code_upc = []

# get all the category links in the first page
url = get_links_of_category_in_first_page(url)

# get all the page links from each categories
for single_url_of_category in url :
    all_books_url = all_books_url + get_all_books_links_of_one_category(single_url_of_category)

# write all the informations asked
with open('scape.csv','w',encoding='utf-8_sig',newline='') as file :
    header = ['Titre :','Catégorie:','Descripton :','UPC Code :','Etoile :', 'Prix hors taxe :','Prix taxe compris :','Stock :']
    writer =  csv.DictWriter(file,fieldnames=header)
    writer.writeheader()
    for single_url in all_books_url :
        data,links_image = get_data_in_book_page(single_url)
        code_upc = data['UPC Code :']
        writer.writerow(data)
        print(links_image)
        print(code_upc)
        image = session.get(links_image)
        #make a image fold if there is not
        if not os.path.exists('image') :
            os.mkdir('image')
        # name the images by using their upc code
        with open('image\\'+ code_upc +'.jpg','wb') as file :
            file.write(image.content)
