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

                # Update parameters in PLC from Thingworx values in cloud
                if not SaniTrend.ConfigUpdateRunning and SaniTrend.isConnected and SaniTrend.Virtual_Tag_Config:
                    PLC.write(SaniTrend.Virtual_Tag_Config)
                    
            else:
                PLC.open()

            # Send in-memory data to Thingworx
            if (SaniTrend.TwxDataRows) > 1:
                SaniTrend.SendDataToTwx()
                   
        except CommError:
            PLCErrorCount += 1
            print(f'Communication Error! Fail Count: {PLCErrorCount}')
            SaniTrend.LogErrorToFile('PLC Comms Failed', CommError)
            if PLCErrorCount < 6:
                time.sleep(10)
            else:
                time.sleep(30)
            PLC = LogixDriver(SaniTrend.PLCIPAddress)

        except KeyboardInterrupt:
            print("\n\nExiting Python and closing PLC connection...\n\n\n")
            PLC.close()
            runCode = False

        except Exception as error:
            print(error)
            print('Shutting Down...')
            PLC.close()
            SaniTrend.LogErrorToFile('Final Exception', error)
            # runCode = False

if __name__ == "__main__":
    main()