from typing import List


def char_is_letter(c: str) -> bool:
    return "a" <= c <= "z" or "A" <= c <= "Z" or c in ["'", "&"]


def char_is_kana(c) -> bool:
    return u'\u3040' <= c <= u'\u309F' or u'\u30A0' <= c <= u'\u30FF'


def char_is_little_kana(c) -> bool:
    return c in [u'\u3083', u'\u3085', u'\u3087', u'\u30A1', u'\u30A3', u'\u30A5', u'\u30A7', u'\u30A9', u'\u30E3',
                 u'\u30E5', u'\u30E7', u'\u3041', u'\u3043', u'\u3045', u'\u3047', u'\u3049']


def kanji_combine(kanji: str) -> List[List[str]]:
    results = [[kanji]]
    if len(kanji) > 1:
        for i in range(1, len(kanji)):
            results += [[kanji[:i]] + inf_results for inf_results in kanji_combine(kanji[i:])]
    return results
