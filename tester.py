from pprint import pprint
from utils import gcDatabaseWebScrapper

data = gcDatabaseWebScrapper.getCharaDataFromUrl('https://gcdatabase.com/characters/covenant_of_light_tarmiel/1')
pprint(data)