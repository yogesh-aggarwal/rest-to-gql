import config


class GenerateModelJS:
    def __init__(self, tools):
        self.tools = tools
        self.modelFileContent = []

        self.appendFileHeader()
        self.generateModels()

    def appendFileHeader(self):
        header = [
            'const mongoose = require("mongoose");\n',
            "const Schema = mongoose.Schema;\n\n",
        ]
        self.modelFileContent.append("".join(header))

    def appendFileFooter(self, modelName):
        header = [
            f'const {modelName} = mongoose.model("{modelName}", {modelName}Model, {modelName});\n',
            f"export default {modelName};\n",
        ]
        self.modelFileContent.append("".join(header))

    def generateModels(self):
        for model in self.tools.models:
            self.modelFileContent.append(
                f"const {model['name']}Model = new Schema(" + "{\n"
            )
            if model["name"][-1].lower() != "s":
                model["name"] = f'{model["name"]}s'

            for value in model["values"]:
                self.modelFileContent.append(
                    f'{config.tab*1}{value["name"]}: '
                    + "{\n"
                    + f'{config.tab*2}type: {value["type"]},\n'
                    + f"{config.tab*2}reqired: true,\n"
                    + config.tab * 1
                    + "},\n"
                )
            self.modelFileContent.append("});\n\n")
            self.appendFileFooter(modelName=model["name"])
            self.writeModelToFile(modelName=model["name"])

    def writeModelToFile(self, modelName):
        with open(f"{modelName.lower()}s.js", "w+") as f:
            f.writelines(self.modelFileContent)
