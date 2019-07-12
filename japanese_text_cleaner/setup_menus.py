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

from anki.hooks import addHook
from aqt.utils import tooltip

from .dialogs.change_log import ChangeLogDialog
from .dialogs.furigana import JapaneseRedundantFuriganaFixerDialog
from .dialogs.spacing import JapaneseSpacingFixerDialog


def open_dialog(browser, cls):
    nids = browser.selectedNotes()
    if nids:
        cls(browser, nids).exec_()
    else:
        tooltip("You must select some cards first")


def open_changelog_dialog(browser):
    ChangeLogDialog(browser).exec_()


def setup_menus(browser):
    menu = browser.form.menuEdit
    menu.addSeparator()
    submenu = menu.addMenu("Japanese Text Cleaner")
    action = submenu.addAction("Spacing Fixer")
    action.triggered.connect(
        lambda _: open_dialog(browser, JapaneseSpacingFixerDialog))
    action = submenu.addAction("Furigana Fixer")
    action.triggered.connect(
        lambda _: open_dialog(browser, JapaneseRedundantFuriganaFixerDialog))
    action = submenu.addAction("View Log")
    action.triggered.connect(
        lambda _: open_changelog_dialog(browser))


addHook("browser.setupMenus", setup_menus)
