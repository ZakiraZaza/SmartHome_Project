import time
import json
import random
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Konfiguracija
ENDPOINT = "a16zv792co800v-ats.iot.eu-central-1.amazonaws.com"
CLIENT_ID = "TempSensor_01"
PATH_TO_CERT = "certificate.pem.crt"
PATH_TO_KEY = "private.pem.key"
PATH_TO_ROOT = "AmazonRootCA.pem"
TOPIC_PUB = "home/sensors/temp"

# MQTT konekcija
print("Inicijalizacija senzora...")
myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myMQTTClient.configureEndpoint(ENDPOINT, 8883)
myMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

# Podesavanje parametara konekcije
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

# Povezivanje na AWS
print("Povezivanje na AWS IoT Core...")
try:
    myMQTTClient.connect()
    print("USPJESNO POVEZANO!")
except Exception as e:
    print(f"Greska pri povezivanju: {e}")
    exit()

# Glavna petlja i slanje podataka
while True:
    # Simulirana random temperatura izmedju 20 i 30 stepeni
    temp_value = round(random.uniform(20.0, 30.0), 2)
    
    # Kreira se poruka u JSON formatu
    message = {
        "device_id": CLIENT_ID,
        "temperature": temp_value,
        "timestamp": int(time.time())
    }
    
    # Pretvaranje u JSON string
    json_message = json.dumps(message)
    
    # Salje se na AWS putem publish
    print(f"Saljem podatke: {json_message}")
    myMQTTClient.publish(TOPIC_PUB, json_message, 1)
    
    # Cekanje 5 sekundi
    time.sleep(5)