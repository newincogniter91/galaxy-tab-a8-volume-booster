# Tab A8 Volume Boost (Magisk Module)

Un modulo Magisk personalizzato per spingere il volume oltre il limite del 100% di fabbrica mantenendo inalterata la barra grafica di sistema.

> ?? **DISCLAIMER / COMPATIBILIT**
> - **Compatibilit:** Progettato **ESCLUSIVAMENTE** per **Samsung Galaxy Tab A8 (SM-X200)**.
> - **Non funziona su altri dispositivi Android:** Il modulo interagisce con controlli hardware specifici del chip Unisoc (`VBC DAC0 DG Set`). Utilizzarlo su altri processori (Qualcomm, MediaTek, Exynos) non avr alcun effetto.
> - **Responsabilit:** L'uso di valori di guadagno eccessivi pu causare distorsione o danneggiare gli altoparlanti. Usa il modulo a tuo rischio.

---

## ??? Come funziona

- **Barra stock inalterata:** Da 0% a 100% la barra del volume e la progressione in dB funzionano esattamente come di fabbrica.
- **Boost oltre il 100%:** Una volta raggiunto il 100% della barra visiva (step 15/15), ogni ulteriore pressione del tasto **Volume +** incrementa il guadagno hardware del DAC (`tinymix`), sbloccando potenza audio aggiuntiva.
- **Reset automatico:** Premendo **Volume -** o abbassando la barra sotto il 100%, il guadagno torna immediatamente al valore di fabbrica (26).

---

## ?? Creazione dello ZIP del Modulo

Puoi generare lo ZIP pronto da flashare eseguendo lo script Python di build:

```bash
python create_module.py
