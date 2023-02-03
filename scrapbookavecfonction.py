from requests_html import HTMLSession
import csv
import os

def url_de_page_suivante(url_actuelle) :
    session = HTMLSession()
    page = session.get(url_actuelle)
    if page.html.find('li.next a', first='True') != None :
        url_actuelle = list(page.html.find('li.next a', first='True').absolute_links)[0]
        return url_actuelle
    else :
        return None

def element_page(url) :
    session = HTMLSession()
    page = session.get(url)
    titre = page.html.find('div.product_main h1', first='true').text
    category = page.html.find('.breadcrumb > li:nth-child(3) > a:nth-child(1)')[0].text
    production_descripton = page.html.find('article.product_page p', first='true').text
    liens = page.html.absolute_links
    code_upc = page.html.find('table.table-striped tr td', first='true').text
    # print(f'the code upc of this book is :{code_upc}')
    star_rating = page.html.find('p.star-rating', first='true')
    star = star_rating.attrs.get('class')[1]
    price_withouttaxe = page.html.find('table.table-striped tr td')[2].text
    price = page.html.find('table.table tr td')[3].text
    stock = page.html.find('table.table tr td')[5].text
    image_url = str(page.html.find('div.active img')[0].attrs.get('src'))
    return [titre],[category],[production_descripton],[code_upc],[star],[price_withouttaxe],[price],[stock,image_url]

def url_des_page_category(url) :
    session = HTMLSession()
    page = session.get(url)
    urls = []
    tous_les_liens_par_category = page.html.find('ul.nav-list a')
    for lien in tous_les_liens_par_category :
        urls.append(list(lien.absolute_links))
    del(urls[0])
    return urls

def urls_dune_category(url) :
    session = HTMLSession()
    urlspage = []
    i = 0
    while url != None :
        page = session.get(url)
        while i < len(page.html.find('div.image_container a')) :
            urlspage.append = list(page.html.find('div.image_container a')[i].absolute_links)
            i += 1
        url = url_de_page_suivante(url)

    return urlspage


url = 'http://books.toscrape.com/catalogue/category/books/travel_2/index.html '
for urlss in urls_dune_category(url) :
    print(urlss)


'''
for url_une_page in url_des_page_category(url) :
    print(url_une_page[0])
    t = element_page(url_une_page[0])

   #with open('chanpin.csv','a+',encoding='utf-8_sig',newline='') as f :
    #   writer =  csv.writer(f)
    #   writer.writerows(zip(t))
'''