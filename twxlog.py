import SaniTrendCloud
import ast
import time

SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")

num_lines = 0



with open("TwxData.log", "r+") as file:
    num_lines = sum(1 for _ in file)
    file.seek(0)
    start_time = time.perf_counter()
    if num_lines < 64:
        twx_data = []
        lines = file.readlines()
        for line in lines:
            data = ast.literal_eval(line.strip())
            for item in data:
                twx_data.append(item)
            
        result = SaniTrend._LogThingworxData(twx_data)
        
        print(result)
        if result == 200:
            file.seek(0)
            for _ in file:
                file.write("")
            file.truncate()
    else:
        twx_data = []
        for _ in range(64):
            log_entry = file.readline().strip()
            for dict in log_entry:
                twx_data.append(dict)

        result = SaniTrend._LogThingworxData(twx_data)
        print(result)
        if result == 200:
            file.seek(0)
            for _ in range(64):
                file.write("")
            file.truncate()

    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f'{total_time} seconds for 64 lines')
