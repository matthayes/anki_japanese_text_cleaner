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
from collections import namedtuple

from anki.db import DB

ChangeLogEntry = namedtuple("ChangeLogEntry", ["ts", "nid", "fld", "old", "new"])


class ChangeLog:
    """Tracks changes made to notes"""
    def __init__(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_path, "..", "user_files", "changelog.db")
        need_create = not os.path.exists(db_path)
        self.db = DB(db_path)
        self.db.setAutocommit(True)
        if need_create:
            self._create_tables()
            self._create_indices()
        self.db.setAutocommit(False)
        max_id = self.db.scalar("select max(id) from changelog")
        if max_id is not None:
            self.next_id = max_id + 1
        else:
            self.next_id = 0

    def close(self):
        self.db.close()

    def commit_changes(self):
        self.db.commit()
        self.db.mod = False

    def record_change(self, op, init_ts, change):
        self.db.execute(
            """
            insert into changelog (id, op, init_ts, ts, nid, fld, old, new)
            values (?,?,?,?,?,?,?,?)
            """, self.next_id, op, init_ts, change.ts, change.nid, change.fld,
            change.old, change.new)
        self.next_id += 1

    def record_and_commit_changes(self, op, init_ts, changes):
        data = []
        for change in changes:
            data.append((self.next_id, op, init_ts, change.ts, change.nid, change.fld,
                         change.old, change.new))
            self.next_id += 1
        self.db.executemany("""
            insert into changelog (id, op, init_ts, ts, nid, fld, old, new)
            values (?,?,?,?,?,?,?,?)
        """, data)
        self.commit_changes()

    def _create_tables(self):
        self.db.executescript("""
            create table if not exists changelog (
              id      integer primary key,
              -- identifies the operation performed
              op      text not null,
              -- timestamp (ms) when bulk changes were initiated
              init_ts integer not null,
              -- timestamp (ms) when field was changed
              ts      integer not null,
              -- note id
              nid     integer not null,
              -- field name
              fld     text not null,
              -- old value of field
              old     text not null,
              -- new value of field
              new     text not null
            );
        """)

    def _create_indices(self):
        self.db.executescript("""
            create index if not exists ix_changelog_ts on changelog (ts);
        """)
