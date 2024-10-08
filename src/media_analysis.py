import base64
import itertools
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

import cv2
import easyocr
from deepface import DeepFace
from fuzzywuzzy import fuzz
from openai import Client
from openai.types.audio import TranscriptionVerbose
from pydantic import BaseModel, Field


class Tag(BaseModel):
    tag: Literal[
        "przerywniki",
        # "za szybkie tempo",
        "nadmierne powtórzenia",
        "zmiana tematu wypowiedzi",
        "trudne, za długie słowa",
        "żargon",
        "obcy język",
        # "za długa pauza",
        "za dużo liczb",
        # "drugi plan",
        # "odwracanie się",
        "przekręcenia",
        # "gestykulacja",
        "przerywniki",
        # "mimika",
        # "za cicho",
        # "szeptem",
        "błędne słowa",
        # "wypowiedź niezgodna z transkrypcją",
        # "szum",
        "za długie zdania",
        "używanie strony biernej",
        # "akcentowanie",
        "za dużo liczb",
        # "mówienie głośniej",
    ]
    przyklad: str


class AspektyJezykowe(BaseModel):
    ocena: str = Field(
        description="Ocena aspektów językowych wypowiedzi w nawiązaniu do prostego języka."
    )
    tagi: list[Tag] = Field(description="Tagi wypowiedzi z przykładami występowania.")


class SentymentWypowiedzi(BaseModel):
    fragment: str = Field(description="Fragment wypowiedzi.")
    sentyment: int = Field(
        description="Sentyment fragmentu: -5 negatywny, +5 pozytywny"
    )


class NiezrozumialyWyraz(BaseModel):
    wyraz: str = Field(description="Wyraz błędny lub niezrozumiały.")
    opis: str = Field(description="Dlaczego ten wyraz jest nieprawidłowy.")


class AnaysisResults(BaseModel):
    pytania: list[str] = Field(description="Utwórz 10 pytań do wypowiedzi.")
    grupa_docelowa: str = Field(
        description="Dla jakiej grupy docelowej kierowana jest ta wypowiedź?"
    )
    wyrazenia_kluczowe: list[str] = Field(
        description="Lista kluczowych wyrazów i fraz."
    )
    aspekty_jezykowe: AspektyJezykowe
    sentyment_wypowiedzi: list[SentymentWypowiedzi] = Field(
        description="Cała wypowiedź podzielona na fragmenty."
    )
    podsumowanie: str = Field(description="Krótkie podsumowanie wypowiedzi.")
    niezrozumiale_wyrazy: list[NiezrozumialyWyraz] = Field(
        description="Lista wyrazów błędnych lub niezrozumiałych w wypowiedzi."
    )
    sugestie_doboru_slow: list[str] = Field(
        description="Proponowane zmiany doboru słów."
    )
    poprawiona_wypowiedz: str = Field(
        description="Przepisana wypowiedź z poprawionymi aspektami językowymi oraz błędnymi wyrazami."
    )
    angielskie_tlumaczenie: str = Field(
        description="Tłumaczenie wypowiedzi na język angielski."
    )


class VisualTags(BaseModel):
    osoby_w_drugim_planie: bool = Field(description="Czy film zawiera drugoplanowca?")
    odwracanie_sie: bool = Field(description="Czy osoba prowadząca odwraca się?")
    gestykulacja: bool = Field(description="Czy osoba prowadząca gestykuluje?")
    mimika: bool = Field(description="Czy osoba prowadząca używa wyraźnej mimiki?")


class Analyzer:
    def __init__(self, openai_api_key: str):
        self.client = Client(api_key=openai_api_key)

    def transcribe(self, file_path: str) -> TranscriptionVerbose:
        with open(file_path, "rb") as f:
            return self.client.audio.transcriptions.create(
                file=f,
                model="whisper-1",
                response_format="verbose_json",
                language="pl",
                timestamp_granularities=["word", "segment"],
            )

    def rate_subtitles(self, transcription: str, subtitles: list[str]) -> str:
        result = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Treść wypowiedzi w filmie:\n{transcription}\n\n"
                    f"Treść napisów filmu:\n{"\n".join(subtitles)}",
                },
                {
                    "role": "system",
                    "content": "Czy napisy są zgodne z treścią wypowiedzi? "
                    "Czy zawierają jakieś błędy lub pomyłki? "
                    "Napisz krótką informację.",
                },
            ],
            model="gpt-4o-2024-08-06",
        )

        return result.choices[0].message.content  # type: ignore

    def analyze_transcription(self, transcription: str) -> AnaysisResults:
        result = self.client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "user",
                    "content": transcription,
                },
                {
                    "role": "system",
                    "content": "Na podstawie powyższej transkrypcji wypowiedzi wypełnij model JSON.",
                },
            ],
            model="gpt-4o-2024-08-06",
            response_format=AnaysisResults,
        )

        message = result.choices[0].message

        if message.refusal is not None:
            raise Exception(message.refusal)

        return message.parsed  # type: ignore

    def analyze_frames(self, frames: Path) -> VisualTags:
        content = [
            {
                "type": "text",
                "text": "Na podstawie klatek z filmu uzupełnij model JSON.",
            },
        ]

        content.extend(
            (
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64.b64encode(open(base64_file, "rb").read()).decode()}",
                        "detail": "low",
                    },
                }
                for base64_file in sorted(frames.iterdir())  # type: ignore
            )
        )

        result = self.client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "user",
                    "content": content,
                },  # type: ignore
            ],
            model="gpt-4o-2024-08-06",
            response_format=VisualTags,
        )

        message = result.choices[0].message

        if message.refusal is not None:
            raise Exception(message.refusal)

        return message.parsed  # type: ignore


def get_frames(input_path: str) -> TemporaryDirectory:
    temp_frames = TemporaryDirectory()
    vidcap = cv2.VideoCapture(input_path)
    success, image = vidcap.read()
    success = True

    for i in itertools.count():
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (i * 1_000))
        success, image = vidcap.read()

        if not success:
            break

        cv2.imwrite(str(Path(temp_frames.name) / f"frame_{i:0>8}.png"), image)

    return temp_frames


def crop_frames(input_path: Path) -> TemporaryDirectory:
    temp_dir = TemporaryDirectory()

    for file in os.listdir(input_path):
        img = cv2.imread(str(input_path / file))
        crop_img = img[918:1050, 460:1475]
        cv2.imwrite(str(Path(temp_dir.name) / file), crop_img)

    return temp_dir


def extract_subtitles(input_path: Path) -> list[str]:
    reader = easyocr.Reader(["pl"])

    subtitles = [
        " ".join(reader.readtext(str(input_path / file), detail=0))
        for file in sorted(os.listdir(input_path))
    ]

    subtitles = filter(lambda subtitle: subtitle.strip(), subtitles)
    previous_subtitle = None

    def is_duplicate(new_subtitle: str) -> bool:
        nonlocal previous_subtitle

        if previous_subtitle is None:
            previous_subtitle = new_subtitle
            return False

        result = fuzz.ratio(previous_subtitle, new_subtitle)
        previous_subtitle = new_subtitle
        return result > 90

    return list(filter(lambda subtitle: not is_duplicate(subtitle), subtitles))


def emotion_analysis(input_path: Path) -> list[dict[str, float]]:
    emotions = []

    for file in sorted(input_path.iterdir()):
        try:
            result = DeepFace.analyze(cv2.imread(str(file)), actions=["emotion"])[0]
            if result["face_confidence"] >= 0.75:
                emotions.append(result["emotion"])
        except ValueError:
            # no face detected
            continue

    return emotions
