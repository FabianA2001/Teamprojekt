# Teamprojekt

## Inhalt
Dieses Temaprojekt beinhaltet einen Algorithmus für das Close-Enough
Area Travelling Salesman Problem inklusiver Turn-Costs. Der Algorithmus erhält
eine Menge an Flächen und muss in möglichst kurzer Zeit eine möglichst kurze
Rundreise finden, die alle Flächen besucht und dabei möglichst kleine
Abbiegewinkel nutzt.

## Installation

auf MacOS und Linux ist es sinnvoll ein virtuelles environment zu haben um pip
zu nutzen. Diese kann mit `python3 -m venv .` im aktuzellen Ordner erzeugt
werden.

Aktiviert werden für die aktuelle Konsole, kann das environment mit folgendem
befehl `source bin/active`. sollte die Konsole neugestartet werden, muss das
environment erneut aktiviert werden.

alle benötigeten Pakete sind in der requirements.txt definiert dieses kann mit
`pip install -r requirements.txt` genutzt werden

das Programm kann standarmäßig mit `python3 main.py` gestartet werden, dann
werden eine jpg mit den Koordinaten und eine csv datei mit den Koordiaten
erstellt mit `python3 main.py -h` kann eine hilfe für die möglichen Arugmente
angezeigt werden.
