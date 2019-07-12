# Copyright 2019 Matthew Hayes

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from .exceptions import JapaneseReadingFormattingError, TextProcessingUnexpectedError
from .html import del_tag, ins_tag
from .split import formatting_aware_split
from .validation import (valiate_no_spaces_chunk, validate_all_spaces_chunk, validate_chunk_is_html_tag,
                         validate_japanese_reading_formatting)


def clean_redundant_furigana(src, output_html_diff=False):
    """
    Cleans redundant furigana from the beginning and end of text.  Any kana at the beginning
    or end of square brackets that match the kana at the beginning or end of the corresponding
    expression that precedes it wll be removed.  The text is adjusted so the square brackets
    correspond to the correct expression after trimming.
    """
    validate_japanese_reading_formatting(src)

    cleaned = []
    for tt, chunk in formatting_aware_split(src):
        if not chunk:
            continue

        if tt == "text":
            # A chunk with no spaces or html tags.

            valiate_no_spaces_chunk(chunk)

            new_chunk = _trim_redundant_furigana_from_chunk(chunk)
            if output_html_diff and chunk != new_chunk:
                cleaned.append(del_tag(chunk))
                cleaned.append(ins_tag(new_chunk))
            else:
                cleaned.append(new_chunk)
        elif tt == "html":
            # a chunk that is an html tag. append this as is.
            validate_chunk_is_html_tag(chunk)
            cleaned.append(chunk)
        elif tt == "spaces":
            # A chunk with only spaces.
            validate_all_spaces_chunk(chunk)
            cleaned.append(chunk)
        else:
            raise TextProcessingUnexpectedError("Unexpected type {}".format(tt))

    return "".join(cleaned)


def _trim_redundant_furigana_middle(src):
    m = re.match(r"""^
        ([^\[\]]+)
        \[
            ([^\[\]]+)
        \]
    $""", src, re.VERBOSE)
    if m:
        expression, furigana = m.group(1), m.group(2)
        expression_chars = set(expression)
        furigana_chars = set(furigana)
        common_chars = expression_chars.intersection(furigana_chars)
        if common_chars:
            pattern = "([" + "".join(common_chars) + "]+)"
            expression_split = re.split(pattern, expression)
            furigana_split = re.split(pattern, furigana)
            if len(expression_split) == len(furigana_split):
                result = ""
                success = True
                for i, chunks in enumerate(zip(expression_split, furigana_split)):
                    exp_chunk, furi_chunk = chunks
                    if i % 2 == 0:
                        # no common chars, so build the reading
                        if result:
                            result += " "
                        result += exp_chunk
                        result += "["
                        result += furi_chunk
                        result += "]"
                    else:
                        if exp_chunk == furi_chunk:
                            # same string, so no reading necessary
                            result += exp_chunk
                        else:
                            success = False
                            break
                if success:
                    return result
                else:
                    return src
            else:
                return src
        else:
            # No common characters between expression and furigana, no nothing to do.
            return src
    else:
        return src


def _trim_redundant_furigana_from_chunk(src):
    """Trims redundant furigana from an entire chunk"""
    m = re.match(r"""^
        ([^\[\]]+)
        \[
            ([^\[\]]+)
        \]
        ([^\[\]]*)
    $""", src, re.VERBOSE)
    if m:
        expression, furigana, extra = m.group(1), m.group(2), m.group(3)
        trim_start_len = 0
        trim_end_len = 0
        while expression[:(trim_start_len + 1)] == furigana[:(trim_start_len + 1)]:
            trim_start_len += 1
        while expression[-(trim_end_len + 1):] == furigana[-(trim_end_len + 1):]:
            trim_end_len += 1
        if trim_start_len or trim_end_len:
            beginning = ""
            if trim_start_len:
                beginning += expression[:trim_start_len]
                beginning += " "
            middle = ""
            if trim_end_len:
                middle += expression[trim_start_len:-trim_end_len]
            else:
                middle += expression[trim_start_len:]
            middle += "["
            if trim_end_len:
                reading = furigana[trim_start_len:-trim_end_len]
            else:
                reading = furigana[trim_start_len:]
            if not reading:
                raise JapaneseReadingFormattingError("Bad formatting found within: {}".format(src))
            middle += reading
            middle += "]"
            end = ""
            if trim_end_len:
                end += expression[-trim_end_len:]
            end += extra
            return beginning + _trim_redundant_furigana_middle(middle) + end
        else:
            return _trim_redundant_furigana_middle(src)
    else:
        return src
