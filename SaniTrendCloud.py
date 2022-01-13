import platform
import json
from pycomm3.exceptions import CommError
import threading
import time
from datetime import datetime
from requests.models import HTTPError
import requests
import os
import dateutil.parser
from influxdb import InfluxDBClient

# Overall Configuration Class to import that has
# auxillary functions necesaary for the cloud
class SaniTrend:
    '''Set up SaniTrend parameters, tags, cloud configurations, etc...'''
    def __init__(self, *, ConfigFile=''):
        
        self.Sim_Value = 30
        
        self.PLCIPAddress = ''
        self.PLCScanRate = 1000
        self.Tags = []
        self.TagData = []
        self.TagTable = []
        self.DataLog = []
        self.TwxDataRows = []
        self.Database = ''
        self.ServerURL = ''
        self.SMINumber = ''
        self.ConnectionStatusTime= 2
        self.isConnected = False
        self._PLC_Last_Scan = 0
        self._ConnectionStatusRunning = False
        self._LastStatusUpdate = 0
        self._ConnectionStatusSession = requests.Session()
        self._ThingworxSession = requests.Session()
        self._TwxTimerSP = 2000
        self._SendingToTwx = False
        self._DatalogTimerSP = 5000
        self._OS = platform.system()
        self._HttpHeaders = {
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.TwxDataShape = {
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
        # Get Configuration Data From JSON File
        self.LoadConfig(ConfigFile=ConfigFile)


    # Read in configuration file and set values on object
    def LoadConfig(self, *, ConfigFile):
        with open(ConfigFile) as file:
            self._configData = json.load(file)
            self.PLCIPAddress = self._configData['Config']['PLCIPAddress']
            self.PLCScanRate = int(self._configData['Config']['PLCScanRate'])
            self.SMINumber = self._configData['Config']['SMINumber']
            self.ServerURL = f'http://localhost:8000/Thingworx/Things/{self.SMINumber}/'
            self._TwxTimerSP = int(self._configData['Config']['TwxTimerSP']) * 0.001
            self.Database = self._configData['Config']['Database']
            self._DatalogTimerSP = int(self._configData['Config']['DatalogTimerSP']) * 0.001
            self.TagTable = self._configData['Tags']
            for dict in self.TagTable:
                self.Tags.append(dict['tag'])

        return self

    def PLCScanTimerDN(self):
        '''Get difference between current ms time and last plc scan ms time and check if it is greater than the setpoint'''
        current_mils = self.GetTimeMS()
        if (current_mils - self._PLC_Last_Scan) > self.PLCScanRate:
            self._PLC_Last_Scan = current_mils
            return True
        else:
            return False


    # Get specific tag value from globally returned tag list from PLC through pycomm3
    def GetTagValue(self, *, TagName=''):
        '''Get specific tag value from globally returned tag list from PLC through pycomm3'''
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
        '''Simple function to get current time in milliseconds. Useful for time comparisons
           ex.  startTime = ObjectName.GetTimeMS()
           endTime = ObjectName.GetTimeMS()
           totalTimeDifferenceInMilliseconds = (endTime - startTime)'''
        return round(time.time() * 1000)


    # Function to check for connection status to Thingworx platform based upon time interval.
    def ConnectionStatus(self):
        '''Check if Thingworx Edge Microserver is connected to Thingworx Cloud Platform. Updates isConnected parameter of class object'''
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


    # In-Memory Data Storage to be sent to Thingworx
    def LogData(self,):
        threading.Thread(target=self._LogData).start()
        
    def _LogData(self,):
        timestamp = self.GetTimeMS()
        for dict in self.TagTable:
            twx_value = {}
            twx_tag = dict['tag']
            twx_basetype = dict['twxtype']
            tag_value = self.GetTagValue(TagName=twx_tag)
            twx_tag_value = round(tag_value, 2) if isinstance(tag_value, float) else tag_value
            twx_value['time'] = timestamp
            twx_value['quality'] = 'GOOD'
            twx_value['name'] = twx_tag
            twx_value['value'] = {
                'value' : twx_tag_value,
                'baseType' : twx_basetype
            }
            self.TwxDataRows.append(twx_value)

        if (timestamp - self._Twx_Last_Write) > self._TwxTimerSP and self.isConnected:
            self._Twx_Last_Write = timestamp
            twx_data = self.TwxDataRows.copy()
            response_code = self.SendToTwx(twx_data)
            self.TwxDataRows = []

    # Wrapper function to send data to Thingworx
    def SendToTwx(self,ThingworxData: list) -> int:
        url = f'{self.ServerURL}Services/UpdatePropertyValues'
        values = {}
        values['rows'] = ThingworxData
        values['dataShape'] = self.TwxDataShape

            try:
                thingworx_json = {
                    'values' : values
                }

                serviceResult = self._ThingworxSession.post(url, headers=self._HttpHeaders, json=thingworx_json, verify=True, timeout=5)
                if serviceResult.status_code == 200:
                    try:
                        pass
                        # self.InfluxClient.write_points(influx_update, database='sanitrend', time_precision='ms', protocol='line')
                        self.TwxDataRows = []
                    except Exception as e:
                        pass
                        # self.LogErrorToFile('Update Influx Data Failed!', 'Change me to "e" to gather exception.')
                else:
                    self.LogErrorToFile('_SendToTwx', serviceResult)

            except Exception as e:
                self.LogErrorToFile('_SendToTwx', e)
                      
        except Exception as e:
                self.LogErrorToFile('_SendToTwx', e)

    def LogErrorToFile(self, name, error):
        errorTopDirectory = f'../STCErrorLogs'
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

        month = f'_{currentDateTime.month}' if currentDateTime.month > 9 else f'_0{currentDateTime.month}'
        day = f'_{currentDateTime.day}' if currentDateTime.day > 9 else f'_0{currentDateTime.day}'
        errorLog = f'STC_Errors_{datetime.now().year}{month}{day}.log'
        writePath = os.path.join(errorMonthDirectory, errorLog)
        mode = 'a+' if os.path.exists(writePath) else 'w+'
        with open(writePath, mode) as f:
            f.write(f'{currentDateTime},{name},{error}\n')
            print(f'{currentDateTime},{name},{error}\n')