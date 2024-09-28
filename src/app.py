from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st
from moviepy.editor import VideoFileClip

from media_analysis import Analyzer

STEP_COUNT = 6

st.write(
    """
    # :red[wideo]buzdygan
    od **kontentbuzdygan**
    """
)

openai_api_key = st.text_input(
    "Klucz API OpenAI",
    help="Utwórz konto i wprowadź swój klucz",
    type="password",
)

video = st.file_uploader(
    "Prześlij film, który chcesz przeanalizować", disabled=not openai_api_key
)

if video:
    st.video(video)

    progress = 0
    progress_bar = st.progress(progress / STEP_COUNT, text="Oddzielanie dźwięku…")

    video_file = NamedTemporaryFile(delete_on_close=False)
    video_file.write(video.getvalue())
    video_file.close()
    clip = VideoFileClip(video_file.name)
    audio_file = NamedTemporaryFile(suffix=".mp3", delete_on_close=False)
    audio_file.close()
    clip.audio.write_audiofile(audio_file.name)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Generowanie transktypcji…")
    analyzer = Analyzer(openai_api_key)
    transcription = analyzer.transcribe(audio_file.name)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Wydzielanie klatek filmu…")

    st.write("## Transkrypcja")

    if transcription.segments:
        for segment in transcription.segments:
            st.write(timedelta(seconds=segment.start), segment.text)

    saved_frames = analyzer.get_frames(video_file.name)
    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Przycinanie klatek filmu…")
    cropped_frames = analyzer.crop_frames(Path(saved_frames.name))
    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Oddzielanie napisów…")
    extracted_subtitles = analyzer.extract_subtitles(Path(cropped_frames.name))

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie jakości napisów…")

    st.write("## Napisy w filmie")
    if extracted_subtitles:
        st.write("\n".join(f"- {subtitle}" for subtitle in extracted_subtitles))
    else:
        st.write("Nie wykryto napisów w filmie.")

    subtitle_rating = analyzer.rate_subtitles(transcription.text, extracted_subtitles)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie jakości wypodziedzi…")

    st.write("### Ocena jakości napisów w filmie")
    st.write(subtitle_rating)

    analysis_results = analyzer.analyze_transcription(transcription.text)

    progress_bar.empty()

    st.write("## Analiza")
    st.write("### 10 Pytań do filmu")

    if analysis_results.wyrazenia_kluczowe:
        st.write(
            "\n".join(
                f"{i}. {question}"
                for i, question in enumerate(analysis_results.pytania, 1)
            )
        )
    else:
        st.write("Brak pytań do wypowiedzi.")

    st.write("### Grupa docelowa filmu")
    st.write(analysis_results.grupa_docelowa)

    st.write("### Kluczowe wyrażenia")
    if analysis_results.wyrazenia_kluczowe:
        st.write("\n".join(f"- {word}" for word in analysis_results.wyrazenia_kluczowe))
    else:
        st.write("Nie wykryto kluczowych wyrażeń.")

    st.write("### Aspekty językowe")

    st.write(f"Tag: {analysis_results.aspekty_jezykowe.tag}")
    st.write(f"Opis: {analysis_results.aspekty_jezykowe.ocena}")

    st.write("### Sentyment wypowiedzi")
    if analysis_results.sentyment_wypowiedzi:
        st.line_chart(
            [sentiment.sentyment for sentiment in analysis_results.sentyment_wypowiedzi]
        )
        for sentiment in analysis_results.sentyment_wypowiedzi:
            st.write(f"- „{sentiment.fragment}”: sentyment {sentiment.sentyment}")
    else:
        st.write("Nie wykryto zmian sentymentu w wypowiedzi.")

    st.write("### Podsumowanie wypowiedzi")
    st.write(analysis_results.podsumowanie)

    st.write("### Niezrozumiałe wyrazy")
    if analysis_results.niezrozumiale_wyrazy:
        st.write(
            "\n".join(
                f"- „{word.wyraz}” — {word.opis}"
                for word in analysis_results.niezrozumiale_wyrazy
            )
        )
    else:
        st.write("Nie wykryto niezrozumiałych wyrazów.")

    st.write("### Poprawiona wypowiedź")
    st.write(analysis_results.poprawiona_wypowiedz)

    st.write("### Sugestie doboru słów")
    if analysis_results.sugestie_doboru_slow:
        st.write(
            "\n".join(
                f"- {suggestion}"
                for suggestion in analysis_results.sugestie_doboru_slow
            )
        )
    else:
        st.write("Brak sugestii doboru słów.")

    st.write("### Angielskie tłumaczenie")
    st.write(analysis_results.angielskie_tlumaczenie)
