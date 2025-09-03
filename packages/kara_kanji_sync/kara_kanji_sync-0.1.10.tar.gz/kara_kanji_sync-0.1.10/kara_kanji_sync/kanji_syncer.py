import re
from difflib import SequenceMatcher
from importlib import resources as impresources
from typing import Optional, List, Tuple

import cutlet
import wanakana
from pysubs2 import SSAFile, SSAEvent

from kara_kanji_sync import resources
from kara_kanji_sync.pronunciation import get_furigana
from kara_kanji_sync.utils import char_is_kana, char_is_little_kana, char_is_letter

template_file = (impresources.files(resources) / 'template.ass')

katsu = cutlet.Cutlet()
katsu.use_foreign_spelling = False

# Regexes used by syncer
k_regex = r'\{\\kf?\d{1,3}}'
romaji_regex = (r"^([aeiou]|[kmgnrbp][aeiou]|sa|sh[auio]|ch[auio]|su|se|so|ta|chi|tsu|te|to|ha|hi|fu|he|ho|wa|n|za|"
                r"ji|zu|ze|zo|ja|ju|jo|da|de|do|vu|y[auo]|[knhmrbpg]y[auo]|wo|tu)")

romaji_re = re.compile(romaji_regex)
pattern = re.compile(r"\{\\kf?\d{,3}}")
syl_pattern = re.compile(r"\{\\(?P<style>kf?)(?P<duration>\d{1,3})}(?P<syl>[\w’'&]+\s?)")
tilde_pattern = re.compile(r'((\{\\kf?\d{1,3}}\w+)~?(?:\{\\kf?\d{1,3}}\s?~\s?)+)')


class SubEvent:
    text: str

    def to_timing(self):
        pass

    def __repr__(self):
        return self.to_timing()


class SimpleSubEvent(SubEvent):
    def __init__(self, tag: str, duration: int, text: str):
        self.text = text
        self.tag = tag
        self.duration = duration

    def to_timing(self):
        return "{\\" + self.tag + str(self.duration) + "}" + self.text


class KanjiSubEvent(SubEvent):
    def __init__(self, text: str, sub_events: List[SimpleSubEvent]):
        self.text = text
        self.sub_events = sub_events

    def to_timing(self):
        separator = "!" if len("".join([sub_event.text for sub_event in self.sub_events])) < 3 else "<"
        return ("{\\" + self.sub_events[0].tag + str(self.sub_events[0].duration) + "}" + self.text + "|"
                + separator + self.sub_events[0].text +
                "".join(["{\\" + sub_event.tag + str(sub_event.duration) + "}" + "#" + "|" + sub_event.text
                         for sub_event in self.sub_events[1:]]))


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def make_timed_syl(k_style: str, duration: int, syl: str, furigana: Optional[List[Tuple[str, int, str]]] = None) -> str:
    if furigana is None:
        return "{\\" + k_style + str(duration) + "}" + syl
    else:
        separator = "!" if len("".join([furi[2] for furi in furigana])) < 3 else "<"
        return ("{\\" + furigana[0][0] + str(furigana[0][1]) + "}" + syl + "|" + separator + furigana[0][2]
                + "".join(["{\\" + style + str(timing) + "}" + "#" + "|" + furi
                           for (style, timing, furi) in furigana[1:]]))


def subs_to_text(raw_sub_text: str) -> str:
    return re.sub(r'\{\\kf?\d{1,3}}', '', raw_sub_text)


class KanjiSyncer:

    def __init__(self):
        self.errors = {}
        self.subtitles_file: SSAFile | None = None
        self.subtitle_lines: List[SSAEvent] | None = None
        self.lyrics: List[str] | None = None
        self.current_line_index = 0
        self.all_matches = []
        self.all_groups = []
        self.kanji_sub_file: SSAFile | None = None
        self.resolution = 1080
        self.unknown_syllables = []

    def make_subtitles_lines(self) -> List[SSAEvent]:
        # Special treatment if a file is from kara.moe
        if self.subtitles_file.events[0].effect == "template pre-line all keeptags":
            raw_lines = [event for event in self.subtitles_file.events[1:] if event.is_comment]
            subtitle_lines = []
            for event in raw_lines:
                offset = min(1000, event.start)
                event.start -= offset
                event.text = r"{\k" + str(offset // 10) + "}" + event.text
                subtitle_lines.append(event)
            self.subtitle_lines = subtitle_lines
        else:
            self.subtitle_lines = self.subtitles_file.events
        return self.subtitle_lines

    def get_template(self) -> SSAFile:
        kanji_sub_file = SSAFile.load(template_file)
        base_resolution = 1080
        ratio = base_resolution / self.resolution
        if self.resolution != base_resolution:
            base_font_size = 80
            base_top_marginv = 80
            base_top_marginv_right = 220
            base_bottom_marginv = 180
            base_bottom_marginv_right = 40
            base_furi_shift = 15
            base_outline = 5
            base_shadow = 3

            font_size = int(base_font_size / ratio)
            top_marginv = int(base_top_marginv / ratio)
            top_marginv_right = int(base_top_marginv_right / ratio)
            bottom_marginv = int(base_bottom_marginv / ratio)
            bottom_marginv_right = int(base_bottom_marginv_right / ratio)
            furi_shift = int(base_furi_shift / ratio)
            outline = int(base_outline / ratio)
            shadow = int(base_shadow / ratio)

            kanji_sub_file.styles['Kanji Bottom'].fontsize = font_size
            kanji_sub_file.styles['Kanji Bottom'].marginv = bottom_marginv
            kanji_sub_file.styles['Kanji Bottom'].outline = outline
            kanji_sub_file.styles['Kanji Bottom'].shadow = shadow
            kanji_sub_file.styles['Kanji Bottom - Right'].fontsize = font_size
            kanji_sub_file.styles['Kanji Bottom - Right'].marginv = bottom_marginv_right
            kanji_sub_file.styles['Kanji Bottom - Right'].outline = outline
            kanji_sub_file.styles['Kanji Bottom - Right'].shadow = shadow
            kanji_sub_file.styles['Kanji Top'].fontsize = font_size
            kanji_sub_file.styles['Kanji Top'].marginv = top_marginv
            kanji_sub_file.styles['Kanji Top'].outline = outline
            kanji_sub_file.styles['Kanji Top'].shadow = shadow
            kanji_sub_file.styles['Kanji Top - Right'].fontsize = font_size
            kanji_sub_file.styles['Kanji Top - Right'].marginv = top_marginv_right
            kanji_sub_file.styles['Kanji Top - Right'].outline = outline
            kanji_sub_file.styles['Kanji Top - Right'].shadow = shadow

            template_furi = (r"{\pos(!line.left+syl.center!,!line.middle-line.height+"
                             + str(furi_shift) +
                             r"!)\an5\k!syl.start_time/10!\k$kdur}")
            furi_events = [event for event in kanji_sub_file.events if event.effect == "template furi"]
            for event in furi_events:
                event.text = template_furi

        return kanji_sub_file

    def make_matches_and_groups(self):
        all_matches = []
        all_groups = []
        for line_index, lyrics_line in enumerate(self.lyrics):
            line = (lyrics_line
                    .replace(u'\u3000', " ")
                    .replace("？", " ")
                    .replace("?", " ")
                    .replace("!", "")
                    .replace("、", " ")
                    .replace(",", " ")
                    .replace("…", "")
                    .replace('。', " ")
                    .replace('“', " ")
                    .replace('”', " ")
                    .replace('･', " ")
                    .replace('’', "'")
                    .replace('「', " ")
                    .replace('」', " ")
                    .replace('なぁ', "なあ")
                    .replace('ねぇ', "ねえ")
                    .strip())

            raw_line = self.subtitle_lines[line_index].text

            initial_shift = pattern.match(raw_line).group(0)
            raw_line = (raw_line[len(initial_shift):].lower()
                        .replace('“', "")
                        .replace('”', "")
                        .replace('"', "")
                        .replace('"', "")
                        .replace(',', ""))

            ## Rewriting the timed lines
            rewrote_line = ""

            # Fuse the ~
            kt_regex = r'\{\\kf?(\d{1,3})}'
            time_pattern = re.compile(kt_regex)
            for matches in tilde_pattern.findall(raw_line):
                total_time = sum([int(time_match) for time_match in time_pattern.findall(matches[0])])
                replace = re.sub(r"\d+(?=})", str(total_time), matches[1])
                raw_line = raw_line.replace(matches[0], replace)

            # Separating syllables strictly
            for syl in syl_pattern.finditer(raw_line):
                if len(syl[3].strip()) == 1:
                    rewrote_line += syl.group(0)
                else:
                    syl_match = romaji_re.match(syl.group("syl"))
                    if syl_match and syl.group("syl").strip() == syl_match.group(0):
                        rewrote_line += syl.group(0)
                    elif syl_match:
                        rewrote_line += make_timed_syl(syl.group("style"),
                                                       0,
                                                       syl_match.group(0))
                        rewrote_line += make_timed_syl(syl.group("style"),
                                                       int(syl.group("duration")),
                                                       syl.group("syl").replace(syl_match.group(0), '', 1))
                    elif len(syl.group("syl").strip()) > 1 and syl.group("syl")[0] == syl.group("syl")[1]:
                        rewrote_line += make_timed_syl(syl.group("style"),
                                                       0,
                                                       syl.group("syl")[0])
                        rewrote_line += make_timed_syl(syl.group("style"),
                                                       int(syl.group("duration")),
                                                       syl.group("syl")[1:])
                    else:
                        rewrote_line += syl.group(0)
                        self.unknown_syllables.append(syl.group("syl").strip())

            # analyze kanji line

            ## Make regex from hiragana and katakana
            # establish the whole kanji/kana/others sequence
            reg_line = "^"
            groups = []
            ongoing_kanji_group = ""
            ongoing_word = ""

            for kana_index, kana in enumerate(line):
                if char_is_little_kana(kana):
                    groups[-1] += kana
                elif kana in [u'\u3063', u'\u30C3'] and not char_is_kana(line[kana_index + 1]):  # っ ッ
                    ongoing_kanji_group += kana
                elif char_is_kana(kana):
                    if ongoing_kanji_group:
                        groups.append(ongoing_kanji_group)
                        ongoing_kanji_group = ""
                    groups.append(kana)
                elif char_is_letter(kana):
                    ongoing_word += kana
                elif kana == ' ':
                    if ongoing_word:
                        groups.append(ongoing_word)
                        ongoing_word = ""
                else:
                    ongoing_kanji_group += kana

            if ongoing_kanji_group:
                groups.append(ongoing_kanji_group)
            if ongoing_word:
                groups.append(ongoing_word)

            all_groups.append(groups)

            # convert the sequence in regex
            has_little_tsu = False
            for j, group in enumerate(groups):
                if group in [u'\u3063', u'\u30C3']:  # っ ッ
                    has_little_tsu = True
                elif group == u"\u30FC":  # ー
                    reg_line += r"(" + k_regex + wanakana.to_romaji(groups[j - 1]).lower()[-1] + r"\s?)"
                elif group == u"\u306F":  # は
                    reg_line += r"(" + k_regex + r"[wh]a\s?)"
                elif group == u"\u3092":  # を
                    reg_line += r"(" + k_regex + r"w?o\s?)"
                elif group == u"\u3078":  # へ
                    reg_line += r"(" + k_regex + r"h?e\s?)"
                elif group == u"\u3065":  # づ
                    reg_line += r"(" + k_regex + r"d?zu\s?)"
                elif group == "とぅ":  # とぅ
                    reg_line += r"(" + k_regex + r"to?u\s?)"
                elif group == "フェ":  # とぅ
                    reg_line += r"(" + k_regex + r"fe\s?)"
                elif char_is_kana(group[0]):
                    romaji = wanakana.to_romaji(group).lower()
                    if has_little_tsu:
                        reg_line += r"(" + k_regex + romaji[0] + r"\s?)"
                        has_little_tsu = False
                    reg_line += r"(" + k_regex + romaji + r"\s?)"
                elif char_is_letter(group[0]):
                    reg_line += (r"("
                                 + k_regex + group[0]
                                 + "".join([r"(?:" + k_regex + ")?" + letter for letter in group[1:]])
                                 + r"\s?)")
                else:
                    reg_line += r"(" + k_regex + r".*\s?)"

            reg_line += r"$"

            line_pattern = re.compile(reg_line, flags=re.IGNORECASE)
            matches = line_pattern.findall(rewrote_line)

            if matches and len(matches[0][0]) == 1:
                matches = [[matches[0]]]

            # lazy_reg_line
            lazy_reg_line = reg_line.replace(".*", ".*?")
            lazy_line_pattern = re.compile(lazy_reg_line, flags=re.IGNORECASE)
            lazy_matches = lazy_line_pattern.findall(rewrote_line)

            # Compare lazy and greedy matches
            if matches:
                matches = [[m for m in matches[0]]]
                unmatch_indexes = []
                for match_index, match in enumerate(matches[0]):
                    if match != lazy_matches[0][match_index]:
                        unmatch_indexes.append(match_index)

                if unmatch_indexes:
                    # treat by group of 3
                    for indexes in range(0, len(unmatch_indexes), 3):
                        if (katsu.romaji(groups[unmatch_indexes[indexes]]).lower() == subs_to_text(
                                lazy_matches[0][unmatch_indexes[indexes]].strip()) and
                                katsu.romaji(groups[unmatch_indexes[indexes + 1]]).lower() == subs_to_text(
                                    lazy_matches[0][unmatch_indexes[indexes + 1]].strip())):
                            for j in range(3):
                                matches[0][unmatch_indexes[indexes + j]] = lazy_matches[0][unmatch_indexes[indexes + j]]
                all_matches.append(matches[0])
            else:
                all_matches.append([])

        self.all_matches = all_matches
        self.all_groups = all_groups

    def assemble(self, kanjis: str, timed_matches: List[Tuple[str, int, str]]) -> List[SubEvent]:
        if len(kanjis) == 1:
            return [KanjiSubEvent(kanjis,
                                  [SimpleSubEvent(s_match[0],
                                                  s_match[1],
                                                  wanakana.to_hiragana(s_match[2].strip())
                                                  if wanakana.to_hiragana(s_match[2].strip()) != s_match[2].strip()
                                                  else u'\u3063')
                                   for s_match in timed_matches])]
        else:
            syl_text = "".join([tm[2] for tm in timed_matches]).strip().replace(' ', '')
            furis = get_furigana(kanjis.replace(" ", ""), syl_text)

            if not furis:
                self.errors.setdefault(self.current_line_index, [])
                self.errors[self.current_line_index].append(f"Could not find furigana combination for {kanjis} "
                                                            f"with syllables '{syl_text}'")
                return [KanjiSubEvent(kanjis,
                                      [SimpleSubEvent(s_match[0],
                                                      s_match[1],
                                                      wanakana.to_hiragana(s_match[2].strip())
                                                      if wanakana.to_hiragana(s_match[2].strip()) != s_match[2].strip()
                                                      else u'\u3063')
                                       for s_match in timed_matches])]

            timed_matches_index = 0
            sub_events = []
            for furi in furis:
                if furi.hiragana_reading:
                    remaining_syl = furi.hiragana_reading
                    associated_timed_matches = []
                    while remaining_syl != "":
                        current_match = timed_matches[timed_matches_index]
                        associated_timed_matches.append(current_match)
                        remaining_syl = remaining_syl[len(wanakana.to_hiragana(current_match[2])):]
                        timed_matches_index += 1
                    sub_events.append(KanjiSubEvent(furi.kanji,
                                                    [SimpleSubEvent(s_match[0],
                                                                    s_match[1],
                                                                    wanakana.to_hiragana(s_match[2].strip())
                                                                    if wanakana.to_hiragana(s_match[2].strip()) !=
                                                                       s_match[
                                                                           2].strip()
                                                                    else u'\u3063')
                                                     for s_match in associated_timed_matches]))
                else:  # we got a kana and not a kanji
                    current_match = timed_matches[timed_matches_index]
                    sub_events.append(SimpleSubEvent(current_match[0], current_match[1], furi.kanji))
                    timed_matches_index += 1

            return sub_events

    def sync_line_match(self, match, groups, timed_line: SSAEvent, lyrics_line: str, style) -> SSAEvent:
        new_line = pattern.match(timed_line.text).group(0)
        # Rewrite the new line from here
        if match:
            if len(match) == len(groups):
                sub_events = []
                for group_index, group in enumerate(groups):
                    if char_is_letter(group[0]):
                        sub_events += [SimpleSubEvent(syl[0], int(syl[1]), syl[2])
                                       for syl in syl_pattern.findall(match[group_index])]
                    elif char_is_kana(group[0]):
                        timed_syl = syl_pattern.match(match[group_index])
                        sub_events.append(SimpleSubEvent(timed_syl.group('style'), timed_syl.group('duration'), group))
                    else:
                        sub_events += self.assemble(group, syl_pattern.findall(match[group_index]))

                # Add missing spaces and punctuation
                lyrics_index = 0
                sub_event_index = 0
                while lyrics_index < len(lyrics_line):
                    if (sub_event_index < len(sub_events)
                            and sub_events[sub_event_index].text.startswith(lyrics_line[lyrics_index].lower())):
                        new_line += sub_events[sub_event_index].to_timing()
                        lyrics_index += len(sub_events[sub_event_index].text)
                        sub_event_index += 1
                    else:
                        new_line += r"{\k0}" + lyrics_line[lyrics_index]
                        lyrics_index += 1

            return SSAEvent(start=timed_line.start, end=timed_line.end, type="Comment", effect="karaoke",
                            text=new_line,
                            style=style)

        self.errors.setdefault(self.current_line_index, [])
        self.errors[self.current_line_index].append("Could not sync line")

        return SSAEvent(start=timed_line.start, end=timed_line.end, type="Comment",
                        text="Error on this line",
                        style=style)

    def sync_subs(self, kanji_style: str = "Kanji Top") -> SSAFile:
        self.kanji_sub_file = self.get_template()
        style = kanji_style
        for matches_index, matches in enumerate(self.all_matches):
            self.current_line_index = matches_index + 1
            self.kanji_sub_file.extend([self.sync_line_match(matches, self.all_groups[matches_index],
                                                             self.subtitle_lines[matches_index],
                                                             self.lyrics[matches_index],
                                                             style)])
            style = f"{kanji_style} - Right" if style == kanji_style else kanji_style

        return self.kanji_sub_file
