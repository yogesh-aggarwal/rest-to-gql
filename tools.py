import config
import requests
import json


class BaseTools:
    # ? Decides whether to create a new interface or not for nested types
    interfaceExists = False

    def __init__(self):
        # ? Type interfaces are appended to it
        self.types = config.types
        # ? Input interfaces are appended to it
        self.inputs = config.inputs
        # ? Schema interfaces are appended to it
        self.schema = config.schema
        # ? Stores the nested types that are object based
        self.nestedTypes = []
        # ? Stores the {getName: Name} type objects for `query` inputs resolving
        self.schemaQueryInputNames = []
        # ? Stores the {(create, update, delete)Name(args: {}): Name} type objects for `mutation` inputs resolving
        self.schemaMutationInputNames = []

        self.types = config.types
        self.inputs = config.inputs

    def writeQueryToFile(self):
        """
        Writes the final query to a file
        """
        # ? Saving the resultant query to the file
        with open(config.queryFile, "w+") as f:
            f.write(f"#? Generated with <3\n{self.inputs}\n{self.types}\n{self.schema}")

    def getStrict(self):
        """
        Returns "!" if there's is strict type defined for the `gql` query response
        """
        return "!" if config.strict else ""

    def addCurlyBraces(self, x):
        """
        Adds curly braces around an object (useful when
        creating gql interfaces using "f-string" in python)
        """
        return "{" + x + "}"

    def getPrefixByRequestName(self, req):
        if req == "get":
            return "get"
        elif req == "delete":
            return "delete"
        elif req in ["put", "post"]:
            return "update"
        else:
            return req

    @staticmethod
    def getResponse(
        url="", toJson=True, base=True, prepare=False, reqType="get", data={}
    ):
        """
        Helps in fetching the API
        `base`: Whether to attach the API root URL or not
        `toJson`: Whether to convert the fetch results to JSON object or not
        `prepare`: Opp. to `url`. List of (urlWords, params)
        """
        # ? Prepare the URL from the config file
        if prepare:
            url = ""
            paramIndex = 0
            for keyword in prepare[0]:
                # ? Inserting the value in place of keywords like ":id"
                if ":" not in keyword:
                    url += f"{keyword}{config.splitter}"
                else:
                    url += f"{prepare[1][paramIndex]}{config.splitter}"
                    paramIndex += 1
        else:
            if not url:
                raise ValueError("No URL Provided.")

        url = f"{config.apiBase if base else ''}/{url}"
        # ? "//" sometimes occurs when len(arguments) != len(param values)
        url = url.replace("//", "/")
        # ? Fix: Due to above step "https://" or "http://" get changed to "https:/" or "http:/"
        url = url.replace(":/", "://")

        # ? Fetching the result
        if reqType == "get":
            result = requests.get(url).text
        elif reqType == "put":
            result = requests.put(url).text
        elif reqType == "post":
            result = requests.post(url).text
        elif reqType == "patch":
            result = requests.patch(url).text
        elif reqType == "post":
            result = requests.delete(url).text
        else:
            raise ValueError(f"Invalid request type: {reqType}")

        return json.loads(result) if toJson else result


class ParseTools(BaseTools):
    def __init__(self):
        super().__init__()

    @staticmethod
    def parseTypeByObj(x):
        """
        Identifies what gql type should be assigned to an object
        """
        if isinstance(x, str):
            return "String"
        elif str(x) == "True" or str(x) == "False":
            return "Boolean"
        elif isinstance(x, int) or isinstance(x, float):
            return "Number"
        else:
            return False

    @staticmethod
    def parseTypeByName(x, err=True):
        """
        Identifies what gql type should be assigned to an object by its python class name
        """
        if x in ["int", "float"]:
            return "Number"
        elif x in ["str"]:
            return "String"
        elif x in ["int", "float"]:
            return "Number"
        elif x in ["bool"]:
            return "Boolean"
        else:
            if err:
                raise ValueError(f'Unknown data type: "{x}"')
            return False

    def parseResponseForType(self, res, name="Main"):
        """
        Generates the type for `gql` query based on 
        the variables. It creates the root type & all
        the nested types are appended to `nestedTypes`
        object. Then they are fetched in the next step
        (outside this function).
        """
        # ? Check for dict because on arrays it gives error during slicing for the value
        res = res if isinstance(res, dict) else res[0]

        # ? Looping through the dict variables
        for parentAttrib in res:
            # ? Creating a new type if not created yet
            if not self.interfaceExists:
                self.types += f"\ntype {name} " + "{\n"
                # ? Setting to `True` so that in the next round no new types get created for the same interface
                self.interfaceExists = True

            # ? Identifying the `gql` type
            typ = self.parseTypeByObj(res[parentAttrib])
            isArray = (
                True
                if isinstance(res[parentAttrib], list)
                or isinstance(res[parentAttrib], tuple)
                else False
            )
            if typ:
                # ? Appending the entry to the type interface. Eg: `_id: String!`
                if isArray:  # ? For arrays appending like `[String]`
                    self.types += f"{config.tab}{parentAttrib}: [{typ}{self.getStrict()}]{self.getStrict()}\n"
                else:  # ? For normal values like `String`
                    self.types += (
                        f"{config.tab}{parentAttrib}: {typ}{self.getStrict()}\n"
                    )
            else:  # ? Type may be a nested object or an array
                if isArray:  # ? For arrays appending like `[String]`
                    self.types += f"{config.tab}{parentAttrib}: [{name}{parentAttrib.title()}{self.getStrict()}]{self.getStrict()}\n"
                else:  # ? For normal values like `String`
                    self.types += f"{config.tab}{parentAttrib}: {name}{parentAttrib.title()}{self.getStrict()}\n"
                # ? self.types += f"{config.tab}{parentAttrib}: {name}{parentAttrib.title()}{self.getStrict()}\n"  #? Passing a reference in the main type for the nested type
                # ? Saving the attributes of the nested type
                self.nestedTypes.append(
                    {"name": f"{name}{parentAttrib.title()}", "data": res[parentAttrib]}
                )
        # ? If there's no error & query created successfully then closing it.
        if self.types:
            self.types += "}\n"

    def parseResponseForInputs(self, args, name="Main"):
        """
        Generates the inputs fpr `gql` query based on the variables.
        """
        # # ? Check whether to create a new input interface or not
        # if not self.interfaceExists:
        self.inputs += f"\ninput {name}Inp " + "{\n"

        # ? Loop through dict like {name: "id", type: "String"}
        for arg in args:
            self.inputs += (
                f"{config.tab}{arg['name']}: {arg['type']}{self.getStrict()}\n"
            )

    def parseSchema(self, prefix="get"):
        """
        Parses all the `type` & `input` interfaces into a unified schema
        """
        # & Queries
        # ? Initiating new resolver
        self.schema += "type QueryResolver {" if self.schemaQueryInputNames else ""
        # ? Loop through dict like {User: UserInp} (name: input_name)
        for typ in self.schemaQueryInputNames:
            args = (
                f"(args: {typ}Inp)"
                if typ  # ? If the `type` defination has inputs
                else ""
            )
            # ? Concat the `QueryResolver` entry
            self.schema += f"\n{config.tab}get{typ}{args}: {typ}{self.getStrict()}\n"

        # ? Complete the `QueryResolver` `type` defination
        self.schema += "}\n" if self.schemaQueryInputNames else ""

        # & Mutations
        # ? Initiating new resolver
        self.schema += (
            "type MutationResolver {" if self.schemaMutationInputNames else ""
        )
        # ? Loop through dict like {User: UserInp} (name: input_name)
        for typ in self.schemaMutationInputNames:
            args = (
                f"(args: {typ}Inp)"
                if typ  # ? If the `type` defination has inputs
                else ""
            )
            # ? Concat the `QueryResolver` entry
            self.schema += f"\n{config.tab}{typ}{args}: {typ}{self.getStrict()}\n"

        # ? Complete the `QueryResolver` `type` defination
        self.schema += "}\n" if self.schemaMutationInputNames else ""

        # ? Finalizing the schema
        self.schema += (
            "\nschema {\n"
            + (
                f"{config.tab}query: QueryResolver\n"
                if self.schemaQueryInputNames
                else ""
            )
            + (
                f"{config.tab}mutation: MutationResolver\n"
                if self.schemaMutationInputNames
                else ""
            )
            + "}\n"
        )


class Analyse(ParseTools):
    def __init__(self):
        super().__init__()

    def analyseEndPoint(
        self, urlWords, params, name="", reqType="get", sameResponse=False, resData={}
    ):
        """
        Getting details about the end point from the config file
        """
        # ? Contains args in form of `{ argName: argTypeAsOfGraphQL }`
        args = []
        # ? Contains all the words other than arguments that are present in URL
        keywords = []
        # ? Seperating out the parameters & keywords
        for param in urlWords:
            # ? This means it's not a parameter
            if ":" not in param:
                keywords.append(param)
            else:
                # ? Specially formatting a parameter to dict of {name, type}
                param = param.split("[")
                args.append(
                    {
                        "name": param[0].replace(":", ""),
                        "type": self.parseTypeByName(param[1][:-1]),
                    }
                )

        keywords = tuple(
            map(lambda x: x.title(), keywords)
        )  # ? Filtering out the blank strings

        # & If arguments are present that means URL need an `input` interface, prepare that.
        if args:
            if not name:
                if reqType == "get":
                    name = keywords[0]
                    # ? Creating input for the parent route
                    self.schemaQueryInputNames.append(name)
                else:
                    name = f"{self.getPrefixByRequestName(reqType)}{keywords[0]}"
                    # ? Creating input for the parent route
                    self.schemaMutationInputNames.append(name)

            self.parseResponseForInputs(args, name=name)
            self.inputs += "}\n"

        # & Fetching API
        if sameResponse:
            res = resData
        else:
            res = self.getResponse(prepare=(urlWords, params), reqType=reqType)

        # & Parsing the response so as to start the generation process
        self.parseResponseForType(res, name=f"{name}")
        # & Completing the types for the pending nested type interfaces that are left during generation of parent types
        for pendingNestObj in self.nestedTypes:
            self.interfaceExists = False
            self.parseResponseForType(
                pendingNestObj["data"], name=f"{pendingNestObj['name']}",
            )

        # print(f"[MAIN]: \n{'='*40}\n{self.types}\n{'='*40}")


# ? Exported class
class Tools(Analyse):
    def __init__(self):
        super().__init__()
