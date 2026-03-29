# Razvoj sigurne cloud-bazirane platforme za IoT integraciju

Ovaj projekat je realizovan kao praktični dio **Master teze** na **Elektrotehničkom fakultetu Univerziteta u Sarajevu (ETF Sarajevo)**. 
Fokus rada je na implementaciji sigurnosnih mehanizama u IoT sistemima korištenjem Amazon Web Services (AWS) infrastrukture.
Cilj ovog projekta je dizajn i implementacija prototipa sigurne, centralizovane platforme za pametne uređaje koja rješava problem fragmentacije IoT uređaja i njihovih sigurnosnih ranjivosti. 
Platforma omogućava povezivanje različitih uređaja (senzori temperature, pametna svjetla), prikupljanje telemetrijskih podataka i daljinsko upravljanje.

<div align="center">
  <img src="https://github.com/user-attachments/assets/2029914d-27ff-458a-b65e-11d0d7d3c146" alt="master drawio" width="800"/>
  <br>
  <i>Slika 1: Arhitektura sistema</i>
</div>

## Korištene tehnologije

*   **Jezik simulacije** je Python 3 (simulacija Edge uređaja kao što je Raspberry Pi)
*   **AWS Servisi:** 
    *   AWS IoT Core (MQTT Broker)
    *   Amazon DynamoDB (Baza podataka)
    *   AWS Lambda (Backend logika "Serverless")
    *   Amazon API Gateway (REST API)
    *   Amazon Cognito (Identitet i autentikacija)
*   **Frontend:** HTML (Single-Page Application sa Cognito SDK)

### Ključne funkcionalnosti i sigurnost
Uređaji koriste MQTT protokol osiguran sa TLS 1.2 (mTLS certifikati). AWS IoT Policies striktno ograničavaju uređaje (npr. senzor može samo slati podatke, ne može primati komande).
Omogućeno je 1utomatsko usmjeravanje očitanja senzora u NoSQL bazu podataka (DynamoDB). Web aplikacija je zaštićena **Amazon Cognito** servisom (API Gateway prihvata isključivo validne JWT tokene).

## Priprema i instalacija za upotrebu

Prije pokretanja projekta, potrebno je osigurati sljedeće okruženje na lokalnom računaru.

### Provjera verzije Pythona i instalacija SDK
Sistem zahtijeva Python 3. Provjera verzije i instalacija potrebne AWS biblioteke vrši se u terminalu:

```bash
PS C:\Users\zakir> python --version
Python 3.12.10
```
Potrebna dodatno instalacija AWSIoTPythonSDK:
```bash
PS C:\Users\zakir> pip install AWSIoTPythonSDK
```
### AWS IoT endpoint (CloudShell)
Da bi Python skripte mogle komunicirati sa AWS oblakom, potreban je specifičan endpoint.
Endpoint se dobija putem AWS CloudShell-a (ikona terminala >_ u gornjem desnom uglu AWS konzole) pokretanjem sljedeće naredbe:
```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

Dobijeni rezultat (korišten u ovom projektu):
```bash
a16zv792co800v-ats.iot.eu-central-1.amazonaws.com
```
***Napomena***: Ovaj endpoint je unesen direktno u .py kodove uređaja (sensor.py i light.py) kako bi se uspostavila konekcija između lokalnog Pythona i AWS IoT Core-a.

### AWS certifikati
Za svaki uređaj kreirani su i preuzeti X.509 certifikati unutar AWS IoT konzole. U terminalu možete koristiti komandu dir za provjeru da li su svi potrebni fajlovi pravilno smješteni u folderu uređaja prije pokretanja:
- certificate.pem.crt
- private.pem.key
- root-CA.crt
- sensor.py (ili light.py)

### Pokretanje projekta
Za pokretanje simulacije senzora potrebno je doći do foldera gdje se nalazi kod za senzor i pokrenuti skriptu. Senzor će početi generisati telemetrijske podatke o temperaturi i slati ih na AWS.
```bash
PS C:\Users\zakir> cd OneDrive\Desktop\SmartHome_Project\TempSensor_01
PS C:\Users\zakir\OneDrive\Desktop\SmartHome_Project\TempSensor_01> python3 sensor.py
```
![Rad senzora u terminalu]([OVDJE UBACI SLIKU: Screenshot tvog crnog terminala/CMD-a gdje piše "Saljem podatke..."])

Moguće je izvršiti testiranje MQTT veze (subscription). Da bi se potvrdilo da podaci uspješno stižu u Cloud, korišten je MQTT test client (Subscription) unutar AWS IoT konzole. Pretplatom na temu home/sensors/temp, podaci se prate u realnom vremenu.
![MQTT Test Klijent]([OVDJE UBACI SLIKU: Screenshot AWS MQTT test klijenta gdje se vide zeleni prozori sa primljenom temperaturom])

Podaci sa senzora se putem IoT Rules automatski usmjeravaju u DynamoDB. Svi podaci se bilježe u kreiranoj tabeli, a rezultati se mogu pregledati pod opcijom "Explore table items".
![DynamoDB Tabela]([OVDJE UBACI SLIKU: Screenshot tvoje DynamoDB tabele gdje se vide ID uređaja, timestamp i očitana temperatura])

Zatim je potrebno u novom terminalu pokrenuti skriptu za pametno svjetlo (python light.py).
```bash
PS C:\Users\zakir> cd OneDrive\Desktop\SmartHome_Project\SmartLight_01
PS C:\Users\zakir\OneDrive\Desktop\SmartHome_Project\SmartLight_01> python3 light.py
```
Nakon toga, otvoriti index.html u web pregledniku i prijaviti se koristeći validne kredencijale (sistem je zaštićen AWS Cognito servisom).
Kroz web preglednik moguće je poslati komandu za paljenje/gašenje svjetla. API Gateway validira JWT token i okida Lambda funkciju koja pali svjetlo.
![Web Aplikacija Login]([OVDJE UBACI SLIKU: Screenshot forme za prijavu na web stranici])
![Web Aplikacija Dashboard]([OVDJE UBACI SLIKU: Screenshot web stranice nakon logina sa upaljenim svjetlom i odgovorom servera])

### Analiza sigurnosti 
Sistem je testiran na nekoliko kritičnih sigurnosnih scenarija:
- Odbijanje neovlaštenih uređaja: Pokušaj konekcije bez validnog X.509 certifikata rezultira prekidom veze na nivou TLS handshake-a.
- Autorizacija na nivou teme (Topic): Senzor koji pokuša poslati komandu na temu pametnog svjetla je odbijen zbog IoT Polisa.
- Zaštita API-ja: Pokušaj slanja POST zahtjeva preko web stranice bez ispravnog JWT tokena iz Cognita rezultira 401 Unauthorized greškom, čime je dokazano da napadači ne mogu manipulisati uređajima putem javnog API-ja.
