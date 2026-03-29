import time
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Konfiguracija svjetiljke
ENDPOINT = "a16zv792co800v-ats.iot.eu-central-1.amazonaws.com"
CLIENT_ID = "SmartLight_01"
PATH_TO_CERT = "certificate.pem.crt"
PATH_TO_KEY = "private.pem.key"
PATH_TO_ROOT = "root-CA.pem"

TOPIC_SUB = "home/light/command" # ovdje se slusaju komande
TOPIC_PUB = "home/light/status" # odgovara se ovdje

# Funkcija koja se okida kad stigne poruka
def customCallback(client, userdata, message):
    payload = message.payload.decode('utf-8')
    print(f"\n[NOVA PORUKA] Primljeno na temu: {message.topic}")
    print(f"Sadrzaj: {payload}")
    
    try:
        data = json.loads(payload)
        # Logika ako stigne on ili off
        if data.get("action") == "ON":
            print(">>> Svjetlo je upaljeno. <<<")
            # Saljemo potvrdu nazad
            status_msg = json.dumps({"deviceId": CLIENT_ID, "status": "ON", "msg": "Svjetlo radi"})
            myMQTTClient.publish(TOPIC_PUB, status_msg, 0)
            
        elif data.get("action") == "OFF":
            print(">>> Svjetlo je ugaseno. <<<")
            status_msg = json.dumps({"deviceId": CLIENT_ID, "status": "OFF", "msg": "Mrak"})
            myMQTTClient.publish(TOPIC_PUB, status_msg, 0)
            
    except Exception as e:
        print("Greska u citanju poruke", e)

# Konekcija
print("Inicijalizacija svjetla...")
myMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myMQTTClient.configureEndpoint(ENDPOINT, 8883)
myMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

print("Povezivanje na AWS IoT Core...")
myMQTTClient.connect()
print("Uspjesno povezano! Cekaju se komande...")

# pretlata - subsrcibe
# slusa se tema home/light/command
myMQTTClient.subscribe(TOPIC_SUB, 1, customCallback)

# beskonacna petlja samo da drzi skriptu zivom zbog naredbi
while True:
    time.sleep(1)