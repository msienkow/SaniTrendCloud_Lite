import SaniTrendCloud
import ast
import time

SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")

num_lines = 0



with open("TwxData.log", "r+") as file:
    num_lines = sum(1 for _ in file)
    file.seek(0)
    start_time = time.perf_counter()
    if num_lines < 128:
        twx_data = []
        lines = file.readlines()
        for line in lines:
            data = ast.literal_eval(line.strip())
            for item in data:
                twx_data.append(item)
            
        result = SaniTrend._LogThingworxData(twx_data)
        print(twx_data)
        print(result)

        # for line in file:
        #             data = ast.literal_eval(line.strip())
                
        #         end_time = time.perf_counter()
        # total_time += end_time - start_time
        # print(result)
    
    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f'{total_time} seconds for {num_lines} lines')
