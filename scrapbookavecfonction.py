import csv
import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from requests_html import HTMLSession


# find if there is a next button in the page
def next_page_url(page) -> Optional[str]:
    next_page_link_a_tag = page.html.find('li.next a', first='True')
    if next_page_link_a_tag is not None:
        next_page_link = list(next_page_link_a_tag.absolute_links)
        return next_page_link[0]
    else:
        nex_page_link = None
        return nex_page_link


def get_links_of_category_in_first_page(first_page_url: str) -> List[str]:
    """
    Find all the category links in the first page except category: "book"

    :param first_page_url: le lien vers la page d'accueil du site
    :return: Une liste d'urls vers les pages des categories
    """
    page = session.get(first_page_url)
    category_links = []
    all_category_content = page.html.find('ul.nav-list a')
    for category_content in all_category_content:
        category_link = list(category_content.absolute_links)[0]
        category_links.append(category_link)

    # Sur le site, le premier lien renvoie en arrière donc on le supprime
    category_links.pop(0)

    return category_links


# get all the links in a single detail page of category
def get_links_of_books_in_page(page) -> list[str]:
    # For Tuple, List, Optional objects, look at the module 'typings' in the standard library

    # Find book links in the page
    books_a_tags = page.html.find('div.image_container a')
    book_links_in_page = []

    for a_tag in books_a_tags:
        book_links_in_page = book_links_in_page + list(a_tag.absolute_links)

    return book_links_in_page


# get all the book's links of the site
def get_all_books_links_of_one_category(category_link: str) -> List[str]:
    print(f'Récupération des livres de la catégorie {category_link}')
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
def get_data_in_book_page(url: str) -> Tuple[Dict[str, str], str]:
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
    data = {'Titre': title, 'Catégorie': category, 'Descripton': production_descripton, 'UPC Code': code_upc,
            'Etoile': star_rating, 'Prix hors taxe': price_without_tax, 'Prix taxe compris': price_with_tax,
            'Stock': inventory}

    return data, image_absolute_link


URL = 'http://books.toscrape.com/'
session = HTMLSession()
all_books_urls = []
data_all_books = {}
links_all_images = []
all_code_upc = []

# get all the category links in the first page
print(f'Récupération des liens des catégories')
category_urls = get_links_of_category_in_first_page(URL)
print(f'{len(category_urls)} catégories trouvées')

# get all the page links from each categories
print(f'Récupération des liens de tous les livres par catégorie')
for single_url_of_category in category_urls:
    all_books_urls = all_books_urls + get_all_books_links_of_one_category(single_url_of_category)
print(f'{len(all_books_urls)} livres trouvés')

# write all the informations asked
csv_path = 'zhao_yuhao_1_donneescrape_13012023.csv'
print(f'Génération du fichier csv au chemin {csv_path} et récupération des images')

# make a image fold if there is not
if not os.path.exists('image'):
    os.mkdir('image')

with open(csv_path, 'w', encoding='utf-8_sig', newline='') as file:
    header = ['Titre', 'Catégorie', 'Descripton', 'UPC Code', 'Etoile', 'Prix hors taxe', 'Prix taxe compris', 'Stock']
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()

    for single_url in all_books_urls:
        data, links_image = get_data_in_book_page(single_url)
        writer.writerow(data)
        image = session.get(links_image)
        # name the images by using their upc code
        # use pathlib to solve the problem of /
        image_to_write = Path('image/' + data['UPC Code'] + '.jpg')
        with open(image_to_write, 'wb') as file:
            file.write(image.content)

print(f'Fini!')
