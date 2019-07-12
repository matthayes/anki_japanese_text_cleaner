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

import os
import time
import traceback
from collections import namedtuple

from aqt.qt import (QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFontDatabase, QHBoxLayout, QLabel,
                    QPlainTextEdit, QStandardPaths, Qt, QVBoxLayout)
from aqt.utils import askUser

from ..db.change_log import ChangeLog, ChangeLogEntry
from ..text.exceptions import TextProcessingError

DIFF_PRE = """<html>
<head>
<style>
p {
    font-family: "Lucida Console", Monaco, monospace;
}
ins {
    background-color: lightgreen;
    text-decoration: none;
}
del {
    background-color: lightpink;
    text-decoration: none;
}
</style>
</head>
<body>"""

DIFF_POST = """</body>
</html>
"""

NoteChange = namedtuple("NoteChange", ["nid", "old", "new"])


class NoteFixError(Exception):
    """Thrown when unexpected error occurs while fixing notes"""
    pass


class TextCleanerDialogBase(QDialog):
    """Base class for dialogs"""

    def __init__(self, browser, nids, description, title):
        super().__init__(parent=browser)
        self.browser = browser
        self.nids = nids
        self.description = description
        self.title = title
        self.changelog = ChangeLog()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(self.title)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        vbox = QVBoxLayout()
        vbox.addLayout(self._ui_top_row())
        vbox.addLayout(self._ui_field_select_row())
        vbox.addWidget(self._ui_log())
        vbox.addLayout(self._ui_bottom_row())

        self.setLayout(vbox)

    def _ui_top_row(self):
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(self.description))
        return hbox

    def _ui_field_select_row(self):
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignLeft)
        hbox.addWidget(QLabel("Field:"))

        model = self.browser.mw.col.getNote(self.nids[0]).model()
        field_names = self.browser.mw.col.models.fieldNames(model)

        self.field_selection = QComboBox()
        self.field_selection.addItems(field_names)
        hbox.addWidget(self.field_selection)

        return hbox

    def _ui_log(self):
        self.log = QPlainTextEdit()
        self.log.setTabChangesFocus(False)
        self.log.setReadOnly(True)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(self.log.font().pointSize() - 2)
        self.log.setFont(font)
        return self.log

    def _ui_bottom_row(self):
        hbox = QHBoxLayout()

        buttons = QDialogButtonBox(Qt.Horizontal, self)

        # Button to check if content needs to be changed
        check_btn = buttons.addButton("&Check",
                                      QDialogButtonBox.ActionRole)
        check_btn.setToolTip("Check")
        check_btn.clicked.connect(lambda _: self.onCheck())

        # Button to generate diff of proposed content changes
        diff_btn = buttons.addButton("&Diff",
                                     QDialogButtonBox.ActionRole)
        diff_btn.setToolTip("Show diff")
        diff_btn.clicked.connect(lambda _: self.onDiff())

        # Button to make the proposed changes
        fix_btn = buttons.addButton("&Fix",
                                    QDialogButtonBox.ActionRole)
        fix_btn.setToolTip("Fix")
        fix_btn.clicked.connect(lambda _: self.onFix())

        # Button to close this dialog
        close_btn = buttons.addButton("&Close",
                                      QDialogButtonBox.RejectRole)
        close_btn.clicked.connect(self.close)

        hbox.addWidget(buttons)
        return hbox

    def clean_content(self, content, output_html_diff=False):
        raise NotImplementedError("clean_content")

    def onCheck(self):
        """Checks which notes need to be updated for the selected field"""
        append_to_log = self.log.appendPlainText

        try:
            self.log.clear()
            nids = self.nids
            field_name = self.field_selection.currentText()

            checked = 0
            need_clean = 0
            failed_notes = []
            for nid in nids:
                note = self.browser.mw.col.getNote(nid)
                if field_name in note:
                    content = note[field_name]
                    try:
                        cleaned_content = self.clean_content(content)
                        if content != cleaned_content:
                            append_to_log("Need to update note for nid {}:".format(nid))
                            append_to_log("{}\n=>\n{}\n".format(content, cleaned_content))
                            need_clean += 1
                    except TextProcessingError as e:
                        failed_notes.append((nid, content, str(e)))
                    checked += 1
            if failed_notes:
                append_to_log("Found {} notes that failed to be processed:".format(len(failed_notes)))
                for nid, _, exc in failed_notes:
                    append_to_log("{}: {}\n".format(nid, exc))
            append_to_log("Checked {} notes".format(checked))
            append_to_log("Found {} notes ({:.0f}%) need to be updated".format(
                need_clean, 0 if not checked else 100.0 * need_clean / checked))
            if failed_notes:
                append_to_log("Found {} notes that failed to be processed".format(len(failed_notes)))

        except Exception:
            append_to_log("Failed while checking notes:\n{}".format(traceback.format_exc()))

        # Ensure QPlainTextEdit refreshes (not clear why this is necessary)
        self.log.repaint()

    def onDiff(self):
        """Produces HTML diff of the updates that would be made"""
        append_to_log = self.log.appendPlainText

        lines = []
        try:
            self.log.clear()
            nids = self.nids
            field_name = self.field_selection.currentText()

            cnt = 0
            need_clean = 0
            failed_notes = []
            for nid in nids:
                note = self.browser.mw.col.getNote(nid)
                if field_name in note:
                    content = note[field_name]
                    try:
                        cleaned_content = self.clean_content(content, output_html_diff=True)
                        if content != cleaned_content:
                            lines.append((nid, cleaned_content))
                            need_clean += 1
                    except TextProcessingError as e:
                        failed_notes.append((nid, content, str(e)))
                    cnt += 1
            if failed_notes:
                append_to_log("Found {} notes that failed to be processed:".format(len(failed_notes)))
                for nid, _, exc in failed_notes:
                    append_to_log("{}: {}\n".format(nid, exc))
            append_to_log("Checked {} notes. Found {} notes need updating.".format(
                cnt, need_clean))
            if failed_notes:
                append_to_log("Found {} notes that failed to be processed".format(len(failed_notes)))

            if len(lines) > 0:
                ext = ".html"
                default_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
                path = os.path.join(default_path, f"diff{ext}")

                options = QFileDialog.Options()

                # native doesn't seem to works
                options |= QFileDialog.DontUseNativeDialog

                # we'll confirm ourselves
                options |= QFileDialog.DontConfirmOverwrite

                result = QFileDialog.getSaveFileName(
                    self, "Save HTML diff", path, f"HTML (*{ext})",
                    options=options)

                if not isinstance(result, tuple):
                    raise Exception("Expected a tuple from save dialog")
                file = result[0]
                if file:
                    do_save = True
                    if not file.lower().endswith(ext):
                        file += ext
                    if os.path.exists(file):
                        if not askUser("{} already exists. Are you sure you want to overwrite it?".format(file),
                                       parent=self):
                            do_save = False
                    if do_save:
                        append_to_log("Saving to {}".format(file))
                        with open(file, "w", encoding="utf-8") as outf:
                            outf.write(DIFF_PRE)
                            for nid, line in lines:
                                outf.write("<p>nid {}:</p>\n".format(nid))
                                outf.write("<p>{}</p>\n".format(line))
                            outf.write(DIFF_POST)
                        append_to_log("Done")

            # Ensure QPlainTextEdit refreshes (not clear why this is necessary)
            self.log.repaint()

        except Exception:
            append_to_log("Failed while checking notes:\n{}".format(traceback.format_exc()))

    def onFix(self):
        """Updates the selected notes where the content needs to be updated"""
        append_to_log = self.log.appendPlainText

        try:
            self.log.clear()
            nids = self.nids
            field_name = self.field_selection.currentText()

            append_to_log("Checking how many notes need to be updated")
            checked = 0
            note_changes = []
            failed_notes = []
            for nid in nids:
                note = self.browser.mw.col.getNote(nid)
                if field_name in note:
                    content = note[field_name]
                    try:
                        cleaned_content = self.clean_content(content)
                        if content != cleaned_content:
                            note_changes.append(NoteChange(
                                nid=nid, old=content, new=cleaned_content))
                    except TextProcessingError as e:
                        failed_notes.append((nid, content, str(e)))
                    checked += 1

            if failed_notes:
                append_to_log("Found {} notes that failed to be processed:".format(len(failed_notes)))
                for nid, _, exc in failed_notes:
                    append_to_log("{}: {}\n".format(nid, exc))

            append_to_log("{} of {} notes will be updated".format(len(note_changes), checked))

            if failed_notes:
                append_to_log("Found {} notes that failed to be processed.".format(len(failed_notes)))

            self.log.repaint()

            if askUser("{} of {} notes will be updated.  Are you sure you want to do this?".format(
                    len(note_changes), checked), parent=self):

                append_to_log("Beginning update")

                self.browser.mw.checkpoint("{} ({} {})".format(
                    self.checkpoint_name, len(note_changes),
                    "notes" if len(note_changes) > 1 else "note"))
                self.browser.model.beginReset()

                cleaned = 0
                try:
                    init_ts = int(time.time() * 1000)
                    for note_change in note_changes:
                        note = self.browser.mw.col.getNote(note_change.nid)
                        content = note[field_name]

                        # content should not have changed
                        if content != note_change.old:
                            # this should never happen
                            raise NoteFixError("nid {} old and new content do not match".format(
                                note_change.nid))

                        cleaned_content = note_change.new

                        append_to_log("Updating note for nid {}:".format(nid))
                        append_to_log("{}\n=>\n{}\n".format(content, cleaned_content))

                        ts = int(time.time() * 1000)

                        note[field_name] = cleaned_content
                        note.flush()

                        self.changelog.record_change(
                            self.op, init_ts,
                            ChangeLogEntry(
                                ts=ts, nid=nid, fld=field_name,
                                old=content, new=cleaned_content))

                        cleaned += 1

                    append_to_log("Updated {} notes ({:.0f}%)".format(
                        cleaned, 0 if not checked else 100.0 * cleaned / checked))

                finally:
                    if cleaned:
                        self.changelog.commit_changes()
                        self.browser.mw.requireReset()
                    self.browser.model.endReset()

            else:
                append_to_log("User aborted update")

        except Exception:
            append_to_log("Failed while checking notes:\n{}".format(traceback.format_exc()))

        # Ensure QPlainTextEdit refreshes (not clear why this is necessary)
        self.log.repaint()

    def close(self):
        self.changelog.close()
        super().close()
