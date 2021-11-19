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
        self._AppKey = ''
        self._OS = platform.system()
        self.LoadConfig(ConfigFile=ConfigFile)
        self._HttpHeaders = {
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'appKey': self._AppKey
        }
        

    # Read in configuration file and set values on object
    def LoadConfig(self, *, ConfigFile):
        with open(ConfigFile) as file:
            self._configData = json.load(file)
            self.PLCIPAddress = self._configData['Config']['PLCIPAddress']
            self.ServerURL = self._configData['Config']['ServerURL']
            self.SMINumber = self._configData['Config']['SMINumber']
            self._AppKey = self._configData['Config']['AppKey']
            self.Tags = self._configData['Tags']
        return self._configData

    # Get specific tag value from globally returned tag list from PLC through pycomm3
    def GetTagValue(self, *, TagData=[], TagName=''):
        if TagData and TagName:
            result = [item.value for item in TagData if item[0] == TagName]
            return result[0]
        else:
            return None

    # Simpe function to get current time in milliseconds. Useful for time comparisons
    # ex.  startTime = ObjectName.GetTimeMS()
    #      endTime = ObjectName.GetTimeMS()
    #      totalTimeDifferenceInMilliseconds = (endTime - startTime)
    def GetTimeMS(self,):
        return round(time.time() * 1000)

    # Run RESTApi POST service to get current server time seconds
    # Using number value more accurate than just boolean on/off
    def _CloudWatchdog(self,):
        url = self.ServerURL + 'Things/Connection_Test/Services/ConnectionTest'
        try:
            serviceResult = self._CloudWatchdogSession.post(url, headers=self._CloudWatchdogHeaders, timeout=5)
            if serviceResult.status_code == 200:
                self.CloudWatchdogValue = (serviceResult.json())['rows'][0]['result']
                
            else:
                self.LogErrorToFile('_CloudWatchdog', serviceResult)
                self.CloudWatchdogValue = 0

        except Exception as e:
            self.CloudWatchdogValue = 0
            self.LogErrorToFile('_CloudWatchdog', e)
            
        # Release Bit so watchdog can run again
        self._CloudWatchdogRunning = False


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