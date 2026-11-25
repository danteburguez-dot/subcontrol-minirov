#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
companero_ptz.py — Corre en la Raspberry Pi DENTRO del submarino.

Recibe por UDP (puerto 14551) mensajes:  "PTZ <cam> <angulo>"
   <cam>:   1 = Arriba · 3 = Izquierda · 4 = Derecha   (índices de la app)
   <angulo>: 0-360° donde apunta la cámara

Mueve los servos de giro 360° de las cámaras PTZ vía PCA9685 (I2C).

Instalación en la Pi:
    pip install adafruit-circuitpython-servokit
    Conectar el PCA9685 al I2C de la Pi (SDA=GPIO2, SCL=GPIO3, VCC 5V)
    Servos PTZ en canales: CAM Arriba → ch 0 · CAM Izquierda → ch 1 · CAM Derecha → ch 2
    Ejecutar al arranque:  python3 companero_ptz.py &   (o como servicio systemd)

NOTA: usa servos de rotación continua (360°). Como no tienen feedback de
posición absoluta, el script gira durante el tiempo necesario para llegar al
ángulo pedido (control en lazo abierto con calibración VEL_GRADOS_POR_SEG).
"""
import socket
import time

PUERTO = 14551
ANG_ACTUAL = {1: 0.0, 3: 0.0, 4: 0.0}     # ángulo actual estimado por cámara
SERVO_CANAL = {1: 0, 3: 1, 4: 2}          # canal PCA9685 de cada cámara PTZ
VEL_GRADOS_POR_SEG = 60.0                 # calibrar con tu servo
VENTANA = 1.2                             # s de giro máximo por comando

try:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16)
    SERVOS_OK = True
except Exception as e:
    print("ServoKit no disponible (modo simulación):", e)
    SERVOS_OK = False


def girar_hacia(cam, objetivo):
    """Gira la cámara `cam` hasta `objetivo` grados por el camino más corto."""
    actual = ANG_ACTUAL[cam]
    delta = ((objetivo - actual + 180) % 360) - 180   # -180..180
    if abs(delta) < 1.0:
        return
    duracion = min(VENTANA, abs(delta) / VEL_GRADOS_POR_SEG)
    canal = SERVO_CANAL[cam]
    if SERVOS_OK:
        # signo: ajusta si tu servo gira al revés (cambia - por +)
        kit.servo[canal].angle = 90 - (100 if delta > 0 else -100) * 0.4
        time.sleep(duracion)
        kit.servo[canal].angle = 90                    # parar
    ANG_ACTUAL[cam] = (actual + delta) % 360
    print(f"CAM {cam}: {actual:.0f}° → {ANG_ACTUAL[cam]:.0f}° (Δ{delta:.0f}°)")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PUERTO))
    sock.settimeout(2.0)
    print(f"companero_ptz escuchando UDP :{PUERTO} …")
    while True:
        try:
            datos, _ = sock.recvfrom(64)
            texto = datos.decode("utf-8", "ignore").strip()
            partes = texto.split()
            if len(partes) == 3 and partes[0] == "PTZ":
                cam = int(partes[1])
                objetivo = float(partes[2]) % 360.0
                if cam in ANG_ACTUAL:
                    girar_hacia(cam, objetivo)
        except socket.timeout:
            continue
        except Exception as e:
            print("Error:", e)
            time.sleep(0.5)


if __name__ == "__main__":
    main()
