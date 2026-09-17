#!/bin/sh

# this script installs clevertagger and Zmorge, and configures ParZu to use them.

# Bricht bei jedem Fehler ab. Ohne das lief das Skript frueher bis zum Ende durch, auch wenn die
# Downloads fehlgeschlagen waren -- der Docker-Build meldete Erfolg und das Image war unbrauchbar:
# Jeder gunicorn-Worker starb sofort mit "Cannot open transducer file".
set -e

SCRIPTPATH=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPTPATH"

TRANSDUCER=zmorge-20150315-smor_newlemma.ca
TAGGER_MODEL=hdt_ab.zmorge-20140521-smor_newlemma.model

mkdir -p external

# get clevertagger
[ -d external/clevertagger ] || git clone https://github.com/rsennrich/clevertagger external/clevertagger

# get Wapiti and compile it
[ -d external/Wapiti ] || git clone https://github.com/rsennrich/Wapiti external/Wapiti
[ -x external/Wapiti/wapiti ] || (cd external/Wapiti && make)

# get models
# Die Universitaet Zuerich liefert diese beiden Dateien nicht mehr aus: Das Verzeichnis antwortet
# mit 403, die Dateien mit 404, und der fruehere Host kitt.ifi.uzh.ch loest gar nicht mehr auf.
# Wer sie noch hat, legt sie vor dem Bauen nach external/ -- dann wird nichts heruntergeladen.
# Die wget-Aufrufe bleiben stehen, falls die Quelle wieder erreichbar wird.
cd external
[ -f "$TRANSDUCER" ] || {
    wget -c "https://pub.cl.uzh.ch/users/sennrich/zmorge/transducers/$TRANSDUCER.zip"
    unzip -u "$TRANSDUCER.zip"
}
[ -f "$TAGGER_MODEL" ] || {
    wget -c "https://pub.cl.uzh.ch/users/sennrich/zmorge/models/$TAGGER_MODEL.zip"
    unzip -u "$TAGGER_MODEL.zip"
}
cd ..

# Lieber hier abbrechen als ein Image bauen, dessen Arbeiterprozesse beim ersten Aufruf sterben.
for datei in "external/$TRANSDUCER" "external/$TAGGER_MODEL" external/Wapiti/wapiti; do
    [ -f "$datei" ] || {
        echo "install.sh: $datei fehlt." >&2
        echo "Die Zmorge-Dateien sind bei der Universitaet Zuerich nicht mehr abrufbar." >&2
        echo "Lege sie von Hand nach $SCRIPTPATH/external/ und rufe install.sh erneut auf." >&2
        exit 1
    }
done

# configure clevertagger
sed -i "s,^SMOR_MODEL =.*$,SMOR_MODEL = '$SCRIPTPATH/external/$TRANSDUCER'," external/clevertagger/config.py
sed -i "s,^CRF_MODEL =.*$,CRF_MODEL = '$SCRIPTPATH/external/$TAGGER_MODEL'," external/clevertagger/config.py
sed -i "s,^CRF_BACKEND_EXEC =.*$,CRF_BACKEND_EXEC = '$SCRIPTPATH/external/Wapiti/wapiti'," external/clevertagger/config.py

# configure ParZu
cp config.ini.example config.ini
sed -i "s,^smor_model =.*$,smor_model = $SCRIPTPATH/external/$TRANSDUCER," config.ini
sed -i "s,^taggercmd =.*$,taggercmd = $SCRIPTPATH/external/clevertagger/clevertagger," config.ini
