from . import config
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
        # ? Stores the {getName: Name} type objects for `query` resolving
        self.schemaQueryData = {}
        # ? Stores the {(create, update, delete)Name(args: {}): Name} type objects for `mutation` resolving
        self.schemaMutationData = {}

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

    @staticmethod
    def getResponse(url="", toJson=True, base=True, prepare=False):
        """
        Helps in fetching the API
        `base`: Whether to attach the API root URL or not
        `toJson`: Whether to convert the fetch results to JSON object or not
        `prepare`: Opp. to `url`. List of (url, params)
        """
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

        # ? Fetching the result
        result = requests.get(f"{config.apiBase if base else ''}/{url}").text
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

    def parseResponseForTypes(self, res, name="Main"):
        """
        Generates the types for `gql` query based on 
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
        # ? Check whether to create a new input interface or not
        if not self.interfaceExists:
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
        # ? Queries
        self.schema += (
            f"type {'QueryResolver' if prefix=='get' else 'MutationResolver'} " "{"
        )  # ? Initiating new resolver
        # ? Loop through dict like {User: UserInp} (name: input_name)
        for typ in self.schemaQueryData:
            args = (
                f"(args: {self.schemaQueryData[typ]})"
                if self.schemaQueryData[typ]  # ? If the `type` defination has inputs
                else ""
            )
            # ? Concat the `QueryResolver` entry
            self.schema += (
                f"\n{config.tab}{prefix}{typ}{args}: {typ}{self.getStrict()}\n"
            )

        self.schema += "}\n"  # ? Complete the `QueryResolver` `type` defination

        # ? Finalizing the schema
        self.schema += (
            "\nschema {\n"
            + f"{config.tab}query: QueryResolver\n{config.tab}mutation: MutationResolver\n"
            + "}\n"
        )


class Analyse(ParseTools):
    def __init__(self):
        super().__init__()

    def analyseEndPoint(self, url, params):
        """
        Getting details about the end point from the config file
        """
        args = []
        keywords = []
        # ? Seperating out the parameters & keywords
        for param in url:
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

        # ? If there're arguments required by `type` interface then passing data to schemaData as {name: nameInp}
        self.schemaQueryData[keywords[0]] = f"{keywords[0]}Inp" if args else False

        # ? Creating input for the parent route
        if args:
            self.parseResponseForInputs(args, name=keywords[0])
            self.inputs += "}\n"

        # ? & Main
        # ? Fetching API
        res = self.getResponse(prepare=(url, params))
        # ? Parsing the response so as to start the generation process
        self.parseResponseForTypes(res, name=keywords[0])
        # ? Completing the types for the pending nested type interfaces that are left during generation of parent types
        for pendingNestObj in self.nestedTypes:
            self.interfaceExists = False
            self.parseResponseForTypes(
                pendingNestObj["data"], name=f"{pendingNestObj['name']}",
            )

        print(f"[MAIN]: \n{'='*40}\n{self.types}\n{'='*40}")


# Exported class
class Tools(Analyse):
    pass
