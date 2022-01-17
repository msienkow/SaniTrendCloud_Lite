import SaniTrendCloud
import ast
import time

SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")

num_lines = 0



with open("TwxData.log", "r") as file:
    num_lines = sum(1 for _ in file)
    file.seek(0)
    total_time = 0
    for line in file:
        start_time = time.perf_counter()
        data = ast.literal_eval(line.strip())

        result = SaniTrend._LogThingworxData(data)
        end_time = time.perf_counter()
        total_time += end_time - start_time
        print(result)
    
    avg_time = total_time / num_lines
    print(avg_time)
