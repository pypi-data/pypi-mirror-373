# Copyright (c) 2024 Deb Mishra
# This file is part of persistentidgenerator
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import sqlite3, sys, os, io, contextlib

sys.path.append("..")
from persistentidgenerator import domainSet, defLoc, dbPath, tableList
from persistentidgenerator import squerySavedID, uquerySavedID, iquerySavedID
from persistentidgenerator import iquerydroppedID, squerydroppedIDs, squerydroppedIDt


class guidgen:
    def __init__(self):
        self.numid = 1_000_000_000
        if dbPath is not None:
            self.fPath = dbPath
        else:
            self.fPath = defLoc
        self.stdout_stream = io.StringIO()
        self.stderr_stream = io.StringIO()

    # Create a sqlite database to store sql ids
    def create_database(self):
        with contextlib.redirect_stdout(self.stdout_stream), contextlib.redirect_stderr(
            self.stderr_stream
        ):
            dbName = self.fPath + "sqlidstore.db"
            if not os.path.exists(dbName):
                sys.stdout.write(f"Creating new database at {dbName}.\n")
                try:
                    conn = sqlite3.connect(dbName)
                    sys.stdout.write(
                        f"successfully connected to the database stored at {dbName}\n"
                    )
                    return conn
                except sqlite3.Error as e:
                    sys.stderr.write(f"Error connecting database:{e}\n")
            else:
                sys.stdout.write(
                    f"Database already present at {dbName}. Connecting to existing database\n"
                )
                try:
                    conn = sqlite3.connect(dbName)
                    sys.stdout.write(
                        f"successfully connected to the database stored at {dbName}\n"
                    )
                    return conn
                except sqlite3.Error as e:
                    sys.stderr.write(f"Error connecting database:{e}\n")
        self.logout = self.stdout_stream.getvalue()
        self.logerr = self.stderr_stream.getvalue()
        return self

    # Check if the table exist
    def table_exists(self, tableName):
        with contextlib.redirect_stdout(self.stdout_stream), contextlib.redirect_stderr(
            self.stderr_stream
        ):
            conn = self.create_database()
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tableName}'\n"
            )
            self.res = cursor.fetchone()
            conn.close()
        self.logout = self.stdout_stream.getvalue()
        self.logerr = self.stderr_stream.getvalue()
        return self

    def create_table(self):
        with contextlib.redirect_stdout(self.stdout_stream), contextlib.redirect_stderr(
            self.stderr_stream
        ):
            for t in tableList:
                res = self.table_exists(t).res
                if res is None:
                    conn = guidgen().create_database()
                    cursor = conn.cursor()
                    cursor.execute(tableList[t])
                    conn.commit()
                    conn.close()
                    sys.stdout.write(f"table {t} created\n")
                else:
                    sys.stdout.write(f"table {t} already exists\n")
        self.logout = self.stdout_stream.getvalue()
        self.logerr = self.stderr_stream.getvalue()
        return self

    # Generate an unique ID that can be used across
    def generate_id(self, cat="oth"):
        with contextlib.redirect_stdout(self.stdout_stream), contextlib.redirect_stderr(
            self.stderr_stream
        ):
            self.create_table()
            conn = self.create_database()
            cursor = conn.cursor()
            try:
                catval = domainSet[cat]
                cursor.execute(squerySavedID, (cat,))
                numericId = cursor.fetchone()
                if numericId is None:
                    self.numericId = domainSet[cat] * self.numid + 1
                    cursor.executemany(
                        iquerySavedID,
                        [
                            (cat, self.numericId),
                        ],
                    )
                    self.category = cat
                    self.masterId = cat.upper() + str(self.numericId)
                else:
                    limit = (catval + 1) * self.numid
                    if numericId[0] < limit:
                        self.numericId = numericId[0] + 1
                        cursor.execute(uquerySavedID, (self.numericId, cat))
                        self.category = cat
                        self.masterId = cat.upper() + str(self.numericId)
                    else:
                        sys.stderr.write(
                            f"the latest master id {numericId} is already at limit of {limit}. Can't add a new one. Program will exit.\n"
                        )
                conn.commit()
            except KeyError:
                sys.stderr.write(f"Key {cat} not found in dictionary")
                self.masterId = None
                self.numericId = None
                self.category = cat
            finally:
                conn.close()
            self.logout = self.stdout_stream.getvalue()
            self.logerr = self.stderr_stream.getvalue()
            return self

    # Once a master id is removed, it has to go to the droppedID table. So that it can be reused
    def drop_id(self, id, cat="oth"):
        with contextlib.redirect_stdout(self.stdout_stream), contextlib.redirect_stderr(
            self.stderr_stream
        ):
            guidgen().create_table()
            conn = guidgen().create_database()
            cursor = conn.cursor()
            cursor.execute(squerydroppedIDs, (cat,))
            vals = cursor.fetchone()
            cursor.execute(squerydroppedIDt, (cat, id))
            valt = cursor.fetchone()
            if vals is None:
                sys.stderr.write(
                    "There is no entries in the savedID table. Redundant drop request\n"
                )
            elif vals[0] < id:
                sys.stderr.write(
                    f"Input value {id} is higher than lastest value {val[0]}. Redundant drop request\n"
                )
            elif valt is not None:
                sys.stderr.write(
                    f"the value {id} and category {cat} combinations is already dropped.\n"
                )
            else:
                cursor.execute(iquerydroppedID, (cat, id))
            conn.commit()
            conn.close()
            self.logout = self.stdout_stream.getvalue()
            self.logerr = self.stderr_stream.getvalue()
            return self
