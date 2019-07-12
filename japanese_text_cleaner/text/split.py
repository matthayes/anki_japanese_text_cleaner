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


def formatting_aware_split(content):
    """
    Split the line into a sequence of chunks, while being aware of formatting such as HTML
    tags and Japanese readings.

    Result is a list of tuples, where for each tuple the first value is a type and the
    second value is a string.

    The type can be:
    - "text":   A chunk of text with no html tags and no spaces except
                for within square brackets (a Japanese reading)
    - "html":   A chunk that is an html tag.
    - "spaces": A chunk with only spaces.
    """

    split = re.split(
        # japanese reading (this will capture spaces within the square brackets by design).
        # This along with the non-capture case are considered text chunks that can be
        # merged together.
        r"(\[[^\[\]]+\])|"
        # html tag (this will capture spaces within the angle brackets by design)
        r"(<[a-zA-Z][a-zA-Z0-9]*\b[^>]*>|</[a-zA-Z][a-zA-Z0-9]*>)|"
        # spaces (this captures any other spaces not captured by previous cases)
        r"( +)", content)

    result = []
    for i, chunk in enumerate(split):
        if not chunk:
            continue
        if i % 4 in (0, 1):
            # No match, so a chunk with no spaces, no html tags, no reading,
            # or, Group 1 match, so a Japanese reading.

            # Merge all consecutive text chunks together.
            if result and result[-1][0] == "text":
                result[-1] = ("text", result[-1][1] + chunk)
            else:
                result.append(("text", chunk))
        elif i % 4 == 2:
            # Group 2: HTML tag
            result.append(("html", chunk))
        else:
            # Group 3: Spaces
            result.append(("spaces", chunk))

    return result
