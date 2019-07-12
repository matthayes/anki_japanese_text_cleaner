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


class TextProcessingError(Exception):
    """Base class for all text processing errors"""
    pass


class TextProcessingUnexpectedError(Exception):
    """Indicates an unexpected internal error due to a programmatic bug."""
    pass


class JapaneseReadingFormattingError(TextProcessingError):
    """
    Thrown when an text with invalid formatting for Japanese reading is detected.
    """
    pass
