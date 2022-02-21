import SaniTrendCloud
import time
from pycomm3 import LogixDriver
from pycomm3.exceptions import CommError

def main():
    # Set up SaniTrend parameters, tags, cloud configurations, etc...
    SaniTrend = SaniTrendCloud.SaniTrend(ConfigFile="../SaniTrendConfig.json")
    
    PLCErrorCount = 0
    
    runCode = True

    while runCode:
        try:
            with LogixDriver(SaniTrend.PLCIPAddress) as PLC:
                # Get Connection Status For EMS
                SaniTrend.ConnectionStatus()
            
                # Send in-memory data to Thingworx
                if len(SaniTrend.TwxDataRows) > 0:
                    SaniTrend.SendDataToTwx()
                    
                connected = PLC.connected
                
                # Code to be run only while a connection to the PLC exists
                while connected:
                    connected = PLC.connected
                    PLCErrorCount = 0
                    scan_plc = SaniTrend.PLCScanTimerDN()               
                    if scan_plc:
                        # Read PLC tags
                        SaniTrend.TagData = PLC.read(*SaniTrend.Tags)
                        
                        # Store Data to in-memory Log
                        SaniTrend.LogData()

                        # Update SaniTrend Watchdog Bit
                        PLC.write('SaniTrend_Watchdog', SaniTrend.GetTagValue(TagName='PLC_Watchdog'))

                    # Update parameters in PLC from Thingworx values in cloud
                    SaniTrend.GetVirtualSetupData()
                    if not SaniTrend.ConfigUpdateRunning and SaniTrend.isConnected and SaniTrend.Virtual_Tag_Config:
                        PLC.write(*SaniTrend.Virtual_Tag_Config)
                    
                    # Check if pc has reboot request
                    reboot = SaniTrend.GetTagValue(TagName='Reboot')
                    if reboot:
                        PLC.write('Reboot_Response', 2)
                        runCode = False
                        if not SaniTrend.Logging:
                            time.sleep(2)
                            SaniTrend.RebootPC()

            
                   
        except CommError:
            PLCErrorCount += 1
            print(f'Communication Error! Fail Count: {PLCErrorCount}')
            SaniTrend.LogErrorToFile('PLC Comms Failed', CommError)
            if PLCErrorCount < 6:
                time.sleep(10)
            else:
                time.sleep(30)

        except KeyboardInterrupt:
            print("\n\nExiting Python and closing PLC connection...\n\n\n")
            runCode = False

        except Exception as error:
            print(error)
            print('Final Exception. Restarting Code in 30 seconds...')
            SaniTrend.LogErrorToFile('Final Exception', error)
            time.sleep(30)
            # runCode = False

if __name__ == "__main__":
    main()