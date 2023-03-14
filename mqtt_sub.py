#global variable
import global_var

#used package
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

global_var.initialize()

#influxDB connect
client = InfluxDBClient(
   url=global_var.influx_url,
   token=global_var.token,
   org=global_var.org,
)

write_api = client.write_api(write_options=SYNCHRONOUS)

#write in interval, bcz monitor collected in 100 HZ = 10 milliseconds
time_change = timedelta(milliseconds = 10)

ecg = []
ppg = []

# 當連線得到回應時，要做的動作
# 將訂閱主題寫在on_connet中,如果我們失去連線或重新連線時,程式將會重新訂閱
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    
    client.subscribe("test/topic")

# 當接收到從伺服器發送的訊息時要進行的動作
# 轉換編碼utf-8才看得懂中文
def on_message(client, userdata, msg):
    saveData(msg.topic, msg.payload.decode('utf-8'))
    
def saveData(topic, data):
    json_object = json.loads(data)
    
    if len(json_object["ecg"]) == len(json_object["ppg"]) == 100:
        time_now = datetime.utcnow()
        for i in range(100):
            
            point = Point("test2") \
                .tag("room", json_object["Room"]) \
                .field("ECG", json_object["ecg"][i]) \
                .field("PPG", json_object["ppg"][i]) \
                .time(time_now)
                
            ecg.append(json_object["ecg"][i])
            ppg.append(json_object["ppg"][i])
            client_response = write_api.write(bucket=global_var.bucket, org=global_var.org, record=point)
            
            time_now = time_now + time_change
            
            """
            if client_response is None:
                # TODO Maybe also return the data that was written
                print("ERROR in :" , json_object["Room"])
            """
    
# 連線設定
# 初始化地端程式 CMD
#mosquitto_sub -t test/topic -v -h (IP of monitor's PI) -p 1883 -u mqtt -P 9079

#打開 server CMD
#mosquitto.exe -c mosquitto.conf -v

client = mqtt.Client()

# 設定連線的動作
client.on_connect = on_connect

# 設定接收訊息的動作
client.on_message = on_message

# 設定登入帳號密碼
client.username_pw_set("mqtt","9079")

# 設定連線資訊(IP, Port, 連線時間)
client.connect("192.168.38.209", 1883, 60)

# 開始連線，執行設定的動作和處理重新連線問題
# 也可以手動使用其他loop函式來進行連接
client.loop_forever()