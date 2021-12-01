import SaniTrendCloud
import time
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
                SaniTrend.TagData = PLC.read(*SaniTrend.Tags)
                SaniTrend.LogData()
                PLCErrorCount = 0

            else:
                PLC.open()

            # result = client.query('select * from data where SentToTwx = false')
            # results = list(result)
            # results = []
            # print(results)
            time.sleep(SaniTrend.PLCScanRate * 0.001)
            # json_payload2 = []

            # for row in results:
            #     for dict in row:
            #         data = {
            #                 "measurement" : "data",
            #                 "tags" : {},
            #                 "time" : 0,
            #                 "fields" : {}
            #                 }

            #         fields = {}
            #         for key,value in dict.items():
            #             if key != 'time' and key != 'SentToTwx':
            #                 fields[key] = value
            #             elif key == 'time':
            #                 data[key] = value
            #             elif key == 'SentToTwx':
            #                 fields[key] = True
            #         data['fields'] = fields
            #         json_payload2.append(data)

            # # client.write_points(json_payload2)
            # print(json_payload2)

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
            runCode = False

if __name__ == "__main__":
    main()