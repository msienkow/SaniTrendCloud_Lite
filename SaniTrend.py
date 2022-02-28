import SaniTrendCloud
import time
from pycomm3 import LogixDriver
from pycomm3.exceptions import CommError

def main():
    # Set up SaniTrend parameters, tags, cloud configurations, etc...
    SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")
    # Setup PLC Communication Driver
    PLC = LogixDriver(SaniTrend.PLCIPAddress)
    PLCErrorCount = 0
    runCode = True
    while runCode:
        try:
            # Get Connection Status For EMS
            SaniTrend.ConnectionStatus()
            if PLC.connected:
                PLCErrorCount = 0
                scan_plc = SaniTrend.PLCScanTimerDN()  
                             
                if scan_plc:
                    # Read PLC tags
                    SaniTrend.TagData = PLC.read(*SaniTrend.Tags) 
                    # Store Data to in-memory Log
                    SaniTrend.LogData()
                    
                    # Update Communication Status
                    comms = []
                    watchdog = SaniTrend.GetTagValue(TagName='PLC_Watchdog')
                    watchdog_data = ('SaniTrend_Watchdog', watchdog)
                    twx_data = ('Twx_Alarm', not SaniTrend.isConnected)
                    comms.extend((watchdog_data, twx_data))
                    PLC.write(*comms)
                    
                # Update parameters in PLC from Thingworx values in cloud
                SaniTrend.GetVirtualSetupData()
                if not SaniTrend.ConfigUpdateRunning and SaniTrend.isConnected and SaniTrend.Virtual_Tag_Config:
                    PLC.write(*SaniTrend.Virtual_Tag_Config)

                # Check if pc has reboot request
                reboot = SaniTrend.GetTagValue(TagName='Reboot')
                if reboot:
                    PLC.write('Reboot_Response', 2)
                    runCode = False
                    PLC.close()
                    if not SaniTrend.Logging:
                        time.sleep(2)
                        SaniTrend.RebootPC()
            else:
                PLC.open()
                
            # Send in-memory data to Thingworx
            if len(SaniTrend.TwxDataRows) > 0:
                SaniTrend.SendDataToTwx()
                   
        except CommError:
            PLCErrorCount += 1
            print(f'Communication Error! Fail Count: {PLCErrorCount}')
            SaniTrend.LogErrorToFile('PLC Comms Failed', CommError)
            if PLCErrorCount < 6:
                time.sleep(10)
                PLC = LogixDriver(SaniTrend.PLCIPAddress)
            
            else:
                time.sleep(30)
            PLC = LogixDriver(SaniTrend.PLCIPAddress)
            
        except KeyboardInterrupt:
            print("\n\nExiting Python and closing PLC connection...\n\n\n")
            PLC.close()
            runCode = False
            
        except Exception as error:
            print(f'Critical Error: {error} Restarting Code in 30 Seconds...')
            PLC.close()
            SaniTrend.LogErrorToFile('Final Exception', error)
            time.sleep(30)
            PLC = LogixDriver(SaniTrend.PLCIPAddress)
            # runCode = False
            
if __name__ == "__main__":
    main()