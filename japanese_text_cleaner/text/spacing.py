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

from .exceptions import TextProcessingUnexpectedError
from .html import del_tag
from .split import formatting_aware_split
from .validation import (valiate_no_spaces_chunk, validate_all_spaces_chunk, validate_chunk_is_html_tag,
                         validate_japanese_reading_formatting)


def clean_spaces(src, output_html_diff=False):
    """
    Cleans extraneous spaces from Japanese text, with special handling for the furigana syntax
    that the Japanese Support plugin (https://ankiweb.net/shared/info/3918629684) uses.

    This operates line by line.  For each line it:

    * Removes spaces at the beginning of the line
    * Removes spaces at the end of the line
    * Removes spaces within the line that do not correspond to furigana
    """
    return "\n".join(_clean_spaces_from_line(s, output_html_diff) for s in src.split("\n"))


def _clean_spaces_from_line(src, output_html_diff):
    cleaned = []

    validate_japanese_reading_formatting(src)

    split = formatting_aware_split(src)

    text_content_len = 0

    # Split the line into chunks alternating between all spaces and no spaces.  Chunks at even indices
    # will have no spaces.  Chunks at odd indices will have only spaces.
    for i, parts in enumerate(split):
        tt, chunk = parts
        if not chunk:
            continue

        if tt == "text":
            # A chunk with no spaces or html tags.
            valiate_no_spaces_chunk(chunk)

            text_content_len += len(chunk)

            cleaned.append(chunk)
        elif tt == "html":
            # a chunk that is an html tag. append this as is.  this may have spaces
            # but we obviously want these preserved.
            validate_chunk_is_html_tag(chunk)
            cleaned.append(chunk)
        elif tt == "spaces":
            # A chunk with only spaces.  We need to determine whether we can remove some.
            # To determine this we need to look ahead for furigana.

            validate_all_spaces_chunk(chunk)

            if not text_content_len:
                # Leading spaces at the beginning of a line, so drop. Even if we have furigana,
                # leading spaces are not necessary. For furigana, spaces are only necessary
                # within the line.
                if output_html_diff:
                    cleaned.append(del_tag(chunk))
            else:
                # Check for furigana. If there is then we need to keep one space.
                next_chunk = None

                # Look ahead for a chunk of characters that have square brackets
                # indicating furigana.  When we encounter spaces we stop because
                # any furigana corresponding to this set of spaces would have been
                # found before the next set of spaces.
                j = i + 1
                while j < len(split):
                    if split[j][0] == "text":
                        if split[j][1] and re.search(r"\[[^\[\]]+\]", split[j][1]):
                            # we found some furigana
                            next_chunk = split[j][1]
                            break
                        # else either no text or no furigana, so we keep looking either way
                    elif split[j][0] == "html":
                        # ignore html tags
                        pass
                    elif split[j][0] == "spaces":
                        if split[j][1]:
                            # chunk with spaces only. no furigana following previous spaces then.
                            break
                    j += 1

                if next_chunk:
                    if len(chunk) >= 2:
                        # Drop all but the last space.
                        if output_html_diff:
                            cleaned.append(del_tag(chunk[:-1]))
                        cleaned.append(chunk[-1])
                    else:
                        # We need this space, so append as is.
                        cleaned.append(chunk)
                else:
                    # There is no furigana after these spaces, so spaces aren't needed.
                    if output_html_diff:
                        cleaned.append(del_tag(chunk))
        else:
            raise TextProcessingUnexpectedError("Unexpected type {}".format(tt))

    return "".join(cleaned)
