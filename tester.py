from pprint import pprint
from utils import gcDatabaseWebScrapper
import cv2
baseUrl = 'https://gcdatabase.com'


charaUrls = gcDatabaseWebScrapper.getCharaUrls(baseUrl+'/characters')
charas = [gcDatabaseWebScrapper.getCharaDataFromUrl(
    f'{baseUrl}/{charaUrl}') for charaUrl in charaUrls]
charas = gcDatabaseWebScrapper.checkForSrSsr(charas)
for chara in charas:
    nameFile = 'D:/Images/7dsgc/CharaPics/'+chara.name+'.png'
    with open(nameFile,'wb') as f:
        f.write(chara.binImg)
    img = cv2.imread(nameFile)
    cv2.imwrite(nameFile,img)