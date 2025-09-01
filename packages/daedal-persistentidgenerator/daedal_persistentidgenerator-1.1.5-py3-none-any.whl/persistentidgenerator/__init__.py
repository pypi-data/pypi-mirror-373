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

# -----------------------------Program to generate sequential ids ---------------
import os

# Create variables that can be used across the module
domainSet = {
    "fx": 1,
    "hp": 2,
    "sec": 3,
    "idx": 4,
    "bmrk": 5,
    "hld": 6,
    "por": 7,
    "ent": 8,
    "oth": 0,
}
defLoc = "./"
dbPath = os.getenv("SLITE_DB_PATH")
createQuery = """CREATE TABLE IF NOT EXISTS savedID (
    category VARCHAR(20) PRIMARY KEY UNIQUE,
    last_value BIGINT)"""
droppedQuery = """CREATE TABLE IF NOT EXISTS droppedID (
    id INTEGER PRIMARY KEY,
    category VARCHAR(20),
    dropped_value BIGINT)"""
tableList = {"savedID": createQuery, "droppedID": droppedQuery}
squerySavedID = "select last_value from savedID where category=?"
uquerySavedID = "update savedID set last_value = ? where category=?"
iquerySavedID = "insert into savedID (category, last_value) values (?,?)"
iquerydroppedID = "insert into droppedID (category, dropped_value) values (?,?)"
squerydroppedIDs = "select last_value from savedID where category=?"
squerydroppedIDt = "select 1 from droppedID where category=? and dropped_value=?"
