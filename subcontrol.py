#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
 SUBCONTROL v1.0 — Estación de superficie para mini-ROV submarino
============================================================================
 Controles por TECLADO:
   W / S        : adelante / atrás
   A / D        : lateral izquierda / derecha
   E / Q        : subir / bajar
   ← / →        : girar (yaw)
   1            : luces par 1 (superiores)  ON/OFF
   2            : luces par 2 (inferiores)  ON/OFF
   3            : luces de los domos PTZ (cámaras 2/4/5) ON/OFF
   L            : todas las luces ON/OFF
   G (mantener) : abrir pinza
   H (mantener) : cerrar pinza
   U / O        : arpoón — girar gimbal izq / der
   I / K        : arpoón — subir / bajar gimbal
   Y            : autoapuntado ON/OFF
   P            : SEGURO del arpoón ON/OFF
   F4           : 🎯 DISPARAR ARPOÓN (requiere seguro QUITADO)
   F5 (mantener): recoger hilo del arpoón (carrete motorizado)
   , / .        : girar cámara PTZ seleccionada (360°)
   /            : vigilancia automática ON/OFF (la PTZ gira sola)
   C            : AUTO-GANCHO ON/OFF (aproxima y agarra solo)
   ESPACIO      : parada inmediata de motores
   F1           : ⛔ PARADA DE EMERGENCIA (motores a cero + desarme)
   F2           : ⬆ SUBIDA DE EMERGENCIA (emergir a superficie)
   F3           : normalizar (cancelar estado de emergencia)

 Controles por MANDO (Xbox / PS4, si hay mando conectado):
   Stick izq    : moverse (adelante/lateral)
   Stick der X  : girar          Stick der Y : subir/bajar
   A / B        : luces 1 / 2
   X (mantener) : abrir pinza    Y (mantener): cerrar pinza
   LB           : PARADA DE EMERGENCIA     RB : SUBIDA DE EMERGENCIA
   Back         : normalizar     Start : ARMAR / DESARMAR
   D-pad ↑      : disparar arpoón (con seguro quitado)
   D-pad ↓      : seguro ON/OFF    D-pad ← : autoapuntado
   D-pad →      : recoger hilo del arpoón (mantener)

 Sin submarino conectado la app entra en MODO DEMO (telemetría y video
 simulados) para probar toda la interfaz en el PC.
============================================================================
"""
from __future__ import annotations

import json
import math
import os
import queue
import random
import socket
import sys
import threading
import time

import tkinter as tk
from tkinter import ttk

import numpy as np

try:
    import cv2  # opencv-python-headless
    CV_OK = True
except Exception:
    CV_OK = False

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except Exception:
    PIL_OK = False

try:
    from pymavlink import mavutil
    import pymavlink.dialects.v20.ardupilotmega  # asegura el empaquetado
    MAV_OK = True
except Exception:
    MAV_OK = False

try:
    import pygame
    PYGAME_OK = True
except Exception:
    PYGAME_OK = False

VERSION = "1.0"

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "subcontrol_config.json")

# ----------------------------------------------------------------------------
# Configuración
# ----------------------------------------------------------------------------
DEFAULT_CONFIG = {
    "sub_ip": "192.168.2.1",
    "mavlink_puerto": 14550,
    "modo_conexion": "udpout",          # udpout = enviar a la IP del sub | udpin = escuchar difusión
    "camaras": [
        {"nombre": "Punta",     "url": "rtsp://192.168.2.1:8554/cam1", "ptz": False},
        {"nombre": "Arriba",    "url": "rtsp://192.168.2.1:8554/cam2", "ptz": True},
        {"nombre": "Abajo",     "url": "rtsp://192.168.2.1:8554/cam3", "ptz": False},
        {"nombre": "Izquierda", "url": "rtsp://192.168.2.1:8554/cam4", "ptz": True},
        {"nombre": "Derecha",   "url": "rtsp://192.168.2.1:8554/cam5", "ptz": True},
    ],
    "ptz_puerto_udp": 14551,   # puerto en la Pi para mover las cámaras PTZ
    "ptz_velocidad": 40,       # grados/seg en vigilancia automática
    "canal_luces_1": 8,   # servo/relé par superior
    "canal_luces_2": 9,   # servo/relé par inferior
    "canal_pinza": 10,    # servo pinza
    "canal_gimbal_yaw": 11,   # servo gimbal arpoón — giro
    "canal_gimbal_pitch": 12, # servo gimbal arpoón — elevación
    "canal_arpon": 13,        # servo disparador arpoón
    "canal_carrete": 14,      # motor carrete del hilo (recogida)
    "canal_luces_ptz": 15,    # anillos LED de las 3 cámaras domo PTZ
    "gimbal_rango_grados": 60,
    "autoapuntado": True,
    "capacidad_wh": 180,  # 2× DeWalt DCB205 20V 5Ah (90 Wh c/u)
    "potencia_media_w": 120,
    "invertir_eje_z": False,
    "escala_movimiento": 800,
    "a_d_girar": False,        # true = A/D giran (estilo auto) y ←/→ mueven de lado
    "rampa_empuje": 1.2,       # sube/baja el empuje de a poco (0→1 en ~1 s)
    "tiempo_subida_emergencia_s": 90,
    "umbral_golpe_g": 3.0,     # aceleración (g) que cuenta como golpe
}

BTN_A, BTN_B, BTN_X, BTN_Y = 0, 1, 2, 3
BTN_BACK, BTN_START = 4, 6
BTN_LB, BTN_RB = 9, 10


def cargar_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    cfg["camaras"] = [dict(c) for c in DEFAULT_CONFIG["camaras"]]
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            guardado = json.load(f)
        for k, v in guardado.items():
            if k == "camaras" and isinstance(v, list):
                for i, cam in enumerate(v[:5]):
                    if isinstance(cam, dict) and i < len(cfg["camaras"]):
                        cfg["camaras"][i].update(cam)
            else:
                cfg[k] = v
    except Exception:
        pass
    return cfg


def guardar_config(cfg: dict) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def limitar(v: float, lim: float = 1.0) -> float:
    return max(-lim, min(lim, v))


# ----------------------------------------------------------------------------
# Frame de video (hilo por cámara). Sin URL → genera señal DEMO.
# ----------------------------------------------------------------------------
def demo_frame(w: int, h: int, idx: int, t: float, aviso="SIN SENAL - MODO DEMO"):
    if not CV_OK:
        return None
    gx = np.linspace(0.0, 1.0, w, dtype=np.float32)
    gy = np.linspace(0.0, 1.0, h, dtype=np.float32)
    X, Y = np.meshgrid(gx, gy)
    onda = 0.5 + 0.5 * np.sin((X * 6.0 + Y * 3.0) * 2.0 + t * 1.5 + idx * 0.7)
    base = 20 + 45 * onda
    img = np.zeros((h, w, 3), dtype=np.float32)
    img[..., 0] = base * 0.55
    img[..., 1] = base * 0.95
    img[..., 2] = base * 1.15
    img = np.clip(img, 0, 255).astype(np.uint8)
    for i in range(16):  # burbujas
        x0 = (i * 97 + idx * 31) % w
        y0 = (int(i * 53 + idx * 17) + int(t * (20 + (i % 5) * 9))) % h
        cv2.circle(img, (int(x0), int(h - 1 - y0)), 2, (190, 210, 220), -1, cv2.LINE_AA)
    ys = int((0.5 + 0.5 * math.sin(t * 1.2 + idx * 0.9)) * (h - 1))
    cv2.line(img, (0, ys), (w - 1, ys), (70, 150, 180), 1)
    cv2.putText(img, f"CAM {idx + 1}", (12, 32), cv2.FONT_HERSHEY_SIMPLEX,
                0.85, (240, 240, 240), 2, cv2.LINE_AA)
    cv2.putText(img, aviso, (12, h - 14), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (150, 200, 255), 1, cv2.LINE_AA)
    return img


class CameraFeed(threading.Thread):
    def __init__(self, idx: int, get_url, get_demo=None, size=(448, 252)):
        super().__init__(daemon=True)
        self.idx = idx
        self.get_url = get_url
        self.get_demo = get_demo or (lambda: True)
        self.size = size
        self.fps = 0.0
        self._frame = None
        self._lock = threading.Lock()
        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        cap = None
        url_prev = None
        t_last = time.time()
        contador = 0
        t_cont = time.time()
        while self.alive.is_set():
            url = self.get_url() or ""
            demo = self.get_demo()
            if not CV_OK or not url or demo:
                # modo demo (o cámara sin configurar): señal simulada animada
                time.sleep(0.12)
                with self._lock:
                    self._frame = demo_frame(*self.size, self.idx, time.time(),
                                             aviso="MODO DEMO" if demo else "SIN SEÑAL")
                self.fps = 0.0
                continue
            if url != url_prev:
                if cap is not None:
                    cap.release()
                cap = cv2.VideoCapture(url)
                url_prev = url
            ok, fr = cap.read()
            ahora = time.time()
            if not ok:
                if ahora - t_last > 6.0:
                    cap.release()
                    cap = None
                    url_prev = None
                time.sleep(0.2)
                continue
            fr = cv2.resize(fr, (self.size[0], self.size[1]))
            t_last = ahora
            contador += 1
            if ahora - t_cont >= 1.0:
                self.fps = contador / (ahora - t_cont)
                contador = 0
                t_cont = ahora
            with self._lock:
                self._frame = fr

    def obtener(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    def detener(self):
        self.alive.clear()


# ----------------------------------------------------------------------------
# Enlace MAVLink con ArduSub (telemetría + mandos + emergencias)
# ----------------------------------------------------------------------------
class SubLink(threading.Thread):
    def __init__(self, cfg: dict, estado: dict, log, eventos=None):
        super().__init__(daemon=True)
        self.cfg = dict(cfg)
        self.estado = estado
        self.log = log
        self.eventos = eventos
        self.alive = threading.Event()
        self.alive.set()
        self.cmd = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}
        self.aplicado = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}  # empuje real (rampa)
        self._t_rampa = 0.0
        self.aux = {"luces1": False, "luces2": False, "luces_ptz": False, "pinza": 0,
                    "gimbal_yaw": 1500.0, "gimbal_pitch": 1500.0,
                    "arpon": 1000, "carrete": 1500}  # pinza: 1 abrir, -1 cerrar, 0 centro
        self._arpon_hasta = 0.0
        self._carrete_pago_hasta = 0.0
        self.emergencia = None  # None | "stop" | "subida"
        self.master = None
        self._t_hb = 0.0
        self._t_manual = 0.0
        self._t_rc = 0.0
        self._disarm_pend = False
        self._emerg_prev = None
        self._t_emerg_ini = 0.0
        self._t_dep = 0.0
        self._t_ultimo_golpe = 0.0

    def run(self):
        while self.alive.is_set():
            try:
                self._conectar_y_operar()
            except Exception as e:
                self.estado["conectado"] = False
                self.log(f"Enlace MAVLink: {e} — reintentando en 2 s…")
            time.sleep(2.0)

    def _conectar_y_operar(self):
        if not MAV_OK:
            self.log("pymavlink no disponible — la app funciona en MODO DEMO.")
            time.sleep(3600)
            return
        modo = self.cfg.get("modo_conexion", "udpout")
        if modo == "udpin":
            conn = f"udpin:0.0.0.0:{self.cfg['mavlink_puerto']}"
        else:
            conn = f"udpout:{self.cfg['sub_ip']}:{self.cfg['mavlink_puerto']}"
        try:
            self.master = mavutil.mavlink_connection(conn, source_system=255, source_component=190)
        except TypeError:
            self.master = mavutil.mavlink_connection(conn)
        try:
            self.master.mav.port.settimeout(0.02)
        except Exception:
            pass
        self.log(f"Enlace {conn} abierto — esperando heartbeat del submarino…")
        while self.alive.is_set():
            msg = None
            try:
                msg = self.master.recv_msg()
            except Exception:
                msg = None
            ahora = time.time()
            if msg is not None:
                self._procesar(msg)
            elif self._t_hb and ahora - self._t_hb > 4.0:
                self.estado["conectado"] = False
            self._paso_envio(ahora)
            time.sleep(0.004)

    def _procesar(self, msg):
        t = msg.get_type()
        if t == "HEARTBEAT":
            self._t_hb = time.time()
            self.estado["conectado"] = True
            self.estado["armado"] = bool(msg.base_mode & 128)
            try:
                self.estado["modo"] = self.master.flightmode
            except Exception:
                pass
        elif t == "SYS_STATUS":
            if msg.voltage_battery > 0:
                self.estado["volt"] = msg.voltage_battery / 1000.0
            if 0 <= msg.battery_remaining <= 100:
                self.estado["batt"] = float(msg.battery_remaining)
        elif t == "VFR_HUD":
            if msg.heading:
                self.estado["rumbo"] = float(msg.heading)
        elif t == "ATTITUDE":
            self.estado["roll"] = math.degrees(msg.roll)
            self.estado["pitch"] = math.degrees(msg.pitch)
        elif t == "NAMED_VALUE_FLOAT":
            nm = msg.name if isinstance(msg.name, str) else msg.name.decode("utf-8", "ignore")
            if nm.strip() == "Dep":
                self.estado["profundidad"] = abs(float(msg.value))
                self._t_dep = time.time()
        elif t == "GLOBAL_POSITION_INT":
            if time.time() - self._t_dep > 2.0:
                self.estado["profundidad"] = abs(msg.relative_alt) / 1000.0
        elif t in ("RAW_IMU", "SCALED_IMU2", "SCALED_IMU3"):
            self._detectar_golpe(msg)

    def _detectar_golpe(self, msg):
        """Sensor de golpes: picos de aceleración de la IMU > umbral."""
        ahora = time.time()
        if ahora - self._t_ultimo_golpe < 1.5:
            return
        try:
            ax, ay, az = float(msg.xacc), float(msg.yacc), float(msg.zacc)
        except Exception:
            return
        g = math.sqrt(ax * ax + ay * ay + az * az) / 1000.0
        umbral = self.cfg.get("umbral_golpe_g", 3.0)
        if g < umbral:
            return
        self._t_ultimo_golpe = ahora
        # el eje con mayor aceleración indica el lado del impacto
        comps = {"frontal": -ax, "popa": ax, "lateral derecho": -ay,
                 "lateral izquierdo": ay, "superior": -az, "inferior": az}
        lado = max(comps, key=lambda k: abs(comps[k]))
        self.log(f"💥 GOLPE DETECTADO: {lado} · {g:.1f} g")
        if self.eventos:
            self.eventos.put(("golpe", (lado, g, ahora)))

    def _paso_envio(self, ahora: float):
        if self.master is None or self._t_hb == 0:
            return
        # ventana de disparo del arpoón: tras el impulso vuelve a seguro
        if self.aux["arpon"] > 1500 and time.time() > self._arpon_hasta:
            self.aux["arpon"] = 1000
        # tras el disparo, soltar hilo brevemente para no frenar el arpón
        if self.aux["carrete"] == 1000 and time.time() > self._carrete_pago_hasta:
            self.aux["carrete"] = 1500
        if self.emergencia != self._emerg_prev:
            if self.emergencia == "subida":
                self._t_emerg_ini = ahora
                self.log("EMERGENCIA: subiendo a superficie (luces ON, pinza abierta)…")
            elif self.emergencia == "stop":
                self._disarm_pend = True
                self.log("EMERGENCIA: motores a cero + desarme enviado.")
            self._emerg_prev = self.emergencia

        if self.emergencia == "stop":
            self._enviar_manual(0, 0, 0, 0)
            self.aplicado = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}
            self.aux["arpon"] = 1000
            self.aux["carrete"] = 1500
            if self._disarm_pend:
                try:
                    self.master.arducopter_disarm()
                except Exception:
                    try:
                        self.master.mav.command_long_send(
                            self.master.target_system, 1,
                            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0.0, 0, 0, 0, 0, 0, 0)
                    except Exception:
                        pass
                self._disarm_pend = False
            self._enviar_aux(ahora)
            return

        if self.emergencia == "subida":
            # POTENCIA INSTANTÁNEA (sin rampa): los motores van directo al pico
            dz = 1.0 if not self.cfg.get("invertir_eje_z") else -1.0
            u = self.cmd
            esc = self.cfg.get("escala_movimiento", 800)
            self._enviar_manual(u["x"] * esc, u["y"] * esc, dz, u["r"] * esc)
            self.aplicado = {"x": u["x"], "y": u["y"], "z": dz, "r": u["r"]}
            self.aux["luces1"] = True
            self.aux["luces2"] = True
            self.aux["pinza"] = 1
            self.aux["arpon"] = 1000
            self.aux["carrete"] = 1500
            self._enviar_aux(ahora)
            limite = self.cfg.get("tiempo_subida_emergencia_s", 90)
            if self.estado["profundidad"] < 0.3 or ahora - self._t_emerg_ini > limite:
                self.emergencia = None
                self._enviar_manual(0, 0, 0, 0)
                self.log("Emergencia finalizada: superficie alcanzada (o límite de tiempo).")
            return

        # rampa de empuje: los motores aceleran y frenan de a poco (sin picos)
        # (en emergencias se salta la rampa: potencia inmediata)
        c = self.cmd
        a = self.aplicado
        ahora_r = time.time()
        dt = min(0.25, max(0.005, ahora_r - self._t_rampa)) if self._t_rampa else 0.05
        self._t_rampa = ahora_r
        tasa = self.cfg.get("rampa_empuje", 1.2) * dt
        for k in ("x", "y", "z", "r"):
            dif = c[k] - a[k]
            if dif == 0.0:
                continue
            # REVERSA instantánea: si cambia el sentido, respuesta inmediata
            if a[k] * c[k] < 0:
                a[k] = c[k]
                continue
            paso = max(-tasa, min(tasa, dif))
            if c[k] == 0.0:
                paso = max(-tasa * 4.0, min(tasa * 4.0, dif))   # FRENO rápido
            elif abs(c[k]) < abs(a[k]):
                paso *= 2.0                                     # soltar: 2×
                if abs(paso) > abs(dif):
                    paso = dif
            a[k] += paso
        esc = self.cfg.get("escala_movimiento", 800)
        self._enviar_manual(a["x"] * esc, a["y"] * esc, a["z"] * esc, a["r"] * esc)
        self._enviar_aux(ahora)

    def _enviar_manual(self, x, y, z, r):
        if time.time() - self._t_manual < 0.045:
            return
        self._t_manual = time.time()
        x, y, z, r = int(x), int(y), int(z), int(r)
        try:
            self.master.mav.manual_control_send(x, y, z, r, 0, 0)
        except TypeError:
            try:
                self.master.mav.manual_control_send(x, y, z, r, 0, self.master.target_system, 1)
            except Exception:
                pass
        except Exception:
            pass

    def _enviar_aux(self, ahora: float):
        if ahora - self._t_rc < 0.1:
            return
        self._t_rc = ahora
        ch = [0] * 16
        ch[self.cfg.get("canal_luces_1", 8) - 1] = 1900 if self.aux["luces1"] else 1000
        ch[self.cfg.get("canal_luces_2", 9) - 1] = 1900 if self.aux["luces2"] else 1000
        p = self.aux["pinza"]
        ch[self.cfg.get("canal_pinza", 10) - 1] = 1900 if p > 0 else (1000 if p < 0 else 1500)
        try:
            ch[self.cfg.get("canal_gimbal_yaw", 11) - 1] = int(max(1000, min(2000, self.aux["gimbal_yaw"])))
            ch[self.cfg.get("canal_gimbal_pitch", 12) - 1] = int(max(1000, min(2000, self.aux["gimbal_pitch"])))
            ch[self.cfg.get("canal_arpon", 13) - 1] = int(self.aux["arpon"])
            ch[self.cfg.get("canal_carrete", 14) - 1] = int(self.aux["carrete"])
            ch[self.cfg.get("canal_luces_ptz", 15) - 1] = 1900 if self.aux["luces_ptz"] else 1000
        except Exception:
            pass
        try:
            self.master.mav.rc_channels_override_send(self.master.target_system, 1, *ch)
        except Exception:
            pass

    def fijar_modo(self, modo: str):
        if self.master and self._t_hb:
            try:
                self.master.set_mode(modo)
                self.log(f"Modo → {modo}")
            except Exception as e:
                self.log(f"No se pudo fijar modo {modo}: {e}")

    def armar(self):
        if self.master and self._t_hb:
            try:
                self.master.arducopter_arm()
                self.log("ARMADO enviado.")
            except Exception as e:
                self.log(f"No se pudo armar: {e}")

    def desarmar(self):
        self.emergencia = "stop"

    def disparar(self):
        """Dispara el arpoón: impulso de servo y soltado de hilo (carrete)."""
        if self.emergencia:
            return False
        self.aux["arpon"] = 1900
        self._arpon_hasta = time.time() + 0.35
        self.aux["carrete"] = 1000
        self._carrete_pago_hasta = time.time() + 0.6
        return True

    def detener(self):
        self.alive.clear()


# ----------------------------------------------------------------------------
# Mando de juego (Xbox / PS4) vía pygame
# ----------------------------------------------------------------------------
class MandoThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.ejes = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}
        self.botones = [False] * 16
        self.conectado = False
        self.alive = threading.Event()
        self.alive.set()

    def run(self):
        if not PYGAME_OK:
            return
        try:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            pygame.init()
            pygame.joystick.init()
            js = None
            while self.alive.is_set():
                for ev in pygame.event.get():
                    if ev.type == pygame.JOYDEVICEADDED:
                        try:
                            js = pygame.joystick.Joystick(ev.device_index)
                            js.init()
                            self.conectado = True
                        except Exception:
                            js = None
                    elif ev.type == pygame.JOYDEVICEREMOVED:
                        js = None
                        self.conectado = False
                        self.botones = [False] * 16
                        self.ejes = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}
                if js is None and pygame.joystick.get_count() > 0:
                    try:
                        js = pygame.joystick.Joystick(0)
                        js.init()
                        self.conectado = True
                    except Exception:
                        js = None
                if js is not None:
                    pygame.event.pump()
                    try:
                        ax = [js.get_axis(i) if i < js.get_numaxes() else 0.0 for i in range(6)]
                        self.ejes["x"] = limitar(-ax[1])
                        self.ejes["y"] = limitar(ax[0])
                        self.ejes["r"] = limitar(ax[2])
                        self.ejes["z"] = limitar(-ax[3])
                    except Exception:
                        pass
                    try:
                        for i in range(min(16, js.get_numbuttons())):
                            self.botones[i] = bool(js.get_button(i))
                    except Exception:
                        pass
                time.sleep(0.03)
        except Exception:
            self.conectado = False

    def detener(self):
        self.alive.clear()


# ----------------------------------------------------------------------------
# Interfaz principal
# ----------------------------------------------------------------------------
COL_FONDO = "#0d1117"
COL_PANEL = "#161b22"
COL_BORDE = "#30363d"
COL_TEXTO = "#c9d1d9"
COL_ACENTO = "#58a6ff"
COL_VERDE = "#3fb950"
COL_AMBAR = "#d29922"
COL_ROJO = "#f85149"
COL_NARANJA = "#e3b341"
PANEL_W, PANEL_H = 448, 252

# colores del modelo 3D (RGB)
AZUL = [63, 185, 201]
GRIS = [110, 119, 129]
GRIS_OSC = [70, 76, 84]
ROJO = [248, 81, 73]
AMARILLO = [210, 153, 34]
BLANCO = [230, 237, 243]
PLATA = [160, 169, 178]
ACERO = [125, 135, 150]
NARANJA = [227, 179, 65]
VERDE3D = [63, 185, 80]
CRISTAL2 = [139, 200, 255]
VERDE = COL_VERDE  # compatibilidad con secciones previas


class App(tk.Tk):
    def __init__(self, test=False):
        super().__init__()
        self.title(f"SUBCONTROL v{VERSION} — Estación de superficie · mini-ROV")
        self.geometry("1300x820")
        self.minsize(1150, 720)
        self.configure(bg=COL_FONDO)
        self.test = test

        self.cfg = cargar_config()
        self.estado = {"conectado": False, "modo": "—", "armado": False,
                       "profundidad": 0.0, "rumbo": 0.0, "volt": 0.0, "batt": 0.0,
                       "roll": 0.0, "pitch": 0.0}
        self.teclas = set()
        self.mando_ejes = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}
        self.mando_btns = [False] * 16
        self.mando_prev = [False] * 16
        self.luces = [False, False]
        self.luces_ptz = False     # anillos LED de los domos PTZ
        self.pinza = 0
        self.emergencia = None
        self.activado = False       # 🔒 bloqueo: ENTER para habilitar motores
        self.gimbal = {"yaw": 0.0, "pitch": 0.0}   # grados del gimbal del arpoón
        self.arpon_seguro = True
        self.autoaim = bool(self.cfg.get("autoapuntado", True))
        self.objetivos = {"cam1": None, "cam3": None}  # objetivo CAM1 y CAM3
        self._bg = {"cam1": None, "cam3": None}        # fondo para detección
        self._fcount = 0
        self._pago_hasta = 0.0      # ventana de soltado de hilo tras el disparo
        self.auto_gancho = False    # aproximación y agarre automático
        self.gancho_estado = "OFF"
        self._gancho_cierre_hasta = 0.0
        self.golpes = []
        self.impacto = None         # {"lado":…, "g":…, "t":…}
        self.vista3d = {"yaw": 115.0, "pitch": 12.0, "zoom": 0.34}
        self._drag = None
        self._rumbo_prev = None   # para rotar el modelo 3D con el rumbo real
        self._prop_ang = 0.0
        self.demo_flag = True        # True = cámaras muestran señal demo
        self.ptz = {}               # índice de cámara → ángulo 0-360°
        for i, c in enumerate(self.cfg["camaras"]):
            if c.get("ptz"):
                self.ptz[i] = 0.0
        self.ptz_sel = None         # cámara PTZ seleccionada
        self.ptz_auto = False       # vigilancia automática
        self._last_ptz = {}
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception:
            self._sock = None
        self.eventos = queue.Queue()
        self.demo_prof = 0.0
        self.demo_rumbo = 0.0
        self.demo_batt = 88.0
        self.demo_roll = 0.0
        self.demo_pitch = 0.0
        self._construir_ui()

        self.feeds = [CameraFeed(i, lambda i=i: self.cfg["camaras"][i]["url"],
                                 get_demo=lambda: self.demo_flag,
                                 size=(640, 360)) for i in range(5)]
        for f in self.feeds:
            f.start()
        self.link = SubLink(self.cfg, self.estado, self.log, eventos=self.eventos)
        self.link.start()
        self.mando = MandoThread()
        self.mando.start()

        self.bind("<KeyPress>", self._tecla_pulsada)
        self.bind("<KeyRelease>", self._tecla_soltada)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.focus_set()

        self.after(100, self._tick_telem)
        self.after(66, self._tick_video)
        self.after(50, self._tick_control)
        self.after(120, self._tick_3d)

        self.log(f"SUBCONTROL v{VERSION} iniciado. Mando: "
                 + ("detectado" if PYGAME_OK else "no disponible (sin pygame)"))
        self.log("🔒 BLOQUEADO: presiona ENTER (una vez) para habilitar los motores.")
        if self.test:
            self.after(2500, self.destroy)

    # ---------------------------------------------------------------- UI
    def _seccion(self, padre, titulo):
        f = tk.Frame(padre, bg=COL_PANEL, highlightbackground=COL_BORDE, highlightthickness=1)
        tk.Label(f, text=titulo, bg=COL_PANEL, fg=COL_ACENTO,
                 font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x", padx=10, pady=(8, 2))
        return f

    def _construir_ui(self):
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except Exception:
            pass
        estilo.configure("green.Horizontal.TProgressbar", troughcolor=COL_BORDE,
                         background=COL_VERDE, thickness=14)

        # ---- Cabecera
        head = tk.Frame(self, bg=COL_PANEL, highlightbackground=COL_BORDE, highlightthickness=1)
        head.pack(fill="x")
        tk.Label(head, text="SUBCONTROL", bg=COL_PANEL, fg=COL_ACENTO,
                 font=("Segoe UI", 16, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(head, text="Estación de superficie · mini-ROV 6 motores",
                 bg=COL_PANEL, fg=COL_TEXTO).pack(side="left", padx=4)
        self.dot = tk.Canvas(head, width=16, height=16, bg=COL_PANEL, highlightthickness=0)
        self.dot_id = self.dot.create_oval(2, 2, 14, 14, fill="#555", outline="")
        self.dot.pack(side="left", padx=(18, 4))
        self.lbl_estado = tk.Label(head, text="Conectando…", bg=COL_PANEL, fg=COL_TEXTO)
        self.lbl_estado.pack(side="left")
        self.lbl_modo = tk.Label(head, text="Modo: —   |   DESARMADO", bg=COL_PANEL,
                                 fg=COL_AMBAR, font=("Segoe UI", 11, "bold"))
        self.lbl_modo.pack(side="right", padx=14)
        self.lbl_gate = tk.Label(head, text="🔒 BLOQUEADO · ENTER para activar",
                                 bg=COL_PANEL, fg=COL_ROJO,
                                 font=("Segoe UI", 11, "bold"))
        self.lbl_gate.pack(side="right", padx=6)

        # ---- Cuerpo
        body = tk.Frame(self, bg=COL_FONDO)
        body.pack(fill="both", expand=True)
        video = tk.Frame(body, bg=COL_FONDO)
        video.pack(side="left", fill="both", expand=True, padx=(10, 6), pady=8)
        sb_frame = tk.Frame(body, bg=COL_FONDO, width=362)
        sb_frame.pack(side="right", fill="y", padx=(6, 10), pady=8)
        sb_frame.pack_propagate(False)
        sb_scroll = ttk.Scrollbar(sb_frame, orient="vertical")
        canvas_sb = tk.Canvas(sb_frame, bg=COL_FONDO, highlightthickness=0,
                              yscrollcommand=sb_scroll.set)
        sb_scroll.configure(command=canvas_sb.yview)
        sb_scroll.pack(side="right", fill="y")
        canvas_sb.pack(side="left", fill="both", expand=True)
        sidebar = tk.Frame(canvas_sb, bg=COL_FONDO)
        canvas_sb.create_window((0, 0), window=sidebar, anchor="nw", tags="inner")
        # el contenido se adapta al ancho visible (nada cortado a la derecha)
        canvas_sb.bind("<Configure>", lambda e: canvas_sb.itemconfigure(
            "inner", width=max(220, e.width - 4)))
        sidebar.bind("<Configure>", lambda e: canvas_sb.configure(
            scrollregion=canvas_sb.bbox("all")))
        # rueda del mouse desplaza el panel SOLO con el cursor encima
        canvas_sb.bind("<Enter>", lambda e: canvas_sb.bind_all(
            "<MouseWheel>", lambda ev: canvas_sb.yview_scroll(-ev.delta // 120, "units")))
        canvas_sb.bind("<Leave>", lambda e: canvas_sb.unbind_all("<MouseWheel>"))

        # ---- Cámaras estilo "videollamada": principal grande + 4 miniaturas
        self.orden = [0, 1, 2, 3, 4]   # orden[0] = cámara principal
        self.fotos = [None]
        self.fotos_mini = [None, None, None, None, None]

        izq = tk.Frame(video, bg=COL_FONDO)
        izq.pack(side="left", fill="both", expand=True)
        der = tk.Frame(video, bg=COL_FONDO, width=180)
        der.pack(side="right", fill="y")
        der.pack_propagate(False)

        marco_main = tk.Frame(izq, bg=COL_BORDE, highlightbackground=COL_BORDE,
                              highlightthickness=1)
        marco_main.pack(fill="both", expand=True)
        self.lbl_main = tk.Label(marco_main, bg="#000", fg="#666",
                                 text=(f"CAM 1 — {self.cfg['camaras'][0]['nombre']}\n"
                                       "(clic en una miniatura para agrandar)"),
                                 font=("Segoe UI", 11))
        self.lbl_main.pack(fill="both", expand=True)
        self.cap_main = tk.Label(marco_main, bg=COL_PANEL, fg=COL_TEXTO, anchor="w",
                                 text=f"CAM 1 · {self.cfg['camaras'][0]['nombre']}")
        self.cap_main.pack(fill="x")

        # ---- Fila inferior: modelo 3D + instrumentos de vuelo
        fila31 = tk.Frame(izq, bg=COL_FONDO)
        fila31.pack(fill="x", pady=(6, 0))
        marco3d = tk.Frame(fila31, bg=COL_BORDE, highlightbackground=COL_BORDE,
                           highlightthickness=1)
        marco3d.pack(side="left", fill="both", expand=True)
        fila3d = tk.Frame(marco3d, bg=COL_PANEL)
        fila3d.pack(fill="x")
        tk.Label(fila3d, text="MODELO 3D EN VIVO — arrastra: girar · rueda: zoom · doble clic: reset",
                 bg=COL_PANEL, fg=COL_ACENTO, font=("Segoe UI", 8, "bold")).pack(
            side="left", padx=8, pady=2)
        tk.Button(fila3d, text="Simular golpe (demo)", bg=COL_PANEL, fg=COL_ROJO,
                  activebackground=COL_BORDE, relief="flat", font=("Segoe UI", 8),
                  command=self._simular_golpe).pack(side="right", padx=6, pady=2)
        self.cv3d = tk.Canvas(marco3d, height=188, bg="#0b0f14", highlightthickness=0)
        self.cv3d.pack(fill="x")
        self.lbl_golpes = tk.Label(marco3d, bg=COL_PANEL, fg=COL_TEXTO, anchor="w",
                                   text="Golpes: 0 · sin impactos registrados",
                                   font=("Consolas", 9))
        self.lbl_golpes.pack(fill="x", padx=8, pady=(0, 4))
        self._geo = self._geo_rov()
        _todos = np.vstack([c[0] for c in self._geo])
        self._centro3d = (_todos.min(axis=0) + _todos.max(axis=0)) / 2.0
        self._ext3d = _todos.max(axis=0) - _todos.min(axis=0)
        self._fit3d = False
        self.cv3d.bind("<ButtonPress-1>", self._drag3d_ini)
        self.cv3d.bind("<B1-Motion>", self._drag3d)
        self.cv3d.bind("<MouseWheel>", self._zoom3d)
        self.cv3d.bind("<Double-Button-1>", lambda e: self._reset3d())

        # ---- Instrumentos de vuelo: horizonte artificial + brújula
        marco_ins = tk.Frame(fila31, bg=COL_BORDE, highlightbackground=COL_BORDE,
                             highlightthickness=1, width=380)
        marco_ins.pack(side="right", fill="y")
        marco_ins.pack_propagate(False)
        tk.Label(marco_ins, text="INSTRUMENTOS DE VUELO", bg=COL_PANEL,
                 fg=COL_ACENTO, font=("Segoe UI", 8, "bold")).pack(fill="x", pady=2)
        self.cv_ins = tk.Canvas(marco_ins, width=360, height=188,
                                bg="#0b0f14", highlightthickness=0)
        self.cv_ins.pack(fill="both", expand=True)
        self.lbl_ins = tk.Label(marco_ins, bg=COL_PANEL, fg=COL_TEXTO, anchor="w",
                                text="EMP 0% · R +0° · P +0°", font=("Consolas", 8))
        self.lbl_ins.pack(fill="x", padx=6, pady=(0, 3))

        self.minis = []
        for pos in range(5):
            m = tk.Frame(der, bg=COL_BORDE, highlightbackground=COL_BORDE,
                         highlightthickness=1, cursor="hand2")
            m.pack(fill="x", pady=(0, 3))
            lbl = tk.Label(m, bg="#000", fg="#666", text=f"CAM {pos+1}",
                           font=("Segoe UI", 8))
            lbl.pack(fill="x")
            cap = tk.Label(m, bg=COL_PANEL, fg=COL_TEXTO, anchor="w",
                           font=("Segoe UI", 7), text=f"CAM {pos+1}")
            cap.pack(fill="x")
            for wgt in (m, lbl, cap):
                wgt.bind("<Button-1>", lambda e, p=pos: self._elegir_cam(p))
            self.minis.append((m, lbl, cap))

        # ---- Panel EMERGENCIA (primero, bien visible)
        s = self._seccion(sidebar, "EMERGENCIA")
        s.pack(fill="x", pady=(0, 6))
        self.btn_emerg = tk.Button(s, text="⛔ PARADA EMERGENCIA [F1]",
                                   bg=COL_ROJO, fg="white", activebackground="#c0392b",
                                   font=("Segoe UI", 10, "bold"), relief="flat",
                                   command=self._emerg_parada)
        self.btn_emerg.pack(fill="x", padx=10, pady=(4, 3), ipady=5)
        self.btn_subida = tk.Button(s, text="⬆ SUBIDA EMERGENCIA [F2]",
                                    bg=COL_NARANJA, fg="#111", activebackground="#c9a227",
                                    font=("Segoe UI", 10, "bold"), relief="flat",
                                    command=self._emerg_subida)
        self.btn_subida.pack(fill="x", padx=10, pady=3, ipady=5)
        self.btn_norm = tk.Button(s, text="Normalizar [F3]",
                                  bg=COL_PANEL, fg=COL_TEXTO, activebackground=COL_BORDE,
                                  font=("Segoe UI", 9), relief="flat",
                                  command=self._emerg_normalizar)
        self.btn_norm.pack(fill="x", padx=10, pady=(3, 8))

        # ---- TELEMETRÍA
        s = self._seccion(sidebar, "TELEMETRÍA")
        s.pack(fill="x", pady=6)
        fila = tk.Frame(s, bg=COL_PANEL)
        fila.pack(fill="x", padx=10)
        self.lbl_prof = tk.Label(fila, text="0.0 m", bg=COL_PANEL, fg=COL_VERDE,
                                 font=("Consolas", 30, "bold"))
        self.lbl_prof.pack(side="left")
        tk.Label(fila, text="PROFUNDIDAD", bg=COL_PANEL, fg=COL_TEXTO,
                 font=("Segoe UI", 8)).pack(side="left", padx=(8, 0), pady=(16, 0))
        self.lbl_rumbo = tk.Label(s, text="Rumbo: 0°", bg=COL_PANEL, fg=COL_TEXTO,
                                  font=("Consolas", 13))
        self.lbl_rumbo.pack(fill="x", padx=10, pady=(0, 8))

        # ---- ENERGÍA
        s = self._seccion(sidebar, "ENERGÍA")
        s.pack(fill="x", pady=6)
        self.bar_ener = ttk.Progressbar(s, maximum=100, value=0,
                                        style="green.Horizontal.TProgressbar")
        self.bar_ener.pack(fill="x", padx=10, pady=(2, 4))
        self.lbl_ener = tk.Label(s, text="— %  ·  — V  ·  ≈ — min", bg=COL_PANEL,
                                 fg=COL_TEXTO, font=("Consolas", 12))
        self.lbl_ener.pack(fill="x", padx=10, pady=(0, 8))

        # ---- LUCES
        s = self._seccion(sidebar, "SISTEMA DE LUCES")
        s.pack(fill="x", pady=6)
        fila = tk.Frame(s, bg=COL_PANEL)
        fila.pack(fill="x", padx=10, pady=(2, 8))
        self.btn_l1 = tk.Button(fila, text="Par 1 superior", bg=COL_PANEL, fg=COL_TEXTO,
                                activebackground=COL_BORDE, relief="flat",
                                font=("Segoe UI", 9), command=lambda: self._toggle_luces(0))
        self.btn_l1.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self.btn_l2 = tk.Button(fila, text="Par 2 inferior", bg=COL_PANEL, fg=COL_TEXTO,
                                activebackground=COL_BORDE, relief="flat",
                                font=("Segoe UI", 9), command=lambda: self._toggle_luces(1))
        self.btn_l2.pack(side="left", fill="x", expand=True, padx=(3, 0))
        self.btn_lptz = tk.Button(s, text="Luces de domos PTZ   [3]", bg=COL_PANEL,
                                  fg=COL_ACENTO, activebackground=COL_BORDE,
                                  relief="flat", font=("Segoe UI", 9, "bold"),
                                  command=self._toggle_luces_ptz)
        self.btn_lptz.pack(fill="x", padx=10, pady=(0, 2))
        tk.Button(s, text="Todas ON / OFF   [L]", bg=COL_PANEL, fg=COL_AMBAR,
                  activebackground=COL_BORDE, relief="flat", font=("Segoe UI", 9, "bold"),
                  command=self._toggle_todas).pack(fill="x", padx=10, pady=(0, 8))

        # ---- PINZA
        s = self._seccion(sidebar, "PINZA / GARRA")
        s.pack(fill="x", pady=6)
        fila = tk.Frame(s, bg=COL_PANEL)
        fila.pack(fill="x", padx=10, pady=(2, 8))
        self.btn_abrir = tk.Button(fila, text="◀ ABRIR (G)", bg=COL_PANEL, fg=COL_TEXTO,
                                   activebackground=COL_BORDE, relief="flat", font=("Segoe UI", 10))
        self.btn_abrir.pack(side="left", fill="x", expand=True, padx=(0, 3), ipady=5)
        self.btn_cerrar = tk.Button(fila, text="CERRAR (H) ▶", bg=COL_PANEL, fg=COL_TEXTO,
                                    activebackground=COL_BORDE, relief="flat", font=("Segoe UI", 10))
        self.btn_cerrar.pack(side="left", fill="x", expand=True, padx=(3, 0), ipady=5)
        self.btn_abrir.bind("<ButtonPress-1>", lambda e: self._pinza_btn(1))
        self.btn_abrir.bind("<ButtonRelease-1>", lambda e: self._pinza_btn(0))
        self.btn_cerrar.bind("<ButtonPress-1>", lambda e: self._pinza_btn(-1))
        self.btn_cerrar.bind("<ButtonRelease-1>", lambda e: self._pinza_btn(0))
        self.btn_autogancho = tk.Button(s, text="Auto-gancho: OFF   [C]", bg=COL_PANEL,
                                        fg=COL_AMBAR, activebackground=COL_BORDE,
                                        relief="flat", font=("Segoe UI", 9, "bold"),
                                        command=self._toggle_auto_gancho)
        self.btn_autogancho.pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(s, text="Agarre reforzado: servo 20 kg·cm + dedos dentados de acero",
                 bg=COL_PANEL, fg="#8b949e", font=("Segoe UI", 7)).pack(
            fill="x", padx=10, pady=(0, 8))

        # ---- ARPOÓN
        s = self._seccion(sidebar, "ARPOÓN · GIMBAL · HILO")
        s.pack(fill="x", pady=6)
        self.btn_seguro = tk.Button(s, text="🔒 SEGURO: ACTIVADO", bg=COL_ROJO, fg="white",
                                    activebackground=COL_BORDE, relief="flat",
                                    font=("Segoe UI", 9, "bold"), command=self._toggle_seguro)
        self.btn_seguro.pack(fill="x", padx=10, pady=(2, 2))
        fila = tk.Frame(s, bg=COL_PANEL)
        fila.pack(fill="x", padx=10, pady=2)
        self.btn_autoaim = tk.Button(fila, text="Autoapuntado: ON", bg=COL_VERDE, fg="#0d1117",
                                     activebackground=COL_BORDE, relief="flat",
                                     font=("Segoe UI", 8, "bold"), command=self._toggle_autoaim)
        self.btn_autoaim.pack(side="left", fill="x", expand=True, padx=(0, 3))
        self.lbl_gimbal = tk.Label(fila, text="G:+0° P:+0°", bg=COL_PANEL, fg=COL_TEXTO,
                                   font=("Consolas", 9))
        self.lbl_gimbal.pack(side="left", padx=6)
        self.btn_disparo = tk.Button(s, text="🎯  DISPARAR ARPOÓN   [F4]", bg="#3d444d",
                                     fg="#8b949e", activebackground="#3d444d", relief="flat",
                                     font=("Segoe UI", 11, "bold"), command=self._disparar)
        self.btn_disparo.pack(fill="x", padx=10, pady=(4, 3), ipady=7)
        tk.Button(s, text="⏪ RECOGER HILO (mantener)   [F5]", bg=COL_PANEL, fg=COL_AMBAR,
                  activebackground=COL_BORDE, relief="flat", font=("Segoe UI", 9, "bold"),
                  command=self._log_recoger).pack(fill="x", padx=10, pady=(0, 8))

        # ---- CÁMARAS PTZ (360°)
        s = self._seccion(sidebar, "CÁMARAS PTZ · GIRO 360°")
        s.pack(fill="x", pady=6)
        self.lbl_ptz = tk.Label(s, text="Cámara PTZ: — (haz clic en una miniatura PTZ)",
                                bg=COL_PANEL, fg=COL_TEXTO, font=("Consolas", 9),
                                wraplength=300, justify="left")
        self.lbl_ptz.pack(fill="x", padx=10, pady=(2, 4))
        fila = tk.Frame(s, bg=COL_PANEL)
        fila.pack(fill="x", padx=10)
        self.btn_ptz_izq = tk.Button(fila, text="⟲ girar [ , ]", bg=COL_PANEL, fg=COL_TEXTO,
                                     activebackground=COL_BORDE, relief="flat",
                                     font=("Segoe UI", 9))
        self.btn_ptz_izq.pack(side="left", fill="x", expand=True, padx=(0, 3), ipady=4)
        self.btn_ptz_der = tk.Button(fila, text="[ . ] girar ⟳", bg=COL_PANEL, fg=COL_TEXTO,
                                     activebackground=COL_BORDE, relief="flat",
                                     font=("Segoe UI", 9))
        self.btn_ptz_der.pack(side="left", fill="x", expand=True, padx=(3, 0), ipady=4)
        self.btn_ptz_auto = tk.Button(s, text="Vigilancia automática: OFF   [/]", bg=COL_PANEL,
                                      fg=COL_TEXTO, activebackground=COL_BORDE,
                                      relief="flat", font=("Segoe UI", 9, "bold"),
                                      command=self._toggle_ptz_auto)
        self.btn_ptz_auto.pack(fill="x", padx=10, pady=(4, 8))
        tk.Label(s, text="PTZ: Arriba · Izquierda · Derecha (giran 360° para vigilar)",
                 bg=COL_PANEL, fg="#8b949e", font=("Segoe UI", 7)).pack(
            fill="x", padx=10, pady=(0, 8))

        # ---- MANIOBRA
        s = self._seccion(sidebar, "MANIOBRA")
        s.pack(fill="x", pady=6)
        fila = tk.Frame(s, bg=COL_PANEL)
        fila.pack(fill="x", padx=10, pady=(2, 4))
        tk.Label(fila, text="Modo:", bg=COL_PANEL, fg=COL_TEXTO).pack(side="left")
        self.cb_modo = ttk.Combobox(fila, values=["STABILIZE", "MANUAL", "ALT_HOLD", "POSHOLD"],
                                    state="readonly", width=12)
        self.cb_modo.set("STABILIZE")
        self.cb_modo.pack(side="left", padx=6)
        self.cb_modo.bind("<<ComboboxSelected>>", self._modo_sel)
        self.btn_arm = tk.Button(s, text="ARMAR", bg=COL_PANEL, fg=COL_VERDE,
                                 activebackground=COL_BORDE, relief="flat",
                                 font=("Segoe UI", 10, "bold"),
                                 command=self._toggle_arm)
        self.btn_arm.pack(fill="x", padx=10, pady=(0, 4))
        self.var_adg = tk.BooleanVar(value=bool(self.cfg.get("a_d_girar", False)))
        ttk.Checkbutton(s, text="A/D giran (estilo auto) en vez de mover de lado",
                        variable=self.var_adg,
                        command=self._toggle_adg).pack(fill="x", padx=10, pady=(0, 2))
        tk.Label(s, text="TECLADO: W/S adelante · A/D lateral · E/Q vertical · ←→ girar\n"
                         "MANDO: sticks izq/der · A/B luces · X/Y pinza · LB/RB emergencia",
                 bg=COL_PANEL, fg="#8b949e", font=("Consolas", 8), justify="left"
                 ).pack(fill="x", padx=10, pady=(0, 8))

        # ---- AJUSTES
        s = self._seccion(sidebar, "AJUSTES DE CONEXIÓN")
        s.pack(fill="x", pady=6)
        grid = tk.Frame(s, bg=COL_PANEL)
        grid.pack(fill="x", padx=10, pady=(2, 4))
        self.var_ip = tk.StringVar(value=self.cfg["sub_ip"])
        self.var_puerto = tk.StringVar(value=str(self.cfg["mavlink_puerto"]))
        self.var_modo = tk.StringVar(value=self.cfg["modo_conexion"])
        self.vars_cams = [tk.StringVar(value=c["url"]) for c in self.cfg["camaras"]]
        for r, (et, var) in enumerate([("IP del sub", self.var_ip),
                                       ("Puerto MAV", self.var_puerto),
                                       ("Modo enlace", self.var_modo)]):
            tk.Label(grid, text=et, bg=COL_PANEL, fg=COL_TEXTO, font=("Segoe UI", 8)).grid(
                row=r, column=0, sticky="w", pady=1)
            e = tk.Entry(grid, textvariable=var, bg="#0d1117", fg=COL_TEXTO,
                         insertbackground=COL_TEXTO, relief="flat", width=22)
            e.grid(row=r, column=1, sticky="e", pady=1)
        for i, var in enumerate(self.vars_cams):
            tk.Label(grid, text=f"CAM {i+1}", bg=COL_PANEL, fg=COL_TEXTO,
                     font=("Segoe UI", 8)).grid(row=i, column=2, sticky="w", padx=(10, 2), pady=1)
            tk.Entry(grid, textvariable=var, bg="#0d1117", fg=COL_TEXTO,
                     insertbackground=COL_TEXTO, relief="flat", width=26).grid(
                row=i, column=3, sticky="e", pady=1)
        tk.Button(s, text="APLICAR Y RECONECTAR", bg=COL_ACENTO, fg="#0d1117",
                  activebackground="#79b8ff", relief="flat", font=("Segoe UI", 9, "bold"),
                  command=self._aplicar_ajustes).pack(fill="x", padx=10, pady=(2, 8))

        # ---- Registro
        logf = tk.Frame(self, bg=COL_PANEL, highlightbackground=COL_BORDE, highlightthickness=1)
        logf.pack(fill="x", side="bottom")
        self.txt_log = tk.Text(logf, height=5, bg="#0d1117", fg="#9fb3c8",
                               font=("Consolas", 8), relief="flat", state="disabled")
        self.txt_log.pack(fill="x", padx=8, pady=4)

    # ------------------------------------------------------------ eventos UI
    def log(self, texto):
        self.eventos.put(("log", f"[{time.strftime('%H:%M:%S')}] {texto}"))

    def _tecla_pulsada(self, ev):
        k = ev.keysym.lower()
        if ev.keysym in ("Return", "KP_Enter"):
            self.activado = not self.activado
            self.log("🔓 ACTIVADO — motores habilitados (Enter)."
                     if self.activado else
                     "🔒 BLOQUEADO — presiona ENTER para habilitar los motores.")
            return
        if ev.keysym == "F1":
            self._emerg_parada()
        elif ev.keysym == "F2":
            self._emerg_subida()
        elif ev.keysym == "F3":
            self._emerg_normalizar()
        elif ev.keysym == "F4":
            self._disparar()
        elif ev.keysym == "space":
            self.teclas.clear()
        else:
            self.teclas.add(k)

    def _tecla_soltada(self, ev):
        k = ev.keysym.lower()
        self.teclas.discard(k)
        if k == "1":
            self._toggle_luces(0)
        elif k == "2":
            self._toggle_luces(1)
        elif k == "l":
            self._toggle_todas()
        elif k == "3":
            self._toggle_luces_ptz()
        elif k == "p":
            self._toggle_seguro()
        elif k == "y":
            self._toggle_autoaim()
        elif k == "slash":
            self._toggle_ptz_auto()
        elif k == "c":
            self._toggle_auto_gancho()

    def _emerg_parada(self):
        self.emergencia = "stop"
        self.teclas.clear()
        self.arpon_seguro = True
        self.activado = False
        if self.link:
            self.link.emergencia = "stop"
            self.link.aux["carrete"] = 1500
        self.log("⛔ PARADA DE EMERGENCIA — motores a cero, arpoón en seguro, desarme. BLOQUEADO (ENTER para reactivar).")

    def _emerg_subida(self):
        self.emergencia = "subida"
        if self.link:
            self.link.emergencia = "subida"
        self.log("⬆ SUBIDA DE EMERGENCIA activada.")

    def _emerg_normalizar(self):
        if self.emergencia:
            self.emergencia = None
            self.activado = False
            if self.link:
                self.link.emergencia = None
            self.log("Normalizar: sin emergencia activa. BLOQUEADO (ENTER para reactivar).")

    def _toggle_luces(self, i):
        self.luces[i] = not self.luces[i]
        if self.link:
            self.link.aux["luces1"] = self.luces[0]
            self.link.aux["luces2"] = self.luces[1]
        self.log(f"Luces par {i+1}: {'ON' if self.luces[i] else 'OFF'}")

    def _toggle_todas(self):
        destino = not (self.luces[0] and self.luces[1])
        self.luces = [destino, destino]
        if self.link:
            self.link.aux["luces1"] = destino
            self.link.aux["luces2"] = destino
        self.log(f"Todas las luces: {'ON' if destino else 'OFF'}")

    def _toggle_luces_ptz(self):
        self.luces_ptz = not self.luces_ptz
        if self.link:
            self.link.aux["luces_ptz"] = self.luces_ptz
        self.log(f"Luces de los domos PTZ: {'ON' if self.luces_ptz else 'OFF'}")

    def _pinza_btn(self, v):
        self.pinza = v
        if self.link:
            self.link.aux["pinza"] = v

    def _elegir_cam(self, pos):
        """Estilo videollamada: la miniatura clicada pasa a la vista principal."""
        if pos <= 0:
            return
        self.orden[0], self.orden[pos] = self.orden[pos], self.orden[0]
        i = self.orden[0]
        self.log(f"Cámara principal → CAM {i+1} · {self.cfg['camaras'][i]['nombre']}")
        if self.cfg["camaras"][i].get("ptz"):
            self.ptz_sel = i
            self.log(f"Cámara PTZ seleccionada: CAM {i+1} · usa ',' y '.' para girarla 360°")

    def _toggle_ptz_auto(self):
        self.ptz_auto = not self.ptz_auto
        self.log(f"Vigilancia automática: {'ON — la cámara PTZ gira sola' if self.ptz_auto else 'OFF'}")

    # ------------------------------------------- modelo 3D en vivo
    PROPS = [((150, 56, -38), "x", 1), ((150, -56, -38), "x", -1),
             ((-150, 56, -38), "x", -1), ((-150, -56, -38), "x", 1),
             ((150, 0, 96), "z", 1), ((-150, 0, 96), "z", -1),
             ((-266, 0, 0), "x", 1)]

    def _geo_rov(self):
        """Silueta de submarino real (loft de anillos) + todos los mecanismos."""
        faces = []

        def caja(p1, p2, color):
            x0, y0, z0 = p1
            x1, y1, z1 = p2
            v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                          [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
                         dtype=float)
            for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1),
                      (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)):
                faces.append((v[list(f)], color))

        def placa(pts, color):
            q = np.array(pts, dtype=float)
            faces.append((q, color))
            faces.append((q[::-1].copy(), color))

        # ---- casco tipo submarino: loft de anillos (morro y cola redondeados)
        N = 24
        angs = np.linspace(0, 2 * np.pi, N, endpoint=False)
        perfil = [(-262, 4), (-252, 22), (-230, 38), (-180, 47), (-80, 50),
                  (40, 50), (140, 46), (200, 38), (240, 24), (262, 6)]
        anillos = [np.stack([np.full(N, float(xr)), rr * np.sin(angs),
                             rr * np.cos(angs)], axis=1) for xr, rr in perfil]
        for k in range(len(anillos) - 1):
            A, B = anillos[k], anillos[k + 1]
            for i in range(N):
                j = (i + 1) % N
                zmed = float((A[i][2] + A[j][2] + B[i][2] + B[j][2]) / 4.0)
                col = [72, 82, 92] if zmed >= 0 else [142, 58, 52]
                faces.append((np.array([A[i], A[j], B[j], B[i]]), col))
        faces.append((anillos[0], [60, 68, 76]))    # cola (hélice delante)
        faces.append((anillos[-1], [96, 104, 112]))  # punta del morro

        # ---- vela (torre de mando) + periscopio, sobre la cubierta
        caja((-40, -16, 46), (60, 16, 100), [92, 102, 112])
        caja((0, -4, 100), (18, 4, 132), [92, 102, 112])
        caja((-14, -22, 118), (26, 22, 124), [102, 112, 122])

        # ---- timones en cruz en la cola (como la foto)
        placa([(-262, 0, -56), (-218, 0, -56), (-218, 0, 58), (-262, 0, 58)],
              [82, 92, 102])
        placa([(-262, -54, -8), (-218, -54, -8), (-218, 54, 8), (-262, 54, 8)],
              [92, 102, 112])

        # ---- mecanismos: 4 pods horizontales bajo la panza
        for xx, yy in ((150, 56), (150, -56), (-150, 56), (-150, -56)):
            sy = 1 if yy > 0 else -1
            caja((xx - 22, sy * 28, -46), (xx + 22, yy, -30), GRIS_OSC)
        # ---- 2 verticales como torretas en cubierta
        for xx in (150, -150):
            caja((xx - 22, -16, 46), (xx + 22, 16, 96), GRIS_OSC)

        # ---- arpoón bajo el morro: gimbal + cañón + punta
        caja((0, -20, -74), (70, 20, -48), GRIS_OSC)
        caja((70, -6, -66), (520, 6, -56), PLATA)
        caja((520, -4, -62), (580, 4, -60), ROJO)

        # ---- pinza reforzada (bajo el morro, al lado del arpoón)
        caja((110, -34, -86), (150, 34, -58), ACERO)
        caja((150, -30, -78), (196, -18, -68), ACERO)
        caja((150, 18, -78), (196, 30, -68), ACERO)

        # ---- 4 luces 10 W alrededor del morro
        for p1, p2 in (((252, -30, 12), (264, -10, 32)),
                       ((252, -30, -32), (264, -10, -12)),
                       ((252, 10, 32), (264, 30, 12)),
                       ((252, 10, -32), (264, 30, -12))):
            caja(p1, p2, BLANCO)

        # ---- cámaras: punta (morro), abajo, y 3 domos PTZ con LED
        caja((236, -12, 34), (256, 12, 52), GRIS_OSC)              # CAM1 base
        caja((248, -10, 40), (260, 10, 58), CRISTAL2)             # domo CAM1
        caja((56, -12, -60), (84, 12, -48), GRIS_OSC)             # CAM3 abajo
        caja((118, -12, 46), (142, 12, 64), GRIS_OSC)             # CAM2 base (cubierta)
        caja((142, -10, 40), (154, 10, 62), CRISTAL2)             # cúpula CAM2
        for dx in (-8, 0, 8):                                      # LEDs CAM2
            caja((126 + dx - 3, -4, 46), (126 + dx + 3, 4, 52), BLANCO)
        for s in (1, -1):                                          # CAM4/CAM5
            caja((-8, s * 48, 6), (8, s * 60, 28), GRIS_OSC)
            caja((6, s * 50, 8), (18, s * 60, 26), CRISTAL2)
            for dz in (10, 16, 22):                                # LEDs c/u
                caja((-6, s * 54, dz - 3), (0, s * 60, dz + 3), BLANCO)

        # ---- hatch de baterías en cubierta (popa)
        caja((-190, -24, 44), (-120, 24, 54), GRIS_OSC)
        return faces

    def _proyectar(self, pts):
        vy = math.radians(self.vista3d["yaw"])
        vp = math.radians(self.vista3d["pitch"])
        cy, sy = math.cos(vy), math.sin(vy)
        cp, sp = math.cos(vp), math.sin(vp)
        p = pts - self._centro3d          # centrar el modelo (el arpoón desplaza el bbox)
        x, y, z = p[:, 0], p[:, 1], p[:, 2]
        x1 = x * cy - y * sy
        y1 = x * sy + y * cy
        y2 = y1 * cp - z * sp
        z2 = y1 * sp + z * cp
        return x1, y2, z2

    def _tick_3d(self):
        self._dibujar3d()
        self._dibujar_instrumentos()
        self.after(120, self._tick_3d)

    def _dibujar_instrumentos(self):
        """Horizonte artificial (alabeo/cabeceo) + brújula de rumbo."""
        cv = self.cv_ins
        try:
            w = max(80, cv.winfo_width())
            h = max(60, cv.winfo_height())
        except Exception:
            return
        cv.delete("all")
        roll = self.estado.get("roll", 0.0)
        pitch = self.estado.get("pitch", 0.0)
        rumbo = self.estado["rumbo"]

        # ===== horizonte artificial (izquierda) =====
        ax, ay = int(w * 0.32), h // 2
        R = min(int(h * 0.42), 74)
        rr = math.radians(roll)
        cr, sr = math.cos(rr), math.sin(rr)
        K = 3.0

        def rot(dx, dy):
            return (ax + dx * cr - dy * sr, ay + dx * sr + dy * cr)

        off = pitch * K
        L = 1200
        p1, p2 = rot(-L, off), rot(L, off)
        cielo = (p1[0], p1[1], p2[0], p2[1],
                 rot(L, off - L)[0], rot(L, off - L)[1],
                 rot(-L, off - L)[0], rot(-L, off - L)[1])
        tierra = (p1[0], p1[1], p2[0], p2[1],
                  rot(L, off + L)[0], rot(L, off + L)[1],
                  rot(-L, off + L)[0], rot(-L, off + L)[1])
        cv.create_polygon(cielo, fill="#1e6fd9", outline="")
        cv.create_polygon(tierra, fill="#8a5a2b", outline="")
        cv.create_line(p1[0], p1[1], p2[0], p2[1], fill="white", width=2)
        for d in (-20, -10, 10, 20):                     # escalera de cabeceo
            o = (pitch - d) * K
            q1, q2 = rot(-26, o), rot(26, o)
            cv.create_line(q1[0], q1[1], q2[0], q2[1],
                           fill="white", width=1, dash=(4, 3))
            t = rot(34, o)
            cv.create_text(t[0], t[1], text=str(abs(d)), fill="white",
                           font=("Consolas", 7))
        # máscara circular (tapar lo que sale del aro)
        cv.create_rectangle(0, 0, w, ay - R, fill="#0b0f14", outline="")
        cv.create_rectangle(0, ay + R, w, h, fill="#0b0f14", outline="")
        cv.create_rectangle(0, ay - R, ax - R, ay + R, fill="#0b0f14", outline="")
        cv.create_rectangle(ax + R, ay - R, w, ay + R, fill="#0b0f14", outline="")
        cv.create_oval(ax - R, ay - R, ax + R, ay + R, outline="#58a6ff", width=2)
        for a in (-60, -45, -30, -15, 0, 15, 30, 45, 60):  # escala de alabeo
            aa = math.radians(a)
            x1s = ax + (R + 2) * math.sin(aa)
            y1s = ay - (R + 2) * math.cos(aa)
            x2s = ax + (R + (14 if a % 30 == 0 else 7)) * math.sin(aa)
            y2s = ay - (R + (14 if a % 30 == 0 else 7)) * math.cos(aa)
            cv.create_line(x1s, y1s, x2s, y2s, fill="#c9d1d9", width=1)
        pa = math.radians(roll)
        cv.create_line(ax, ay, ax + (R - 6) * math.sin(pa),
                       ay - (R - 6) * math.cos(pa), fill="yellow", width=2)
        cv.create_line(ax - 26, ay, ax - 8, ay, fill="yellow", width=3)
        cv.create_line(ax + 8, ay, ax + 26, ay, fill="yellow", width=3)
        cv.create_oval(ax - 3, ay - 3, ax + 3, ay + 3, fill="yellow", outline="")

        # ===== brújula (derecha) =====
        cx2, cy2 = int(w * 0.74), h // 2
        R2 = min(int(h * 0.40), 66)
        cv.create_oval(cx2 - R2, cy2 - R2, cx2 + R2, cy2 + R2,
                       outline="#30363d", width=2)
        for a in range(0, 360, 15):
            ang = math.radians(a - rumbo)
            sa, ca = math.sin(ang), math.cos(ang)
            mayor = (a % 45 == 0)
            cv.create_line(cx2 + R2 * sa, cy2 - R2 * ca,
                           cx2 + (R2 - (10 if mayor else 5)) * sa,
                           cy2 - (R2 - (10 if mayor else 5)) * ca,
                           fill="#c9d1d9", width=1)
        letras = {0: "N", 45: "NE", 90: "E", 135: "SE", 180: "S",
                  225: "SO", 270: "O", 315: "NO"}
        for a, txt in letras.items():
            ang = math.radians(a - rumbo)
            cv.create_text(cx2 + (R2 - 20) * math.sin(ang),
                           cy2 - (R2 - 20) * math.cos(ang),
                           text=txt,
                           fill="#58a6ff" if a in (0, 90, 180, 270) else "#8b949e",
                           font=("Segoe UI", 8, "bold"))
        cv.create_polygon(cx2 - 5, cy2 - R2 - 9, cx2 + 5, cy2 - R2 - 9,
                          cx2, cy2 - R2 + 1, fill="yellow", outline="")
        cv.create_text(cx2, cy2 + 1, text=f"{rumbo:.0f}°",
                       fill="white", font=("Consolas", 12, "bold"))
        cv.create_text(cx2, cy2 + 17, text="RUMBO", fill="#8b949e",
                       font=("Segoe UI", 7))

        c = (self.link.aplicado if self.link
             else {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0})
        empuje = max(abs(c["x"]), abs(c["y"]), abs(c["z"]), abs(c["r"]))
        try:
            self.lbl_ins.configure(
                text=(f"EMP {empuje * 100:.0f}% · R {roll:+.0f}° · "
                      f"P {pitch:+.0f}° · {self.estado['modo']}"))
        except Exception:
            pass

    def _dibujar3d(self):
        cv = self.cv3d
        try:
            w = max(80, cv.winfo_width())
            h = max(80, cv.winfo_height())
        except Exception:
            return
        cv.delete("all")
        for k, ccol in enumerate(("#0a0e14", "#0b1017", "#0c121a", "#0d141c")):
            cv.create_rectangle(0, k * h // 4, w, (k + 1) * h // 4,
                                fill=ccol, outline="")
        s = self.vista3d["zoom"]
        cx, cz = w / 2.0, h / 2.0 + 8
        # auto-encuadre la primera vez y tras "reset" (doble clic)
        if not self._fit3d and w > 120 and h > 60:
            self.vista3d["zoom"] = max(
                0.12, min(1.2, min(w / max(1.0, self._ext3d[0]),
                                   h / max(1.0, self._ext3d[2])) * 0.78))
            s = self.vista3d["zoom"]
            self._fit3d = True
        # rotación en vivo: el modelo gira según el rumbo real del submarino
        rumbo = self.estado["rumbo"]
        if self._rumbo_prev is None:
            self._rumbo_prev = rumbo
        delta = (rumbo - self._rumbo_prev + 180.0) % 360.0 - 180.0
        if abs(delta) > 0.01:
            self.vista3d["yaw"] -= delta
            self._rumbo_prev = rumbo
        ahora = time.time()
        golpe_act = self.impacto is not None and ahora - self.impacto["t"] < 3.0
        flash = int(ahora * 6) % 2 == 0
        luz = np.array([0.45, -0.5, -0.74])
        normales_lado = {"frontal": (1, 0, 0), "popa": (-1, 0, 0),
                         "lateral derecho": (0, 1, 0), "lateral izquierdo": (0, -1, 0),
                         "superior": (0, 0, 1), "inferior": (0, 0, -1)}
        vy = math.radians(self.vista3d["yaw"])
        vp = math.radians(self.vista3d["pitch"])
        cyv, syv = math.cos(vy), math.sin(vy)
        cpv, spv = math.cos(vp), math.sin(vp)
        dibujos = []
        for pts, color in self._geo:
            n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
            nn = np.linalg.norm(n)
            if nn <= 1e-6:
                continue
            n = n / nn
            rc = pts.mean(axis=0) - self._centro3d
            if float(np.dot(n, rc)) < 0:
                n = -n
            # ocultar caras traseras: SOLO se ve el exterior del submarino
            a, b, c = n
            if (a * syv + b * cyv) * cpv - c * spv > 0:
                continue
            x1, y2, z2 = self._proyectar(pts)
            px = cx + x1 * s
            py = cz - z2 * s
            col = np.array(color[:3], dtype=float)
            if golpe_act and flash:
                nl = np.array(normales_lado[self.impacto["lado"]], dtype=float)
                if float(np.dot(n, nl)) > 0.55:
                    col = np.array([248.0, 81.0, 73.0])
            brillo = 0.45 + 0.55 * max(0.0, float(np.dot(n, luz)))
            col = tuple(int(min(255, c * brillo)) for c in col)
            dibujos.append((float(y2.mean()), px, py, col))
        dibujos.sort(key=lambda d: -d[0])
        for _, px, py, col in dibujos:
            coords = []
            for ax, ay in zip(px.tolist(), py.tolist()):
                coords.append(ax)
                coords.append(ay)
            cv.create_polygon(coords, fill="#%02x%02x%02x" % col,
                              outline="#0b0f14", width=1)

        # cable (tether) saliendo por la cola
        t0 = self._proyectar(np.array([[-262.0, 0.0, 8.0]]))
        t1 = self._proyectar(np.array([[-310.0, 8.0, 18.0]]))
        t2 = self._proyectar(np.array([[-380.0, 14.0, 30.0]]))
        cv.create_line(cx + t0[0][0] * s, cz - t0[2][0] * s,
                       cx + t1[0][0] * s, cz - t1[2][0] * s,
                       cx + t2[0][0] * s, cz - t2[2][0] * s,
                       fill="#9fb3c8", width=2, dash=(7, 5))

        # hélices girando — según el empuje aplicado (con la rampa suave)
        c = (self.link.aplicado if self.link
             else {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0})
        empuje = max(abs(c["x"]), abs(c["y"]), abs(c["z"]), abs(c["r"]))
        self._prop_ang += 0.25 + 0.9 * empuje
        for (hub, eje, signo) in self.PROPS:
            hx, hy, hz = self._proyectar(np.array([np.array(hub, dtype=float)]))
            hpx, hpy = cx + hx[0] * s, cz - hz[0] * s
            for k in range(3):
                th = self._prop_ang * signo + k * math.pi / 3.0
                if eje == "x":
                    dirv = np.array([0.0, math.cos(th), math.sin(th)]) * 30.0
                else:
                    dirv = np.array([math.cos(th), math.sin(th), 0.0]) * 30.0
                base = np.array([np.array(hub, dtype=float) + dirv])
                tx, _, tz = self._proyectar(base)
                cv.create_line(hpx, hpy, cx + tx[0] * s, cz - tz[0] * s,
                               fill="#f85149", width=2)

        # cámaras PTZ: flecha de vista que gira 360° en el modelo
        campos_ptz = {1: (132, 0, 66), 3: (0, 58, 18), 4: (0, -58, 18)}
        for i, ang_cam in self.ptz.items():
            if i not in campos_ptz:
                continue
            hub = np.array(campos_ptz[i], dtype=float)
            a = math.radians(ang_cam)
            tip = hub + np.array([math.cos(a), math.sin(a), 0.0]) * 60.0
            hx, _, hz = self._proyectar(np.array([hub]))
            tx, _, tz = self._proyectar(np.array([tip]))
            cv.create_line(cx + hx[0] * s, cz - hz[0] * s,
                           cx + tx[0] * s, cz - tz[0] * s, fill="#58a6ff", width=2)
            cv.create_oval(cx + hx[0] * s - 3, cz - hz[0] * s - 3,
                           cx + hx[0] * s + 3, cz - hz[0] * s + 3,
                           fill="#58a6ff", outline="")

        cv.create_text(10, 12, anchor="nw", text=f"6 motores · empuje {empuje * 100:.0f}%",
                       fill="#8b949e", font=("Consolas", 9))
        if golpe_act:
            cv.create_text(w - 10, 12, anchor="ne",
                           text=f"💥 GOLPE {self.impacto['lado'].upper()} · {self.impacto['g']:.1f} g",
                           fill=COL_ROJO if flash else "white",
                           font=("Segoe UI", 11, "bold"))

    def _drag3d_ini(self, ev):
        self._drag = (ev.x, ev.y)

    def _drag3d(self, ev):
        if not self._drag:
            return
        dx, dy = ev.x - self._drag[0], ev.y - self._drag[1]
        self._drag = (ev.x, ev.y)
        self.vista3d["yaw"] += dx * 0.5
        self.vista3d["pitch"] = max(-80.0, min(80.0, self.vista3d["pitch"] - dy * 0.4))

    def _zoom3d(self, ev):
        f = 1.1 if ev.delta > 0 else 0.9
        self.vista3d["zoom"] = max(0.12, min(1.2, self.vista3d["zoom"] * f))

    def _reset3d(self):
        self.vista3d = {"yaw": 115.0, "pitch": 12.0, "zoom": 0.34}
        self._fit3d = False

    def _registrar_golpe(self, dato):
        lado, g, t = dato
        self.impacto = {"lado": lado, "g": float(g), "t": float(t)}
        self.golpes.append(self.impacto)
        self.lbl_golpes.configure(
            text=(f"Golpes: {len(self.golpes)} · último: {lado} ({g:.1f} g) "
                  f"a las {time.strftime('%H:%M:%S', time.localtime(t))}"),
            fg=COL_ROJO)
        self.log(f"💥 Golpe registrado en el modelo 3D: {lado} ({g:.1f} g)")

    def _simular_golpe(self):
        lados = ["frontal", "popa", "lateral derecho", "lateral izquierdo",
                 "superior", "inferior"]
        self._registrar_golpe((random.choice(lados),
                               round(3.0 + random.random() * 3.0, 1), time.time()))

    def _toggle_auto_gancho(self):
        self.auto_gancho = not self.auto_gancho
        if self.auto_gancho:
            self.gancho_estado = "buscando objetivo…"
        self.log("🎯 AUTO-GANCHO: " +
                 ("ON — el sub aproxima y agarra solo." if self.auto_gancho else "OFF."))

    def _steer_gancho(self, demo):
        """Corrige el rumbo del sub para llevar la pinza al objetivo detectado."""
        cmd = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}
        o3 = self.objetivos.get("cam3")
        o1 = self.objetivos.get("cam1")
        if o3 is not None:
            dx, dy = o3[4], o3[5]
            area = o3[2] * o3[3]
            if abs(dx) < 0.12 and abs(dy) < 0.12 and area > 1400:
                self._gancho_capturar()
                return cmd
            cmd["y"] = limitar(dx * 1.2)
            cmd["x"] = limitar(-dy * 1.2)
            self.gancho_estado = "alineando pinza (CAM abajo)"
            return cmd
        if o1 is not None:
            dx = o1[4]
            cmd["r"] = limitar(dx)
            if abs(dx) < 0.25:
                cmd["x"] = 0.30
            self.gancho_estado = "aproximando (CAM punta)"
            if demo and abs(dx) < 0.2:
                self._gancho_capturar()
            return cmd
        self.gancho_estado = "buscando objetivo…"
        return cmd

    def _gancho_capturar(self):
        self.gancho_estado = "¡PRESA AGARRADA!"
        self._gancho_cierre_hasta = time.time() + 1.5
        self.auto_gancho = False
        self.log("🎯 AUTO-GANCHO: objetivo alineado — cerrando pinza (autoagarre).")

    def _toggle_seguro(self):
        self.arpon_seguro = not self.arpon_seguro
        self.log(f"Arpoón: seguro {'ACTIVADO' if self.arpon_seguro else 'QUITADO — listo para disparar'}")

    def _toggle_autoaim(self):
        self.autoaim = not self.autoaim
        self.log(f"Autoapuntado: {'ON' if self.autoaim else 'OFF'}")

    def _log_recoger(self):
        self.log("Carrete: recogiendo hilo (mantén pulsado el botón o F5).")

    def _disparar(self):
        if self.arpon_seguro:
            self.log("Disparo bloqueado: SEGURO activado (P o D-pad ↓ para quitar).")
            return
        if self.emergencia:
            self.log("Disparo bloqueado: hay una emergencia activa.")
            return
        ok = False
        if self.link and self.link.is_alive() and self.estado["conectado"]:
            ok = self.link.disparar()
        if ok:
            self._pago_hasta = time.time() + 0.6
            self.log("🎯 ARPOÓN disparado — hilo soltando 0.6 s, luego carrete libre.")
        else:
            self.log("(demo) Disparo simulado — sin submarino conectado.")

    def _toggle_arm(self):
        if self.estado["conectado"]:
            if self.estado["armado"]:
                self._emerg_parada()
            else:
                self.link.armar()
        else:
            self.log("(demo) ARMAR/DESARMAR solo con submarino conectado.")

    def _toggle_adg(self):
        self.cfg["a_d_girar"] = bool(self.var_adg.get())
        guardar_config(self.cfg)
        modo = "A/D GIRAN (estilo auto) y ←/→ mueven de lado" if self.cfg["a_d_girar"] \
            else "A/D mueven de lado y ←/→ giran"
        self.log(f"Controles: {modo}")

    def _modo_sel(self, ev=None):
        if self.estado["conectado"]:
            self.link.fijar_modo(self.cb_modo.get())
        else:
            self.log(f"(demo) Modo seleccionado: {self.cb_modo.get()}")

    def _aplicar_ajustes(self):
        self.cfg["sub_ip"] = self.var_ip.get().strip()
        try:
            self.cfg["mavlink_puerto"] = int(self.var_puerto.get().strip())
        except ValueError:
            pass
        self.cfg["modo_conexion"] = self.var_modo.get().strip() or "udpout"
        for i, var in enumerate(self.vars_cams):
            self.cfg["camaras"][i]["url"] = var.get().strip()
        guardar_config(self.cfg)
        self.log("Ajustes guardados — reconectando…")
        try:
            self.link.detener()
            self.link.join(timeout=3)
        except Exception:
            pass
        self.link = SubLink(self.cfg, self.estado, self.log, eventos=self.eventos)
        self.link.start()

    def _cerrar(self):
        try:
            self.link.detener()
            self.mando.detener()
            for f in self.feeds:
                f.detener()
        except Exception:
            pass
        self.destroy()

    # ------------------------------------------------------------- bucles
    def _tick_telem(self):
        try:
            while True:
                tipo, dato = self.eventos.get_nowait()
                if tipo == "log":
                    self.txt_log.configure(state="normal")
                    self.txt_log.insert("end", dato + "\n")
                    if int(self.txt_log.index("end-1c").split(".")[0]) > 300:
                        self.txt_log.delete("1.0", "150.0")
                    self.txt_log.configure(state="disabled")
                    self.txt_log.see("end")
                elif tipo == "golpe":
                    self._registrar_golpe(dato)
        except queue.Empty:
            pass

        con = self.estado["conectado"]
        self.demo_flag = not con
        if not con:
            self._simular_demo(0.1)

        prof = self.estado["profundidad"]
        self.lbl_prof.configure(text=f"{prof:.1f} m")
        self.lbl_rumbo.configure(text=f"Rumbo: {self.estado['rumbo']:.0f}°")

        pct = self.estado["batt"]
        volt = self.estado["volt"]
        est_min = (self.cfg["capacidad_wh"] * (pct / 100.0) /
                   max(1.0, self.cfg["potencia_media_w"]) * 60.0) if pct > 0 else 0
        self.bar_ener.configure(value=pct)
        color = COL_VERDE if pct > 40 else (COL_AMBAR if pct > 20 else COL_ROJO)
        self.lbl_ener.configure(text=f"{pct:.0f} %  ·  {volt:.1f} V  ·  ≈ {est_min:.0f} min",
                                fg=color)
        self.lbl_ener.configure(bg=COL_PANEL)

        self.dot.itemconfigure(self.dot_id,
                               fill=COL_VERDE if con else (COL_AMBAR if self.emergencia is None else COL_ROJO))
        if con:
            self.lbl_estado.configure(text=f"CONECTADO · {self.cfg['sub_ip']}", fg=COL_VERDE)
        else:
            self.lbl_estado.configure(text="MODO DEMO (sin submarino)", fg=COL_AMBAR)
        armado = self.estado["armado"]
        if self.activado:
            self.lbl_gate.configure(text="🔓 ACTIVADO · (Enter = bloquear)", fg=COL_VERDE)
        else:
            self.lbl_gate.configure(text="🔒 BLOQUEADO · ENTER para activar", fg=COL_ROJO)
        self.lbl_modo.configure(
            text=f"Modo: {self.estado['modo']}   |   {'🔴 ARMADO' if armado else 'DESARMADO'}",
            fg=COL_ROJO if armado else COL_AMBAR)
        self.btn_arm.configure(text="DESARMAR" if armado else "ARMAR",
                               fg=COL_ROJO if armado else COL_VERDE)

        self.btn_l1.configure(bg=COL_AMBAR if self.luces[0] else COL_PANEL,
                              fg="#111" if self.luces[0] else COL_TEXTO)
        self.btn_l2.configure(bg=COL_AMBAR if self.luces[1] else COL_PANEL,
                              fg="#111" if self.luces[1] else COL_TEXTO)
        self.btn_lptz.configure(bg=COL_AMBAR if self.luces_ptz else COL_PANEL,
                                fg="#111" if self.luces_ptz else COL_ACENTO)

        self.lbl_gimbal.configure(text=f"G:{self.gimbal['yaw']:+.0f}° P:{self.gimbal['pitch']:+.0f}°")
        if self.arpon_seguro:
            self.btn_seguro.configure(text="🔒 SEGURO: ACTIVADO", bg=COL_ROJO, fg="white")
            self.btn_disparo.configure(bg="#3d444d", fg="#8b949e")
        else:
            self.btn_seguro.configure(text="🔓 SEGURO QUITADO — LISTO", bg=COL_VERDE, fg="#0d1117")
            self.btn_disparo.configure(bg=COL_ROJO, fg="white")
        self.btn_autoaim.configure(text=f"Autoapuntado: {'ON' if self.autoaim else 'OFF'}",
                                   bg=COL_VERDE if self.autoaim else COL_PANEL,
                                   fg="#0d1117" if self.autoaim else COL_TEXTO)

        if self.ptz_sel is not None:
            nom = self.cfg["camaras"][self.ptz_sel]["nombre"]
            self.lbl_ptz.configure(
                text=(f"Cámara PTZ: CAM {self.ptz_sel+1} · {nom} · "
                      f"{self.ptz[self.ptz_sel]:.0f}° · vigilancia "
                      f"{'ON' if self.ptz_auto else 'OFF'}"))
        self.btn_ptz_auto.configure(
            text=f"Vigilancia automática: {'ON' if self.ptz_auto else 'OFF'}   [/]",
            bg=COL_VERDE if self.ptz_auto else COL_PANEL,
            fg="#0d1117" if self.ptz_auto else COL_TEXTO)
        self.btn_autogancho.configure(
            text=f"Auto-gancho: {'ON' if self.auto_gancho else 'OFF'}   [C]"
                 + (f" · {self.gancho_estado}" if self.auto_gancho else ""),
            bg=COL_VERDE if self.auto_gancho else COL_PANEL,
            fg="#0d1117" if self.auto_gancho else COL_AMBAR)

        self.after(100, self._tick_telem)

    def _simular_demo(self, dt):
        c = (self.link.aplicado if self.link
             else {"x": 0, "y": 0, "z": 0, "r": 0})
        if self.emergencia == "subida":
            self.demo_prof = max(0.0, self.demo_prof - 1.5 * dt)
            if self.demo_prof <= 0.01:
                self.emergencia = None
                self.log("(demo) Superficie alcanzada — emergencia finalizada.")
        elif self.emergencia == "stop":
            pass
        else:
            self.demo_prof = max(0.0, min(15.0, self.demo_prof - c["z"] * 1.2 * dt))
            self.demo_rumbo = (self.demo_rumbo + c["r"] * 40.0 * dt) % 360.0
            gasto = 0.02 + 0.05 * (abs(c["x"]) + abs(c["y"]) + abs(c["z"]))
            self.demo_batt = max(5.0, self.demo_batt - gasto * dt)
        self.estado["profundidad"] = self.demo_prof
        self.estado["rumbo"] = self.demo_rumbo
        self.estado["batt"] = self.demo_batt
        self.estado["volt"] = 16.8 * (0.75 + 0.25 * self.demo_batt / 100.0)
        self.estado["modo"] = "STABILIZE (demo)"
        self.demo_roll += (limitar(-c["y"] * 0.9 - c["r"] * 0.2, 28.0)
                           - self.demo_roll) * min(1.0, dt * 3.0)
        self.demo_pitch += (limitar(c["x"] * 0.5, 18.0)
                            - self.demo_pitch) * min(1.0, dt * 3.0)
        self.estado["roll"] = self.demo_roll
        self.estado["pitch"] = self.demo_pitch

    def _tick_control(self):
        # Mando: bordes de pulsación
        if self.mando and self.mando.conectado:
            b = self.mando.botones
            e = self.mando.ejes
            if b[BTN_LB] and not self.mando_prev[BTN_LB]:
                self._emerg_parada()
            if b[BTN_RB] and not self.mando_prev[BTN_RB]:
                self._emerg_subida()
            if b[BTN_BACK] and not self.mando_prev[BTN_BACK]:
                self._emerg_normalizar()
            if b[BTN_A] and not self.mando_prev[BTN_A]:
                self._toggle_luces(0)
            if b[BTN_B] and not self.mando_prev[BTN_B]:
                self._toggle_luces(1)
            if b[BTN_START] and not self.mando_prev[BTN_START]:
                self._toggle_arm()
            if b[11] and not self.mando_prev[11]:
                self._disparar()
            if b[12] and not self.mando_prev[12]:
                self._toggle_seguro()
            if b[13] and not self.mando_prev[13]:
                self._toggle_autoaim()
            self.mando_prev = list(b)
            self.mando_ejes = dict(e)

        # combinar teclado + mando (válido también durante emergencia subida)
        tx = (1 if "w" in self.teclas else 0) - (1 if "s" in self.teclas else 0)
        tz = (1 if "e" in self.teclas else 0) - (1 if "q" in self.teclas else 0)
        if self.cfg.get("a_d_girar"):
            # estilo auto: A/D giran, flechas mueven de lado
            tr = limitar((1 if "d" in self.teclas else 0) -
                         (1 if "a" in self.teclas else 0))
            ty = limitar((1 if "Right" in self.teclas else 0) -
                         (1 if "Left" in self.teclas else 0))
        else:
            ty = (1 if "d" in self.teclas else 0) - (1 if "a" in self.teclas else 0)
            tr = (1 if "Right" in self.teclas else 0) - (1 if "Left" in self.teclas else 0)
        x = limitar(tx + self.mando_ejes["x"])
        y = limitar(ty + self.mando_ejes["y"])
        z = limitar(tz + self.mando_ejes["z"])
        r = limitar(tr + self.mando_ejes["r"])

        if self.emergencia == "subida":
            # sube a superficie solo (pico instantáneo) y PUEDES dirigir al instante
            gx = x if self.activado else 0.0
            gy = y if self.activado else 0.0
            gr = r if self.activado else 0.0
            if self.link:
                self.link.emergencia = "subida"
                self.link.cmd = {"x": gx, "y": gy, "z": 0.0, "r": gr}
        elif self.emergencia == "stop":
            if self.link:
                self.link.emergencia = "stop"
        else:
            if self.activado:
                if self.auto_gancho:
                    cmd = self._steer_gancho(not self.estado["conectado"])
                else:
                    cmd = {"x": x, "y": y, "z": z, "r": r}
            else:
                cmd = {"x": 0.0, "y": 0.0, "z": 0.0, "r": 0.0}
            if self.link:
                self.link.cmd = cmd

            # pinza: teclado (G/H) o mando (X/Y)
            if "g" in self.teclas:
                p = 1
            elif "h" in self.teclas:
                p = -1
            elif self.mando_btns[BTN_Y]:
                p = -1
            elif self.mando_btns[BTN_X]:
                p = 1
            else:
                p = 0
            if not self.activado:
                p = 0
            if time.time() < self._gancho_cierre_hasta and self.activado:
                p = -1
            self.pinza = p
            if self.link:
                self.link.aux["pinza"] = p
            if self.link:
                self.link.aux["luces_ptz"] = self.luces_ptz

            # gimbal del arpoón: teclado U/I/O/K o autoapuntado
            manual_gim = ("u" in self.teclas or "i" in self.teclas
                          or "o" in self.teclas or "k" in self.teclas)
            if manual_gim:
                if "u" in self.teclas:
                    self.gimbal["yaw"] -= 2.5
                if "o" in self.teclas:
                    self.gimbal["yaw"] += 2.5
                if "i" in self.teclas:
                    self.gimbal["pitch"] += 2.5
                if "k" in self.teclas:
                    self.gimbal["pitch"] -= 2.5
            elif self.autoaim and self.objetivos["cam1"]:
                dx, dy = self.objetivos["cam1"][4], self.objetivos["cam1"][5]
                self.gimbal["yaw"] += limitar(-dx, 1.0) * 2.0
                self.gimbal["pitch"] += limitar(-dy, 1.0) * 2.0
            self.gimbal["yaw"] = limitar(self.gimbal["yaw"], 60.0)
            self.gimbal["pitch"] = limitar(self.gimbal["pitch"], 45.0)

            # carrete del hilo: F5 / D-pad → recogen (1900); reposo 1500
            recogiendo = ("f5" in self.teclas) or (self.mando.conectado and self.mando_btns[14])
            if time.time() < self._pago_hasta:
                pass  # el carrete está soltando hilo tras el disparo
            elif self.link:
                self.link.aux["carrete"] = 1900 if recogiendo else 1500
                rango = max(1.0, self.cfg.get("gimbal_rango_grados", 60))
                self.link.aux["gimbal_yaw"] = 1500 + self.gimbal["yaw"] * 500.0 / rango
                self.link.aux["gimbal_pitch"] = 1500 + self.gimbal["pitch"] * 500.0 / (rango * 0.75)

        # Cámaras PTZ: rotación manual (',' / '.') o vigilancia automática
        if self.ptz_sel is not None:
            dt = 0.05
            mano = (-1 if "comma" in self.teclas else 0) + (1 if "period" in self.teclas else 0)
            if self.ptz_auto:
                self.ptz[self.ptz_sel] = (self.ptz[self.ptz_sel] +
                                          self.cfg.get("ptz_velocidad", 40) * dt) % 360.0
            elif mano:
                self.ptz[self.ptz_sel] = (self.ptz[self.ptz_sel] + mano * 60.0 * dt) % 360.0
            ang = self.ptz[self.ptz_sel]
            if self._sock and abs(ang - self._last_ptz.get(self.ptz_sel, -999.0)) >= 1.0:
                self._last_ptz[self.ptz_sel] = ang
                try:
                    self._sock.sendto(
                        f"PTZ {self.ptz_sel} {ang:.1f}".encode("utf-8"),
                        (self.cfg["sub_ip"], self.cfg.get("ptz_puerto_udp", 14551)))
                except Exception:
                    pass

        self.after(50, self._tick_control)

    def _tick_video(self):
        if not PIL_OK or not CV_OK:
            self.after(400, self._tick_video)
            return
        # detección de objetivo: CAM1 (punta, arpoón) y CAM3 (abajo, pinza)
        fr1 = self.feeds[0].obtener()
        self._fcount += 1
        if fr1 is not None and self._fcount % 3 == 0:
            self._detectar_objetivo(fr1, "cam1")
        fr3 = self.feeds[2].obtener()
        if fr3 is not None and self._fcount % 3 == 1:
            self._detectar_objetivo(fr3, "cam3")

        # ---- vista principal
        i_main = self.orden[0]
        fr = self.feeds[i_main].obtener()
        if fr is not None:
            self._overlay_cazador(fr, i_main)
            nombre = self.cfg["camaras"][i_main]["nombre"]
            img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
            ph = ImageTk.PhotoImage(img, master=self)
            self.lbl_main.configure(image=ph, text="")
            self.fotos[0] = ph
            url = self.cfg["camaras"][i_main]["url"]
            demo = not self.estado["conectado"]
            if demo or not url:
                self.cap_main.configure(text=f"CAM {i_main+1} · {nombre} · DEMO")
            else:
                self.cap_main.configure(
                    text=f"CAM {i_main+1} · {nombre} · {self.feeds[i_main].fps:.1f} fps")

        # ---- miniaturas
        for pos in range(5):
            marco, lbl, cap = self.minis[pos]
            i = self.orden[pos]
            if pos == 0:
                marco.configure(highlightbackground=COL_ACENTO, highlightthickness=2)
                lbl.configure(bg=COL_PANEL, fg=COL_ACENTO,
                              text=f"▶ PRINCIPAL — CAM {i+1}")
                cap.configure(text=self.cfg["camaras"][i]["nombre"])
                continue
            marco.configure(highlightbackground=COL_BORDE, highlightthickness=1)
            fr2 = self.feeds[i].obtener()
            if fr2 is not None:
                chico = cv2.resize(fr2, (160, 90))
                cv2.rectangle(chico, (0, 0), (160, 15), (25, 25, 25), -1)
                cv2.putText(chico, f"CAM {i+1} · {self.cfg['camaras'][i]['nombre']}",
                            (3, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.32,
                            (240, 240, 240), 1, cv2.LINE_AA)
                img = Image.fromarray(cv2.cvtColor(chico, cv2.COLOR_BGR2RGB))
                ph = ImageTk.PhotoImage(img, master=self)
                lbl.configure(image=ph, text="", bg="#000")
                self.fotos_mini[pos] = ph
            cap.configure(text=f"CAM {i+1} · {self.cfg['camaras'][i]['nombre']}")
        self.after(66, self._tick_video)

    def _overlay_cazador(self, fr, idx):
        """Rótulos + retículas + objetivo en la vista principal."""
        h, w = fr.shape[:2]
        demo = not self.estado["conectado"]
        cv2.rectangle(fr, (0, 0), (w, 30), (25, 25, 25), -1)
        nombre = self.cfg["camaras"][idx]["nombre"]
        cv2.putText(fr, f"CAM {idx+1} · {nombre}" + ("  ·  MODO DEMO" if demo else ""),
                    (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (240, 240, 240), 1, cv2.LINE_AA)
        if demo:
            cv2.putText(fr, "MODO DEMO", (8, h - 36), cv2.FONT_HERSHEY_SIMPLEX,
                        0.55, (60, 200, 255), 1, cv2.LINE_AA)

        # retícula "+" en las cámaras PTZ (giro 360°) + ángulo de vista
        if self.cfg["camaras"][idx].get("ptz"):
            cx, cy = w // 2, h // 2
            cv2.line(fr, (cx - 22, cy), (cx + 22, cy), (255, 166, 88), 2)
            cv2.line(fr, (cx, cy - 22), (cx, cy + 22), (255, 166, 88), 2)
            cv2.circle(fr, (cx, cy), 5, (255, 166, 88), 1)
            ang = self.ptz.get(idx, 0.0)
            cv2.putText(fr, f"PTZ 360° · {ang:.0f}°", (8, h - 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 166, 88), 1, cv2.LINE_AA)

        # CAM punta: arpoón + autoapuntado
        if idx == 0 and not demo:
            cx, cy = w // 2, h // 2
            cv2.drawMarker(fr, (cx, cy), (0, 255, 120), cv2.MARKER_CROSS, 26, 2)
            obj = self.objetivos["cam1"]
            if obj is not None:
                x, y, bw, bh = obj[:4]
                cv2.rectangle(fr, (x, y), (x + bw, y + bh), (0, 200, 255), 2)
                cv2.putText(fr, "OBJETIVO", (x, max(14, y - 6)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 200, 255), 1, cv2.LINE_AA)
            cv2.putText(fr, f"AUTOAIM:{'ON' if self.autoaim else 'OFF'} "
                            f"SEGURO:{'ON' if self.arpon_seguro else 'OFF'}",
                        (8, h - 36), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 120) if self.autoaim else (170, 170, 170), 1, cv2.LINE_AA)

        # CAM abajo: pinza + auto-gancho
        if idx == 2 and not demo:
            cx, cy = w // 2, h // 2
            cv2.line(fr, (cx - 18, cy), (cx + 18, cy), (0, 255, 255), 2)
            cv2.line(fr, (cx, cy - 18), (cx, cy + 18), (0, 255, 255), 2)
            obj = self.objetivos["cam3"]
            if obj is not None:
                x, y, bw, bh = obj[:4]
                cv2.rectangle(fr, (x, y), (x + bw, y + bh), (0, 255, 255), 2)
                cv2.putText(fr, "PRESA", (x, max(14, y - 6)), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(fr, f"AUTO-GANCHO: {self.gancho_estado}",
                        (8, h - 16), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (0, 255, 255) if self.auto_gancho else (170, 170, 170), 1, cv2.LINE_AA)

    def _detectar_objetivo(self, fr, clave="cam1"):
        """Detección: objeto en movimiento más grande y alargado (pez) en la
        cámara dada ('cam1' = punta/arpoón, 'cam3' = abajo/pinza)."""
        try:
            small = cv2.resize(fr, (160, 90))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            bg = self._bg.get(clave)
            if bg is None or bg.shape != gray.shape:
                bg = gray.astype(np.float32)
            cv2.accumulateWeighted(gray, bg, 0.03)
            self._bg[clave] = bg
            bg8 = cv2.convertScaleAbs(bg)
            diff = cv2.absdiff(gray, bg8)
            _, th = cv2.threshold(diff, 22, 255, cv2.THRESH_BINARY)
            th = cv2.dilate(th, np.ones((3, 3), np.uint8), iterations=2)
            cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            mejor = None
            mejor_area = 0
            for c in cnts:
                x, y, w, h = cv2.boundingRect(c)
                area = w * h
                if area < 50 or area > 160 * 90 * 0.6:
                    continue
                r = max(w, h) / max(1.0, min(w, h))
                if r < 1.15 or r > 8.0:  # cuerpos alargados = peces
                    continue
                if area > mejor_area:
                    mejor_area = area
                    mejor = (x, y, w, h)
            if mejor:
                sx = fr.shape[1] / 160.0
                sy = fr.shape[0] / 90.0
                x = int(mejor[0] * sx)
                y = int(mejor[1] * sy)
                w = int(mejor[2] * sx)
                h = int(mejor[3] * sy)
                cx = x + w // 2
                cy = y + h // 2
                dx = (cx - fr.shape[1] / 2.0) / (fr.shape[1] / 2.0)
                dy = (cy - fr.shape[0] / 2.0) / (fr.shape[0] / 2.0)
                self.objetivos[clave] = (x, y, w, h, dx, dy)
            else:
                self.objetivos[clave] = None
        except Exception:
            self.objetivos[clave] = None


def main():
    test = "--test" in sys.argv
    app = App(test=test)
    app.mainloop()
    if test:
        print("SELFTEST OK")


if __name__ == "__main__":
    main()
