import os
import re
import pickle

from visor.models import Card
from django.core.management import call_command

class UpdateDatabase:
    """
    This class will be used to update the Django Database from a Pickle object.
    The path to the Pickle file will be always placed at "visor/CopenMed_Reasoner" and it should
    have a filename following the pattern "reasoning#.pkl", being "#" the version of the current
    database.
    Currently, this file will clean all available migrations and databases and reconstruct everything
    from the beginning.
    """

    def __init__(self):
        fnIntermediate = os.path.join(os.getcwd(), "visor", "CopenMed_Reasoner", "reasoning3.pkl")
        with open(fnIntermediate, 'rb') as fh:
            self.database = pickle.load(fh)

    def addEntry(self, _entity, _familiy, _description, _resources):
        """Create a new card model and save it in the database"""
        card = Card()
        card.entity = _entity
        card.family = _familiy
        card.description = _description
        card.resources = _resources
        card.save()

    def reconstructDatabase(self):
        """Reconstruct the Django Database based on the CopenMed Database (Pickle)"""
        call_command("makemigrations", "visor", interactive=False)
        call_command("migrate", interactive=False)
        entries = self.database[1]
        for key in entries:
            arguments = {}
            entry = entries[key]
            arguments["_entity"] = entry[0]
            arguments["_familiy"] = entry[2]
            arguments["_description"] = "Not avalaible"
            arguments["_resources"] = "Not Avalaible"
            self.addEntry(**arguments)

    def cleanDatabase(self):
        """Clean the database so we can reconstruct it from scratch"""
        os.remove("db.sqlite3") if os.path.exists("db.sqlite3") else None
        migrations_dir = os.path.join("visor", "migrations")
        for file in os.listdir(migrations_dir):
            if re.search(r"[0-9][0-9][0-9][0-9]", file):
                os.remove(os.path.join(migrations_dir, file))

if __name__=="__main__":
    # Run the database reconstruction process
    update = UpdateDatabase()
    update.cleanDatabase()
    update.reconstructDatabase()
