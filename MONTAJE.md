# 🔧 MANUAL DE MONTAJE — Mini-ROV paso a paso

Guía completa para construir el submarino: casco, 6 motores, 5 cámaras (3 PTZ 360°),
arpoón con hilo, pinza reforzada, doble batería DeWalt 20 V y toda la electrónica.

**Tiempo total estimado: 3–5 fines de semana.** Construye fase por fase y **no saltes
las pruebas**: cada fase termina con un test obligatorio.

---

## Herramientas necesarias

- Soldador + estaño, multímetro, pistola de silicona/epoxi de 2 componentes
- Taladro + brocas (metal/acrílico), sierra para PVC
- Llaves Allen/fixas, cinta Teflón, grasa de silicona para juntas
- Impresora 3D (o servicio de impresión ~30 USD para las ~12 piezas)
- PC con el `SubControl.exe` ya compilado (ver README)

---

## FASE 1 — Casco presurizado (día 1–2)

1. **Corta el tubo acrílico** Ø100 mm a 45 cm. Lija los bordes.
2. **Perfora las tapas**: tapa frontal 1 hueco Ø40 mm para el domo; tapa popera 4 huecos
   Ø10 mm para prensa-estopas + 1 hueco Ø25 mm para el conector RJ45 IP68.
3. **Monta el domo** en la tapa frontal con epoxi marine (capa continua, sin burbujas).
4. **Prensas-estopas**: enrosca con Teflón; mete por cada una un cable de 6 hilos
   (AwG22) que llegue a media carcasa (los pasarás a los motores en la Fase 3).
5. **Conector RJ45 IP68** en la tapa popera: suelda el cable Cat6 de 20 m a su parte
   interna (8 hilos: T568B) y sella con epoxi.
6. **Prueba de fuga OBLIGATORIA:**
   - Cierra el casco VACÍO con las juntas engrasadas con grasa de silicona.
   - Mete dentro un pañuelo de papel (indicador de humedad).
   - Súmargelo 2 h en un balde/caleo a 1,5 m (o haz presión manual si tienes bomba).
   - **Si el papel está seco → aprobado. Si hay humedad → localiza, sella, repite.**

✅ **Puerta de calidad:** casco estanco sin burbujas en el epoxi.

---

## FASE 2 — Motores sellados (día 3–4, 6 unidades + 2 pods giratorios)

1. Pega cada motor brushless (2212/2836) con epoxi **dentro de su tubo** de 85 mm.
2. Sella el eje: pasa el eje por un **doble O-ring engrasado** en la tapa del tubo.
3. Rellena el interior del tubo con **aceite mineral** hasta cubrir el motor
   (los bobinados aguantan aceite; compensa con un tubito de respiración).
4. Cable de 3 hilos del motor (AwG16) soldado al **ESC Readytosky 40A 2–6S OPTO**
   (configurado ANTES en BLHeliSuite32: **modo 3D/reversa**, y encapsulado en epoxi).
5. Marca cada motor: **PL1, PL2 (popa-izq), PR1, PR2 (popa-der), LI, LD
   (laterales, hélices hacia atrás) y PI, PD (pods giratorios)**.
6. Sella las 8 uniones ESC–tubo con silicona neutra.
7. **Los 2 pods laterales giratorios (PI/PD):** el tubo sellado del motor va
   montado sobre un **servo sumergible DS3218 (IP67)** orientado para que el pod
   gire en el **plano VERTICAL** (0° = adelante, 90° = hélice abajo, −90° =
   hélice arriba, 180° = atrás). Los cables del motor pasan por un **anillo
   deslizante de 6 hilos** — el POD COMPLETO gira sin eje atravesando sello
   (cero fugas). El software mueve los servos **en pasos de 45°**.

✅ **Prueba:** conecta 1 ESC a un receptor/beambreaker y gira el motor 30 s —
ninguna fuga, giro libre. En los pods: manda "POD 90 0.5" por UDP y verifica
que el servo gira el pod completo con suave paso.

---

## FASE 3 — Frame (medio día)

1. Corta el tubo PVC de 25 mm: 4 rieles largos de 56 cm + 4 montantes de 16 cm +
   2 travesaños de 30 cm (según medidas del modelo 3D).
2. Pégalos con codo/PVC cemento siguiendo la plantilla del `modelo3d.scad`.
3. Motores: los **4 horizontales en la placa de popa** (en 2×2, y = ±42,
   z = −14 y +16 — máximo empuje hacia adelante), los **2 horizontales
   laterales** (hélices mirando hacia atrás, y = ±50, a media altura) y los
   **2 pods laterales giratorios** en los costados (servo sumergible DS3218 +
   anillo deslizante de 6 hilos). **Nota:** la subida/bajada la hacen los pods
   (ArduSub se configura sin motores verticales).
4. Coloca el casco en el centro con abrazaderas acolchadas.

---

## FASE 4 — Electrónica dentro del casco (día 5–6)

### Tabla de direcciones I2C (¡no mezclar!)

| Dispositivo | Dirección | Nota |
|---|---|---|
| PCA9685 #1 (ArduSub) | **0x40** | puente A0 sin soldar |
| PCA9685 #2 (cámaras PTZ) | **0x41** | suelda puente A0 |
| INA219 batería A | **0x44** | puente A1 |
| INA219 batería B | **0x45** | puente A1+A0 |
| BNO055 (IMU/golpes) | 0x28 | |
| MS5837 (presión) | 0x76 | |

### Tabla de salidas (PCA9685 #1 = canales RC 1–14)

| Canal | Función | Wire gauge |
|---|---|---|
| 1–4 | Motores horizontales FL FR RL RR | 16 AwG |
| 5–6 | Motores verticales VL VR | 16 AwG |
| 8 | Luces par 1 (superior) | 18 AwG |
| 9 | Luces par 2 (inferior) | 18 AwG |
| 10 | Servo pinza MG996R | 22 AwG |
| 11 | Gimbal yaw (arpoón) | 22 AwG |
| 12 | Gimbal pitch (arpoón) | 22 AwG |
| 13 | Servo disparador arpoón | 22 AwG |
| 14 | Motor carrete de hilo | 22 AwG |

**PCA9685 #2** → ch0: PTZ Arriba · ch1: PTZ Izquierda · ch2: PTZ Derecha.

### Pasos

1. Monta la **placa base**: Pi 4 + 2× PCA9685 + BNO055 + MS5837 + 2× INA219 en
   una placa de protoboard soldada o placa perf.
2. Conecta los 6 ESC a los canales 1–6 (¡señal+tierra, sin BEC conectado en serie!
   usa un solo BEC/regulador 5 V para todos los servos).
3. Conecta los reguladores de **entrada ancha (9–40 V)**: buck 5 V/3 A → Pi y
   servos; buck 12 V/5 A → luces.
4. Conecta los cables de los motores desde las prensas-estopas.
5. Cámaras: 5× USB con cables cortos hacia el hub dentro del casco.
6. **Banco de capacitores 1000 µF/35 V + TVS 30 V** sobre el bus principal.
7. Foto de referencia de TODO el cableado antes de cerrar.

✅ **Prueba:** alimenta con la batería de herramienta vía adaptador (sin cerrar el
casco): la Pi arranca, `ping 192.168.2.1` responde, BlueOS visible en el navegador.

---

## FASE 5 — Energía a prueba de todo (día 7)

1. En la tapa popera exterior, en una **caja estanca pequeña**:
   - 2× **adaptador anti-chispa XT60** (uno por batería) → sus **breaker 40 A** →
     sus módulos **LVD (corte a 15,0 V)** → sus **diodo-ideal 60 A** → **bus común**.
2. Bus común → fusible 5 A → regulador 5 V (electrónica) y fusible 10 A → regulador
   12 V (luces). Motores directo del bus con cable 14 AwG.
3. Los **INA219** van en serie de cada rama antes del diodo-ideal (miden cada batería).
4. **DS18B20** pegado a la caja de baterías → Pi.
5. Hatch popero: bahía con asa para sacar/poner los packs DeWalt DCB205.

✅ **Prueba:** conecta las 2 baterías (una llena, otra descargada): el sistema debe
quedar alimentado por la llena **sin chispas y sin ningún ajuste**. Desconecta la
llena: la otra sigue alimentando sin reinicio de la Pi.

6. **La "puertita" de carga** (costado popero-estribor del casco): hatch estanco
   pequeño con **conector XT60 de panel** hacia dentro → 2 módulos **cargador
   CC-CV 21 V/3 A con balance** (compatibles con packs DeWalt) → cada pack.
   Por fuera se conecta la **fuente de pared 24 V** (solo con el sub en seco).
7. Sube `companero_carga.py` a la Pi como servicio: mientras carga, las 4 luces
   **parpadean lento**; al completar, **parpadean rápido** unos minutos.

---

## FASE 6 — Luces (medio día)

4× LED 10 W con lente de 90° en cruz frontal (arriba, abajo, izquierda, derecha),
cada uno con su disipador pegado al frame (el agua refrigera). Cable 18 AwG a los
canales 8–9 (pares) vía los MOSFET/relés.

---

## FASE 7 — Las 5 cámaras ELP y los 3 domos PTZ (día 8)

1. **CAM1 Punta:** módulo **ELP USBFHD01M (Sony IMX291, lente 2,1 mm = 170°)**
   detrás del domo frontal, orientado al frente. Cable USB al hub de la Pi.
2. **CAM3 Abajo:** mismo módulo ELP, bajo el domo, inclinada 25° hacia abajo
   (mira la pinza y el fondo).
3. **CAM2/4/5 — los 3 domos PTZ (arriba, izquierda, derecha):**
   - En cada soporte: **servo de 360°** (PCA9685 #2: ch0 = arriba, ch1 = izq, ch2 = der)
   - Módulo **ELP mini** dentro de la **cúpula acrílica** (impermeabilizada con O-ring)
   - **Anillo de 6 LEDs blancos** alrededor de la cúpula → cable 22 AwG al
     MOSFET del **canal 15** → luz propia para oscuridad (tecla `3` en la app)
4. Sella cada cúpula y soporte con O-ring + grasa de silicona.
5. Prueba en la app: clic en miniatura → `,`/`.` para girar; `3` para las luces.

---

## FASE 8 — Arpoón + carrete + pinza (día 9–10)

### Arpoón
1. Caja del **gimbal** (2 servos MG90S en cruz, yaw + pitch) bajo el domo.
2. **Cañón** Ø12 × 480 mm alineado al gimbal; anclajes de **gomas de 16 mm** (2 bandas
   en tensión máxima → potencia plena a ~2 m).
3. **Servo disparador** (ch13) con gatillo de retención; **SEGURO siempre activado** al arrancar la app.
4. **Carrete motorizado** (motor N20, ch14) con el **hilo de 100–150 kg**: nudo +
   pegamento en el tambor (no se suelta nunca), 30 m.
5. Arpón de acero inox Ø6–7 mm con punta tri-corte.

### Pinza
1. Base con servo **MG996R** (20 kg·cm) sellada en caja con eje por O-ring.
2. Dedos dentados de acero inox + goma antideslizante, muelle de retorno.
3. Verifica en la app: botones ABRIR/CERRAR con fuerza completa.

---

## FASE 9 — Tether y consola (medio día)

1. Cable Cat6 de 20 m: una punta al RJ45 IP68 del casco, otra al **adaptador
   USB→RJ45** de tu PC.
2. Monta el **carrete de pesca/barrilete** en un soporte junto al PC: el cable pasa
   por la guía de cerámica; para recogerlo solo gira la manivela (opción motorizada
   con motor DC si prefieres).
3. Cable con **flotabilidad neutra**: foami/perlas de foam cada 40 cm.

---

## FASE 10 — Software (día 11)

1. **Flashea la microSD** con la imagen de **BlueOS** (companion oficial de ArduSub).
2. En BlueOS: instala **ArduSub** y configura el backend de salida PWM en **PCA9685**.
3. Sube `companero_ptz.py` a la Pi y actívalo como servicio (ver su cabecera).
4. Calibra en ArduSub: acelerómetro (BNO055), brújula, y el **frame de motores**
   (tipo VERTICALROV/custom) hasta que los 6 empujen en la dirección correcta.
5. Configura los canales auxiliares 8–14 como *servo* (no RC input).
6. En tu PC: abre `SubControl.exe` → Ajustes → IP `192.168.2.1`, puerto 14550,
   URLs RTSP de las 5 cámaras → **APLICAR Y RECONECTAR**.
7. Prueba en la app: telemetría (profundidad 0.0 m), luces ON/OFF, pinza, PTZ girando.
8. Activa el servicio `companero_carga.py` (indicador de carga con las luces).
9. Activa `companero_vectored.py` (servicio): mueve los 2 pods laterales
   giratorios según las órdenes de la app (UDP puerto 14552).

---

## FASE 11 — Flotabilidad y trim (medio día)

1. Con baterías puestas, añade **foam por arriba** hasta que el sub flote con
   **2–3 cm sobre el agua** (flotabilidad neta positiva: si falla todo, sube solo).
2. Distribuye peso abajo (plomos chicos) hasta que quede **derecho sin motores**.
3. Prueba de trim en ALT_HOLD: debe sostener profundidad sin oscilar.

---

## FASE 12 — Pruebas progresivas (¡no saltear!)

| Nivel | Dónde | Verifica |
|---|---|---|
| 1. Bañera | agua dulce | fugas, motores, luces, cámaras, PTZ, pinza |
| 2. Estanque 1–3 m | con ayudante | profundidad en pantalla, ALT_HOLD, auto-gancho con un objeto |
| 3. Lago/ playa 5 m | línea de seguridad al muelle | arpoón a un blanco flotante, carrete de hilo |
| 4. 10 m | con visibilidad | sensor de golpes (golpe suave a la mano sobre el casco), emergencias F1/F2 |
| 5. 15 m | zona despejada | misión completa: buceo, PTZ vigilancia, caza, regreso |

Después de cada inmersión en sal: **lavar con agua dulce** y pañuelo de control
dentro del casco (debe seguir seco).

---

## FASE 13 — Primera misión de caza (checklist)

- [ ] Baterías DeWalt cargadas (2), breaker ON
- [ ] Cable conectado a la PC y al sub · app CONECTADA 🟢
- [ ] Trim verificado · flotabilidad positiva
- [ ] Luces probadas · PTZ girando · autoapuntado ON (`Y`)
- [ ] SEGURO del arpoón ON hasta tener el objetivo delante (`P` para quitar)
- [ ] AUTO-GANCHO (`C`) cuando veas la presa en CAM3
- [ ] Recoger hilo con `F5` tras cada tiro
- [ ] Fuente de pared a mano para la puertita de carga
- [ ] Emergencias memorizadas: **F1 parada · F2 subir · F3 normalizar**
- [ ] Normativa local de pesca revisada

---

## Problemas típicos de montaje

| Síntoma | Causa probable | Solución |
|---|---|---|
| Motor no gira | ESC sin señal / canal mal | revisa ch1–6 y tierra común |
| Servos vibran | 2 BEC conectados a la vez | un solo regulador 5 V alimenta servos |
| Pi se reinicia al armar | caída de tensión en el bus | revisa capacitores y gauge de cable |
| Fuga en prensa-estopas | falta teflón/grasa | reensambla con cinta y grasa |
| INA219 no aparece | dirección I2C duplicada | revisa la tabla de direcciones |
| PTZ no gira | script no corre / dirección PCA9685 | `0x41` en #2 y servicio activo |

---

## Resumen de etapas

```
Casco + fuga ✓ → 6 motores ✓ → frame ✓ → electrónica + ping ✓ →
energía a prueba de todo ✓ → luces ✓ → 5 cámaras + PTZ ✓ →
arpoón + pinza ✓ → tether + carrete ✓ → software ✓ → trim ✓ →
bañera → 3 m → 5 m → 10 m → 15 m → 🎯 primera caza
```

Con esto tienes el submarino completo. ¡Suerte en la construcción! 🌊🛥️
