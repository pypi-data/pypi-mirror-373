from typing import Literal, Union
import urllib.request
from deep_translator import GoogleTranslator

PERCENTAGE = "%.f%%"
PERCENTAGE_UNTIL_1 = "%.1f%%"
PERCENTAGE_UNTIL_2 = "%.2f%%"

vowels = ["ㅏ","ㅐ","ㅑ","ㅒ","ㅓ","ㅔ","ㅕ","ㅖ","ㅗ","ㅘ","ㅙ","ㅚ","ㅛ","ㅜ","ㅝ","ㅞ","ㅟ","ㅠ","ㅡ","ㅢ","ㅣ"]
consonants = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
finals = ["","ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
def is_korean(char: str) -> bool:
    cp = ord(char)
    return (
        0x1100 <= cp < 0x1200 or 
        0x3130 <= cp < 0x3190 or 
        0xA960 <= cp < 0xA980 or 
        0xD7B0 <= cp < 0xD800 or 
        0xAC00 <= cp <= 0xD7A3
    )
def group(group_name: Literal['Hangul Jamo', 'Hangul Compatibility Jamo', 'Hangul Jamo Extended-A', 'Hangul Jamo Extended-B', 'Hangul Syllables']) -> range:
    match group_name:
        case 'Hangul Jamo':
            return range(0x1100, 0x1200)
        case 'Hangul Compatibility Jamo':
            return range(0x3130, 0x3190)
        case 'Hangul Jamo Extended-A':
            return range(0xA960, 0xA980)
        case 'Hangul Jamo Extended-B':
            return range(0xD7B0, 0xD800)
        case 'Hangul Syllables':
            return range(0xAC00, 0xD7A3)
def _esc(s: str):
    return "".join(
        "\\u{:04X}".format(ord(c)) if ord(c) <= 0xFFFF else "\\U{:08X}".format(ord(c))
        for c in s
    )
def _no_finals():
    return [0xAC00 + (L * 21 * 28) + (V * 28) for L in range(19) for V in range(21)]
def _with_finals():
    return [0xAC00 + (L * 21 * 28) + (V * 28) + T for L in range(19) for V in range(21) for T in range(1, 28)]
def _find(obj, sized):
    try:
        return sized.index(obj)
    except ValueError:
        return None
def combine(s: Union[str, bytes], *, ensure_korean: bool = True, only_syl: bool = False) -> Union[str, bytes]:
    savetype = type(s)
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    generated_string = []
    nofinals = _no_finals()
    for char in s:
        if generated_string and generated_string[-1] in consonants and char in vowels:
            idx_c = _find(generated_string[-1], consonants) or 0
            idx_v = _find(char, vowels) or 0
            new_unicode = 0xAC00 + idx_c * 21 * 28 + idx_v * 28
            generated_string[-1] = chr(new_unicode)
            continue
        if generated_string and ord(generated_string[-1]) in nofinals and char in finals:
            old_unicode = ord(generated_string[-1])
            idx_t = _find(char, finals) or 0
            new_unicode = old_unicode + idx_t
            generated_string[-1] = chr(new_unicode)
            continue
        if ensure_korean and not is_korean(char):
            generated_string.append(_esc(char))
        else:
            generated_string.append(char)
    if only_syl and len(generated_string) > 1:
        raise ValueError("found multi-syllable string")
    result = "".join(generated_string)
    if savetype is bytes:
        result = result.encode("utf-8")
    return result
def extend(s: Union[str, bytes], *, ensure_korean: bool = True, only_syl: bool = False) -> Union[str, bytes]:
    savetype = type(s)
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    if only_syl and len(s) > 1:
        raise ValueError("found multi-syllable string")
    generated_string = []
    for char in s:
        if not is_korean(char):
            if ensure_korean:
                generated_string.append(_esc(char))
            else:
                generated_string.append(char)
            continue
        old_unicode = ord(char) - 0xAC00
        idx_c = old_unicode // (21 * 28)
        idx_v = (old_unicode % (21 * 28)) // 28
        idx_t = (old_unicode % (21 * 28)) % 28
        generated_string.append(consonants[idx_c])
        generated_string.append(vowels[idx_v])
        generated_string.append(finals[idx_t])
    result = "".join(generated_string)
    if savetype is bytes:
        result = result.encode("utf-8")
    return result

def get_sound(s: Union[str, bytes], *, only_korean: bool = True) -> Union[str, bytes]:
    generated_string = ""
    consonants_match = {"ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt", "ㄹ": "r", "ㅁ": "m", "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s", "ㅆ": "ss", "ㅇ": "",  "ㅈ": "j", "ㅉ": "jj", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h"}
    vowels_match = {"ㅏ": "a","ㅐ": "ae","ㅑ": "ya","ㅒ": "yae","ㅓ": "eo","ㅔ": "e","ㅕ": "yeo","ㅖ": "ye","ㅗ": "o","ㅘ": "wa","ㅙ": "wae","ㅚ": "oe","ㅛ": "yo","ㅜ": "u","ㅝ": "wo","ㅞ": "we","ㅟ": "wi","ㅠ": "yu","ㅡ": "eu","ㅢ": "ui","ㅣ": "i"}
    finals_match = {"": "", "ㄱ": "k","ㄲ": "k","ㄳ": "k","ㄴ": "n","ㄵ": "n","ㄶ": "n","ㄷ": "t","ㄹ": "l","ㄺ": "k","ㄻ": "m","ㄼ": "p","ㄽ": "l","ㄾ": "l","ㄿ": "p","ㅀ": "l","ㅁ": "m","ㅂ": "p","ㅄ": "p","ㅅ": "t","ㅆ": "t","ㅇ": "ng","ㅈ": "t","ㅊ": "t","ㅋ": "k","ㅌ": "t","ㅍ": "p","ㅎ": "t"}
    for char in s:
        if only_korean and not is_korean(char):
            raise ValueError(f"Non-Korean character detected: {char}")
        initial, vowel, final = extend(char)
        generated_string += consonants_match.get(initial, "")
        generated_string += vowels_match.get(vowel, "")
        generated_string += finals_match.get(final, "")
    return generated_string

def from_sound(s: Union[str, bytes]) -> Union[str, bytes]:
    if isinstance(s, bytes):
        s = s.decode("utf-8")
    consonants_match = {
        "g": "ㄱ", "kk": "ㄲ", "n": "ㄴ", "d": "ㄷ", "tt": "ㄸ",
        "r": "ㄹ", "m": "ㅁ", "b": "ㅂ", "pp": "ㅃ", "s": "ㅅ",
        "ss": "ㅆ", "": "ㅇ", "j": "ㅈ", "jj": "ㅉ", "ch": "ㅊ",
        "k": "ㅋ", "t": "ㅌ", "p": "ㅍ", "h": "ㅎ"
    }
    vowels_match = {
        "a": "ㅏ","ae": "ㅐ","ya": "ㅑ","yae": "ㅒ","eo": "ㅓ","e": "ㅔ",
        "yeo": "ㅕ","ye": "ㅖ","o": "ㅗ","wa": "ㅘ","wae": "ㅙ","oe": "ㅚ",
        "yo": "ㅛ","u": "ㅜ","wo": "ㅝ","we": "ㅞ","wi": "ㅟ","yu": "ㅠ",
        "eu": "ㅡ","ui": "ㅢ","i": "ㅣ"
    }
    result_jamo = []
    i = 0
    while i < len(s):
        matched = False
        for length in (3, 2, 1):
            chunk = s[i:i+length]
            if chunk in consonants_match:
                result_jamo.append(consonants_match[chunk])
                i += length
                matched = True
                break
            if chunk in vowels_match:
                result_jamo.append(vowels_match[chunk])
                i += length
                matched = True
                break
        if not matched:
            result_jamo.append(s[i])
            i += 1
    generated_string = combine("".join(result_jamo))
    return generated_string.encode() if isinstance(s, bytes) else generated_string

def words(*, source: str = None, filter: bool = True) -> list:
    url = "https://raw.githubusercontent.com/acidsound/korean_wordlist/master/wordslistUnique.txt"
    if source != None:
        url = source
    urllib.request.urlretrieve(url, "korean_words.txt")
    with open("korean_words.txt", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    if filter:
        words = [w for w in words if all('가' <= ch <= '힣' for ch in w) and len(w) >= 2]
    return words

def to_korean(text: str, *, start: str = None) -> str:
    if start == None:
        start = "auto"
    translator = GoogleTranslator(source=start, target="ko")
    return translator.translate(text)

def from_korean(text: str, *, destination: str) -> str:
    translator = GoogleTranslator(source="ko", target=destination)
    return translator.translate(text)

def to_int(korean_text: str, *, needs_place_values: bool = True) -> int:
    value_match = {"일": 1, "이": 2, "삼": 3, "사": 4, "오": 5,
                   "육": 6, "칠": 7, "팔": 8, "구": 9, "영": 0, "공": 0}
    place_match = {"십":1e+1,"백":1e+2,"천":1e+3,"만":1e+4,"억":1e+8,
                   "조":1e+12,"경":1e+16,"해":1e+20,"자":1e+24,"양":1e+28,
                   "구":1e+32,"간":1e+36,"정":1e+40,"재":1e+44,"극":1e+48,
                   "항하사":1e+52,"아승기":1e+56,"나유타":1e+60,"불가사의":1e+64,
                   "무량대수":1e+68}
    if not needs_place_values:
        digits = [str(value_match[ch]) for ch in korean_text if ch in value_match]
        return int("".join(digits)) if digits else 0
    total = 0
    section = 0
    num = 0
    for ch in korean_text:
        if ch in value_match:
            num = value_match[ch]
        elif ch in place_match:
            unit = place_match[ch]
            if unit >= 1e+4:
                section = (section + (num or 1)) * unit
                total += section
                section = 0
            else:
                section += (num or 1) * unit
            num = 0
        else:
            raise ValueError(f"Unknown character: {ch}")
    return int(total + section + num)

def from_int(num: int, *, include_place_values: bool = True) -> str:
    place_match_flipped = {1e+1:"십",1e+2:"백",1e+3:"천",1e+4:"만",1e+8:"억",1e+12:"조",1e+16:"경",1e+20:"해",1e+24:"자",1e+28:"양",1e+32:"구",1e+36:"간",1e+40:"정",1e+44:"재",1e+48:"극",1e+52:"항하사",1e+56:"아승기",1e+60:"나유타",1e+64:"불가사의",1e+68:"무량대수"}
    value_match_flipped = {1:"일",2:"이",3:"삼",4:"사",5:"오",6:"육",7:"칠",8:"팔",9:"구",0:"영"}
    merged = place_match_flipped | value_match_flipped
    merged = dict(sorted(merged.items(), reverse=True))
    result = ""
    for n, m in merged.items():
        while num >= n:
            result += m
            num -= n
    if not include_place_values:
        for m in place_match_flipped.values():
            result = result.replace(m, "")
    return result

def korean_ratio(text: str, *, style: str = None) -> Union[float, str]:
    pct_count_int = 0
    for char in text:
        pct_count_int += is_korean(char)
    pct_float = pct_count_int / len(text)
    if style == None:
        return pct_float
    else:
        return style % (pct_float * 100)

def fully_korean(text: str) -> bool:
    return korean_ratio(text, style="%.f%%") == "100%"