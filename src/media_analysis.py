from openai import Client
from openai.types.audio import TranscriptionVerbose
from pydantic import BaseModel, Field
import easyocr
import cv2
import os
from PIL import Image
from tempfile import NamedTemporaryFile, TemporaryDirectory


class AspektyJezykowe(BaseModel):
    ocena: str = Field(
        description="Ocena aspektów językowych wypowiedzi w nawiązaniu do prostego języka wraz z wyliczeniem wskaźników."
    )
    tag: str = Field(description="Tag powyższej oceny.")


class SentymentWypowiedzi(BaseModel):
    fragment: str = Field(description="Fragment wypowiedzi.")
    sentyment: int = Field(
        description="Sentyment fragmentu: -5 negatywny, +5 pozytywny"
    )


class AnaysisResults(BaseModel):
    pytania: list[str] = Field(description="Utwórz 10 pytań do wypowiedzi.")
    grupa_docelowa: str = Field(
        description="Dla jakiej grupy docelowej kierowana jest ta wypowiedź?"
    )
    wyrazenia_kluczowe: list[str] = Field(description="Lista kluczowych zdań i fraz.")
    aspekty_jezykowe: AspektyJezykowe
    sentyment_wypowiedzi: list[SentymentWypowiedzi]
    podsumowanie: str = Field(description="Krótkie podsumowanie wypowiedzi.")
    niezrozumiale_wyrazy: list[str] = Field(
        description="Lista wyrazów błędnych lub niezrozumiałych."
    )
    poprawiona_wypowiedz: str = Field(
        description="Przepisana wypowiedź z poprawionymi aspektami językowymi oraz błędnymi wyrazami."
    )
    sugestie_doboru_slow: list[str] = Field(
        description="Proponowane zmiany doboru słów."
    )
    angielskie_tlumaczenie: str = Field(
        description="Tłumaczenie wypowiedzi na język angielski."
    )


class Analyzer:
    def __init__(self):
        self.client = Client()

    # TODO: Allow passing the file directly
    def transcribe(self, filename: str) -> TranscriptionVerbose:
        with open(filename, "rb") as f:
            return self.client.audio.transcriptions.create(
                file=f,
                model="whisper-1",
                response_format="verbose_json",
                language="pl",
                timestamp_granularities=["segment"],
            )

    def analyze_transcription(self, transcription: str) -> AnaysisResults:
        result = self.client.beta.chat.completions.parse(
            messages=[
                {
                    "content": transcription,
                    "role": "user",
                },
                {
                    "content": "Na podstawie powyższej transkrypcji wypowiedzi wypełnij model JSON.",
                    "role": "system",
                },
            ],
            model="gpt-4o-2024-08-06",
            response_format=AnaysisResults,
        )

        return result.choices[0].message.parsed

    def get_frames(self, pathIn):
        temp_frames = TemporaryDirectory()
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
            cv2.imwrite(temp_frames.name + "\\frame%d.jpg" % count, image)
            count = count + 1

        return temp_frames

    def crop_frames(self, pathIn):
        temp_dir = TemporaryDirectory()

        for file in os.listdir(pathIn.name):
            img = cv2.imread(pathIn.name + "\\" + file)
            crop_img = img[918:1050, 460:1475]
            cv2.imwrite(temp_dir.name + "\\" + file, crop_img) 
        
        return temp_dir

    def extract_subtitles(self, pathIn):
        subtitles = []

        for i in range(len(os.listdir(pathIn.name))):
            reader = easyocr.Reader(['pl'])
            result = reader.readtext(pathIn.name + "\\frame%d.jpg" % i, detail=0)
            subtitles.append(" ".join(result))

        return dict.fromkeys(subtitles).keys()
