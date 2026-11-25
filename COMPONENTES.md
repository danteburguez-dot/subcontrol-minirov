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
| 13 | 6× ESC acuático 30–40 A | con condensador | 6 × 14 = 84 |
| 14 | Anillos de boquilla impresos | nozzle | 5 |

**Subtotal propulsión: ≈ 239**

## 4. Energía — doble batería con conmutación automática

| # | Componente | Specs | Precio |
|---|---|---|---|
| 15 | 2× batería LiPo 4S 10 Ah | plug XT60, marca certificada | 2 × 55 = 110 |
| 16 | 2× módulo diodo-ideal ORing 60 A | cambio automático sin corte (LTC4357) | 2 × 12 = 24 |
| 17 | 2× sensor INA219 | miden V/A de cada batería (I2C → app) | 2 × 4 = 8 |
| 18 | Cargador de balanceo 4S + fuente | carga A y B (o paraboard para ambas) | 35 |
| 19 | Regulador 5 V/12 V + fusibles | para Pi, luces, servos | 12 |
| 20 | Bolsas LiPo-safe ×2 + hatch | guardado y extracción | 12 |

**Subtotal energía: ≈ 201**

## 5. Electrónica central

| # | Componente | Specs | Precio |
|---|---|---|---|
| 19 | Raspberry Pi 4 (2 GB) | companion con ArduSub | 65 |
| 20 | Tarjeta microSD 32 GB | A2 | 8 |
| 21 | Sensor presión MS5837-30BA | profundidad hasta 300 m | 22 |
| 22 | IMU BNO055 (o MPU6050) | estabilización + **sensor de golpes** | 15 |
| 23 | PCA9685 16 canales I2C | servos PTZ + gimbal + extras | 8 |

**Subtotal electrónica: ≈ 118**

## 6. Las 5 cámaras (3 PTZ 360°)

| # | Componente | Specs | Precio |
|---|---|---|---|
| 24 | CAM1 Punta: cámara USB HD | en domo frontal | 18 |
| 25 | CAM3 Abajo: cámara USB HD | mira la pinza (fija) | 15 |
| 26 | CAM2 Arriba: USB + servo 360° | vigilancia PTZ | 15 + 6 |
| 27 | CAM4 Izquierda: USB + servo 360° | vigilancia PTZ | 15 + 6 |
| 28 | CAM5 Derecha: USB + servo 360° | vigilancia PTZ | 15 + 6 |
| 29 | 3× soportes PTZ impresos | estancos con O-ring | 9 |

**Subtotal cámaras: ≈ 105**

## 7. Luces (4 × 10 W a 90°)

| # | Componente | Specs | Precio |
|---|---|---|---|
| 30 | 4× LED buceo 10 W | lente 90°, ~1100 lm c/u | 4 × 12 = 48 |
| 31 | 4× relé/MOSFET 12 V | control por canales 8–9 | 8 |

**Subtotal luces: ≈ 56**

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
| Energía (2 baterías + conmutación auto + cargador) | ~201 |
| Electrónica central | ~118 |
| 5 cámaras (3 PTZ) | ~105 |
| 4 luces 10 W | ~56 |
| Arpoón + hilo + gimbal | ~78 |
| Pinza reforzada | ~24 |
| Tether + consola | ~45 |
| **TOTAL** | **≈ 1.020 USD** (900–1.150 según proveedor y envío) |

### Versiones ajustadas
- **Económica (~700):** 4 motores en vez de 6, 3 cámaras (1 PTZ), luces 2 × 10 W, 1 sola batería.
- **Recomendada (~1.020):** todo lo de esta lista (la de este proyecto).
- **Pro (~1.300):** Pi 5, cámaras de mayor luminosidad, lastre activo, 2° batería extra.

### Herramientas necesarias (si no tienes)
Soldador + estaño, pistola de silicona/epoxi, impresión 3D (o servicio ~30), taladro, multímetro: **≈ 80–150** (inversión única).

### Dónde comprar
- AliExpress / Amazon: motores, ESCs, LiPo, cámaras USB, PCA9685.
- Tiendas de hobbista RC locales: LiPo (mejor calidad/certificadas), gomas de fusil.
- Ferreterías: PVC, herrajes, epoxi.
- **Importante:** compra las LiPo de marcas certificadas y carga siempre con supervisión.
