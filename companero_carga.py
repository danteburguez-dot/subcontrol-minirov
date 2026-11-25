#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
companero_carga.py — corre en la Raspberry Pi DENTRO del submarino.

Vigila la carga de las 2 baterías DeWalt 20V (conectadas por la "puertita"
de carga al costado del casco) y usa las 4 luces del sub como indicador:

  · CARGANDO          → las 4 luces parpadean LENTO (1 s ON / 1 s OFF)
  · CARGA COMPLETA    → las 4 luces parpadean RÁPIDO (0,2 s) durante 10 min
  · Sin carga activa  → luces apagadas

Requisitos en la Pi:
    pip install pi-ina219 smbus2 pymavlink
    Sensores INA219: batería A en 0x44 · batería B en 0x45
    En BlueOS: Instancias MAVLink → añadir endpoint UDP saliente
               a 127.0.0.1:14560 (para recibir aquí el heartbeat)
    Ejecutar al arranque: python3 companero_carga.py &  (o servicio systemd)

Nota: cargar SOLO con el submarino en seco (nunca en el agua).
"""
import time
import sys

FULL_V = 20.4        # pack DeWalt "lleno" (21,0 V cargada; margen)
FULL_A = 0.5         # corriente de carga bajo este valor = llena
T_BLINK_COMPLETA = 600   # 10 min de parpadeo rápido al completar
LUCES_CH = (8, 9)    # canales RC de los 2 pares de luces

DIR_A, DIR_B = 0x44, 0x45


def leer_ina219(direccion):
    """Devuelve (voltaje, corriente_abs) del sensor; (None, None) si falla."""
    try:
        from ina219 import INA219
        ina = INA219(shunt_ohms=0.1, address=direccion)
        ina.configure()
        v = ina.voltage()
        a = abs(ina.current() / 1000.0)
        return v, a
    except Exception:
        return None, None


class Luces:
    """Enciende/apaga los 2 pares de luces vía MAVLink (canales RC 8 y 9)."""

    def __init__(self):
        self.master = None
        self.on = False

    def conectar(self):
        try:
            from pymavlink import mavutil
            self.master = mavutil.mavlink_connection(
                "udpin:0.0.0.0:14560", source_system=255, source_component=191)
            self.master.wait_heartbeat(timeout=15)
            print("companero_carga: enlace MAVLink local OK")
            return True
        except Exception as e:
            print("companero_carga: sin MAVLink (solo simulación):", e)
            self.master = None
            return False

    def set(self, on):
        if on == self.on:
            return
        self.on = on
        if self.master is None:
            return
        try:
            ch = [0] * 16
            for c in LUCES_CH:
                ch[c - 1] = 1900 if on else 1000
            self.master.mav.rc_channels_override_send(
                self.master.target_system, 1, *ch)
        except Exception:
            pass


def main():
    print("companero_carga: vigilando la carga…")
    luces = Luces()
    luces.conectar()

    fase = "reposo"          # reposo | cargando | completa
    t_fase = time.time()
    t_ultimo_blink = 0.0
    estado_blink = False
    avisado_completa = False

    while True:
        va, aa = leer_ina219(DIR_A)
        vb, ab = leer_ina219(DIR_B)
        volts = [v for v in (va, vb) if v is not None]
        amps = [a for a in (aa, ab) if a is not None]

        cargando = any(a > FULL_A for a in amps) if amps else False
        llenas = (len(volts) == 2 and all(v >= FULL_V for v in volts)
                  and not cargando)

        ahora = time.time()
        if cargando and fase != "cargando":
            fase, t_fase = "cargando", ahora
            print("🔌 Cargando — luces parpadeando lento")
        elif llenas and fase != "completa" and not avisado_completa:
            fase, t_fase = "completa", ahora
            print("✅ CARGA COMPLETA — luces parpadeando rápido (10 min)")
        elif fase == "cargando" and not cargando and not llenas:
            fase = "reposo"
            print("⏸ Carga interrumpida — luces apagadas")

        if fase == "cargando":
            # parpadeo LENTO: 1 s ON / 1 s OFF
            if ahora - t_ultimo_blink >= 1.0:
                t_ultimo_blink = ahora
                estado_blink = not estado_blink
                luces.set(estado_blink)
        elif fase == "completa":
            # parpadeo RÁPIDO: 0,2 s ON / 0,2 s OFF, durante 10 min
            if ahora - t_ultimo_blink >= 0.2:
                t_ultimo_blink = ahora
                estado_blink = not estado_blink
                luces.set(estado_blink)
            if ahora - t_fase > T_BLINK_COMPLETA:
                luces.set(False)
                fase = "reposo"
                avisado_completa = True
                print("Fin del aviso de carga completa.")
        else:
            if not llenas:
                avisado_completa = False
            luces.set(False)

        time.sleep(0.05)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
