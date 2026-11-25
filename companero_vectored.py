#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
companero_vectored.py — corre en la Raspberry Pi DENTRO del submarino.

Controla los 2 PODS LATERALES GIRATORIOS (empuje vectorizado):
  · Recibe por UDP (puerto 14552):  "POD <angulo> <empuje>"
      <angulo>:  -90..+90 grados (0 = hacia adelante)
      <empuje>:  0.0 .. 1.0
  · Mueve por I2C (PCA9685 #2, dirección 0x41):
      ch4 = ESC pod izquierdo   · ch5 = ESC pod derecho
      ch6 = servo pod izquierdo · ch7 = servo pod derecho

Los pods giran COMPLETOS (motor sellado montado sobre el servo sumergible
DS3218 IP67); los cables pasan por un anillo deslizante de 6 hilos.

Instalación en la Pi:
    pip install adafruit-circuitpython-servokit
    pca9685 #2 con puente A0 (dirección 0x41)
    python3 companero_vectored.py &   (o servicio systemd)
"""
import socket
import time

PUERTO = 14552
CH_ESC_IZQ, CH_ESC_DER = 4, 5
CH_SERVO_IZQ, CH_SERVO_DER = 6, 7
ANG_SUAVE = 0.35          # suavizado del giro del servo (0..1)

try:
    from adafruit_servokit import ServoKit
    kit = ServoKit(channels=16, address=0x41)
    OK = True
except Exception as e:
    print("ServoKit #2 no disponible (modo simulación):", e)
    OK = False

ang_obj, emp_obj = 0.0, 0.0
ang_act, emp_act = 0.0, 0.0


def aplicar():
    global ang_act, emp_act
    ang_act += (ang_obj - ang_act) * ANG_SUAVE
    emp_act += (emp_obj - emp_act) * ANG_SUAVE
    if OK:
        # ESC en modo 3D/reversa: 1500 = neutro (usamos solo adelante)
        pulso = 1500 + max(0.0, min(1.0, emp_act)) * 400
        for ch in (CH_ESC_IZQ, CH_ESC_DER):
            kit.servo[ch].angle = (pulso - 1500) / 500 * 90 + 90
        # servos: 90° = pod mirando adelante; ±90° = lados
        for ch in (CH_SERVO_IZQ, CH_SERVO_DER):
            kit.servo[ch].angle = 90 + max(-90.0, min(90.0, ang_act)) * 0.5


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PUERTO))
    sock.settimeout(0.1)
    print(f"companero_vectored escuchando UDP :{PUERTO} …")
    while True:
        try:
            datos, _ = sock.recvfrom(64)
            partes = datos.decode("utf-8", "ignore").strip().split()
            if len(partes) == 3 and partes[0] == "POD":
                ang_obj = max(-90.0, min(90.0, float(partes[1])))
                emp_obj = max(0.0, min(1.0, float(partes[2])))
        except socket.timeout:
            emp_obj = 0.0        # sin órdenes: motores de pods a neutro
        except Exception as e:
            print("Error:", e)
            time.sleep(0.3)
        aplicar()
        time.sleep(0.02)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
