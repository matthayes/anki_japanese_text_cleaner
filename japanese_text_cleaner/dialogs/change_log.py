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

import csv
import datetime
import os
import traceback

from aqt.qt import (QDialog, QDialogButtonBox, QFileDialog, QFontDatabase, QHBoxLayout, QLabel, QPlainTextEdit,
                    QStandardPaths, Qt, QVBoxLayout)
from aqt.utils import askUser, tooltip

from ..db.change_log import ChangeLog


class ChangeLogDialog(QDialog):
    """Dialog to view changelog"""

    def __init__(self, browser):
        super().__init__(parent=browser)
        self.browser = browser
        self.changelog = ChangeLog()
        self.display_limit = 500
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("View Log")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        vbox = QVBoxLayout()
        vbox.addLayout(self._ui_top_row())
        vbox.addWidget(self._ui_log())
        vbox.addLayout(self._ui_bottom_row())

        self.setLayout(vbox)

        self.fillLog()

    def _ui_top_row(self):
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Last {} updates".format(self.display_limit)))
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

        # Button to export changelog to a CSV file
        export_btn = buttons.addButton("&Export full history",
                                       QDialogButtonBox.ActionRole)
        export_btn.setToolTip("Export full history to CSV")
        export_btn.clicked.connect(lambda _: self.onExport())

        # Button to close this dialog
        close_btn = buttons.addButton("&Close",
                                      QDialogButtonBox.RejectRole)
        close_btn.clicked.connect(self.close)

        hbox.addWidget(buttons)
        return hbox

    def fillLog(self):
        append_to_log = self.log.appendPlainText
        self.has_records = False
        for rec in reversed(self.changelog.db.all("""
                select op, ts, nid, fld, old, new from changelog
                order by ts desc
                limit {}
                """.format(self.display_limit))):
            self.has_records = True
            op, ts, nid, fld, old, new = rec
            dt = datetime.datetime.utcfromtimestamp(ts / 1000)
            ts_formatted = dt.strftime("%Y-%m-%dT%H:%M:%S")

            append_to_log("""{} [{}] Change {} of nid {}:\n{}\n=>\n{}\n""".format(
                ts_formatted, op, fld, nid, old, new))

        # Ensure QPlainTextEdit refreshes (not clear why this is necessary)
        self.log.repaint()

    def onExport(self):
        append_to_log = self.log.appendPlainText

        if not self.has_records:
            tooltip("Log is empty")
            return

        try:
            ext = ".csv"
            default_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            path = os.path.join(default_path, f"changes{ext}")

            options = QFileDialog.Options()

            # native doesn't seem to works
            options |= QFileDialog.DontUseNativeDialog

            # we'll confirm ourselves
            options |= QFileDialog.DontConfirmOverwrite

            result = QFileDialog.getSaveFileName(
                self, "Save CSV", path, f"CSV (*{ext})",
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
                        field_names = ["ts", "op", "nid", "fld", "old", "new"]
                        writer = csv.DictWriter(outf, fieldnames=field_names)
                        writer.writeheader()
                        for rec in self.changelog.db.all("""
                                select op, ts, nid, fld, old, new from changelog
                                order by ts asc
                                """):
                            op, ts, nid, fld, old, new = rec
                            writer.writerow({
                                "op": op,
                                "ts": ts,
                                "nid": nid,
                                "fld": fld,
                                "old": old,
                                "new": new
                            })

                    append_to_log("Done")
        except Exception:
            append_to_log("Failed while writing CSV:\n{}".format(traceback.format_exc()))
