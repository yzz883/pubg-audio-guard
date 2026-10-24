# PUBG Audio Guard

**Protección auditiva "modo noche" para PUBG** — un procesador de audio que trata únicamente el sonido de PUBG: aplasta los picos de disparos, explosiones y el "golpe sordo" de las granadas, y realza los pasos. Baja el volumen del sistema y sigue oyéndolo todo. Las demás aplicaciones (voz, notificaciones) no se tocan.

[English](README.md) | [简体中文](README_zh-CN.md) | [Русский](README_ru-RU.md) | `Español` | [日本語](README_ja-JP.md)

![captura](docs/screenshot.png)

## Cómo funciona

```
PUBG ──> cable virtual (CABLE Input) ──> esta app (captura → pre-ganancia → EQ → compresor → limitador) ──> auriculares
las demás apps ─────────────────────────────────────────────────────────────────────┘ directas, sin procesar
```

El cable virtual (VB-Cable, gratuito) es una estación intermedia: PUBG reproduce hacia él, la app toma el audio, lo procesa y lo saca por tus auriculares. El limitador fija todos los picos bajo un techo constante; el EQ corta el "golpe en el pecho" de las granadas y el "silbido de tinnitus" que el juego reproduce tras las explosiones. Latencia añadida ~70 ms, imperceptible.

## Instalación

1. **VB-Cable**: descarga de [vb-audio.com/Cable](https://vb-audio.com/Cable/), clic derecho en `VBCABLE_Setup_x64.exe` → *ejecutar como administrador* → **reiniciar**.
2. **Paquetes Python**: `python -m pip install numpy sounddevice scipy`
3. **Ejecutar**: `python pubg_audio_gui.py` (o `start_gui.bat`)

## Enrutar el audio de PUBG

Con el juego corriendo y sonando: `Alt+Tab` → clic derecho en el altavoz de la barra → **Abrir mezclador de volumen** → busca PUBG → dispositivo de salida = **CABLE Input (VB-Audio Virtual Cable)**. Windows lo recuerda; las demás apps siguen con su salida predeterminada.

> ¿Sin sonido en el juego? Pulsa primero [Iniciar] — PUBG apuntado al cable queda mudo sin el procesador.

## Uso del GUI

- **Iniciar / Detener** — enciende/apaga la cadena
- **Probar sonido** — señal sintética de "pasos + disparo" por toda la cadena (sin abrir el juego)
- **Comparar (bypass)** — alterna procesado/original al instante
- **Preajustes** — suave / equilibrado / fuerte (modo noche)
- **Medidores** — niveles y trabajo actual del compresor/limitador en dB
- **Hover en un deslizador** — explicación detallada con consejos
- **Idioma** — desplegable arriba a la derecha
- **Guardar** — escribe `config.json`

## Parámetros

| Parámetro | Valor | Qué hace | Ajuste |
|---|---|---|---|
| Pre-ganancia | +3 dB | realza sonidos suaves | siseo/apagado → bajar 1–2 dB |
| Umbral | -18 dBFS | línea donde empieza la compresión | disparos aún fuertes → bajar; distancia → subir |
| Ratio | 2.5:1 | fuerza de compresión | más alto = más noche, peor distancia |
| Corte graves | -8 dB | quita el "golpe sordo" de granadas | aún suena → -12 |
| Corte agudos | -4 dB | domina el "tinnitus" y la aspereza | aún punza → -8 |
| Techo limitador | -3 dBFS | límite duro de picos | fijo; medidor siempre lleno = comprimir más |

## Preguntas

- **Sin sonido del sistema tras instalar VB-Cable** — el instalador deja el cable como predeterminado. Ejecuta `set_audio_default.ps1` o devuelve auriculares/micrófono a predeterminado en Windows. El GUI avisa de esto.
- **Chasquidos** — más búfer: `python pubg_audio.py --target 6 --blocksize 960`.
- **¿Es un cheat? ¿Ban?** — no. La app solo lee el flujo de audio del sistema y reproduce una copia procesada; no toca el proceso, memoria ni red del juego. PUBG y KRAFTON son marcas de sus propietarios; proyecto no oficial.

## Idiomas

Las traducciones viven en [`i18n.py`](i18n.py): añade `STRINGS["xx_XX"]` (76 claves; las que falten caen al inglés) y regístrala en `SUPPORTED`.

## Licencia

[MIT](LICENSE)
