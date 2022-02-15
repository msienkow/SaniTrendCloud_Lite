import requests
import json
import time

start = time.perf_counter()
headers = {'Accept': 'application/json', 'Connection': 'keep-alive', 'Content-Type': 'application/json'}

#properties = ['_IO_EM_AI_01', 'Inches', 'RPI_Value', 'Sim_Value', 'Test_Analog_Real', 'Test_String', 'Volts']

# for property in properties:
#    url = f'http://localhost:8000/Thingworx/Things/test.thing.123/Properties/{property}'
#    response = requests.get(url, headers=headers)
url = f'http://localhost:8000/Thingworx/Things/test.thing.123/Services/GetPropertyValues'
response = requests.post(url, headers=headers).json()

print(response['rows'][0]['Volts'])
print(response['rows'][0]['name'])
print(response['rows'][0]['description'])

end = time.perf_counter()

total = end - start

print(f'Total Time = {total} seconds')