import platform
import json
from pycomm3.exceptions import CommError
import threading
import time
from datetime import datetime
from requests.models import HTTPError
import requests
import os
from ftplib import FTP
import shutil

# Overall Configuration Class to import that has 
# auxillary functions necesaary for the cloud
class Config:
    def __init__(self, *, ConfigFile=''):
        self.PLCIPAddress = ''
        self.Tags = []
        self.ServerURL = ''
        self.SMINumber = ''
        self.ConnectionStatusTime= 10
        self.isConnected = False
        self._ConnectionStatusRunning = False
        self._LastStatusUpdate = 0
        self._ConnectionStatusSession = requests.Session()
        self._OS = platform.system()
        self.LoadConfig(ConfigFile=ConfigFile)
        self._HttpHeaders = {
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        

    # Read in configuration file and set values on object
    def LoadConfig(self, *, ConfigFile):
        with open(ConfigFile) as file:
            self._configData = json.load(file)
            self.PLCIPAddress = self._configData['Config']['PLCIPAddress']            
            self.SMINumber = self._configData['Config']['SMINumber']
            self.ServerURL = f'http://localhost:8000/Thingworx/{self.SMINumber}/'
            self.Tags = self._configData['Tags']
        return self._configData

    # Get specific tag value from globally returned tag list from PLC through pycomm3
    def GetTagValue(self, *, TagData=[], TagName=''):
        if TagData and TagName:
            result = [item.value for item in TagData if item[0] == TagName]
            return result[0]
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