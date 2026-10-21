SKIPUNZIP=0

if [ ! -x /vendor/bin/tinymix ] && [ ! -x /system/bin/tinymix ]; then
  abort "! tinymix non trovato: modulo non installato"
fi

ui_print "- Tab A8 Volume Boost v2.3"
ui_print "- Sbloccato limite massimo: scende fino a 0"
ui_print "- Autore: incogniter91"

set_perm $MODPATH/service.sh 0 0 0755
set_perm $MODPATH/uninstall.sh 0 0 0755
