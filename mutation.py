import config


class Mutation:
    def __init__(self, tools):
        self.tools = tools
        self.endPoints = []
        self.combineMethods()
        self.init()

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
                reqType="put",
            )
