from pprint import pprint
from bs4 import BeautifulSoup
from utils import gcDatabaseWebScrapper
import random
if __name__ == '__main__':
    url='https://gcdatabase.com/characters/camila/1'
    chara = gcDatabaseWebScrapper.getCharaDataFromUrl(url)
    pprint(chara.skills)