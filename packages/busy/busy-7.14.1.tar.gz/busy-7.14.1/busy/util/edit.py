# Call the system editor

from io import StringIO
from subprocess import run
from tempfile import NamedTemporaryFile

from busy.model.collection import Collection


def edit_text(text: str, command: str):
    with NamedTemporaryFile(mode="w+") as tempfile:
        tempfile.write(text)
        tempfile.seek(0)
        run([command, tempfile.name])
        tempfile.seek(0)
        return tempfile.read()


def edit_items(collection: Collection, indices, command):
    with StringIO() as oldio:
        collection.write_items(oldio, indices)
        oldio.seek(0)
        oldtext = oldio.read()
    newtext = edit_text(oldtext, command)
    with StringIO() as newio:
        newio.write(newtext)
        newio.seek(0)
        newitems = collection.read_items(newio, indices)
    return newitems
