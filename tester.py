from pprint import pprint
from bs4 import BeautifulSoup
from utils import gcDatabaseWebScrapper
import random
if __name__ == '__main__':
    url='https://gcdatabase.com/characters/roxy/1'
    chara = gcDatabaseWebScrapper.getCharaDataFromUrl(url)
    pprint(chara.skills)
    print(chara.passive)
    print(chara.relic)
