import dotenv
from openai import Client
import easyocr
import cv2

if __name__ == '__main__':  # This check is mandatory for Windows.
    print()

dotenv.load_dotenv()

client = Client()

#with open("C:\\Users\\mikolajs\\Downloads\\catcut_HY_2024_film_01.wav", "rb") as f:
#    print(client.audio.transcriptions.create(file=f, model="whisper-1", language="pl", prompt="Słuchaj audio do końca i nie usuwaj niczego. Nie poddawaj audio własnej interpretacji"))


def extractImages(pathIn, pathOut):
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success,image = vidcap.read()
    success = True
    while True:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))    # added this line 
        success,image = vidcap.read()
        print ('Read a new frame: ', success)
        if success is False:
            break
        cv2.imwrite( pathOut + "\\frame%d.jpg" % count, image)     # save frame as JPEG file
        count = count + 1

extractImages("C:\\Users\\mikolajs\\Downloads\\HY_2024_film_01.mp4", "C:\\repos\\hackyeah2024\\frames")

for i in range(32):
    reader = easyocr.Reader(['pl']) # this needs to run only once to load the model into memory
    result = reader.readtext(f"C:\\repos\\hackyeah2024\\frames\\frame{i}.jpg", detail=0)
    print(result)


# 460, 918
# 1475, 918
# 460, 1050
# 
