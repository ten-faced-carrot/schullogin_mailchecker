# Mail-Frontend für Schullogin

Okay, also alle die hier sind, kennen vermutlich [Schullogin](https://schullogin.de). Für alle anderen, sie schreiben auf ihrem Twitter-Account, sie seien ein  
> Identitätsmanagementsystem für alle sächsischen Schulen, Kooperationsprojekt von @Bildung_Sachsen und @tudresden_de

Schön und gut, aber ich wollte nicht andauernd die Seite aufrufen, um Mails abzurufen. Also habe ich dieses System entwickelt.  
Es basiert auf [Selenium](https://selenium.dev) und funktioniert relativ gut dafür. 

## Installation

Falls ihr Sappho installiert habt, könnt ihr einfach 
```
    sappho -aD -S libcrosscompile
    sappho -S jschullogin
```
ausführen. 

Für alle anderen, ihr müsst euch leider Python installieren.
Unter Linux sollte das vorinstalliert sein, ihr braucht aber außerdem noch pip (Auch wenn das bei moderneren Linux Distributionen vorinstalliert sein sollte.)  
Möglicherweise müsst ihr auch `make` installieren. Danach könnt ihr einfach `make clean install` ausführen, das installiert alles für euch.

Für Windows müsst ihr leider alles selbst machen:

```cmd
pip install -r requirements.txt
python main.py
```

Dann meldet ihr euch an und alles läuft