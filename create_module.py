import os
import zipfile
import urllib.request

MODULE_ID = "tab_a8_volume_boost"
ZIP_NAME = f"{MODULE_ID}.zip"
AUTHOR = "incogniter91"

files = {
    "module.prop": f"""id={MODULE_ID}
name=Tab A8 Volume Boost
version=v2.3
versionCode=5
author={AUTHOR}
description=Volume oltre il 100%: con la barra al massimo, Volume+ abbassa il valore DAC fino allo 0 assoluto (senza blocchi)
""",

    "customize.sh": """SKIPUNZIP=0

if [ ! -x /vendor/bin/tinymix ] && [ ! -x /system/bin/tinymix ]; then
  abort "! tinymix non trovato: modulo non installato"
fi

ui_print "- Tab A8 Volume Boost v2.3"
ui_print "- Sbloccato limite massimo: scende fino a 0"
ui_print "- Autore: incogniter91"

set_perm $MODPATH/service.sh 0 0 0755
set_perm $MODPATH/uninstall.sh 0 0 0755
""",

    "service.sh": """#!/system/bin/sh
# Valori di default
CTL="VBC DAC0 DG Set"
STEP=2        # quanti punti SCENDERE per ogni pressione oltre il 100%

[ -f /data/adb/volboost.conf ] && . /data/adb/volboost.conf

ST=/data/local/tmp/volboost.state
LOG=/data/local/tmp/volboost.log

: > "$LOG"

until [ "$(getprop sys.boot_completed)" = 1 ]; do sleep 5; done
sleep 10

TM=/vendor/bin/tinymix
[ -x "$TM" ] || TM=/system/bin/tinymix

getdg()  { $TM "$CTL" | sed -n 's/^[^:]*: *\\([0-9]*\\).*/\\1/p' | head -n1; }
setdg()  { $TM "$CTL" "$1" "$1" >/dev/null 2>&1; }
getvol() { cmd media_session volume --stream 3 --get 2>/dev/null | sed -n 's/.*volume is \\([0-9]*\\) in range \\[[0-9]*\\.\\.\\([0-9]*\\)\\].*/\\1 \\2/p' | head -n1; }

reset() {
  read EXTRA BASE < "$ST"
  if [ "${EXTRA:-0}" -gt 0 ]; then
    setdg "$BASE"
    echo "reset -> $BASE" >> "$LOG"
  fi
  echo "0 0" > "$ST"
}

echo "0 0" > "$ST"
set -- $(getvol); PREV=${1:-0}

# Watcher: se la barra scende sotto il massimo, torna al guadagno stock
(
  while sleep 3; do
    read EXTRA BASE < "$ST"
    [ "${EXTRA:-0}" -gt 0 ] || continue
    set -- $(getvol)
    if [ -n "$2" ] && [ "$1" -lt "$2" ]; then
      reset
    elif [ "$(getdg)" != "$((BASE - EXTRA))" ]; then
      setdg $((BASE - EXTRA))
    fi
  done
) &

getevent -l 2>/dev/null | while read -r _ _ KEY ACT; do
  [ "$ACT" = DOWN ] || continue
  case "$KEY" in
    KEY_VOLUMEUP)
      sleep 0.2
      set -- $(getvol); CUR=${1:-0}; MAX=${2:-0}
      [ "$MAX" -gt 0 ] || continue
      if [ "$CUR" -ge "$MAX" ] && [ "$PREV" -ge "$MAX" ]; then
        read EXTRA BASE < "$ST"
        [ "${EXTRA:-0}" -eq 0 ] && BASE=$(getdg)
        EXTRA=$(( ${EXTRA:-0} + STEP ))
        TARGET=$((BASE - EXTRA))
        
        # Protezione per non scendere sotto 0
        if [ "$TARGET" -lt 0 ]; then
          TARGET=0
          EXTRA=$BASE
        fi
        
        setdg $TARGET
        echo "$EXTRA $BASE" > "$ST"
        echo "up cur=$CUR max=$MAX base=$BASE target=$TARGET" >> "$LOG"
      fi
      PREV=$CUR
      ;;
    KEY_VOLUMEDOWN)
      reset
      sleep 0.2
      set -- $(getvol); PREV=${1:-0}
      ;;
  esac
done
""",

    "uninstall.sh": """#!/system/bin/sh
rm -f /data/local/tmp/volboost.state /data/local/tmp/volboost.log
""",

    "META-INF/com/google/android/updater-script": "#MAGISK\n"
}

def create_zip():
    print("[*] Generazione del modulo Magisk v2.3 (Senza limiti)...")
    
    os.makedirs("META-INF/com/google/android", exist_ok=True)

    for path, content in files.items():
        with open(path, "w", newline="\n", encoding="utf-8") as f:
            f.write(content)
        print(f"  + Creato {path}")

    binary_url = "https://raw.githubusercontent.com/topjohnwu/Magisk/master/scripts/module_installer.sh"
    binary_path = "META-INF/com/google/android/update-binary"
    print("  + Download update-binary di Magisk...")
    try:
        urllib.request.urlretrieve(binary_url, binary_path)
    except Exception as e:
        print(f"  [!] Fallback update-binary local: {e}")
        with open(binary_path, "w", newline="\n") as f:
            f.write("#!/system/bin/sh\n")

    print(f"\n[*] Impacchettamento in {ZIP_NAME}...")
    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for path in list(files.keys()) + [binary_path]:
            zip_file.write(path)
            print(f"  -> Aggiunto a ZIP: {path}")

    print(f"\n[V] Fatto! Modulo sbloccato generato in: {ZIP_NAME}")

if __name__ == "__main__":
    create_zip()
