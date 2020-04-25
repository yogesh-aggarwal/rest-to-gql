import json
from . import config, mutation, query


# & Loading the REST API configurations
def loadStructure(name="./structure.json"):
    with open(name) as f:
        config.structure = json.loads(f.read())


# Load the API configuration file
loadStructure()
# Starting the process
# get = query.Query()
# get.init()
mut = mutation.Mutation()
mut.init()
