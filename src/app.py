import math
from datetime import timedelta
from pathlib import Path
from tempfile import NamedTemporaryFile

import annotated_text
import streamlit as st
from moviepy.editor import VideoFileClip
from streamlit_extras.tags import tagger_component

import media_analysis
from media_analysis import Analyzer

from pathlib import Path

import annotated_text
from streamlit_extras.tags import tagger_component

import textstat
import pandas as pd
import index_mappings

STEP_COUNT = 9
textstat.set_lang("pl")

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

videos = st.file_uploader(
    "Prześlij film, który chcesz przeanalizować",
    accept_multiple_files=True,
    type=["mp4", "webm", "mkv"],
    disabled=not openai_api_key,
)

if videos:
    progress = 0
    progress_bar = st.progress(progress / STEP_COUNT, text="Oddzielanie dźwięku…")

    for video in videos:
        st.video(video)

    video_files = []
    audio_files = []

    for video in videos:
        video_file = NamedTemporaryFile(delete_on_close=False)
        video_files.append(video_file)
        video_file.write(video.getvalue())
        video_file.close()
        clip = VideoFileClip(video_file.name)
        audio_file = NamedTemporaryFile(suffix=".mp3", delete_on_close=False)
        audio_files.append(audio_file)
        audio_file.close()
        clip.audio.write_audiofile(audio_file.name)

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Generowanie transkrypcji…")
    analyzer = Analyzer(openai_api_key)
    transcriptions = [
        analyzer.transcribe(audio_file.name) for audio_file in audio_files
    ]

    for transcription in transcriptions:
        if (
            transcription.segments is not None
            and len(transcription.segments) > 0
            and transcription.words is not None
            and len(transcription.words) > 0
        ):
            transcription.segments[0].start = transcription.words[0].start

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Wydzielanie klatek filmu…")
    saved_frames = [analyzer.get_frames(video_file.name) for video_file in video_files]

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie emocji…")
    emotions = [
        media_analysis.emotion_analysis(Path(saved_frames.name))
        for saved_frames in saved_frames
    ]

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Przycinanie klatek filmu…")
    cropped_frames = [
        analyzer.crop_frames(Path(saved_frames.name)) for saved_frames in saved_frames
    ]

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Oddzielanie napisów…")
    extracted_subtitles = [
        analyzer.extract_subtitles(Path(cropped_frames.name))
        for cropped_frames in cropped_frames
    ]

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie jakości napisów…")

    subtitle_ratings = [
        analyzer.rate_subtitles(transcription.text, subtitles)
        for transcription, subtitles in zip(
            transcriptions, extracted_subtitles, strict=True
        )
        if transcription.text and subtitles
    ]

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Analizowanie jakości wypowiedzi…")
    analysis_results = [
        analyzer.analyze_transcription(transcription.text)
        for transcription in transcriptions
    ]

    progress += 1
    progress_bar.progress(progress / STEP_COUNT, "Wykrywanie problemów wizualnych…")
    visual_tags = [
        analyzer.analyze_frame(Path(saved_frames.name)) for saved_frames in saved_frames
    ]

    progress_bar.empty()

    st.write("## Transkrypcja")

    for i, transcription in enumerate(transcriptions):
        if i > 0:
            st.divider()

        if transcription.segments:
            for segment in transcription.segments:
                chars_per_sec = len(segment.text) / (segment.end - segment.start)
                st.write(
                    timedelta(seconds=math.floor(segment.start)),
                    segment.text,
                    f":{"gray" if 7 < chars_per_sec < 21 else "red"}[({chars_per_sec:.0f} znaków na sekundę)]",
                )

    st.write("## Napisy w filmie")

    for i, extracted_subtitles in enumerate(extracted_subtitles):
        if i > 0:
            st.divider()

        if extracted_subtitles:
            st.write("\n".join(f"- {subtitle}" for subtitle in extracted_subtitles))
        else:
            st.write("Nie znaleziono napisów w filmie.")

    st.write("### Ocena jakości napisów w filmie")

    for i, subtitle_rating in enumerate(subtitle_ratings):
        if i > 0:
            st.divider()

        st.write(subtitle_rating)

    st.write("## Analiza")
    st.write("### 10 Pytań do filmu")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        if analysis_result.wyrazenia_kluczowe:
            st.write(
                "\n".join(
                    f"{i}. {question}"
                    for i, question in enumerate(analysis_result.pytania, 1)
                )
            )
        else:
            st.write("Brak pytań do wypowiedzi.")

    st.write("### Emocje osoby mówiącej")
    for i, emotions in enumerate(emotions):
        if i > 0:
            st.divider()

        st.line_chart(emotions)

    st.write("### Grupa docelowa filmu")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        st.write(analysis_result.grupa_docelowa)

    st.write("### Kluczowe wyrażenia")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        if analysis_result.wyrazenia_kluczowe:
            st.write(
                "\n".join(f"- {word}" for word in analysis_result.wyrazenia_kluczowe)
            )
        else:
            st.write("Nie znaleziono kluczowych wyrażeń.")

    st.write("### Aspekty językowe")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        if analysis_result.aspekty_jezykowe.tagi:
            tags = ", ".join(
                f"{tag.tag} („{tag.przyklad}”)"
                for tag in analysis_result.aspekty_jezykowe.tagi
            )
        else:
            tags = "brak."

        st.write(f"Problemy: {tags}")
        st.write(analysis_result.aspekty_jezykowe.ocena)

    st.write("### Problemy wizualne")

    for visual_tags in visual_tags:
        tag_list = [
            tag
            for tag, value in (
                ("Osoby w drugim planie", visual_tags.osoby_w_drugim_planie),
                ("Odwracanie się", visual_tags.odwracanie_sie),
                ("Gestykulacja", visual_tags.gestykulacja),
                ("Mimika", visual_tags.mimika),
            )
            if value
        ]

        if tag_list:
            tagger_component(
                "",
                tag_list,
                color_name=["blue", "green", "violet", "red"][: len(tag_list)],
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

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        if analysis_result.sentyment_wypowiedzi:
            st.line_chart(
                [
                    sentiment.sentyment
                    for sentiment in analysis_result.sentyment_wypowiedzi
                ]
            )

            annotated_text.annotated_text(
                [
                    (f"„{sentiment.fragment}”", f"sentyment: {sentiment.sentyment}")
                    for sentiment in analysis_result.sentyment_wypowiedzi
                ]
            )
        else:
            st.write("Nie znaleziono zmian sentymentu w wypowiedzi.")

    st.write("### Podsumowanie wypowiedzi")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        st.write(analysis_result.podsumowanie)

    st.write("### Niezrozumiałe wyrazy")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        if analysis_result.niezrozumiale_wyrazy:
            st.write(
                "\n".join(
                    f"- „{word.wyraz}” — {word.opis}"
                    for word in analysis_result.niezrozumiale_wyrazy
                )
            )
        else:
            st.write("Nie znaleziono niezrozumiałych wyrazów.")

    st.write("### Sugestie doboru słów")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        if analysis_result.sugestie_doboru_slow:
            st.write(
                "\n".join(
                    f"- {suggestion}"
                    for suggestion in analysis_result.sugestie_doboru_slow
                )
            )
        else:
            st.write("Brak sugestii doboru słów.")

    st.write("### Poprawiona wypowiedź")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        st.write(f"_{analysis_result.poprawiona_wypowiedz}_")

    st.write("### Angielskie tłumaczenie")

    for i, analysis_result in enumerate(analysis_results):
        if i > 0:
            st.divider()

        st.write(f"_{analysis_result.angielskie_tlumaczenie}_")
