import json
import config, mutation, query, tools


# & Loading the REST API configurations
def loadStructure(name="./structure.json"):
    with open(name) as f:
        config.structure = json.loads(f.read())



# ? Load the API configuration file
loadStructure()
config.tab = " " * config.structure["config"]["tab"]
config.queryFile = config.structure["config"]["file"]
config.strict = config.structure["config"]["strict"]
config.splitter = config.structure["splitter"]
config.apiBase = config.structure["base"]
# ? Starting the process
# get = query.Query()
# get.init()

# # ? Till now everything prepared & now to be written in file

tools = tools.Tools()

get = query.Query(tools)
mut = mutation.Mutation(tools)

# get.init()
mut.init()

tools.parseSchema()
print()
print()
print()
print(tools.schema)
tools.writeQueryToFile()
