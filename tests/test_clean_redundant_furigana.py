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

import pytest

from japanese_text_cleaner.text.exceptions import JapaneseReadingFormattingError
from japanese_text_cleaner.text.furigana import clean_redundant_furigana


class TestCleanSpaces:

    def test_no_furigana(self):
        assert clean_redundant_furigana("abcdef") == "abcdef"

    def test_furigana(self):
        assert clean_redundant_furigana("def[ghi]") == "def[ghi]"
        assert clean_redundant_furigana("abc def[ghi]") == "abc def[ghi]"
        assert clean_redundant_furigana("abc  def[ghi]") == "abc  def[ghi]"

    def test_redundant_furigana(self):
        assert clean_redundant_furigana("defi[ghi]") == "def[gh]i"
        assert clean_redundant_furigana("defi[ghi]z") == "def[gh]iz"
        assert clean_redundant_furigana("gdef[ghi]") == "g def[hi]"
        assert clean_redundant_furigana("gdef[ghi]z") == "g def[hi]z"
        assert clean_redundant_furigana("abc defi[ghi]") == "abc def[gh]i"
        assert clean_redundant_furigana("abc defi[ghi]z") == "abc def[gh]iz"
        assert clean_redundant_furigana("abc  gdef[ghi]") == "abc  g def[hi]"
        assert clean_redundant_furigana("abc  gdef[ghi]z") == "abc  g def[hi]z"

    def test_spaces_in_furigana(self):
        assert clean_redundant_furigana("def[g hi]") == "def[g hi]"
        assert clean_redundant_furigana("abc def[g h i]") == "abc def[g h i]"
        assert clean_redundant_furigana("abc  def[g hi]") == "abc  def[g hi]"
        assert clean_redundant_furigana("gdef[gh i]") == "g def[h i]"

    def test_redundant_furigana_middle(self):
        assert clean_redundant_furigana("abbbc[dbbbe]") == "a[d]bbb c[e]"
        assert clean_redundant_furigana("abbbc[dbbbe] efgmmmmg[zzmmmmyyyy]") == "a[d]bbb c[e] efg[zz]mmmm g[yyyy]"
        assert clean_redundant_furigana("aaabbcddddefg[mmbbnnnddddopqr]") == "aaa[mm]bb c[nnn]dddd efg[opqr]"

        # mismatch in number of b chars
        assert clean_redundant_furigana("abbbc[dbbe]") == "abbbc[dbbe]"

    def test_bad_formatting(self):
        with pytest.raises(JapaneseReadingFormattingError):
            # We should not be left with nothing left in the reading.
            clean_redundant_furigana("abczzzz[abc]def")

    def test_html(self):
        assert clean_redundant_furigana("<b>abc defi[ghi]</b>") == "<b>abc def[gh]i</b>"
        assert clean_redundant_furigana("<b>abc</b> <b>defi[ghi]</b>") == "<b>abc</b> <b>def[gh]i</b>"
        assert clean_redundant_furigana("<span class=\"foo\">abc</span> <span class=\"bar\">defi[ghi]</span>") \
            == "<span class=\"foo\">abc</span> <span class=\"bar\">def[gh]i</span>"
