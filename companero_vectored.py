#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
companero_vectored.py — corre en la Raspberry Pi DENTRO del submarino.

Controla los 2 PODS LATERALES GIRATORIOS (empuje vectorizado):
  · Recibe por UDP (puerto 14552):
      "POD <ang_izq> <emp_izq> <ang_der> <emp_der>"
      <ang>: 0 = hacia adelante · 90 = hacia el costado · 180 = hacia atrás
      <emp>: 0.0 .. 1.0
    (también acepta el formato viejo de 3 campos para compatibilidad)
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

# objetivos y valores actuales (izquierda / derecha)
ang_obj_i = ang_obj_d = 0.0
emp_obj_i = emp_obj_d = 0.0
ang_act_i = ang_act_d = 0.0
emp_act_i = emp_act_d = 0.0


def aplicar():
    global ang_act_i, ang_act_d, emp_act_i, emp_act_d
    ang_act_i += (ang_obj_i - ang_act_i) * ANG_SUAVE
    ang_act_d += (ang_obj_d - ang_act_d) * ANG_SUAVE
    emp_act_i += (emp_obj_i - emp_act_i) * ANG_SUAVE
    emp_act_d += (emp_obj_d - emp_act_d) * ANG_SUAVE
    if OK:
        # ESC en modo 3D/reversa: usamos solo adelante (el POD apunta la dirección)
        for ch, e in ((CH_ESC_IZQ, emp_act_i), (CH_ESC_DER, emp_act_d)):
            pulso = 1500 + max(0.0, min(1.0, e)) * 400
            kit.servo[ch].angle = (pulso - 1500) / 500 * 90 + 90
        # servos: 90° = pod mirando adelante · 0° = atrás · 45/135 = costados
        for ch, a in ((CH_SERVO_IZQ, ang_act_i), (CH_SERVO_DER, ang_act_d)):
            kit.servo[ch].angle = 90 + max(-90.0, min(180.0, a)) * 0.5


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PUERTO))
    sock.settimeout(0.1)
    print(f"companero_vectored escuchando UDP :{PUERTO} …")
    while True:
        try:
            datos, _ = sock.recvfrom(96)
            partes = datos.decode("utf-8", "ignore").strip().split()
            if len(partes) == 5 and partes[0] == "POD":
                ang_obj_i = max(0.0, min(180.0, float(partes[1]) % 360.0))
                emp_obj_i = max(0.0, min(1.0, float(partes[2])))
                ang_obj_d = max(0.0, min(180.0, float(partes[3]) % 360.0))
                emp_obj_d = max(0.0, min(1.0, float(partes[4])))
            elif len(partes) == 3 and partes[0] == "POD":   # formato viejo
                a = max(-90.0, min(90.0, float(partes[1])))
                ang_obj_i = ang_obj_d = a
                emp_obj_i = emp_obj_d = max(0.0, min(1.0, float(partes[2])))
        except socket.timeout:
            emp_obj_i = emp_obj_d = 0.0    # sin órdenes: pods a neutro
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
