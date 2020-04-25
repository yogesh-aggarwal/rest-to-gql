from . import config, tools


class Query(tools.Tools):
    def __init__(self):
        self.types = config.types
        self.inputs = config.inputs
        self.endPoints = config.structure["get"]
        config.tab = " " * config.structure["config"]["tab"]
        config.queryFile = config.structure["config"]["file"]
        config.strict = config.structure["config"]["strict"]
        config.splitter = config.structure["splitter"]
        config.apiBase = config.structure["base"]
        super().__init__()

    def init(self):
        """
        Initialises the process of query generation
        """
        for endPoint in self.endPoints:
            self.interfaceExists = False
            params = tuple(
                filter(lambda x: x != "", endPoint["url"].split(config.splitter))
            )
            print(params)
            self.analyseEndPoint(params, endPoint["params"])

        self.parseSchema()

        self.writeQueryToFile()
