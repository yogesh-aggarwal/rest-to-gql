import config


class Query:
    def __init__(self, tools):
        self.endPoints = config.structure["get"]
        self.tools = tools
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
            self.tools.analyseEndPoint(params, endPoint["params"])
