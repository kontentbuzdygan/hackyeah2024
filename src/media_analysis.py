from openai import Client
from openai.types.audio import TranscriptionVerbose
from pydantic import BaseModel, Field


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
    def __init__(self, openai_api_key: str):
        self.client = Client(api_key=openai_api_key)

    def transcribe(self, file_path: str) -> TranscriptionVerbose:
        with open(file_path, "rb") as f:
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

        message = result.choices[0].message

        if message.refusal is not None:
            raise Exception(message.refusal)

        return message.parsed  # type: ignore
