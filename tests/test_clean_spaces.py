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
from japanese_text_cleaner.text.spacing import clean_spaces


class TestCleanSpaces:

    def test_no_spaces(self):
        assert clean_spaces("abcdef") == "abcdef"

    def test_spaces(self):
        assert clean_spaces("abc def") == "abcdef"
        assert clean_spaces("abc  def") == "abcdef"
        assert clean_spaces("  a b c  d e f  ") == "abcdef"

    def test_furigana(self):
        assert clean_spaces("abc def[ghi]") == "abc def[ghi]"
        assert clean_spaces("abc  def[ghi]") == "abc def[ghi]"
        assert clean_spaces("abc   def[ghi]") == "abc def[ghi]"
        assert clean_spaces("  abc   def[ghi]  ") == "abc def[ghi]"
        assert clean_spaces("  a[bc] de[fghi]  jkl[mnop]  qr  ") == "a[bc] de[fghi] jkl[mnop]qr"

    def test_multiple_lines(self):
        assert clean_spaces("  abc   def[ghi]  \n  mn[aa]  op[qrs]  tuv[wy]  ") \
            == "abc def[ghi]\nmn[aa] op[qrs] tuv[wy]"

    def test_brackets(self):
        with pytest.raises(JapaneseReadingFormattingError):
            clean_spaces("abc[def")

        with pytest.raises(JapaneseReadingFormattingError):
            clean_spaces("abc]def")

        clean_spaces("abc[def]")
        clean_spaces("abc[def]ghi[jk]")

        with pytest.raises(JapaneseReadingFormattingError):
            clean_spaces("abc[def]]")

        with pytest.raises(JapaneseReadingFormattingError):
            clean_spaces("abc[[def]")

    def test_html(self):
        assert clean_spaces("<b>foo</b>") == "<b>foo</b>"
        assert clean_spaces("<b> foo</b>") == "<b>foo</b>"
        assert clean_spaces("<b> foo </b>") == "<b>foo</b>"
        assert clean_spaces("""<a src="foo">bar</b>""") == """<a src="foo">bar</b>"""
        assert clean_spaces("""<a src="foo">bar baz</a>""") == """<a src="foo">barbaz</a>"""
        assert clean_spaces("""  <a src="foo">bar baz</a>   """) == """<a src="foo">barbaz</a>"""
        assert clean_spaces("""<a src="foo">  bar baz</a>   """) == """<a src="foo">barbaz</a>"""
        assert clean_spaces("""  <a src="foo">bar   baz[bee]</a>   """) == """<a src="foo">bar baz[bee]</a>"""
        assert clean_spaces("""blah  <a src="foo">bar[bee]</a>   """) == """blah <a src="foo">bar[bee]</a>"""
        assert clean_spaces("""blah<a src="foo"> bar[bee]</a>   """) == """blah<a src="foo"> bar[bee]</a>"""
        assert clean_spaces("""blah <a src="foo"> bar[bee]</a>   """) == """blah<a src="foo"> bar[bee]</a>"""
        assert clean_spaces("  abc   <a href=\"foo\">def</a>[ghi]  \n  <b>mn</b>[aa]  op[qrs]  tuv[wy]  ") \
            == "abc <a href=\"foo\">def</a>[ghi]\n<b>mn</b>[aa] op[qrs] tuv[wy]"
