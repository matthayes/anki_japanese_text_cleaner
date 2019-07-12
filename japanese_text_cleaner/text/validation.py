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

from .exceptions import JapaneseReadingFormattingError, TextProcessingUnexpectedError


def validate_japanese_reading_formatting(line):
    """
    Raises an exception if it detects:

    * Unbalanced brackets
    * Spaces within brackets
    """

    level = 0
    for c in line:
        if c == "[":
            level += 1
        elif c == "]":
            level -= 1

        if level < 0 or level > 1:
            raise JapaneseReadingFormattingError("Detected mismatched brackets: {}".format(line))

    if level != 0:
        raise JapaneseReadingFormattingError("Detected mismatched brackets: {}".format(line))


def validate_all_spaces_chunk(chunk):
    """Validates the chunk of text is all spaces"""
    # Sanity check. Make sure there are not spaces.
    if not all(" " == c for c in chunk):
        raise TextProcessingUnexpectedError(
            "Found non-spaces in a chunk where only spaces were expected: {}".format(chunk))


def valiate_no_spaces_chunk(chunk):
    """Validates the chunk of text has no spaces except within brackets"""
    level = 0
    for c in chunk:
        if c == "[":
            level += 1
        elif c == "]":
            level -= 1

        if level == 0 and c == " ":
            # Sanity check. This should never happen due to the regex.
            raise TextProcessingUnexpectedError(
                "Found a spaces in a chunk where no spaces were expected: {}".format(chunk))


def validate_chunk_is_html_tag(chunk):
    # Sanity checks. These should never be thrown due to the regex.
    if chunk[0] != "<":
        raise TextProcessingUnexpectedError("Expected HTML tag to start with < for: {}".format(chunk))
    if chunk[-1] != ">":
        raise TextProcessingUnexpectedError("Expected HTML tag to end with > for: {}".format(chunk))
