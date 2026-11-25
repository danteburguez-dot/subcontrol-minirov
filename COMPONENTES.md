# 🔩 LISTA COMPLETA DE COMPONENTES — Mini-ROV con arpoón, PTZ y auto-apuntado

Todos los precios aproximados (USD ≈ EUR). Los motores/servos van sellados según notas.

---

## 1. Casco presurizado (15 m = 2,5 atm)

| # | Componente | Specs | Precio |
|---|---|---|---|
| 1 | Tubo acrílico Ø100 × 5 mm × 45 cm | pared 5 mm, transparente | 35–45 |
| 2 | 2 tapas con doble junta tórica | mecanizadas o impresas en PETG grueso | 20–30 |
| 3 | Juntas tóricas Ø100 (spare ×3) | NBR | 6 |
| 4 | Prensa-estopas ×4 | M10, para cables de 3–6 mm | 12 |
| 5 | Epoxi marine + sellador | 2 componentes | 15 |
| 6 | Domo acrílico frontal | Ø100 media esfera | 18 |

**Subtotal casco: ≈ 106–126**

## 2. Frame y flotabilidad

| # | Componente | Specs | Precio |
|---|---|---|---|
| 7 | Tubo PVC 25 mm × 2 m + codos | frame 55 × 32 cm | 12 |
| 8 | Espuma PU rígida 7 L | placas o espuma en aerosol ×2 | 18 |
| 9 | Herrajes inox + tornillería A4 | tuercas, abrazaderas | 10 |

**Subtotal frame: ≈ 40**

## 3. Propulsión — 6 motores sellados

| # | Componente | Specs | Precio |
|---|---|---|---|
| 10 | 6× motor brushless 2212/2836 | 1000–1400 KV | 6 × 15 = 90 |
| 11 | 6× hélice 2-hélices/hélice 3 palas | 8–9 pulgadas | 6 × 4 = 24 |
| 12 | 6× tubo de motor + aceite mineral | sellado eje con O-ring ×2 | 6 × 6 = 36 |
| 13 | **8× ESC Readytosky 40A 2–6S OPTO** (2 packs de 4 → 6 para los motores + 2 de repuesto) | configurar **modo 3D/reversa** en BLHeliSuite32 + encapsular en epoxi (acuáticos) | 2 × 40 = 80 |
| 14 | Anillos de boquilla impresos | nozzle | 5 |

**Subtotal propulsión: ≈ 239**

## 4. Energía — doble batería 20 V a prueba de todo (cero precauciones)

Diseño autónomo: conectas cualquier batería (llena, a medio usar, incluso descargada) en cualquier orden y el sistema se protege solo.

| # | Componente | Specs | Precio |
|---|---|---|---|
| 15 | **DEWALT DCB205-2C** (kit: 2× batería 20 V MAX XR 5.0 Ah **+ cargador**) | BMS integrado: corte automático por sobredescarga, sobrecarga, corto y sobrecorriente. 18 V nominal / 21 V cargada, 90 Wh c/u, 20 A continuos | **149** (las 2 baterías + cargador) * |
| 16 | 2× adaptador pack-herramienta → XT60 **anti-chispa** | sin arco al conectar, polaridad mecánicamente imposible de invertir | 2 × 12 = 24 |
| 17 | 2× módulo **corte por bajo voltaje (LVD)** 40 A | desconecta la batería sola al llegar a 15,0 V — imposible dañarla por descarga | 2 × 15 = 30 |
| 18 | 2× **diodo-ideal ORing 60 A** | cambio automático entre baterías sin corte (5–30 V) | 2 × 12 = 24 |
| 19 | 2× **interruptor automático (breaker) 40 A** | si hay un corto, se dispara y se rearma con un clic (no cambia fusibles) | 2 × 8 = 16 |
| 20 | Banco de capacitores 1000 µF/35 V + **TVS 30 V** | absorben picos de arranque de motores y regeneración | 10 |
| 21 | Reguladores 5 V/12 V de **entrada ancha (9–40 V)** | aguantan cualquier voltaje de batería sin quemarse | 14 |
| 22 | 2× sensor INA219 | mide V/A de cada batería → app | 2 × 4 = 8 |
| 23 | Sensor de temperatura DS18B20 | alarma en la app si el compartimento de baterías calienta | 2 |
| 24 | **La "puertita" de carga**: hatch lateral estanco + conector XT60 de panel | carga desde la pared sin abrir el casco | 17 |
| 25 | 2× módulo **cargador CC-CV 21 V/3 A con balance** (compatible packs DeWalt, con emulación de termistor) | cargan los packs a bordo con seguridad | 2 × 30 = 60 |
| 26 | Fuente de pared 24 V/90 W | se conecta a la puertita (solo sub en seco) | 20 |

\* Equivalentes si prefieres otra marca (mismo concepto "18/20 V MAX"): **Makita BL1850B** (kit BL1850B-2) · **Milwaukee M18 B5** (kit M18 B5-502) · **Ryobi ONE+ 5 Ah** (el más económico). Si ya tienes herramientas y baterías, valen **0** — solo compra los adaptadores.

**Subtotal energía: ≈ 375** (o ≈ 225 con baterías propias)

### 🛡️ Por qué NO necesita precauciones

| Riesgo | Lo elimina |
|---|---|
| Chispa/arco al conectar | Adaptadores anti-chispa |
| Conectar al revés | Conector de herramienta: físicamente asimétrico |
| Descarga profunda (daña batería) | BMS del pack + módulo LVD a 15 V |
| Cortocircuito | Breaker rearmable + BMS |
| Sobrecarga al cargar | Cargador de la marca (corta solo) — cargas como un celular |
| Corriente inversa entre baterías | Diodo-ideal |
| Picos de los motores | Banco de capacitores + TVS |
| Voltaje incorrecto quema electrónica | Reguladores de entrada ancha + ESCs 2–6S |
| Sobrecalentamiento | Breaker + BMS + sensor DS18B20 con alarma en la app |
| Carga mal hecha | Cargador CC-CV a bordo con balance: enchufas la fuente y listo (como un celular) |

**Carga:** dos modos — (1) packs en su cargador DeWalt de pared, o (2) **desde la puertita** con la fuente de 24 V. Con `companero_carga.py` en la Pi: mientras carga las **4 luces parpadean lento** y al completar **parpadean rápido** (aviso de desconectar). Solo con el sub en seco.

## 5. Electrónica central

| # | Componente | Specs | Precio |
|---|---|---|---|
| 19 | Raspberry Pi 4 (2 GB) | companion con ArduSub | 65 |
| 20 | Tarjeta microSD 32 GB | A2 | 8 |
| 21 | Sensor presión MS5837-30BA | profundidad hasta 300 m | 22 |
| 22 | IMU BNO055 (o MPU6050) | estabilización + **sensor de golpes** | 15 |
| 23 | 2× PCA9685 16 canales I2C | #1 (dir. 0x40): salidas de ArduSub (motores + auxiliares) · #2 (dir. 0x41): servos de cámaras PTZ | 2 × 8 = 16 |

**Subtotal electrónica: ≈ 118**

## 6. Las 5 cámaras (3 PTZ 360°)

| # | Componente | Specs | Precio |
|---|---|---|---|
| 24 | CAM1 Punta: **ELP USB con sensor Sony IMX291 "Starvis"** + lente 170° | brilla en poca luz, video principal | 22 |
| 25 | CAM3 Abajo: **ELP mini (IMX307/IMX291)** | mira la pinza con poca luz | 18 |
| 26 | CAM2 Arriba: **domo PTZ** = módulo **ELP mini** + cúpula acrílica + anillo 6 LEDs blancos + servo 360° | vigilancia con luz propia para oscuridad | 15 + 10 |
| 27 | CAM4 Izquierda: **domo PTZ** (igual) | vigilancia con luz propia | 15 + 10 |
| 28 | CAM5 Derecha: **domo PTZ** (igual) | vigilancia con luz propia | 15 + 10 |
| 29 | 3× soportes PTZ impresos | estancos con O-ring | 9 |

**Subtotal cámaras: ≈ 124**

## 7. Luces (4 × 10 W a 90°)

| # | Componente | Specs | Precio |
|---|---|---|---|
| 30 | 4× LED buceo 10 W | lente 90°, ~1100 lm c/u | 4 × 12 = 48 |
| 31 | 4× relé/MOSFET 12 V | control por canales 8–9 | 8 |
| 32 | 18× LED blanco 5 mm potente (anillos de los 3 domos PTZ) | luz propia de cada domo (canal 15) | 12 |
| 33 | MOSFET canal 15 + 3 resistencias | enciende los 3 anillos a la vez | 3 |

**Subtotal luces: ≈ 71**

## 8. Arpoón con hilo (potencia plena a 2 m)

| # | Componente | Specs | Precio |
|---|---|---|---|
| 32 | Cañón + arpón de acero inox | Ø6–7 mm, punta tri-corte | 20 |
| 33 | 2× gomas/bandas de látex 16 mm | tensión máxima → 2 m sin perder potencia | 12 |
| 34 | Hilo monofilamento 100–150 kg | 30 m (no se suelta: fijado en carrete) | 10 |
| 35 | Carrete motorizado + motor N20 | recoge el hilo (F5 en la app) | 10 |
| 36 | Gimbal 2 servos MG90S | yaw + pitch del apuntado | 14 |
| 37 | Servo disparador MG90S | gatillo (seguro por software) | 6 |
| 38 | Piezas impresas + anclas | 3D | 6 |

**Subtotal arpoón: ≈ 78**

## 9. Pinza de agarre reforzado

| # | Componente | Specs | Precio |
|---|---|---|---|
| 39 | Servo MG996R metálico | 20 kg·cm — agarre fuerte | 10 |
| 40 | Dedos dentados de acero inox | + goma antideslizante | 8 |
| 41 | Módulo sellado impreso + O-ring | eje estanco | 6 |

**Subtotal pinza: ≈ 24**

## 10. Tether 20 m + consola

| # | Componente | Specs | Precio |
|---|---|---|---|
| 42 | Cable Cat6 fino (slim) 20 m | video + control + telemetría | 12 |
| 43 | Conector RJ45 IP68 | desconectable del sub | 10 |
| 44 | Carrete de pesca/barrilete | recoge el cable en la compu | 15 |
| 45 | Adaptador USB 3.0 → RJ45 | si tu PC no tiene puerto de red | 8 |

**Subtotal tether: ≈ 45**

---

## 💰 TOTAL DEL PROYECTO

| Bloque | Costo |
|---|---|
| Casco presurizado | ~115 |
| Frame + flotabilidad | ~40 |
| 6 motores + ESCs | ~239 |
| Energía (2 baterías 20 V herramienta, cero precauciones) | ~278 |
| Electrónica central | ~118 |
| 5 cámaras (3 PTZ) | ~105 |
| 4 luces 10 W | ~56 |
| Arpoón + hilo + gimbal | ~78 |
| Pinza reforzada | ~24 |
| Tether + consola | ~45 |
| **TOTAL** | **≈ 1.230 USD** (≈ 1.080 si ya tienes las baterías DeWalt) |

### Versiones ajustadas
- **Económica (~700):** 4 motores en vez de 6, 3 cámaras (1 PTZ), luces 2 × 10 W, 1 sola batería.
- **Recomendada (~1.230):** todo lo de esta lista (la de este proyecto).
- **Pro (~1.300):** Pi 5, cámaras de mayor luminosidad, lastre activo, 2° batería extra.

### ⚡ Variante con baterías de 20 V (5S)
- **20 V = 5 celdas**: LiPo 5S (18,5 V nominal / 21 V cargada) o **baterías de herramientas** DeWalt/Makita "20V MAX" (18 V nominal / 21 V cargada).
- **Ventaja:** +20–25% de velocidad y empuje (los motores giran más rápido).
- **Requisitos al comprar:** ESCs soportando 2–6S (≥25 V), reguladores 5 V/12 V de entrada ancha (hasta 36 V), cargador de balanceo 5S — o simplemente el cargador de tu marca de herramientas.
- **Atajo económico:** si ya tienes herramientas de 20 V, compra 2 adaptadores XT60 para pack de herramienta (~10 c/u) y usa esas baterías → ahorras ~120 USD.
- El resto del sistema (diodo-ideal ORing, INA219, app) funciona sin cambios; ajusta `capacidad_wh` en `subcontrol_config.json` (5S 10 Ah ≈ 185 Wh; pack herramienta 5 Ah ≈ 100 Wh).

### Herramientas necesarias (si no tienes)
Soldador + estaño, pistola de silicona/epoxi, impresión 3D (o servicio ~30), taladro, multímetro: **≈ 80–150** (inversión única).

### Dónde comprar
- AliExpress / Amazon: motores, ESCs, LiPo, cámaras USB, PCA9685.
- Tiendas de hobbista RC locales: LiPo (mejor calidad/certificadas), gomas de fusil.
- Ferreterías: PVC, herrajes, epoxi.
- **Importante:** compra las LiPo de marcas certificadas y carga siempre con supervisión.
