// ==========================================================================
//  MINI-ROV SUBMARINO — Modelo 3D paramétrico (OpenSCAD)
//  Abrir con OpenSCAD (gratuito): https://openscad.org
//  Unidades en mm · X = adelante · Y = lateral · Z = arriba
//  Componentes: casco Ø100, 6 motores sellados, aletas, 4 luces 10 W,
//  4 cámaras, arpoón con gimbal y carrete de hilo, pinza reforzada,
//  bahía de batería intercambiable, foam de flotabilidad, tether.
// ==========================================================================

$fn = 48;

// ---------- Parámetros principales ----------
casco_r     = 50;    // radio del casco acrílico (Ø100)
casco_l     = 450;   // largo del casco
frame_lx    = 560;   // largo del frame
frame_ly    = 300;   // ancho del frame
frame_rail  = 14;    // sección del riel
motor_r     = 22;    // radio del tubo del motor
motor_l     = 85;    // largo del tubo del motor
arpon_l     = 480;   // cañón del arpoón
arpon_r     = 11;
bateria_l   = 180;   // batería 4S intercambiable

// ---------- Módulos de piezas ----------

module motor_sellado(pos, eje = "x", invertir = false) {
    // Tubo estanco + hélice de 3 palas
    translate(pos) {
        if (eje == "x") {
            rotate([0, 90, 0]) cylinder(r = motor_r, h = motor_l, center = true);
            translate([invertir ? -48 : 48, 0, 0])
                rotate([0, 90, 0]) cylinder(r = 26, h = 10, center = true);
            for (a = [0, 120, 240])
                translate([invertir ? -20 : 20, 0, 0])
                    rotate([a, 0, 0]) cube([4, 34, 8], center = true);
        } else {
            cylinder(r = motor_r, h = motor_l, center = true);
            translate([0, 0, 48]) cylinder(r = 26, h = 10, center = true);
            for (a = [0, 120, 240])
                translate([0, 0, 20]) rotate([0, 0, a]) cube([34, 8, 4], center = true);
        }
    }
}

module luz_led(pos) {
    // LED 10 W con lente de 90° y disipador
    translate(pos) rotate([0, 90, 0]) {
        cylinder(r = 30, h = 26, center = true);
        translate([16, 0, 0]) cylinder(r = 26, h = 4, center = true);
    }
}

module camara(pos, ang = 0) {
    translate(pos) rotate([0, ang, 0])
        cylinder(r = 15, h = 26, center = true);
}

module aleta(tam, pos) {
    translate(pos) cube(tam, center = true);
}

// ---------- Ensamblaje ----------

// CASCO ESTANCO
color("steelblue")
    rotate([0, 90, 0]) cylinder(r = casco_r, h = casco_l, center = true);
color("dimgray") {
    translate([casco_l / 2 + 10, 0, 0])
        rotate([0, 90, 0]) cylinder(r = casco_r + 2, h = 20, center = true);
    translate([-casco_l / 2 - 10, 0, 0])
        rotate([0, 90, 0]) cylinder(r = casco_r + 2, h = 20, center = true);
}
color("lightskyblue", 0.6)
    translate([casco_l / 2 + 18, 0, 8]) sphere(r = 42);          // domo CAM1

// FRAME (6 rieles)
color("gray")
for (yy = [-frame_ly / 2, frame_ly / 2], zz = [-75, 75])
    translate([0, yy, zz]) cube([frame_lx, frame_rail, frame_rail], center = true);
for (xx = [-270, 270], yy = [-frame_ly / 2, frame_ly / 2])
    translate([xx, yy, 0]) cube([frame_rail, frame_rail, 164], center = true);
for (xx = [-270, 270])
    translate([xx, 0, 75]) cube([frame_rail, frame_ly, frame_rail], center = true);

// FOAM DE FLOTABILIDAD
color("gold", 0.9) translate([0, 0, 118]) cube([280, 90, 40], center = true);

// 6 MOTORES: 2 frontales + 2 poperos + 2 verticales
color("dimgray") {
    motor_sellado([235, 105, 0], "x");
    motor_sellado([235, -105, 0], "x");
    motor_sellado([-235, 105, 0], "x", true);
    motor_sellado([-235, -105, 0], "x", true);
    motor_sellado([150, 75, 118], "z");
    motor_sellado([-150, -75, 118], "z");
}

// ALETAS (dorsal + 2 poperas + quilla)
color("tomato") {
    aleta([130, 8, 85], [-190, 0, 128]);
    aleta([100, 8, 80], [-215, 85, 0]);
    aleta([100, 8, 80], [-215, -85, 0]);
}
color("mediumseagreen") aleta([100, 8, 55], [-190, 0, -122]);

// 4 LUCES 10 W (cada 90° alrededor del frente)
color("white") {
    luz_led([245, 0, 78]);
    luz_led([245, 0, -70]);
    luz_led([245, 95, 0]);
    luz_led([245, -95, 0]);
}

// 5 CÁMARAS (3 domos PTZ 360° con anillo LED para oscuridad)
color("lightskyblue", 0.6) {
    translate([casco_l / 2 + 24, 0, 8]) sphere(r = 40);                   // CAM1 punta
    translate([65, 0, 72]) sphere(r = 20);                                // cúpula CAM2
    translate([78, 80, 0]) sphere(r = 20);                                // cúpula CAM4
    translate([78, -80, 0]) sphere(r = 20);                               // cúpula CAM5
}
color("white")
for (i = [0:5]) {
    translate([65 + 17 * cos(i * 60), 17 * sin(i * 60), 60])
        cylinder(r = 4, h = 9, center = true);                            // LEDs CAM2
    for (s = [1, -1])
        translate([78 + 17 * cos(i * 60), s * 84, 17 * sin(i * 60)])
            rotate([90, 0, 0]) cylinder(r = 4, h = 9, center = true);     // LEDs CAM4/CAM5
}
// Módulo térmico MLX90640 (domo superior)
color("dimgray") translate([95, 0, 56]) cube([30, 22, 12], center = true);
color("silver") translate([95, 0, 63]) cylinder(r = 8, h = 6, center = true);
color("dimgray") {
    translate([65, 0, 56]) cylinder(r = 18, h = 22, center = true);       // servo PTZ
    translate([78, 62, 0]) cube([26, 26, 24], center = true);             // servo PTZ izq
    translate([78, -62, 0]) cube([26, 26, 24], center = true);            // servo PTZ der
}
color("silver")
    translate([40, 0, -74]) cylinder(r = 15, h = 26, center = true);      // CAM3 abajo

// ARPOÓN: gimbal + cañón + gomas + carrete de hilo
color("dimgray") {
    translate([60, 0, -100]) cube([90, 60, 60], center = true);   // gimbal
    translate([90, 0, -70]) cube([50, 20, 70], center = true);    // anclaje gomas
    translate([-35, 0, -140]) cube([40, 30, 26], center = true);  // motor carrete
}
color("silver") {
    translate([330, 0, -100])
        rotate([0, 90, 0]) cylinder(r = arpon_r, h = arpon_l, center = true);
    translate([570, 0, -100])
        rotate([0, 90, 0]) cylinder(r = 10, h = 60, center = false);
    translate([10, 0, -140])
        rotate([0, 90, 0]) cylinder(r = 26, h = 34, center = true);  // carrete
}
color("tomato")
for (yy = [16, -16])
    translate([330, yy, -84])
        rotate([0, 90, 0]) cylinder(r = 3.5, h = 470, center = true);  // gomas

// PINZA REFORZADA (servo 20 kg·cm + dedos dentados)
color("slategray") {
    translate([225, 0, -118]) cube([46, 80, 32], center = true);
    for (s = [1, -1])
        translate([285, s * 30, -118])
            rotate([0, 0, s * 14]) cube([75, 14, 16], center = true);
}

// BAHÍA DE BATERÍA INTERCAMBIABLE (hatch rápido)
color("darkorange") translate([-90, 0, -58]) cube([bateria_l, 74, 52], center = true);
color("dimgray") translate([-90, 0, -26]) cube([190, 84, 8], center = true);
color("gold") translate([-90, 0, -20]) cube([30, 10, 8], center = true);

// TETHER (salida del cable de 20 m)
color("silver") translate([-240, 0, -45])
    rotate([0, 90, 0]) cylinder(r = 10, h = 26, center = true);

// PUERTA DE CARGA (la "puertita") + conector XT60 + LED
color("dimgray") translate([-140, -56, 0]) cube([36, 8, 44], center = true);
color("silver") translate([-140, -64, 0])
    rotate([90, 0, 0]) cylinder(r = 7, h = 10, center = true);
color("mediumseagreen") translate([-115, -56, 18]) cube([10, 6, 10], center = true);
