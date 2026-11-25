# 📖 MANUAL DE CONTROL — SUBCONTROL v1.0

Manual completo para pilotar el mini-ROV desde tu computadora.
El sub: 6 motores · 5 cámaras (3 con giro 360°) · 4 luces 10 W · arpoón con hilo ·
pinza reforzada · sensor de golpes · modelo 3D en vivo.

---

## 1. Antes de empezar

1. Conecta el cable de 20 m del submarino a tu PC (puerto RJ45 o adaptador USB→Ethernet).
2. Enciende la batería del submarino (bahía de cambio rápido: abre el hatch popero, conecta la batería con su XT60).
3. Primera vez: configura tu adaptador de red con IP fija `192.168.2.2`, máscara `255.255.255.0`.
4. Abre `SubControl.exe`. El punto de estado dirá:
   - 🟢 **CONECTADO** → enlace con el sub activo.
   - 🟠 **MODO DEMO** → sin sub conectado (puedes practicar todo igual).

## 2. Control por TECLADO

| Tecla | Acción |
|---|---|
| `W` / `S` | Adelante / Atrás |
| `A` / `D` | Lateral izquierda / derecha |
| `E` / `Q` | Subir / Bajar |
| `←` / `→` | Girar (yaw) |
| `ESPACIO` | Parada inmediata de motores |
| `1` / `2` | Luces par superior / inferior (ON-OFF) |
| `3` | Luces de los domos PTZ (ON-OFF) |
| `L` | Todas las luces (ON-OFF) |
| `G` (mantener) | Abrir pinza |
| `H` (mantener) | Cerrar pinza |
| `C` | 🎯 AUTO-GANCHO ON/OFF (aproxima y agarra solo) |
| `U` / `O` | Arpoón: gimbal izquierda / derecha |
| `I` / `K` | Arpoón: gimbal arriba / abajo |
| `Y` | Autoapuntado del arpoón ON/OFF |
| `P` | SEGURO del arpoón ON/OFF |
| `F4` | 🎯 Disparar arpoón |
| `F5` (mantener) | ⏪ Recoger hilo (carrete motorizado) |
| `,` / `.` | Girar cámara PTZ seleccionada (360°) |
| `/` | Vigilancia automática (la PTZ gira sola) |
| `F1` | ⛔ PARADA DE EMERGENCIA |
| `F2` | ⬆ SUBIDA DE EMERGENCIA |
| `F3` | Normalizar emergencia |

> Los controles funcionan cuando la ventana de SUBCONTROL tiene el foco.
> El **empuje sube y baja de a poco** (~1 s de rampa) para cuidar baterías y ESCs; en emergencias la potencia es inmediata.

## 3. Control por MANDO (Xbox / PS4)

| Botón | Acción |
|---|---|
| Stick izquierdo | Moverse (adelante / lateral) |
| Stick derecho X / Y | Girar / Subir-bajar |
| `A` / `B` | Luces 1 / 2 |
| `X` (mantener) | Abrir pinza |
| `Y` (mantener) | Cerrar pinza |
| `LB` | ⛔ Parada de emergencia |
| `RB` | ⬆ Subida de emergencia |
| `Back` | Normalizar emergencia |
| `Start` | Armar / Desarmar |
| D-pad ↑ | Disparar arpoón |
| D-pad ↓ | Seguro arpoón |
| D-pad ← | Autoapuntado |
| D-pad → (mantener) | Recoger hilo |

## 4. Las 5 cámaras (3 con giro 360°)

| # | Posición | Tipo |
|---|---|---|
| CAM 1 | **Punta** (en el domo) | Fija — cámara del arpoón y del autoapuntado |
| CAM 2 | **Arriba** | 🔵 Domo PTZ 360° con luz propia (tecla `3`) |
| CAM 3 | **Abajo** | Fija — mira la pinza y el fondo (auto-gancho) |
| CAM 4 | **Izquierda** | 🔵 PTZ 360° — vigilancia |
| CAM 5 | **Derecha** | 🔵 PTZ 360° — vigilancia |

- **Vista tipo videollamada:** la cámara principal va grande; las demás, como miniaturas a la derecha. **Haz clic en una miniatura** para agrandarla.
- **Retícula "+":** las cámaras PTZ muestran una cruz "+" en el centro con su ángulo de giro (0–360°) para apuntar la vigilancia.
- **Girar una PTZ:** clic en su miniatura → teclas `,` (izquierda) y `.` (derecha). Con `/` activas la **vigilancia automática**: la cámara gira sola sin parar para vigilar el área.
- En el **modelo 3D en vivo** verás una flecha azul que gira mostrando hacia dónde apunta cada cámara PTZ.

## 5. Modelo 3D en vivo (debajo de la cámara principal)

- Muestra el submarino completo en todo momento: casco, 6 motores, aletas, luces, arpoón, pinza y batería.
- **Las 6 hélices giran según el empuje real** que estás mandando (más throttle = giro más rápido).
- **Arrastra** con el ratón para girar la vista, **rueda** para zoom, **doble clic** para reset.
- **Sensor de golpes:** la IMU del sub detecta impactos por encima del umbral (3 g). Al recibir un golpe:
  - Suena/parpadea el aviso **💥 GOLPE** y **la zona golpeada se ilumina en rojo parpadeante** en el modelo 3D.
  - Se registra el lado (frontal, popa, lateral izq/der, superior, inferior) y la fuerza en "g" en el contador de golpes.
  - Botón **"Simular golpe"** para probarlo en modo demo.

## 6. Telemetría y energía

- **PROFUNDIDAD** (metros), **Rumbo** (grados), **batería** (% · V · minutos estimados restantes).
- **Modo**: STABILIZE (estabilizado), ALT_HOLD (profundidad fija), MANUAL, POSHOLD.
- **ARMADO** en rojo = motores listos.

## 7. Arpoón: disparo con hilo (5 pasos)

1. Pon la **CAM 1 (punta)** en grande.
2. Con `Y` activa el **autoapuntado**: detecta el pez (rectángulo naranja) y centra la retícula con el gimbal. Manual: `U/I/O/K`.
3. Quita el **SEGURO** con `P` (botón verde).
4. Dispara con `F4`. El arpón sale a **potencia plena hasta ~2 m** (gomas a máxima tensión: la fuerza no cae en todo el recorrido). El carrete suelta hilo 0.6 s para no frenar el tiro.
5. Recoge el hilo con `F5` (mantener): el carrete motorizado trae de vuelta el arpón con la presa.

**El hilo (100–150 kg de resistencia) va fijado al carrete: nunca se suelta.** Si la presa escapa, recuperas arpón y línea.

## 8. Pinza + AUTO-GANCHO (caza sin esforzarte)

1. Activa `C` (AUTO-GANCHO).
2. El sub busca el objetivo con la CAM punta, se orienta hacia él y avanza solo.
3. Cuando el objetivo entra en la **CAM abajo** (retícula amarilla), el sub se alinea exactamente sobre la presa.
4. Al estar centrado y cerca: **cierra la pinza automáticamente** (agarre reforzado: servo 20 kg·cm + dedos dentados) y el estado pasa a "¡PRESA AGARRADA!".
5. Sube con `E` y recoge.

Puedes hacerlo a mano siempre: `G`/`H` para la pinza y los sticks para acercarte.

## 9. Emergencias

- **F1 — PARADA DE EMERGENCIA:** motores a cero + desarme + arpoón en seguro.
- **F2 — SUBIDA DE EMERGENCIA:** empuje vertical a tope, 4 luces ON, pinza abierta (suelta la presa) hasta superficie.
- **F3 — NORMALIZAR:** cancela la emergencia.
- El cable de 20 m también sirve para **halvar el sub a mano** en rescate.

## 10. Doble batería DeWalt 20 V con cambio automático

- El sub lleva **2 packs DeWalt DCB205 20V MAX 5Ah** con módulos diodo-ideal: la que tiene más voltaje alimenta todo y, cuando una se agota, **la otra toma el control en microsegundos — sin corte**.
- Con los sensores INA219 la app puede mostrar las dos baterías por separado (Bat A / Bat B).
- **Carga modo 1:** saca los packs y ponlos en el cargador DeWalt — corta y balancea solo.
- **Carga modo 2 (la puertita):** con el sub **en seco**, conecta la fuente de pared 24 V al puerto lateral. Mientras carga, **las 4 luces parpadean LENTO**; cuando ambas baterías están llenas, **parpadean RÁPIDO** unos minutos (aviso de "desconecta"). Vigilado por `companero_carga.py` en la Pi.
- Reglas fijas: cargar **nunca** con el sub en el agua ni mojado; packs guardados secos y por debajo de 3 meses sin recargar.

## 11. Seguridad

- Primera salida: agua poco profunda y despejada.
- El sub debe ser **flotante positivo** (si se corta la energía, sube).
- Lava todo con agua dulce después de cada uso.
- Nunca dispares el arpoón hacia personas, el cable o nadadores.
- Respeta la normativa local de pesca (tallas, especies, zonas).

## 12. Solución de problemas

| Problema | Solución |
|---|---|
| No conecta (DEMO) | IP `192.168.2.1` en Ajustes, cable enchufado, batería ON, firewall de Windows. |
| No hay video | URLs RTSP en Ajustes; prueba cámara por cámara. |
| El sub se mueve al revés | `invertir_eje_z` en la configuración o invierte cables de motores. |
| El mando no responde | Conéctalo antes de abrir la app; prueba por USB. |
| Golpes falsos | Sube `umbral_golpe_g` (ej. 4.0) en `subcontrol_config.json`. |
| PTZ no gira | Verifica que `companero_ptz.py` corre en la Pi y el puerto 14551 es libre. |
