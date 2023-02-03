from requests_html import HTMLSession
import csv
import os

url = 'http://books.toscrape.com/'
session = HTMLSession()
page = session.get(url)
liens_in_categories = []

# charger les liens,prix,nom des categories dans une page  :

while url != None :
    page = session.get(url)
    liens_page = page.html.find('div.image_container a')
    for i in range(len(liens_page)) :
        #print(liens_page[i].absolute_links)
        liens_in_categories.append(liens_page[i].absolute_links)
# retrouver la lien suivante s'il s'agit pas la derniere page
    if page.html.find('li.next a', first='True') != None:
        page_suivant = list(page.html.find('li.next a', first='True').absolute_links)
        url = page_suivant[0]
    else:
        break

with open('scrapperbook.csv', 'a+', encoding='utf-8_sig', newline='') as file:
    writer = csv.writer(file)
    # ecrire une haader dans la premier ligne
    writer.writerow(['Titre', 'Categorie', 'code_upc', 'stock', 'Description', 'Star'])
    for lien in liens_in_categories :
        lien_chaque_page = list(lien)[0]
        page = session.get(lien_chaque_page)
        #extraite tous les elemenets demandes depuis une page
        titre = page.html.find('div.product_main h1', first='true').text
        category = page.html.find('.breadcrumb > li:nth-child(3) > a:nth-child(1)')[0].text
        production_descripton = page.html.find('article.product_page p',first = 'true').text
        liens = page.html.absolute_links
        code_upc = page.html.find('table.table-striped tr td', first='true').text
        #print(f'the code upc of this book is :{code_upc}')
        star_rating = page.html.find('p.star-rating', first='true')
        star = star_rating.attrs.get('class')[1]
        price_withouttaxe = page.html.find('table.table-striped tr td')[2].text
        price = page.html.find('table.table tr td')[3].text
        stock = page.html.find('table.table tr td')[5].text
        #ecrire tous les elements demande dans la fichier csv
        writer.writerows(zip([titre],[category],[code_upc],[stock],[production_descripton],[star]))
        # telecharger les images
        image_url = str(page.html.find('div.active img')[0].attrs.get('src'))
        image_absolute_url = 'http://books.toscrape.com'+ image_url.replace('../..','')
        image = session.get(image_absolute_url)
        #creation le repertoire pour les images
        if not os.path.exists('image') :
            os.mkdir('image')
        with open('image\\'+ code_upc +'.jpg','wb') as file :
            file.write(image.content)



