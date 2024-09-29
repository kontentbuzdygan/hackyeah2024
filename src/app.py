from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st
from moviepy.editor import VideoFileClip

from media_analysis import Analyzer
import media_analysis

from pathlib import Path

import annotated_text
from streamlit_extras.tags import tagger_component

import textstat
import pandas as pd
import index_mappings

STEP_COUNT = 10
textstat.set_lang("en")

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
    progress_bar.progress(progress / STEP_COUNT, "Generowanie transkrypcji…")
    analyzer = Analyzer(openai_api_key)
    transcription = analyzer.transcribe(audio_file.name)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Wydzielanie klatek filmu…")
    saved_frames = analyzer.get_frames(video_file.name)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Przycinanie klatek filmu…")
    cropped_frames = analyzer.crop_frames(Path(saved_frames.name))

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Oddzielanie napisów…")
    extracted_subtitles = analyzer.extract_subtitles(Path(cropped_frames.name))

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie emocji…")
    emotions = media_analysis.emotion_analysis(Path(saved_frames.name))

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Oddzielanie napisów…")
    extracted_subtitles = analyzer.extract_subtitles(Path(cropped_frames.name))

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie jakości napisów…")

    subtitle_rating = analyzer.rate_subtitles(transcription.text, extracted_subtitles)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie jakości wypodziedzi…")
    analysis_results = analyzer.analyze_transcription(transcription.text)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Wykrywanie problemów wizualnych…")
    visual_tags = analyzer.analyze_frame(Path(saved_frames.name))

    progress_bar.empty()

    st.write("## Transkrypcja")

    if transcription.segments:
        for segment in transcription.segments:
            st.write(timedelta(seconds=segment.start), segment.text)

    st.write("## Napisy w filmie")
    if extracted_subtitles:
        st.write("\n".join(f"- {subtitle}" for subtitle in extracted_subtitles))
    else:
        st.write("Nie znaleziono napisów w filmie.")

    st.write("### Ocena jakości napisów w filmie")
    st.write(subtitle_rating)

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

    st.write("### Emocje osoby mówiącej")
    st.line_chart(emotions)

    st.write("### Grupa docelowa filmu")
    st.write(analysis_results.grupa_docelowa)

    st.write("### Kluczowe wyrażenia")
    if analysis_results.wyrazenia_kluczowe:
        st.write("\n".join(f"- {word}" for word in analysis_results.wyrazenia_kluczowe))
    else:
        st.write("Nie znaleziono kluczowych wyrażeń.")

    st.write("### Aspekty językowe")

    if analysis_results.aspekty_jezykowe.tagi:
        tags = ", ".join(
            f"{tag.tag} („{tag.przyklad}”)"
            for tag in analysis_results.aspekty_jezykowe.tagi
        )
    else:
        tags = "brak."

    st.write(f"Problemy: {tags}")
    st.write(analysis_results.aspekty_jezykowe.ocena)

    st.write("### Problemy wizualne")
    tag_list = [tag for tag, value in (("Osoby w drugim planie", visual_tags.osoby_w_drugim_planie), ("Odwracanie się", visual_tags.odwracanie_sie), ("Gestykulacja", visual_tags.gestykulacja), ("Mimika", visual_tags.mimika)) if value]
    if tag_list:
        tagger_component(
            "",
            tag_list,
            color_name=["blue", "green", "violet", "red"][:len(tag_list)],
        )
    else:
        st.write("Nie znaleziono problemów wizualnych.")

    st.write("### Indeksy czytelności")
    fog = textstat.gunning_fog(transcription.text)
    flesch = textstat.flesch_reading_ease(transcription.text)
    smog = textstat.smog_index(transcription.text)
    index_table = pd.DataFrame([
        {
            "Indeks": "FOG", "Ocena": fog, "Poziom szkolnictwa": index_mappings.fog_mapping(fog)
        },
        {
            "Indeks": "Flesch", "Ocena": flesch, "Poziom szkolnictwa": index_mappings.flesch_mapping(flesch)
        },
        {
            "Indeks": "SMOG", "Ocena": smog, "Poziom szkolnictwa": index_mappings.smog_mapping(smog)
        },
    ])
    st.dataframe(index_table, hide_index=True, use_container_width=True)

    st.write("### Sentyment wypowiedzi")
    if analysis_results.sentyment_wypowiedzi:
        st.line_chart(
            [sentiment.sentyment for sentiment in analysis_results.sentyment_wypowiedzi]
        )

        annotated_text.annotated_text([(sentiment.fragment, f"sentyment: {sentiment.sentyment}") for sentiment in analysis_results.sentyment_wypowiedzi])
    else:
        st.write("Nie znaleziono zmian sentymentu w wypowiedzi.")

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
        st.write("Nie znaleziono niezrozumiałych wyrazów.")

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

    st.write("### Poprawiona wypowiedź")
    st.write(f"_{analysis_results.poprawiona_wypowiedz}_")

    st.write("### Angielskie tłumaczenie")
    st.write(f"_{analysis_results.angielskie_tlumaczenie}_")
