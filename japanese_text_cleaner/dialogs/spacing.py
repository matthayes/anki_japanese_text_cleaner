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

from ..text.spacing import clean_spaces
from .base import TextCleanerDialogBase


class JapaneseSpacingFixerDialog(TextCleanerDialogBase):
    """Japanese spacing fixer dialog"""

    def __init__(self, browser, nids):
        super().__init__(browser, nids,
                         "Choose the field below to check for spacing",
                         "Check Spacing in Selected Notes")
        self.op = "clean_spaces"
        self.checkpoint_name = "fix japanese spacing"

    def clean_content(self, content, output_html_diff=False):
        return clean_spaces(content, output_html_diff)
