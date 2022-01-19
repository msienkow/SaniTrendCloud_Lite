from email import message
import SaniTrendCloud
import ast
import time
import math

SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")

count = 0

with open("TwxData.log", "r+") as file:
    lines = file.readlines()
    print(len(lines))
    file.seek(0)
    for line in lines:
        twx_data = []
        message = line.strip()
        data = ast.literal_eval(message)
        
        for item in data:
            twx_data.append(item)
        
        result = SaniTrend._LogThingworxData(twx_data)

        if result == 200:
            count = count + 1
            print(result)

        elif result != 200:
            file.write(line)
            print("failed")