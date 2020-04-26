import config


class Query:
    def __init__(self, tools):
        self.endPoints = config.structure["get"]
        self.tools = tools
        super().__init__()
        self.init()

    def init(self):
        """
        Initialises the process of query generation
        """
        for endPoint in self.endPoints:
            self.interfaceExists = False
            urlWords = tuple(
                filter(lambda x: x != "", endPoint["url"].split(config.splitter))
            )
            try:
                endPointNameByUser = endPoint["name"]
            except:
                endPointNameByUser = ""
            try:
                sameResponse = endPoint["sameResponse"]
            except:
                sameResponse = ""
            try:
                exampleData = endPoint["exampleData"]
            except:
                exampleData = {}

            self.tools.analyseEndPoint(
                urlWords,
                endPoint["params"],
                name=endPointNameByUser,
                sameResponse=sameResponse,
                resData=exampleData,
                reqType="get",
            )
