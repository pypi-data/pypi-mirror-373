import argparse
from vgrep.db import DB
from vgrep.fs import FS
from vgrep.file_sync import FileSync
from chromadb import chromadb
from pathlib import Path

# get the search string
parser = argparse.ArgumentParser()
parser.add_argument("search",
                    help="The search string to use for the query")
args = parser.parse_args()

# point to FS
fs = FS([Path('/home/pierre/Documents')])

# set up DB
client = chromadb.PersistentClient(path="./db")
collection = None
try:
    collection =  client.get_collection(name="main")
except chromadb.errors.InvalidCollectionException:
    collection = client.create_collection(name="main")
db = DB(collection)

print(db.query(args.search))
