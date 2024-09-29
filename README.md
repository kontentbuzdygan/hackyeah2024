# wideobuzdygan
od kontentbuzdygan

> Życie jest jak droga
> idziemy z wieloma ludźmi
> ale do końca dochodzimy tylko z nielicznymi...
> ~ Miki

Wygodna aplikacja webowa pozwalająca na dogłębną analizę nagrania wideo wypowiedzi, aby ocenić jego jakość. Umożliwia odczytanie transkryptu, podsumowuje znalezione błędy lub problemy i sugeruje sposoby poprawy.

## Wykorzystane technologie AI/ML
- OpenAI Whisper – transformacja mowy na tekst
- OpenAI GPT – analiza tekstu
- OpenCV – wizja komputerowa
- EasyOCR – rozpoznawanie tekstu z obrazu
- DeepFace - analiza twarzy z obrazu
### Inne technologie
- Streamlit – hosting i interfejs użytkownika
- moviepy – ekstrakcja audio z wideo
- Github - kontrola wersji

## Wypróbuj online
Wypróbuj naszą aplikację bez zbędnych instalacji!
[wideobuzdygan](https://wideobuzdygan.streamlit.app/)

## Instalacja

Wideobuzdygan wymaga [Python3.12](https://www.python.org/downloads/) aby działać prawidłowo.

Pobierz kod z repozytorium.
```sh
git clone https://github.com/kontentbuzdygan/hackyeah2024.git wideobuzdygan
```

Stwórz i aktywuj wirtualne środowisko
```sh
cd wideobuzdygan
python -m venv .venv
source .venv/bin/activate
```

Pobierz dependencje i uruchom serwer
```sh
pip install -r requirements.txt
streamlit run src/app.py
```

Strona powinna być teraz dostępna pod [localhost:8501](http://localhost:8501/)

---
**HackYeah2024, Hell Yeah!**

