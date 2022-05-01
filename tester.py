from pprint import pprint
from utils import gcDatabaseWebScrapper

data = gcDatabaseWebScrapper.getCharaDataFromUrl('https://gcdatabase.com/characters/matrona/1')
pprint(data)