from . import config, tools


class Mutation(tools.Tools):
    def __init__(self):
        self.types = config.types
        self.inputs = config.inputs
        self.endPoints = []
        self.combineMethods()
        config.tab = " " * config.structure["config"]["tab"]
        config.queryFile = config.structure["config"]["file"]
        config.strict = config.structure["config"]["strict"]
        config.splitter = config.structure["splitter"]
        config.apiBase = config.structure["base"]
        super().__init__()

    def combineMethods(self):
        """
        Combines the end points for all other operations other than GET.
        """
        # ? Methods allowed for mutations
        allowedMethods = ["put", "post", "delete", "patch"]
        for method in allowedMethods:
            try:
                self.endPoints.extend(config.structure[method])
            except Exception:
                pass

    def init(self):
        """
        Initialises the process of query generation
        """
        for endPoint in self.endPoints:
            self.interfaceExists = False
            params = tuple(
                filter(lambda x: x != "", endPoint["url"].split(config.splitter))
            )
            self.analyseEndPoint(params, endPoint["params"])

        self.parseSchema(prefix="mutate")

        self.writeQueryToFile()
