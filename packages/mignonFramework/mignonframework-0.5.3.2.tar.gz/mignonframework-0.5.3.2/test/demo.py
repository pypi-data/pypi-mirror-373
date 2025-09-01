from mignonFramework import JsonConfigManager,injectJson



configManager = JsonConfigManager()

@injectJson(configManager)
class Data:
    data: bool


data:Data = Data()
data.data = False
print(data.data)