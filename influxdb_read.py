import global_var
from influxdb_client import InfluxDBClient
import time

global_var.initialize()

client = InfluxDBClient(
   url=global_var.influx_url,
   token=global_var.token,
   org=global_var.org,
)

# Query script
query_api = client.query_api()

query = 'from(bucket:"mqtt_test")\
|> range(start:2023-01-30T08:11:45.000Z,stop:2023-01-30T08:11:46.000Z)\
|> filter(fn:(r) => r._measurement == "test2")\
|> filter(fn:(r) => r.room == "1")\
|> filter(fn:(r) => r._field == "ECG" or r._field == "PPG")\
|> aggregateWindow(every: 10ms, fn: mean)'

start = time.monotonic()
result = query_api.query(org=global_var.org, query=query)

delta = time.monotonic() - start
print("time : ", delta)

results = []
for table in result:
    for record in table.records:
        results.append((record.get_field(), record.get_value()))

print(results)

#