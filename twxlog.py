import SaniTrendCloud
import ast
import time
import math

SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")

num_lines = 0



with open("TwxData.log", "r+") as file:
    clear_file = True
    for _ in file:
        twx_data = []
        line = file.readline()
        if line != "\n":
            data = ast.literal_eval(line.strip())
            
            for item in data:
                twx_data.append(item)
            
            result = SaniTrend._LogThingworxData(twx_data)
            if result == 200:
                file.write("\n")
                print(result)

            elif result != 200 and clear_file:
                clear_file = False
    
    if clear_file:
        file.truncate(0)