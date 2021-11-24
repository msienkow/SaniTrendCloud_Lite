import SaniTrendCloud
import time
import os
from datetime import datetime
from pycomm3 import LogixDriver
from pycomm3.exceptions import CommError
    
def main():

    # Set up SaniTrend parameters, tags, cloud configurations, etc...
    SaniTrend = SaniTrendCloud.Config(ConfigFile="../SaniTrendConfig.json")

    # Setup PLC Communication Driver
    PLC = LogixDriver(SaniTrend.PLCIPAddress)

    PLCErrorCount = 0
    runCode = True

    while runCode:
        try:
            # Get Connection Status For EMS
            SaniTrend.ConnectionStatus()

            if PLC.connected:
                # Read PLC tags
                tagData = PLC.read(*SaniTrend.Tags)

                print(f'Connection Status = {SaniTrend.isConnected}')
 
                # Reset PLC error count if everything succeeded
                PLCErrorCount = 0
                
            else:
                PLC.open()

            time.sleep(0.5)

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
            
        except:
            print('Shutting Down...')
            PLC.close()
            runCode = False

if __name__ == "__main__":
    main()