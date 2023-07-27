# Name: ScrapBot
# Author: Gerhard Eibl
# Creation date: 09/09/2022
# Modification date: 20/07/2023
# Version: 0.5
""" This is a script scraper, to retrieve information from wine dealers """
# -----------------------------------------------------------------------
import json, os
import re
# import psycopg2
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
# from dotenv import load_dotenv

# load_dotenv()

# def get_db_connection():
#     connexion = psycopg2.connect(
#         host="localhost",
#         database="api_alpha",
#         user=os.environ.get("user"),
#         password=os.environ.get("password"),
#     )
#     return connexion
#
#
# conn = get_db_connection()

# variable = ""

y, w, z = 0, 0, 0

urls_dico = {}
urls_filtered_dico = {}
pre_url_dico = {}

URL = "https://www.idealwine.com/fr/cote/bordeaux.jsp"

page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
soup2 = soup.find("div", class_="masonry-layout")

for link in soup2.findAll('a', attrs={'href': re.compile("^/fr/prix-vin/")}):

    link_url = link.get('href')
    urls = link_url.split("Bouteille")
    pre_url = urls[0][:-5]
    urls_filtered = urls[1]
    if urls_filtered not in urls_filtered_dico:
        urls_filtered_dico[urls_filtered] = pre_url

for value in urls_filtered_dico:
    years = 2018

    while years > 1994:
        try:
            description_dico = {}
            wine_URL = 'https://www.idealwine.com/' + urls_filtered_dico[value] + str(years) + '-Bouteille' + value

            wine_page = requests.get(wine_URL)
            wine_soup = BeautifulSoup(wine_page.content, 'html.parser')

            wine_name_soup = wine_soup.find("h2")
            wine_name_with_info = wine_name_soup.find("strong")
            wine_split = wine_name_with_info.text.split("Les informations")

            n_wine_name = unidecode(wine_split[0].replace("'", "_"))

            wine_price_soup = wine_soup.find("article", class_="bg-blue price-table")
            wine_price = wine_price_soup.find_all("span")
            price = re.sub('[^0-9]', '', wine_price[1].text)
            print(wine_URL)
            print("2022 price for : " + value[1:-4] + " " + str(years) + " : " + price + " euros\n")

            wine_data = wine_soup.find("article", class_="hide-print info-cote-new") \
                .find('ul', class_="property")

            wine_li = wine_data.find_all("li")

            for item in wine_li:
                full_data = item.text
                data_split = full_data.split(':')

                title = data_split[0]
                data = data_split[1]

                n_title = unidecode(title)
                n_data = unidecode(data)

                if n_title not in description_dico:
                    description_dico[n_title] = n_data

            if "Appellation " not in description_dico:
                description_dico["Appellation "] = ""
            if "Domaine " not in description_dico:
                description_dico["Domaine "] = ""
            if "Couleur " not in description_dico:
                description_dico["Couleur "] = ""
            if "Encepagement " not in description_dico:
                description_dico["Encepagement "] = ""
            if "Pays/region " not in description_dico:
                description_dico["Pays/region "] = ""
            if "Proprietaire " not in description_dico:
                description_dico["Proprietaire "] = ""

            nom = n_wine_name
            appellation = description_dico["Appellation "].replace("'", "_")
            domaine = description_dico["Domaine "].replace("'", "_")
            millesime = str(years)
            couleur = description_dico["Couleur "]
            encepagement = description_dico["Encepagement "]
            region = description_dico["Pays/region "]
            proprietaire = description_dico["Proprietaire "].replace("'", "_")

            Json_file = {"Nom": nom,
                         "Appellation": appellation,
                         "Domaine": domaine,
                         "Millesime": millesime,
                         "Couleur": couleur,
                         "Encepagement": encepagement,
                         "Region": region,
                         "Proprietaire": proprietaire}

            print("Nom : " + nom + "\n"
                  "Appellation : " + appellation + "\n"
                  "Domaine : " + domaine + "\n"
                  "Millesime : " + millesime + "\n"
                  "Couleur : " + couleur + "\n"
                  "Encepagement : " + encepagement + "\n"
                  "Region : " + region + "\n"
                  "Proprietaire : " + proprietaire + "\n"
                  "Prix : " + price + " euros\n")

            # try:
            #     type = "vin"
            #     item_count = 1
            #     json_config = json.dumps(Json_file)
            #     name = appellation + "-" + nom + "-" + couleur + "-" + millesime
            #     active = False
            #
            #     try:
            #
            #         cursor = conn.cursor()
            #
            #         cursor.execute(
            #             "INSERT INTO placement VALUES (nextval('placement_id_seq'), %s, %s, %s, %s, %s)",
            #             (type, item_count, json_config, name, active),
            #         )
            #
            #         conn.commit()
            #         cursor.close()
            #     except Exception as e_1:
            #         print("Problem inserting into placement")
            #         print(e_1)
            #
            #
            #
            #
            #
            #     try:
            #         cursor = conn.cursor()
            #
            #         cursor.execute("SELECT id FROM placement WHERE name = '{0}';".format(name))
            #         placement = cursor.fetchone()
            #         id_placement = placement[0]
            #         date = "'2022-11-28 21:22:23'"
            #         price = price
            #         currency = "euro"
            #
            #         cursor.execute(
            #             "INSERT INTO placement_price VALUES (nextval('placement_price_id_seq'), %s, %s, %s, %s)",
            #             (id_placement, date, price, currency),
            #         )
            #
            #         conn.commit()
            #         cursor.close()
            #
            #     except Exception as e_2:
            #
            #         print("Problem inserting into placement_price", )
            #         print(e_2)
            #
            # except:
            #     print("Error with DB insertion")

        except:
            print("No year registered for this bottle : " + str(years) + " " + value)

        years -= 1

# conn.close()