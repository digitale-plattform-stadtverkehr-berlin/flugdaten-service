# Flugdaten Service

Webservice um Abflug und Ankfuntsdaten des Berliner Flughafen (BER) zur Verfügung zu stellen.
Die Informationen werden vom BER als Datei zur Verfügung gestellt, die alle 5 Minuten aktualisiert wird.

Abgegben werden die Daten als JSON Daten, geliefert werden Einträge innerhalb der nächsten 12 Stunden.

## Format der Eingabedatei

Es wird eine Datei im ASCII-Standardformat mit folgender Gliederung erzeugt:
1. Fileheader (Filestart)
2. Flughafenkennung (BER)
3. Block1-Header (Starts) (Block1)
4. Nutzdaten Starts
5. Block1 Trailer (Ende Block)
6. Block2-Header (Landungen) (Block2)
7. Nutzdaten Landungen
8. Block2 Trailer (Ende Block)
9. Filetrailer (Fileend)
   

|LfdNr.|Element|Header|Feldlänge|Format-info|Bemerkung|
|------|-------|-----|-------|-------|-------|
|1|FLUGNUMMER|-|8| |Flugnummer
|2|ORIGIN|-|11| |Ziel- / Herkunftsflughafen|
|3|STA/STD|-|4|hhmm|Planzeit
|4|EIBT/EOBT|-|4|hhmm|Erwartete Zeit|
|5|BEMERKUNG|-|6| |Angaben zum aktuellen Status|
|6 (nur bei Depatures)|CHECKIN|-|8| |CheckIn-Bereich nur bei Departure (Block 1)|
|7 (DEP)/6 (ARR)|TERMINAL|-|1| |Terminal|

## Parameter

* **DOWNLOAD_URL** - URL der Datei vom BER
* **DOWNLOAD_USER/DOWNLOAD_PW** - Zugangsdaten für die Datei


* **HOST** - Hostname des Servers - Default:```localhost```
* **PORT** - Port der Anwendung - Default:```8000```

## Docker Image bauen und in GitHub Registry pushen

```bash
> docker build -tdocker.pkg.github.com/digitale-plattform-stadtverkehr-berlin/flugdaten-service/flugdaten-service:<TAG> .
> docker push docker.pkg.github.com/digitale-plattform-stadtverkehr-berlin/flugdaten-service/flugdaten-service:<TAG>
```
