# 🦗 Load DP Merge GUI

> **Integračná verzia grafického nástroja pre záťažové testovanie HTTP/HTTPS a s TCP/UDP režimami**  
> Postavené na Pythone, CustomTkinter, Locust frameworku a Scapy – konfigurácia testu, monitoring a PDF report v jednom nástroji.

<br>

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?logo=linux&logoColor=black)
![Locust](https://img.shields.io/badge/Locust-load%20testing-00AA00)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-9B59B6)
![TCP/UDP](https://img.shields.io/badge/TCP%2FUDP-orange)
![Status](https://img.shields.io/badge/Status-Prototype-orange)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

---

## 📋 Obsah

- [O projekte](#-o-projekte)
- [Hlavné funkcie](#-hlavné-funkcie)
- [Štruktúra projektu](#-štruktúra-projektu)
- [Požiadavky](#-požiadavky)
- [Inštalácia](#-inštalácia)
- [Spustenie aplikácie](#-spustenie-aplikácie)
- [Konfigurácia](#️-konfigurácia)
- [Používanie](#️-používanie)
  - [Config – nastavenia](#️-config--nastavenia)
  - [HTTP/S – spustenie testu](#-https--spustenie-testu)
  - [TCP –  režim](#-tcp---režim)
  - [UDP –  režim](#-udp---režim)
  - [Generate Report – generovanie PDF](#-generate-report--generovanie-pdf)
  - [Reports – správa reportov](#-reports--správa-reportov)
- [Odporúčaný workflow](#-odporúčaný-workflow)
- [Stage Presets](#-stage-presets)
- [Sieťové moduly](#-sieťové-moduly)
- [PDF Report](#-pdf-report)
- [Digitálne podpisovanie](#-digitálne-podpisovanie)
- [Riešenie častých problémov](#-riešenie-častých-problémov)
- [Klávesové skratky](#️-klávesové-skratky)
- [Licencia](#-licencia)
- [Autor](#-autor)

---

## 🔍 O projekte

**Load_Locust  GUI** je pracovná integračná verzia desktopovej aplikácie pre Linux. Základom je HTTP/HTTPS záťažové testovanie cez Locust a režimy TCP a UDP. Aplikácia umožňuje nastaviť cieľový server, pripraviť zdrojové IP adresy, spustiť test, sledovať dostupnosť cieľa, monitorovať sieťovú prevádzku a následne vygenerovať PDF report.


**Základný workflow:**

```text
1. PREPARE      →   2. CONFIGURE   →   3. TEST        →   4. REPORT
   locust_env       IP Pool             HTTP/S Locust      PDF + grafy
   dependencies     Interface           Reachability       Topológia siete
   run_gui.sh       Target              Network RX/TX      Výsledky testu
```

---

## ✨ Hlavné funkcie

| Kategória | Funkcia | Popis |
|---|---|---|
| 🌐 **HTTP/S** | Locust HTTP/HTTPS test | Predvolený HTTP/S test cez `locust_tests/Locustfile_http.py` |
| 🌐 **HTTP/S** | GET/POST požiadavky | Podpora endpointov, request body, timeoutov a SSL nastavení |
| 🌐 **Sieť** | IPv4 + IPv6 IP pool | Generovanie zdrojových IP adries a zápis do `ip_pool.txt` |
| 🌐 **Sieť** | Custom IP pool | Možnosť použiť vlastný `.txt` zoznam IP adries |
| 🌐 **Sieť** | Source ports | Systémové ephemeral porty alebo vlastný port/range podľa nastavenia GUI |
| 🖥️ **Monitoring** | Network Monitor | Záznam RX/TX prevádzky počas testu do `data/network_usage.csv` |
| 🖥️ **Monitoring** | Reachability Monitor | Kontrola dostupnosti cieľového servera počas testu |
| 📊 **Reporting** | PDF Export | Generovanie reportu s metrikami, grafmi, topológiou a voliteľnou tabuľkou chýb |
| 🔏 **Bezpečnosť** | PDF Signing | Voliteľné digitálne podpísanie PDF reportu cez PKCS#12 certifikát |
| ⚡ **Stages** | Stage Presets | Preddefinované scenáre: Flat, Stress, Spike, Endurance, Capacity |
| ⚙️ **Konfigurácia** | Persistent config | Nastavenia z GUI sa ukladajú do `config.env` |
| 🧪 **TCP/UDP** |  režimy |  TCP/UDP testovanie cez Locust + Scapy |

---

## 📁 Štruktúra projektu

```text
Load_DP_merge/
│
├── README.md                        # Popis projektu a návod na použitie
├── .gitignore                       # Súbory, ktoré sa nemajú verzovať
├── locust_gui.py                    # Hlavný súbor GUI aplikácie
├── prepare_tester_python.sh         # Inštalačný skript pre tester
├── run_gui.sh                       # Odporúčaný skript na spustenie GUI cez locust_env
├── requirements.txt                 # Python závislosti projektu
├── config.env                       # Lokálna konfigurácia aplikácie
├── stages.json                      # Aktuálne fázy záťažového testu
├── vut_logo.png                     # Logo použité v PDF reporte
│
├── ip_pool.txt                      # Generovaný aktívny IP pool
├── port_pool.txt                    # Generovaný aktívny port pool, ak sa používa
├── test_config.csv                  # Snapshot konfigurácie posledného testu
│
├── data/                            # Výstupné dáta z testov
│   ├── .gitkeep
│   ├── report_stats.csv             # Generuje Locust
│   ├── report_stats_history.csv     # Generuje Locust
│   ├── report_failures.csv          # Generuje Locust
│   ├── report_exceptions.csv        # Výstup chýb/výnimiek, ak vznikne
│   ├── reachability.csv             # Generuje Reachability.py
│   ├── network_usage.csv            # Generuje Network_monitor.py
│   └── report_metadata.csv          # Metadata z Locustfile
│
├── IP_pool/                         # Uložené IP pool súbory
│   └── .gitkeep
│
├── locust_tests/                    # Locust testovacie súbory
│   ├── Locustfile_http.py           # Predvolený HTTP/HTTPS test
│   ├── Locust_tcp.py                #  TCP test
│   └── Locust_udp.py                #  UDP test
│
├── network/                         # Sieťové a pomocné moduly
│   ├── Create_IP_Pool_skript.py
│   ├── Remove_IP_Pool_skript.py
│   ├── Network_monitor.py
│   ├── Reachability.py
│   ├── Watchdog.py
│   └── Create_topology.py
│
├── misc/                            # Pomocné moduly pre TCP/UDP časť
│   ├── Config_Load.py
│   ├── Packet_create.py
│   ├── Port_scanner.py
│   └── main.py
│
└── report/                          # Reportovací modul a výstupné PDF
    ├── Locust_report_v3.py
    ├── Locust_Report.pdf            # Generovaný report
    └── report.html                  # HTML výstup Locustu, ak vznikne
```

Niektoré súbory vznikajú alebo sa menia automaticky až počas používania aplikácie. Ide najmä o `ip_pool.txt`, `port_pool.txt`, `test_config.csv`, CSV súbory v priečinku `data/` a PDF reporty v priečinku `report/`.

---

## 📦 Požiadavky

### Systémové požiadavky

| Požiadavka | Odporúčanie | Poznámka |
|---|---|---|
| **OS** | Linux / Ubuntu | Projekt používa Linux sieťové nástroje |
| **Python** | 3.10+ | Testované s Python 3.10+ |
| **Sieťové rozhranie** | napr. `ens33`, `eth0`, `eth2` | Musí existovať v systéme testera |
| **Oprávnenia** | sudo | Potrebné pri pridávaní/odoberaní IP adries a pri TCP/UDP Scapy časti |
| **Testovaný server** | HTTP alebo HTTPS server | Server musí byť dostupný z testera |
| **Grafické prostredie** | X11/desktop session | Potrebné pre CustomTkinter GUI |

### Hlavné Python závislosti

```text
ctktooltip
customtkinter
gevent
locust
matplotlib
numpy
pandas
pillow
psutil
pyhanko
python-dotenv
reportlab
requests
scapy
```

Závislosti sú uvedené v `requirements.txt` a inštalačný skript ich nainštaluje do virtuálneho prostredia `locust_env`.

---

## 🚀 Inštalácia

### 1. Rozbalenie projektu

Ak máš projekt ako ZIP súbor:

```bash
unzip Load_DP_merge.zip
cd Load_DP_merge
```

Ak je projekt už v priečinku:

```bash
cd Load_DP_merge
```

### 2. Spustenie automatickej prípravy prostredia

```bash
chmod +x prepare_tester_python.sh
./prepare_tester_python.sh
```

Skript vykoná najmä:

- inštaláciu potrebných systémových balíkov cez `apt`,
- vytvorenie virtuálneho prostredia `locust_env`,
- inštaláciu Python závislostí,
- vytvorenie potrebných priečinkov,
- kontrolu importov Python modulov,
- kontrolu dostupnosti základných sieťových nástrojov.

---

## ▶️ Spustenie aplikácie

### Odporúčaný spôsob

Po inštalácii spúšťaj GUI cez priložený skript:

```bash
./run_gui.sh
```

Tento skript automaticky použije Python interpreter z virtuálneho prostredia:

```text
locust_env/bin/python
```

To je dôležité, pretože GUI aj Locust musia bežať v rovnakom Python prostredí. Inak sa môže stať, že systém vypíše chybu typu `No module named locust` alebo že GUI nenájde niektorú z nainštalovaných knižníc.

### Ručné spustenie

Alternatívne môžeš prostredie aktivovať ručne:

```bash
source locust_env/bin/activate
python3 locust_gui.py
```

### Kontrola, že sa používa správny Locust

```bash
source locust_env/bin/activate
python -m locust --version
```

V projekte sa HTTP/S test spúšťa cez:

```text
python -m locust
```

nie cez samotný systémový príkaz `locust`. Vďaka tomu sa použije rovnaké virtuálne prostredie ako pri GUI.

---

## ⚙️ Konfigurácia

Konfigurácia sa ukladá do súboru:

```text
config.env
```

Názov súboru musí zostať malými písmenami. Na Linuxe sú `config.env` a `Config.env` dva rozdielne súbory.

`config.env` je rozdelený do sekcií:

```text
TEST STAGES
TARGET
IP POOL - IPv4
IP POOL - IPv6
HTTP/S TEST
TCP/UDP TESTS
REACHABILITY
REPORT THRESHOLDS
```

Hodnoty sa ukladajú z GUI. Pri uložení konfigurácie alebo stages môže GUI súbor prepísať v štruktúrovanej podobe.

Príklad dôležitých HTTP/S hodnôt:

```env
TARGET_HOST='https://example.local'
ENDPOINT_PATH='/'
INTERFACE='ens33'
PROCESSES='-1'
HTTP_METHOD='GET'
STOP_TIMEOUT='60'
CONNECT_TIMEOUT='5'
READ_TIMEOUT='15'
SSL_VERIFY='false'
ACCEPT_ENCODING='identity'
```

Počet používateľov, spawn rate a trvanie testu sa riadia cez `STAGES` a `stages.json`.

---

## 🖥️ Používanie

Po spustení aplikácie sa v bočnom menu zobrazia stránky:

```text
Config
HTTP/S
TCP
UDP
Generate Report
Reports
```

---

### ⚙️ Config – nastavenia

V časti **Config** sa nastavuje cieľový server, endpointy, IP pool, rozhranie, reachability monitoring a sieťový monitoring.

#### General

| Parameter | Popis | Príklad |
|---|---|---|
| Target host | URL alebo host testovaného servera | `https://example.local` |
| Endpoint path | Jeden alebo viac endpointov | `/,/health,/api/status` |
| Interface | Sieťové rozhranie testera | `ens33` |
| Test type | Popis testu do reportu | `Load Test` |
| Request failure threshold | Povolené percento Locust chýb | `1` |
| Verify SSL certificate | Zapne alebo vypne overovanie HTTPS certifikátu | `true/false` |
| Disable compression | Nastaví `Accept-Encoding: identity` | vhodné pri meraní priepustnosti |

Endpointy je možné zadať ako zoznam oddelený čiarkou:

```text
/,/health,/api/status
```

#### IP Pool

IP pool sa používa ako zoznam zdrojových IP adries pre test. Podporované sú režimy:

```text
IPv4 range
IPv6 range
IPv6 prefix
Custom pool file
```

Príklad `ip_pool.txt`:

```text
192.168.100.73/24
192.168.100.74/24
```

Pred spustením HTTP/S testu je odporúčané najskôr v GUI kliknúť na:

```text
Setup IP Pool
```

Tým sa vytvorí alebo aktualizuje `ip_pool.txt` a IP adresy sa pridajú na zvolené sieťové rozhranie.

#### Reachability

| Parameter | Popis |
|---|---|
| Interval | Ako často sa overuje dostupnosť servera |
| Timeout | Maximálny čas čakania na odpoveď |
| Source IP | Zdrojová IP pre reachability kontrolu |
| Interface | Rozhranie použité pre reachability monitoring |
| Reachability threshold | Povolené percento výpadkov dostupnosti |

Reachability threshold sa vyhodnocuje oddelene od Locust request failure thresholdu.

#### Actions

| Tlačidlo | Popis |
|---|---|
| **Setup IP Pool** | Pridá IP adresy na rozhranie a vytvorí/aktualizuje `ip_pool.txt` |
| **Save Pool** | Uloží aktuálny IP pool do priečinka `IP_pool/` |
| **Cleanup** | Odstráni IP adresy z rozhrania podľa `ip_pool.txt` |

---

### 🌐 HTTP/S – spustenie testu

HTTP/S časť je hlavná testovacia časť projektu. Predvolený Locustfile je:

```text
locust_tests/Locustfile_http.py
```

#### Define Test

Test je rozdelený do stages. Každá fáza obsahuje:

```text
Duration (s)
Users
Spawn rate
Wait mode
Min
Max
```

Hodnota `Duration (s)` je trvanie konkrétnej fázy, nie kumulatívny čas.

Príklad:

```text
Stage 1: 60 s, 10 users
Stage 2: 120 s, 50 users
Stage 3: 120 s, 100 users
```

Celkové trvanie:

```text
60 + 120 + 120 = 300 s
```

#### Wait mode

| Režim | Význam |
|---|---|
| `between` | Náhodné čakanie medzi Min a Max |
| `constant` | Fixné čakanie podľa hodnoty Min |
| `constant_throughput` | Min sa používa ako cieľová priepustnosť na používateľa |

#### Locust Parameters

| Parameter | Popis |
|---|---|
| Stop timeout | Čas, ktorý Locust čaká na korektné ukončenie taskov |
| Processes | Počet Locust procesov; `-1` znamená automaticky podľa CPU |
| Connect timeout | Timeout pre nadviazanie spojenia |
| Read timeout | Timeout pre čakanie na odpoveď servera |

#### Request Settings

Predvolený HTTP/S Locustfile podporuje hlavne:

```text
GET
POST
```

Pri `GET` sa request body nepoužíva. Pri `POST` je možné zadať JSON request body.

Príklad:

```json
{
  "message": "hello",
  "user": "test"
}
```

#### Spustenie HTTP/S testu

Odporúčaný postup:

```text
1. Config → nastav Target host, Interface, Endpoint path.
2. Config → nastav IP pool.
3. Klikni na Setup IP Pool.
4. HTTP/S → skontroluj stage riadky.
5. HTTP/S → klikni na Start Test.
6. Po skončení testu otvor Generate Report.
```

Pri spustení sa spustí:

```text
Locust HTTP/S test
Reachability monitoring
Network monitoring
```

Výstup je dostupný v paneli **Output Log**.

---

### 🧪 TCP –  režim

TCP režim používa Locust ako orchestrátor a Scapy na odosielanie raw TCP paketov.

Dôležité upozornenie:

```text
TCP režim nie je klasický aplikačný HTTP test.
Ide o sieťové generovanie TCP paketov.
```

Pre TCP/UDP môžu byť potrebné root oprávnenia, pretože Scapy pracuje s raw socketmi. V kóde sa TCP/UDP procesy spúšťajú cez `sudo`.

---

### 🧪 UDP –  režim

UDP režim posiela UDP datagramy cez Scapy a štatistiky zapisuje cez Locust eventy.

Dôležité upozornenie:

```text
UDP nemá prirodzené potvrdenie doručenia.
Report preto vyhodnocuje hlavne lokálne odosielanie paketov, nie aplikačnú odpoveď servera.
```

---

### 📄 Generate Report – generovanie PDF

Po dokončení testu je možné vygenerovať PDF report.

| Parameter | Popis |
|---|---|
| Report name | Názov PDF súboru |
| Save to | Cieľový priečinok |
| Comment | Voliteľný komentár do reportu |
| Include failure details table | Zobrazí detailnú tabuľku chýb |
| Sign PDF | Voliteľné podpísanie reportu |

PDF report obsahuje najmä:

```text
Test Information
Performance Overview
Test Stages
Network Topology
Reachability
Time Series Charts
Network Traffic Analysis
Failure Details
```

Tlačidlo **Delete Data** odstráni výstupné CSV súbory z priečinka `data/` a `test_config.csv`.

---

### 📋 Reports – správa reportov

Táto časť slúži na prezeranie vygenerovaných PDF reportov z priečinka `report/`.

| Akcia | Popis |
|---|---|
| Open | Otvorí PDF report |
| Delete | Odstráni PDF report |
| Refresh | Obnoví zoznam reportov |

---

## ✅ Odporúčaný workflow

### Prvé spustenie

```bash
cd Load_DP_merge
chmod +x prepare_tester_python.sh
./prepare_tester_python.sh
./run_gui.sh
```

### Každé ďalšie spustenie

```bash
cd Load_DP_merge
./run_gui.sh
```

### HTTP/S test + report

```text
1. Config → nastav cieľový server a sieťové rozhranie.
2. Config → nastav IPv4/IPv6 pool.
3. Config → klikni Setup IP Pool.
4. HTTP/S → nastav stages, metódu, timeouty a procesy.
5. HTTP/S → klikni Start Test.
6. Po ukončení testu otvor Generate Report.
7. Nastav názov PDF a klikni Generate Report.
8. Výsledný PDF report nájdeš v priečinku report/.
```

### Ukončenie a vyčistenie IP adries

Po testovaní je vhodné odstrániť IP adresy z rozhrania:

```text
Config → Cleanup
```

---

## 📐 Stage Presets

Aplikácia obsahuje preddefinované profily záťaže.

| Preset | Popis |
|---|---|
| **Flat** | Konštantná záťaž |
| **Stress** | Postupné zvyšovanie záťaže a následné zníženie |
| **Spike** | Krátkodobý prudký nárast záťaže |
| **Endurance** | Dlhodobý test stability |
| **Capacity** | Postupné hľadanie kapacity systému s režimom `constant_throughput` |

Stages sa ukladajú do:

```text
stages.json
```

Pri uložení konfigurácie sa zároveň zapisujú aj do premennej `STAGES` v `config.env`.

---

## 🧩 Sieťové moduly

### `Create_IP_Pool_skript.py`

Pridáva IP adresy na sieťové rozhranie a zapisuje ich do `ip_pool.txt`. Podporuje IPv4, IPv6, rozsah adries aj vlastný zoznam IP adries.

### `Remove_IP_Pool_skript.py`

Odstraňuje IP adresy z rozhrania podľa obsahu `ip_pool.txt`.

### `Network_monitor.py`

Monitoruje RX/TX prevádzku zo sieťového rozhrania a zapisuje výsledky do:

```text
data/network_usage.csv
```

### `Reachability.py`

Priebežne overuje dostupnosť cieľového servera a zapisuje výsledky do:

```text
data/reachability.csv
```

### `Create_topology.py`

Generuje topologický diagram testovacieho prostredia pre PDF report.

### `Watchdog.py`

Pomocný modul pre sledovanie dostupnosti v TCP/UDP časti.

---

## 📊 PDF Report

PDF report je generovaný modulom:

```text
report/Locust_report_v3.py
```

Report využíva najmä tieto súbory:

```text
data/report_stats.csv
data/report_stats_history.csv
data/report_failures.csv
data/report_exceptions.csv
data/network_usage.csv
data/reachability.csv
data/report_metadata.csv
test_config.csv
stages.json
ip_pool.txt
```

Hodnoty použité v reporte sa viažu na snapshot konkrétneho testu. Preto sa pred spustením testu vytvára `test_config.csv`.

---

## 🔏 Digitálne podpisovanie

PDF report je možné podpísať certifikátom vo formáte:

```text
.p12
.pfx
```

V GUI je potrebné nastaviť cestu k certifikátu a heslo. Certifikáty a súkromné kľúče neukladať do verejného repozitára.

---

## 🛠️ Riešenie častých problémov

### GUI píše, že Locust nie je nainštalovaný

Spusti aplikáciu cez:

```bash
./run_gui.sh
```

alebo ručne:

```bash
source locust_env/bin/activate
python -m locust --version
python3 locust_gui.py
```

Ak `python -m locust --version` nefunguje, zopakuj inštaláciu:

```bash
./prepare_tester_python.sh
```

### Test neposiela requesty

Skontroluj, či existuje IP pool:

```bash
cat ip_pool.txt
```

Ak je súbor prázdny alebo neexistuje, v GUI najskôr použi:

```text
Config → Setup IP Pool
```

### V reporte je `IP Pool count: Unknown`

Skontroluj, či bol test spustený až po vytvorení IP poolu. Odporúčané poradie je:

```text
Setup IP Pool → Start Test → Generate Report
```

### `config.env` sa správa divne

Používaj iba:

```text
config.env
```

Nie `Config.env`. Na Linuxe sú to dva rôzne súbory.

### TCP/UDP žiada sudo alebo nefunguje bez práv

TCP/UDP časť používa Scapy a raw sockety, preto môže vyžadovať root oprávnenia. HTTP/S testovanie túto časť nepotrebuje rovnakým spôsobom.

---

## ⌨️ Klávesové skratky

| Skratka | Funkcia |
|---|---|
| `Ctrl` + `+` / `=` | Priblíženie |
| `Ctrl` + `-` | Oddialenie |
| `Ctrl` + `0` | Reset zoomu |

---

## 🧹 Odporúčaný `.gitignore`

```gitignore
__pycache__/
*.py[cod]
*.so
*.egg
*.egg-info/
dist/
build/
venv/
.venv/
locust_env/
.idea/
*.iml
*.log

# lokálna konfigurácia a runtime dáta
config.env
*.env
ip_pool.txt
port_pool.txt
test_config.csv

# výstupy testov
data/*.csv
data/stage_*
report/*.pdf
report/*.png
report/report.html
report/data/

# certifikáty a súkromné kľúče
*.p12
*.pfx
*.key
*.pem

# ponechanie prázdnych priečinkov
!data/.gitkeep
!IP_pool/.gitkeep
```

---

## 📝 Licencia

Projekt je určený na akademické a testovacie účely. Licenciu je možné upraviť podľa požiadaviek repozitára alebo školy.

---

## 👤 Autor

Vytvorené ako prototyp nástroja na záťažové testovanie v rámci diplomovej práce.
---

<div align="center">

*🦗 Load DP Merge GUI – konfiguruj, testuj, monitoruj, reportuj.*

</div>
