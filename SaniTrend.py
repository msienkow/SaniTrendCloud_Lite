import SaniTrendCloud
import time
import os
from datetime import datetime
from pycomm3 import LogixDriver
from pycomm3.exceptions import CommError


def main():

    # Setup Influx Connection
    # client = InfluxDBClient('localhost', 8086, 'sanitrend', 'Tunn3lwa5h', 'sanitrend')
    # client.switch_database('sanitrend')

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

            # Database Paylod
            json_payload = []

            if PLC.connected:
                # Read PLC tags
                tagData = PLC.read(*SaniTrend.Tags)
                inches = round(SaniTrend.GetTagValue(TagData=tagData, TagName='Inches'), 2)
                volts = round(SaniTrend.GetTagValue(TagData=tagData, TagName='Volts'), 2)
                print(f'Connection Status = {SaniTrend.isConnected} inches value = {inches}')

                data = {
                         "measurement" : "data",
                         "tags": {},
                         "time" :datetime.now(),
                         "fields" : {
                             "SentToTwx" : False,
                             "Inches" : inches,
                             "Volts" : volts
                             }
                         }
                json_payload.append(data)

                # # Send Data to InFlux DB
                # client.write_points(json_payload)

                # Reset PLC error count if everything succeeded
                PLCErrorCount = 0

            else:
                PLC.open()

            # result = client.query('select * from data where SentToTwx = false')
            # results = list(result)
            results = []
            print(results)
            time.sleep(5)
            json_payload2 = []

            for row in results:
                for dict in row:
                    data = {
                            "measurement" : "data",
                            "tags" : {},
                            "time" : 0,
                            "fields" : {}
                            }

                    fields = {}
                    for key,value in dict.items():
                        if key != 'time' and key != 'SentToTwx':
                            fields[key] = value
                        elif key == 'time':
                            data[key] = value
                        elif key == 'SentToTwx':
                            fields[key] = True
                    data['fields'] = fields
                    json_payload2.append(data)

            # client.write_points(json_payload2)
            print(json_payload2)

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
            runCode = False

if __name__ == "__main__":
    main()