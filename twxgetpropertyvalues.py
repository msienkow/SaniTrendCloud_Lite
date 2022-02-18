import requests
import json
import time

start = time.perf_counter()
headers = {'Accept': 'application/json', 'Connection': 'keep-alive', 'Content-Type': 'application/json'}

#properties = ['_IO_EM_AI_01', 'Inches', 'RPI_Value', 'Sim_Value', 'Test_Analog_Real', 'Test_String', 'Volts']

# for property in properties:
#    url = f'http://localhost:8000/Thingworx/Things/test.thing.123/Properties/{property}'
#    response = requests.get(url, headers=headers)
url = f'https://sanimatic-dev.cloud.thingworx.com/Thingworx/Things/test.thing.123/Services/GetPropertyValues'
response = requests.post(url, headers=headers)


Virtual_Tag_Config = []
rows = (response.json())['rows'][0]['PropertyConfig']['rows']
analog = 'ANALOG'
digital = 'DIGITAL'

for dict in rows:
    propertyName = dict['PropertyName']
    nameParts = propertyName.split('_')
    propertyType = nameParts[0]
    propertyNumber = int(nameParts[len(nameParts) - 1]) - 1

    if propertyType.upper() in analog:
        tagNameTag = f'Analog_In_Tags[{propertyNumber}]'
        tagName = dict['TagName'] 
        tagData = (tagNameTag, tagName)
        EUMinTag = f'Analog_In_Min[{propertyNumber}]'
        EUMinVal = dict['EUMin']
        EUMinData = (EUMinTag, EUMinVal)
        EUMaxTag = f'Analog_In_Max[{propertyNumber}]'
        EUMaxVal = dict['EUMax']
        EUMaxData = (EUMaxTag, EUMaxVal)
        UnitsTag = f'Analog_In_Units[{propertyNumber}]'
        UnitsVal = dict['Units']
        UnitsData = (UnitsTag, UnitsVal)
        Virtual_Tag_Config.extend((tagData, EUMinData, EUMaxData, UnitsData))

    if propertyType.upper() in digital:
        tagNameTag = f'Digital_In_Tags[{propertyNumber}]'
        tagName = dict['TagName'] 
        tagData = (tagNameTag, tagName)
        Virtual_Tag_Config.append(tagData)

end = time.perf_counter()

total = end - start
print(Virtual_Tag_Config)
print(f'Total Time = {total} seconds')