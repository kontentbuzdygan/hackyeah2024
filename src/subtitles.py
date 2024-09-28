import easyocr
import cv2
import os
from PIL import Image


def extractImages(pathIn, pathOut):
    if not os.path.isdir("frames"):
        os.makedirs("frames")

    subtitles = []
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success,image = vidcap.read()
    success = True

    while True:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))
        success,image = vidcap.read()
        print ('Read a new frame: ', success)
        if success is False:
            break
        cv2.imwrite(pathOut + "\\frame%d.jpg" % count, image)
        img = cv2.imread(pathOut + "\\frame%d.jpg" % count)
        crop_img = img[918:1050, 460:1475]
        cv2.imwrite(pathOut + "\\frame%d.jpg" % count, crop_img)
        count = count + 1

    for i in range(count):
        reader = easyocr.Reader(['pl'])
        result = reader.readtext(pathOut + "\\frame%d.jpg" % i, detail=0)
        subtitles.append(" ".join(result))
        print(subtitles)

    print(dict.fromkeys(subtitles).keys())

extractImages("C:\\Users\\mikolajs\\Downloads\\HY_2024_film_01.mp4", "C:\\repos\\hackyeah2024\\frames")
