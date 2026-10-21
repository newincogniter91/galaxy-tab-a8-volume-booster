#!/system/bin/sh
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

getdg()  { $TM "$CTL" | sed -n 's/^[^:]*: *\([0-9]*\).*/\1/p' | head -n1; }
setdg()  { $TM "$CTL" "$1" "$1" >/dev/null 2>&1; }
getvol() { cmd media_session volume --stream 3 --get 2>/dev/null | sed -n 's/.*volume is \([0-9]*\) in range \[[0-9]*\.\.\([0-9]*\)\].*/\1 \2/p' | head -n1; }

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
