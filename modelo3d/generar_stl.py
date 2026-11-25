#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_stl.py — Genera el modelo 3D del mini-ROV (STL + GLB) con trimesh.

Diseño (unidades: mm, X = adelante, Y = lateral, Z = arriba):
  · Casco estanco: tubo Ø100 × 450 mm con tapas y domo frontal
  · Frame: 6 rieles de aluminio/PVC (55 × 32 cm)
  · 6 motores sellados: 2 frontales, 2 poperos, 2 verticales
  · Aletas: dorsal + 2 estabilizadores poperos + quilla
  · 4 luces LED 10 W a 90° alrededor del frente
  · 4 cámaras (frontal en domo, pinza, popa, lateral)
  · Arpoón con gimbal, gomas, arpón y carrete de hilo
  · Pinza de agarre reforzado
  · Bahía de batería intercambiable (hatch rápido)
  · Foam de flotabilidad arriba
  · Salida de tether (cable de 20 m)

Salida: submarino.stl y submarino.glb (abrir con "Visor 3D" de Windows).
"""
import math
import os
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix, translation_matrix, concatenate_matrices

OUT = os.path.dirname(os.path.abspath(__file__))
S = 1.0  # escala global


def tf_rot(angle, axis):
    return rotation_matrix(np.radians(angle), axis)


def tf_pos(pos):
    return translation_matrix(np.array(pos, dtype=np.float64))


def caja(dim, pos, color, rot=None):
    m = trimesh.creation.box(extents=np.array(dim, dtype=np.float64) * S)
    T = tf_pos(pos)
    if rot is not None:
        T = concatenate_matrices(T, tf_rot(rot[0], rot[1]))
    m.apply_transform(T)
    m.visual.face_colors = color
    return m


def cil(r, h, pos, color, eje="x", rot_extra=None):
    m = trimesh.creation.cylinder(radius=r * S, height=h * S, sections=48)
    if eje == "x":
        m.apply_transform(tf_rot(90, [0, 1, 0]))
    elif eje == "y":
        m.apply_transform(tf_rot(90, [1, 0, 0]))
    T = tf_pos(pos)
    if rot_extra is not None:
        T = concatenate_matrices(T, tf_rot(rot_extra[0], rot_extra[1]))
    m.apply_transform(T)
    m.visual.face_colors = color
    return m


def esfera(r, pos, color):
    m = trimesh.creation.icosphere(subdivisions=3, radius=r * S)
    m.apply_transform(tf_pos(pos))
    m.visual.face_colors = color
    return m


def cono(r, h, pos, color, eje="x", invertir=False):
    m = trimesh.creation.cone(radius=r * S, height=h * S, sections=32)
    if eje == "x":
        m.apply_transform(tf_rot(90, [0, 1, 0]))
        if invertir:
            m.apply_transform(tf_rot(180, [0, 0, 1]))
    T = tf_pos(pos)
    m.apply_transform(T)
    m.visual.face_colors = color
    return m


AZUL = [63, 185, 201, 255]      # casco
GRIS = [110, 119, 129, 255]     # frame
GRIS_OSC = [70, 76, 84, 255]    # motores
ROJO = [248, 81, 73, 255]       # hélices / aletas
AMARILLO = [210, 153, 34, 255]  # foam
BLANCO = [230, 237, 243, 255]   # luces
CRISTAL = [139, 200, 255, 200]  # domo
PLATA = [160, 169, 178, 255]    # arpoón
ACERO = [125, 135, 150, 255]    # pinza
NARANJA = [227, 179, 65, 255]   # batería
VERDE = [63, 185, 80, 255]      # aletas accesorias

partes = []

# ================= CASCO =================
partes.append(cil(50, 450, [0, 0, 0], AZUL))                      # tubo acrílico Ø100
partes.append(cil(52, 20, [235, 0, 0], GRIS_OSC))                 # tapa frontal
partes.append(cil(52, 20, [-235, 0, 0], GRIS_OSC))                # tapa popera
partes.append(esfera(46, [268, 0, 8], CRISTAL))                   # domo cámara frontal

# ================= FRAME =================
for yy in (150, -150):
    for zz in (75, -75):
        partes.append(caja([560, 14, 14], [0, yy, zz], GRIS))     # 4 rieles largos
for xx in (270, -270):
    for yy in (150, -150):
        partes.append(caja([14, 14, 164], [xx, yy, 0], GRIS))     # montantes
for xx in (270, -270):
    partes.append(caja([14, 286, 14], [xx, 0, 75], GRIS))         # travesaños superiores

# ================= FOAM =================
partes.append(caja([280, 90, 40], [0, 0, 118], AMARILLO))

# ================= 6 MOTORES =================
def thruster(pos, eje, invertir=False):
    parts = []
    if eje == "x":
        parts.append(cil(22, 85, pos, GRIS_OSC, eje="x"))
        parts.append(cil(26, 10, [pos[0] + (40 if not invertir else -40), pos[1], pos[2]], GRIS_OSC, eje="x"))
        for a in (0, 120, 240):
            parts.append(caja([34, 8, 3], [pos[0] + (14 if not invertir else -14), pos[1], pos[2]],
                              ROJO, rot=(a, [1, 0, 0])))
    elif eje == "z":
        parts.append(cil(22, 85, pos, GRIS_OSC, eje="z"))
        parts.append(cil(26, 10, [pos[0], pos[1], pos[2] + 40], GRIS_OSC, eje="z"))
        for a in (0, 120, 240):
            parts.append(caja([34, 3, 8], [pos[0], pos[1], pos[2] + 14], ROJO, rot=(a, [0, 0, 1])))
    return parts

# 2 frontales horizontales
partes += thruster([235, 105, 0], "x")
partes += thruster([235, -105, 0], "x")
# 2 poperos horizontales
partes += thruster([-235, 105, 0], "x", invertir=True)
partes += thruster([-235, -105, 0], "x", invertir=True)
# 2 verticales (diagonales para equilibrar par)
partes += thruster([150, 75, 118], "z")
partes += thruster([-150, -75, 118], "z")

# ================= ALETAS =================
partes.append(caja([130, 8, 85], [-190, 0, 128], ROJO))                    # aleta dorsal
partes.append(caja([100, 8, 80], [-215, 85, 0], ROJO))                     # aleta popera der
partes.append(caja([100, 8, 80], [-215, -85, 0], ROJO))                    # aleta popera izq
partes.append(caja([100, 8, 55], [-190, 0, -122], VERDE))                  # quilla

# ================= 4 LUCES 10 W =================
for pos in ([245, 0, 78], [245, 0, -70], [245, 95, 0], [245, -95, 0]):
    partes.append(cil(30, 26, pos, BLANCO, eje="x"))
    partes.append(cil(26, 4, [pos[0] + 15, pos[1], pos[2]], BLANCO, eje="x"))

# ================= 5 CÁMARAS (3 domos PTZ 360° con anillo LED) =================
partes.append(esfera(42, [258, 0, 8], CRISTAL))                            # CAM1 punta (domo)
partes.append(cil(18, 22, [65, 0, 56], GRIS_OSC, eje="z"))                 # servo PTZ CAM2
partes.append(esfera(20, [65, 0, 72], CRISTAL))                            # cúpula CAM2
for k in range(6):                                                         # anillo 6 LEDs CAM2
    a = math.radians(k * 60)
    partes.append(cil(4, 9, [65 + 17 * math.cos(a), 17 * math.sin(a), 60], BLANCO, eje="z"))
partes.append(caja([30, 22, 12], [95, 0, 56], GRIS_OSC))                   # módulo térmico MLX90640
partes.append(cil(8, 6, [95, 0, 63], GRIS_OSC, eje="z"))                   # ventana del térmico
partes.append(cil(15, 26, [40, 0, -74], PLATA, eje="z",
                  rot_extra=(180, [0, 0, 1])))                             # CAM3 abajo (fija)
for yy in (62, -62):                                                       # servos PTZ laterales
    partes.append(caja([26, 26, 24], [78, yy, 0], GRIS_OSC))
sgn = 1
for yy in (62, -62):                                                       # domos CAM4/CAM5 + LEDs
    partes.append(esfera(20, [78, yy + sgn * 18, 0], CRISTAL))
    for k in range(6):
        a = math.radians(k * 60)
        partes.append(cil(4, 9, [78 + 17 * math.cos(a), yy + sgn * 24, 17 * math.sin(a)],
                          BLANCO, eje="y"))
    sgn = -1

# ================= ARPOÓN + GIMBAL + CARRETE =================
partes.append(caja([90, 60, 60], [60, 0, -100], GRIS_OSC))                 # caja gimbal (servos)
partes.append(cil(11, 480, [330, 0, -100], PLATA, eje="x"))                # cañón arpoón
partes.append(cono(10, 60, [570, 0, -100], PLATA, eje="x"))                # punta
for yy in (16, -16):
    partes.append(cil(3.5, 470, [330, yy, -84], ROJO, eje="x"))            # gomas (2 bandas)
partes.append(caja([50, 20, 70], [90, 0, -70], GRIS_OSC))                  # anclaje gomas
partes.append(cil(26, 34, [10, 0, -140], PLATA, eje="x"))                  # carrete de hilo
partes.append(cil(6, 60, [10, 0, -140], PLATA, eje="y"))                   # eje carrete
partes.append(caja([40, 30, 26], [-35, 0, -140], GRIS_OSC))                # motor carrete

# ================= PINZA REFORZADA =================
partes.append(caja([46, 80, 32], [225, 0, -118], ACERO))                   # base servos
for signo in (1, -1):
    partes.append(caja([75, 14, 16], [285, signo * 30, -118], ACERO,
                        rot=(signo * 14, [0, 0, 1])))                      # dedos dentados

# ================= BAHÍA DE BATERÍAS 2× DEWALT DCB205 =================
partes.append(caja([215, 82, 78], [-130, 0, -55], NARANJA))                 # 2 packs 20V 5Ah
partes.append(caja([225, 92, 8], [-130, 0, -13], GRIS_OSC))                 # hatch rápido
partes.append(caja([30, 10, 8], [-130, 0, -7], AMARILLO))                   # asa del hatch

# ================= TETHER =================
partes.append(cil(10, 26, [-240, 0, -45], PLATA, eje="x"))                 # prensa-estopas

# ================= PUERTA DE CARGA (la "puertita") =================
partes.append(caja([36, 8, 44], [-140, -56, 0], GRIS_OSC))                 # puerta lateral
partes.append(cil(7, 10, [-140, -64, 0], PLATA, eje="y"))                  # conector XT60 panel
partes.append(caja([10, 6, 10], [-115, -56, 18], VERDE))                   # LED indicador

# ================= EXPORTAR =================
modelo = trimesh.util.concatenate(partes)
stl_path = os.path.join(OUT, "submarino.stl")
glb_path = os.path.join(OUT, "submarino.glb")
modelo.export(stl_path)
modelo.export(glb_path)
ext = modelo.bounds[1] - modelo.bounds[0]
print(f"Partes: {len(partes)}  |  Triángulos: {len(modelo.faces)}")
print(f"Dimensiones: {ext[0]:.0f} × {ext[1]:.0f} × {ext[2]:.0f} mm")
print(f"Guardado: {stl_path}")
print(f"Guardado: {glb_path}")
