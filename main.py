import json
import config, mutation, query, tools


# & Loading the REST API configurations
def loadStructure(name="./structure.json"):
    with open(name) as f:
        config.structure = json.loads(f.read())

# & Environment setup: Load the API configuration from config file
loadStructure()
config.tab = " " * config.structure["config"]["tab"]
config.queryFile = config.structure["config"]["file"]
config.strict = config.structure["config"]["strict"]
config.splitter = config.structure["splitter"]
config.apiBase = config.structure["base"]


# / Base class
tools = tools.Tools()

# / Inherit tools in query handlers
query.Query(tools)
mutation.Mutation(tools)

# & All the `types` & `inputs` are prepared
tools.parseSchema()
# & Till now everything prepared & now to be written in file
tools.writeQueryToFile()
