# 🌊 SUBCONTROL — Mini-ROV submarino con arpoón, PTZ y auto-apuntado

Estación de control en PC para un mini-submarino teledirigido por cable de 20 m:

- **8 motores** sellados: 4 en popa + 2 laterales (hélices mirando atrás) + **2 pods giratorios** que hacen subir/bajar y el retroceso fino
- **5 cámaras** (punta, arriba, abajo, izquierda, derecha) — **3 domos PTZ 360°** con luz propia (anillo LED) para vigilar en la oscuridad
- Vista tipo videollamada: cámara principal + miniaturas (clic para cambiar)
- **4 luces LED de 10 W** (cada 90°) controladas por parejas
- **Arpoón** con gimbal de autoapuntado, disparo a potencia plena hasta 2 m,
  hilo de alta resistencia (100–150 kg) fijado a **carrete motorizado** (recoger con un botón)
- **Pinza reforzada** (servo 20 kg·cm, dedos dentados de acero) + **AUTO-GANCHO**:
  el sub aproxima, alinea y cierra la pinza solo
- **Sensor de golpes** (IMU): detecta impactos y **los marca en rojo en el modelo 3D en vivo**
- **Modelo 3D en la pantalla** en todo momento, con **hélices girando según el empuje real**
- Telemetría: profundidad, rumbo, batería (%/V/min restantes), modo y armado
- **Sistema de emergencia**: parada (F1), subida a superficie (F2), normalizar (F3)
- **Doble batería LiPo con conmutación automática** (diodo-ideal): si una se agota, la otra toma el control sin corte
- Control por **teclado y mando** (Xbox/PS4)
- MODO DEMO integrado: prueba toda la app sin el submarino conectado

## 🚀 Uso rápido

1. Descarga o clona este repo.
2. Conecta el cable del sub a tu PC y enciende el sub.
3. Ejecuta `SubControl.exe` (está en `dist/` tras compilarlo; ver abajo).
4. Sin sub: la app abre en **MODO DEMO** — juega con todo.

> 📖 Manual completo: [`MANUAL_DE_CONTROL.md`](MANUAL_DE_CONTROL.md)
> 🔩 Componentes y costos: [`COMPONENTES.md`](COMPONENTES.md)

## 🎮 Controles rápidos (teclado)

| | |
|---|---|
| WASD + E/Q + ←→ | moverse |
| `,` `.` + `/` | cámaras PTZ 360° / vigilancia automática |
| `C` | auto-gancho (agarre automático) |
| `U/I/O/K` + `Y` + `P` + `F4` | arpoón: apuntar / autoaim / seguro / disparar |
| `F5` | recoger hilo |
| `G`/`H` | pinza abrir/cerrar |
| `1`/`2`/`L` | luces |
| `F1`/`F2`/`F3` | emergencias |

Mando Xbox/PS4: sticks para moverse, A/B luces, X/Y pinza, LB/RB emergencias, D-pad para el arpoón.

## 🏗️ Construir el ejecutable

```bat
build.bat
```
o manualmente:
```bat
python -m pip install -r requirements.txt
python -m PyInstaller --onefile --noconsole --clean --name SubControl ^
    --hidden-import pymavlink.dialects.v20.ardupilotmega subcontrol.py
```
→ genera `dist\SubControl.exe` (~85 MB).

## 📁 Estructura del proyecto

```
SubControl/
├── SubControl.exe           # ▶ EL EJECUTABLE — doble clic para abrir la app
├── subcontrol.py            # Aplicación de control (fuente principal)
├── companero_ptz.py         # Script para la Raspberry Pi: servos PTZ 360°
├── companero_carga.py       # Script para la Pi: indicador de carga con las luces
├── requirements.txt         # Dependencias
├── build.bat                # Compila el .exe (lo deja en la raíz del proyecto)
├── MANUAL_DE_CONTROL.md     # 📖 Manual de uso completo
├── MONTAJE.md               # 🔧 Manual de construcción fase por fase
├── COMPONENTES.md           # 🔩 Lista de materiales con precios (~1.230 USD)
├── CARRITO_ALIEXPRESS.md    # 🛒 Carrito de compra con búsquedas y precios USD
└── modelo3d/
    ├── modelo3d.scad        # Modelo paramétrico (OpenSCAD)
    ├── generar_stl.py       # Generador del modelo 3D (trimesh)
    ├── submarino.stl        # Modelo exportado (imprimir/ver)
    └── submarino.glb        # Modelo con colores (ábrela con Visor 3D de Windows)
```

## 🔌 Conexión al submarino real

- **Sub:** Raspberry Pi 4 + ArduSub, cámaras RTSP, MAVLink UDP 14550.
- **PTZ:** ejecuta `companero_ptz.py` en la Pi (UDP 14551 + PCA9685).
- **Red:** PC en `192.168.2.2/24`, sub en `192.168.2.1`. Todo configurable en
  `subcontrol_config.json` (se crea junto al .exe) o desde el panel Ajustes.

## 🛡️ Seguridad

El submarino debe ser **flotante positivo**, con failsafe de subida a superficie.
Prueba siempre en agua poco profunda primero. Respeta la normativa de pesca local.

## Licencia

Uso libre para proyectos personales/educativos.
