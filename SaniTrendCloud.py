import platform
import json
from pycomm3.exceptions import CommError
import threading
import time
from datetime import datetime
from requests.models import HTTPError
import requests
import os
import math
import sqlite3

# Overall Configuration Class to import that has
# auxillary functions necesaary for the cloud
class SaniTrend:
    '''Set up SaniTrend parameters, tags, cloud configurations, etc...'''
    def __init__(self, *, ConfigFile=''):
        # SaniTrend Lite Specific Properties
        self.db = os.path.join(os.path.dirname(__file__), 'stc.db')
        self.Logging = False
        self.TagData = []
        self.TagTable = []
        self.TwxDataRows = []
        self.PLC_IPAddress = ''
        self.PLC_Path = ''
        self.Virtual_AIn_Tag = ''
        self.Virtual_DIn_Tag = ''
        self.Virtual_String_Tag = ''
        self.Virtualize_AIn = 0
        self.Virtualize_DIn = 0
        self.Virtualize_String = 0
        self.Virtual_Tag_Config = []

        # Universal Properties
        self.PLCIPAddress = ''
        self.PLCScanRate = 1000
        self.Tags = []
        self.ServerURL = ''
        self.ServerSeconds = 0
        self.SMINumber = ''
        self.ConnectionStatusTime = 2
        self.isConnected = False
        self._PLC_Last_Scan = 0
        self._ConnectionStatusRunning = False
        self.ConfigUpdateRunning = False
        self._LastStatusUpdate = 0
        self._LastConfigUpdate = 0
        self._ConnectionStatusSession = requests.Session()
        self._ThingworxSession = requests.Session()
        self._ConfigSession = requests.Session()
        self._ServerStatusSession = requests.Session()
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
            self.TagTable = self._configData['Tags']
            for dict in self.TagTable:
                self.Tags.append(dict['tag'])

        return self

    def GetVirtualSetupData(self,):
        '''Get Data Configuration for Property Values (Min/Max/Units/Tagname)'''
        timerPreset = 10000
        currentMS = self.GetTimeMS()
        if currentMS - self._LastConfigUpdate >= timerPreset and not self.ConfigUpdateRunning and self.isConnected:
            self.ConfigUpdateRunning = True
            self._LastConfigUpdate = currentMS
            threading.Thread(target=self._GetVirtualSetupData).start()
        return None
        

    def _GetVirtualSetupData(self,):
        '''Threaded method for getting property value configuration.'''
        url = f'{self.ServerURL}Services/GetPropertyValues'
        try:
            serviceResult = self._ConfigSession.post(url, headers=self._HttpHeaders, timeout=None)
            if serviceResult.status_code == 200:
                self.Virtual_Tag_Config = []
                result = serviceResult.json()['rows'][0]
                rows = result['PropertyConfig']['rows']
                analog = 'ANALOG'
                digital = 'DIGITAL'
                
                for props in rows:
                    PropertyName = ''
                    TagName = ''
                    EUMin = 0
                    EUMax = 1
                    EUUnits = ''
                    
                    for key,value in props.items():
                        if key == 'PropertyName':
                            PropertyName = value
                        if key == 'TagName':
                            TagName = value
                        if key == 'EUMin':
                            EUMin = value
                            if EUMin == '':
                                EUMin = 0
                        if key == 'EUMax':
                            EUMax = value
                            if EUMax == '':
                                EUMax = 1
                        if key == 'Units':
                            EUUnits = value
                    
                    nameParts = PropertyName.split('_')
                    propertyType = nameParts[0]
                    propertyNumber = int(nameParts[len(nameParts) - 1]) - 1
                
                    if propertyType.upper() in analog:
                        TagNameTag = f'Analog_In_Tags[{propertyNumber}]'
                        TagData = (TagNameTag, TagName)
                        EUMinTag = f'Analog_In_Min[{propertyNumber}]'
                        EUMinData = (EUMinTag, EUMin)
                        EUMaxTag = f'Analog_In_Max[{propertyNumber}]'
                        EUMaxData = (EUMaxTag, EUMax)
                        UnitsTag = f'Analog_In_Units[{propertyNumber}]'
                        UnitsData = (UnitsTag, EUUnits)
                        self.Virtual_Tag_Config.extend((TagData, EUMinData, EUMaxData, UnitsData))

                    if propertyType.upper() in digital:
                        TagNameTag = f'Digital_In_Tags[{propertyNumber}]' 
                        TagData = (TagNameTag, TagName)
                        self.Virtual_Tag_Config.append(TagData)
                        
                self.PLC_IPAddress = result['PLC_IPAddress']
                self.PLC_Path = result['PLC_Path']
                self.Virtual_AIn_Tag = result['Virtual_AIn_Tag']
                self.Virtual_DIn_Tag = result['Virtual_DIn_Tag']
                self.Virtual_String_Tag = result['Virtual_String_Tag']
                self.Virtualize_AIn = result['Virtualize_AIn']
                self.Virtualize_DIn = result['Virtualize_DIn']
                self.Virtualize_String = result['Virtualize_String']
                
                self.Virtual_Tag_Config.append(('PLC_IPAddress', self.PLC_IPAddress))
                self.Virtual_Tag_Config.append(('PLC_Path', self.PLC_Path))
                self.Virtual_Tag_Config.append(('Virtual_AIn_Tag', self.Virtual_AIn_Tag))
                self.Virtual_Tag_Config.append(('Virtual_DIn_Tag', self.Virtual_DIn_Tag))
                self.Virtual_Tag_Config.append(('Virtual_String_Tag', self.Virtual_String_Tag))
                self.Virtual_Tag_Config.append(('Virtualize_AIn', self.Virtualize_AIn))
                self.Virtual_Tag_Config.append(('Virtualize_DIn', self.Virtualize_DIn))
                self.Virtual_Tag_Config.append(('Virtualize_String', self.Virtualize_String))
                
                
        except Exception as e:
            self.LogErrorToFile('_GetVirtualSetupData', e)

        # Release Bit so code can run again
        self.ConfigUpdateRunning = False

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
        '''Simple function to get current time in milliseconds. Useful for time comparisons\n
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

        return None

    #Run REST request against EMS to see if it is connected to the Thingworx platform
    def _ConnectionStatus(self,):
        url = 'http://localhost:8000/Thingworx/Things/LocalEms/Properties/isConnected'
        try:
            serviceResult = self._ConnectionStatusSession.get(url, headers=self._HttpHeaders, timeout=None)
            if serviceResult.status_code == 200:
                self.isConnected = (serviceResult.json())['rows'][0]['isConnected']
                
            else:
                self.LogErrorToFile('_ConnectionStatus', serviceResult)
                self.isConnected = False
        
        except Exception as e:
            self.isConnected = False
            self._LastStatusUpdate = self.GetTimeMS() + 30000
            self.LogErrorToFile('_ConnectionStatus', e)

        # Release Bit so watchdog can run again
        self._ConnectionStatusRunning = False


    # In-Memory Data Storage to be sent to Thingworx
    def LogData(self,):
        timestamp = self.GetTimeMS()
        for dict in self.TagTable:
            twx_value = {}
            twx_tag = dict['tag']
            twx_basetype = dict['twxtype']
            ignore_type = 'ignore'
            
            if twx_basetype.lower() != ignore_type:
                tag_value = self.GetTagValue(TagName=twx_tag)
                twx_tag_value = round(tag_value, 2) if isinstance(tag_value, float) else tag_value
                twx_value['time'] = timestamp
                twx_value['quality'] = 'GOOD'
                twx_value['name'] = twx_tag
                
                if (twx_basetype == 'NUMBER' and math.isinf(twx_tag_value)):
                    twx_tag_value = -9999
                    twx_value['quality'] = 'BAD'
     
                twx_value['value'] = {
                    'value' : twx_tag_value,
                    'baseType' : twx_basetype
                }

                self.TwxDataRows.append(twx_value)
        

    # Wrapper function to send data to Thingworx
    def SendDataToTwx(self,):
        if not self.Logging:
            twx_data = self.TwxDataRows.copy()
            self.TwxDataRows = []

            if self.isConnected:
                threading.Thread(target=self._SendDataToTwx, args=(twx_data,)).start()
            
            elif not self.isConnected:
                self.Logging = True
                threading.Thread(target=self.LogTwxDataToDB, args=(twx_data,)).start()

        return None

    # Function to send data to Thingworx
    def _SendDataToTwx(self, ThingworxData: list):
        response = self._SendTwxData(ThingworxData)
        if response == 200:
            try:
                self.Logging = True
                select_query = '''select ROWID,TwxData,SentToTwx from sanitrend where SentToTwx = false LIMIT 32'''
                delete_ids = []
                SQLThingworxData = []

                with sqlite3.connect(database=self.db) as db:
                    cur = db.cursor()  
                    cur.execute(''' CREATE TABLE if not exists sanitrend (TwxData text, SentToTwx integer) ''')
                    cur.execute(select_query)  
                    records = cur.fetchall()
                
                    for row in records:
                        delete_ids.append(row[0])
                        twx_data = json.loads(row[1])
                
                        for dict in twx_data:
                            SQLThingworxData.append(dict)
                    
                    logged_data_response = self._SendTwxData(SQLThingworxData)
                    if logged_data_response == 200:
                        delete_query = ''' DELETE FROM sanitrend where ROWID=? '''
                        for id in delete_ids:
                            cur.execute(delete_query, (id,))
                        db.commit()  

            except Exception as e:
                self.LogErrorToFile('_SendDataToTwx', e)
            
            self.Logging = False

        elif response != 200:
            self.Logging = True
            self.LogTwxDataToDB(ThingworxData)
        
        return None

    # Function to send data to Thingworx
    def _SendTwxData(self,ThingworxData: list) -> int:
        url = f'{self.ServerURL}Services/UpdatePropertyValues'
        values = {}
        values['rows'] = ThingworxData
        values['dataShape'] = self.TwxDataShape
        thingworx_json = {
            'values' : values
        }
        status_code = 0
        
        try:
            http_response = self._ThingworxSession.post(url, headers=self._HttpHeaders, json=thingworx_json, timeout=None)
            if http_response.status_code == 200:
               status_code = http_response.status_code

            else:
                self.LogErrorToFile('_SendTwxData', http_response)
                status_code =  http_response.status_code

        except Exception as e:
            self.LogErrorToFile('_SendToTwx', e)
        
        return status_code


    # Log Thingworx message to SQLite database
    def LogTwxDataToDB(self, ThingworxData: list):
        try:
            with sqlite3.connect(database=self.db) as db:
                cur = db.cursor()  
                cur.execute(''' CREATE TABLE if not exists sanitrend (TwxData text, SentToTwx integer) ''')   
                records = []     
                sql_as_text = ''
                insert_query = ''' INSERT INTO sanitrend (TwxData, SentToTwx) VALUES (?,?); '''
                sql_as_text = json.dumps(ThingworxData)
                records.append((sql_as_text, False)) 
                cur.executemany(insert_query, records)
                db.commit()      

        except Exception as e:
            self.LogErrorToFile('LogTwxDataToDB', e)

        self.Logging = False

    def RebootPC(self,):
        platform = self._OS.lower()
        if platform == 'windows':
            os.system('shutdown /r /t 1')
        elif platform == 'linux':
            os.system('sudo reboot')

    def LogErrorToFile(self, name, error):
        errorTopDirectory = f'STCErrorLogs'
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