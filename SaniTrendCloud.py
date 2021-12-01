import platform
import json
from pycomm3.exceptions import CommError
import threading
import time
from datetime import datetime
from requests.models import HTTPError
import requests
import os
from influxdb import InfluxDBClient, resultset

# Overall Configuration Class to import that has
# auxillary functions necesaary for the cloud
class Config:
    def __init__(self, *, ConfigFile=''):
        self.PLCIPAddress = ''
        self.PLCScanRate = 1000
        self.Tags = []
        self.TagData = []
        self.TagTable = []
        self.ServerURL = ''
        self.SMINumber = ''
        self.ConnectionStatusTime= 10
        self.isConnected = False
        self._ConnectionStatusRunning = False
        self._LastStatusUpdate = 0
        self._ConnectionStatusSession = requests.Session()
        self._ThingworxSession = requests.Session()
        self._OS = platform.system()
        self._Influx_Last_Write = time.perf_counter()  
        self._Influx_Log_Buffer = []
        self._InfluxDB = ""
        self._InfluxPort = 0
        self._InfluxUser = ""
        self._InfluxPW = ""
        self.InfluxClient = {}
        self._InfluxTimerSP  = 1
        self._TwxTimerSP = 2
        self._Twx_Last_Write = time.perf_counter()
        self._HttpHeaders = {
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.LoadConfig(ConfigFile=ConfigFile)



    # Read in configuration file and set values on object
    def LoadConfig(self, *, ConfigFile):
        with open(ConfigFile) as file:
            self._configData = json.load(file)
            self.PLCIPAddress = self._configData['Config']['PLCIPAddress']
            self.PLCScanRate = int(self._configData['Config']['PLCScanRate'])
            self.SMINumber = self._configData['Config']['SMINumber']
            self.ServerURL = f'http://localhost:8000/Thingworx/Things/{self.SMINumber}/'
            self._InfluxDB = self._configData['Config']['InfluxDB']
            self._InfluxPort = int(self._configData['Config']['InfluxPort'])
            self._InfluxUser = self._configData['Config']['InfluxUser']
            self._InfluxPW = self._configData['Config']['InfluxPW']
            self._InfluxTimerSP  = int(self._configData['Config']['InfluxTimerSP']) * 0.001
            self._TwxTimerSP = int(self._configData['Config']['TwxTimerSP']) * 0.001
            
            self.InfluxClient = InfluxDBClient('localhost', self._InfluxPort, self._InfluxUser, self._InfluxPW, self._InfluxDB)
            self.InfluxClient.switch_database(self._InfluxDB)
            self.TagTable = self._configData['Tags']
            for dict in self.TagTable:
                self.Tags.append(dict['tag'])

        return self

    # Get specific tag value from globally returned tag list from PLC through pycomm3
    def GetTagValue(self, *, TagName=''):
        if self.TagData and TagName:
            values = (item.value for item in self.TagData if item[0] == TagName)
            for i in values:
                return i
        else:
            return None

    # Simple function to get current time in milliseconds. Useful for time comparisons
    # ex.  startTime = ObjectName.GetTimeMS()
    #      endTime = ObjectName.GetTimeMS()
    #      totalTimeDifferenceInMilliseconds = (endTime - startTime)
    def GetTimeMS(self,):
        return round(time.time() * 1000)


    # Function to check for connection status to Thingworx platform based upon time interval.
    def ConnectionStatus(self):
        timerPreset = self.ConnectionStatusTime * 1000
        if (((self.GetTimeMS() - self._LastStatusUpdate) >= timerPreset) and not self._ConnectionStatusRunning):
            self._ConnectionStatusRunning = True
            self._LastStatusUpdate = self.GetTimeMS()
            threading.Thread(target=self._ConnectionStatus).start()

    #Run REST request against EMS to see if it is connected to the Thingworx platform
    def _ConnectionStatus(self,):
        url = 'http://localhost:8000/Thingworx/Things/LocalEms/Properties/isConnected'
        try:
            serviceResult = self._ConnectionStatusSession.get(url, headers=self._HttpHeaders, timeout=5)
            if serviceResult.status_code == 200:
                self.isConnected = (serviceResult.json())['rows'][0]['isConnected']

            else:
                self.LogErrorToFile('_ConnectionStatus', serviceResult)
                self.isConnected = False

        except Exception as e:
            self.isConnected = False
            self.LogErrorToFile('_ConnectionStatus', e)

        # Release Bit so watchdog can run again
        self._ConnectionStatusRunning = False


    # Wrapper function to call influx db data logging in a thread
    def LogData(self,):
        threading.Thread(target=self._LogData).start()
    
    # Influx DB Data Logging
    def _LogData(self,):
        fields = {}
        data = {
            "measurement": "data",
            "tags" : {},
            "time" : datetime.now(),
            "fields" : {}
        }

        for dict in self.TagTable:
            tag = dict['tag']
            tagValue = self.GetTagValue(TagName=tag)
            value = round(tagValue, 2) if isinstance(tagValue, float) else tagValue
            fields[tag] = value
        fields['SentToTwx'] = False

        data['fields'] = fields
        self._Influx_Log_Buffer.append(data)

        influx_elapsed_time = time.perf_counter() - self._Influx_Last_Write
        if influx_elapsed_time > self._InfluxTimerSP: 
            self._Influx_Last_Write = time.perf_counter() 
            self.InfluxClient.write_points(self._Influx_Log_Buffer)
            # print(f'Logged the folowing data to influx {self._Influx_Log_Buffer}')
            self._Influx_Log_Buffer = []

        twx_elapsed_time = time.perf_counter() - self._Twx_Last_Write
        if twx_elapsed_time > self._TwxTimerSP:
            threading.Thread(target=self._SendToTwx).start()
            self._Twx_Last_Write = time.perf_counter()

    # Query Influx database and send unsent data to Thingworx
    def _SendToTwx(self,):
        json_payload = []
        query = self.InfluxClient.query('select * from data where SentToTwx = false')

        if query:
            url = f'{self.ServerURL}Services/UpdatePropertyValues'
            values = {}
            rows = []
            dataShape = {
                'fieldDefinitions': {
                    'name': {
                        'name': 'name',
                        'aspects': {
                            'isPrimaryKey': True
                        },
                    'description': 'Property name',
                    'baseType': 'STRING',
                    'ordinal': 0
                    },
                    'time': {
                        'name': 'time',
                        'aspects': {},
                        'description': 'time',
                        'baseType': 'DATETIME',
                        'ordinal': 0
                    },
                    'value': {
                        'name': 'value',
                        'aspects': {},
                        'description': 'value',
                        'baseType': 'VARIANT',
                        'ordinal': 0
                    },
                    'quality': {
                        'name': 'quality',
                        'aspects': {},
                        'description': 'quality',
                        'baseType': 'STRING',
                        'ordinal': 0
                    }
                }
            }

            for row in query:
                for dict in row:
                    timestamp = dict['time'] 
                    data = {
                        "measurement" : "data",
                        "tags" : {},
                        "time" : timestamp,
                        "fields" : {}
                    }

                    fields = {}
                    twx_data = {}
                    for key,value in dict.items():
                        twxvalue = {}
                        twxvalue['time'] = timestamp
                        twxvalue['quality'] = 'GOOD'
                        if key != 'time' and key != 'SentToTwx':
                            fields[key] = value
                            twxvalue['name'] = key
                            twxtypes = (item['twxtype'] for item in self.TagTable if item['tag'] == key)
                            for i in twxtypes:
                                baseType = i
                            twxvalue['value'] = {
                                'value' : value,
                                'baseType' : baseType
                            }
                            rows.append(twxvalue)
                        elif key == 'SentToTwx':
                            fields[key] = True
                    data['fields'] = fields
                    json_payload.append(data)

                values['rows'] = rows
                values['dataShape'] = dataShape

            try:
                thingworx_json = {
                    'values' : values
                }
                self.LogErrorToFile('thingworx', json.dumps(thingworx_json))
                serviceResult = self._ThingworxSession.post(url, headers=self._HttpHeaders, json=thingworx_json, verify=True, timeout=5)
                if serviceResult.status_code == 200:
                    self.InfluxClient.write_points(json_payload)
                else:
                    self.LogErrorToFile('_SendToTwx', serviceResult)

            except Exception as e:
                self.isConnected = False
                self.LogErrorToFile('_SendToTwx', e)  

    def LogErrorToFile(self, name, error):
        errorTopDirectory = f'../ErrorLogs'
        currentDateTime = datetime.now()
        errorYear = str(currentDateTime.year)
        errorYearDirectory  = os.path.join(errorTopDirectory, errorYear)
        errorMonth = currentDateTime.strftime('%B')
        errorMonthDirectory = os.path.join(errorYearDirectory, errorMonth)
        directories = [errorTopDirectory, errorYearDirectory, errorMonthDirectory]
        # Try to create directories, if they exists move on
        for directory in directories:
            try:
                os.mkdir(directory)
            except:
                pass

        day = currentDateTime.day if currentDateTime.day < 10 else f'0{currentDateTime.day}'
        month = currentDateTime.month if currentDateTime.month < 10 else f'0{currentDateTime.month}'
        errorLog = f'STC_Errors_{datetime.now().year}{month}{day}.log'
        writePath = os.path.join(errorMonthDirectory, errorLog)
        mode = 'a+' if os.path.exists(writePath) else 'w+'
        with open(writePath, mode) as f:
            f.write(f'{currentDateTime},{name},{error}\n')
            print(f'{currentDateTime},{name},{error}\n')