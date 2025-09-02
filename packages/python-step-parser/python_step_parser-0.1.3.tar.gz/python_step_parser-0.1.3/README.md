# STEP file parser implemented in pure python

## Requirements
* Python 3.7+
* sqlite3

## Usage

To use the code in this library, you can first run the `parser.py` file against your STEP (.step or .stp) file which will extract the data and normalize it into a Sqlite database (.db) file. This database file can then be read by using an open connection and passing it to the provided parser classes which will then read all of the types and attributes required by itself and its heirarcy of children data structures. 