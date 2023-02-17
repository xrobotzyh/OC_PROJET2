import csv
import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from requests_html import HTMLSession
import re
import collections


# find if there is a next button at the  bottom of the page
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
    :return: Une liste d'urls vers les pages des categories,une liste de nom des categories
    """
    page = session.get(first_page_url)
    category_links = []
    category_names = []
    all_category_content = page.html.find('ul.nav-list a')
    for category_content in all_category_content:
        category_link = list(category_content.absolute_links)[0]
        category_name = category_content.text
        category_links.append(category_link)
        category_names.append(category_name)

    # Sur le site, le premier lien 'book' renvoie en arrière donc on le supprime
    del category_links[0]
    del category_names[0]

    return category_links, category_names


# get all the links in a single detail page of category
def get_links_of_books_in_page(page) -> list[str]:
    """
        Find all the links in one page

        :param page: l'objet contient tous les element page
        :return: Une liste d'urls vers les pages produits
        """

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

    # create a dictionary to translate the word to number
    star = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    # using the arguments attrs to get the star rating informations
    star_rating = star[star_rating_information.attrs.get('class')[1]]

    price_without_tax_word = page.html.find('table.table-striped tr td')[2].text
    price_without_tax = re.findall(r"\d+\.?\d*", price_without_tax_word)
    price_with_tax_word = page.html.find('table.table tr td')[3].text
    price_with_tax = re.findall(r"\d+\.?\d*", price_with_tax_word)
    inventory_word = page.html.find('table.table tr td')[5].text
    inventory = re.findall(r"\d+", inventory_word)

    # image links to absolute links by re write the link
    image_link = str(page.html.find('div.active img')[0].attrs.get('src'))
    image_absolute_link = 'http://books.toscrape.com' + image_link.replace('../..', '')

    # Use dictionary to write to the csv
    data = collections.OrderedDict()
    data = {
        'product_page_url': url,
        'UPC Code': code_upc,
        'Titre': title,
        'Prix taxe compris': price_with_tax[0],
        'Prix hors taxe': price_without_tax[0],
        'Stock': inventory[0],
        'Descripton': production_descripton,
        'Catégorie': category,
        'Etoile': star_rating,
        'image link': image_absolute_link
    }

    return data, image_absolute_link


URL = 'http://books.toscrape.com/'
session = HTMLSession()
all_books_urls = []
data_all_books = {}
links_all_images = []
all_code_upc = []
if not os.path.exists('output_data'):
    os.mkdir('output_data')


def run_phase1():
    if not os.path.exists('output_data/phase1'):
        os.mkdir('output_data/phase1')
    product_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    print(f'Récupération des données du livre à l\'url: {product_url}')
    data, _ = get_data_in_book_page(product_url)
    csv_path = Path('output_data/phase1/' + data['UPC Code'] + '.csv')
    del data['image link']
    with open(csv_path, 'w', encoding='utf-8_sig', newline='') as file:
        header = ['product_page_url',
                  'UPC Code',
                  'Titre',
                  'Prix taxe compris',
                  'Prix hors taxe',
                  'Stock',
                  'Descripton',
                  'Catégorie',
                  'Etoile']
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerow(data)
    print(f'Données écrites dans le fichier {csv_path}')


def run_phase2():
    if not os.path.exists('output_data/phase2'):
        os.mkdir('output_data/phase2')
    category_url = 'To do'
    pass


def run_phase3_4():
    # get all the category links in the first page
    print(f'Récupération des liens des catégories')
    category_urls, category_names = get_links_of_category_in_first_page(URL)
    print(f'{len(category_urls)} catégories trouvées')
    # make a CSV folder if there is not have
    if not os.path.exists('output_data'):
        os.mkdir('output_data')

    # make a image folder if there is not have
    if not os.path.exists('output_data/images'):
        os.mkdir('output_data/images')
    i = 0
    nombres_livres = 0
    # For every single category make a separate csv file named by their category name and write a header
    for single_url_of_category in category_urls:
        all_books_urls_of_one_category = get_all_books_links_of_one_category(single_url_of_category)
        # make a directory for all the files csv which is named by their category
        csv_path = Path('output_data/' + category_names[i] + '.csv')
        nombres_livres_dans_une_category = len(all_books_urls_of_one_category)
        # get total number of the books
        nombres_livres = nombres_livres_dans_une_category + nombres_livres
        print(f'{nombres_livres_dans_une_category} livres trouvés dans la: {category_names[i]}')
        print(f'Il y a {i + 1} catégorie qu\'on a trouvé déjà')
        with open(csv_path, 'w', encoding='utf-8_sig', newline='') as file:
            header = ['product_page_url',
                      'UPC Code',
                      'Titre',
                      'Prix taxe compris',
                      'Prix hors taxe',
                      'Stock',
                      'Descripton',
                      'Catégorie',
                      'Etoile',
                      'image link']
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            i = i + 1
            # For every single page in one category, get the informations neededs and download the pictures
            for single_url_of_one_category in all_books_urls_of_one_category:
                data, links_image = get_data_in_book_page(single_url_of_one_category)
                writer.writerow(data)
                image = session.get(links_image)
                # name the images by using their upc code
                # use pathlib to solve the problem of /
                image_to_write = Path('output_data/images/' + data['UPC Code'] + '.jpg')
                with open(image_to_write, 'wb') as file:
                    file.write(image.content)
    print(f'Il y a {nombres_livres} livres au total')
    print(f'Fini!')


print('Executé au chargement du module')

if __name__ == '__main__':
    print('Executé comme un script')
    # run_phase1()
    run_phase2()
    run_phase3_4()
