import contextlib
import json
import os
from importlib import resources as impresources
from kara_kanji_sync import resources
from typing import List

import wanakana
from jisho_api.kanji import Kanji
from jisho_api.word import Word

from kara_kanji_sync.utils import char_is_kana, kanji_combine

jmdict_file = (impresources.files(resources) / 'JmdictFurigana.json')
data = json.load(jmdict_file.open('r', encoding='utf-8-sig'))
already_searched_pronunciations = {}

@contextlib.contextmanager
def suppress_print():
    with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        yield

class KanjiReading:
    kanji: str
    hiragana_reading: str
    romaji_reading: str

    def __init__(self, kanji: str, hiragana_reading: str, romaji_reading: str):
        self.kanji = kanji
        self.hiragana_reading = hiragana_reading
        self.romaji_reading = romaji_reading.lower() if romaji_reading else None

    def __repr__(self):
        return f"{self.kanji} : {self.romaji_reading} ({self.hiragana_reading})"


def group_romaji_reading(reading_list: List[KanjiReading]) -> str:
    return "".join([reading.hiragana_reading for reading in reading_list])


def jisho_pronunciations(kanji: str) -> List[KanjiReading]:
    # Get main kanji readings
    with suppress_print():
        kanji_request = Kanji.request(kanji)
    if not kanji_request:
        return []

    readings = []
    for values in kanji_request.data.main_readings.dict().values():
        if values is not None:
            readings += [wanakana.to_hiragana(read.split(".")[0]).replace("-", "") for read in values]

    # Get additional readings from words
    with suppress_print():
        kanji_words = next((word_config.japanese for word_config in Word.request(kanji).data
                            if word_config.slug == kanji)
                           , [])
    for japanese_word in kanji_words:
        if japanese_word.word and all(
                [char_is_kana(character) for character in japanese_word.word.replace(kanji, "")]):
            # Trim hiragana before and after kanji
            a = japanese_word.word.split(kanji)
            readings.append(wanakana.to_hiragana(japanese_word.reading.lstrip(a[0]).rstrip(a[1])))

    readings = [KanjiReading(kanji, reading, wanakana.to_romaji(reading)) for reading in list(set(readings))]
    additional_readings = []
    for reading in readings:
        if reading.hiragana_reading.endswith("く") and len(reading.hiragana_reading) > 2:
            additional_readings.append(KanjiReading(kanji,
                                                    reading.hiragana_reading.rstrip("く") + "っ",
                                                    reading.romaji_reading.rstrip("u")))
    return readings + additional_readings


def search_jmdict(kanji_text: str, reading: str):
    furigana = next((asso['furigana'] for asso in data
                     if asso['text'] == kanji_text and asso['reading'] == reading), None)
    return furigana


def search_pronunciations_jmdict(kanji_text: str) -> List[List[KanjiReading]]:
    entries = [entry for entry in data if entry["text"] == kanji_text]
    if not entries:
        with suppress_print():
            jisho_result = Word.request(kanji_text)
        if (jisho_result and
                (correspondence := next((j for w in jisho_result.data for j in w.japanese
                                         if j.word and j.word.startswith(kanji_text) and j.reading),
                                        None)) and
                (extended_furi := search_jmdict(correspondence.word, correspondence.reading))):
            nb_kanji = 0
            furi_index = 0
            new_furi = []
            while nb_kanji < len(kanji_text):
                new_furi.append(extended_furi[furi_index])
                furi_index += 1
                nb_kanji += len(extended_furi[furi_index]["ruby"])
            entries.append({"furigana": new_furi})

    return [[KanjiReading(furi['ruby'],
                          furi['rt'] if "rt" in furi else furi['ruby'],
                          wanakana.to_romaji(furi['rt']) if "rt" in furi else None) for furi in entry["furigana"]]
            for entry in entries]


def kanji_readings(kanji: str) -> List[List[KanjiReading]]:
    if kanji in already_searched_pronunciations:
        return already_searched_pronunciations[kanji]

    readings = ([[reading] for reading in jisho_pronunciations(kanji)]
                if len(kanji) == 1 else search_pronunciations_jmdict(kanji))
    if readings:
        already_searched_pronunciations[kanji] = readings

    return readings


def brut_force_multiple_solver(kanjis_groups: List[str], text_to_match: str) -> List[KanjiReading]:
    text_to_match = wanakana.to_hiragana(text_to_match)
    pronunciations = [kanji_readings(kanji) for kanji in kanjis_groups]
    if any(pronunciation == [] for pronunciation in pronunciations):
        return []
    valid_paths = [[]]
    for num_kanji in range(len(pronunciations)):
        new_valid_paths = []
        for valid_path in valid_paths:
            if valid_path:
                path_text = "".join(
                    [group_romaji_reading(pronunciations[p_index][p_value]) for p_index, p_value in
                     enumerate(valid_path)])
            else:
                path_text = ""
            for new_index, pronunciation in enumerate(pronunciations[num_kanji]):
                new_text = path_text + group_romaji_reading(pronunciation)
                if text_to_match.startswith(new_text):
                    new_valid_path = valid_path.copy()
                    new_valid_path.append(new_index)
                    new_valid_paths.append(new_valid_path)
        if not new_valid_paths:
            return []
        valid_paths = new_valid_paths

    for valid_path in valid_paths:
        if "".join([group_romaji_reading(pronunciations[p_index][p_value])
                    for p_index, p_value in enumerate(valid_path)]) == text_to_match:
            return [pronunciation
                    for kanji_index, pronunciation_index in enumerate(valid_path)
                    for pronunciation in pronunciations[kanji_index][pronunciation_index]]

    return []


def get_furigana(kanji: str, romaji: str) -> List[KanjiReading]:
    for combination in kanji_combine(kanji):
        if reading := brut_force_multiple_solver(combination, romaji):
            return reading
    return []
