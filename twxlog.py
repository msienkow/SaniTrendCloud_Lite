import SaniTrendCloud
import ast

SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")

with open("TwxData.log", "r") as file:
    for line in file:
        data = ast.literal_eval(line.strip())

        result = SaniTrend._LogThingworxData(data)
        print(result)
