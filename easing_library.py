import math
import bpy

# --- 1. CURVA BÉZIER CENTRALIZADA (global) ---
# easing_curve = bpy.types.CurveMapping()
# easing_curve.clip_min_x = 0.0
# easing_curve.clip_min_y = 0.0
# easing_curve.clip_max_x = 1.0
# easing_curve.clip_max_y = 1.0
# easing_curve.use_clip = True
# for curve in easing_curve.curves:
#     curve.points.clear()
#     curve.points.new(0.0, 0.0)
#     curve.points.new(1.0, 1.0)
# easing_curve.initialize()

# --- 4. PRESETS DE EASING AUTOMÁTICOS ---
easing_presets = [
    ("LINEAR", "Linear", "", "IPO_LINEAR", 0),
    ("EASE_IN", "Ease In", "", "IPO_EASE_IN", 1),
    ("EASE_OUT", "Ease Out", "", "IPO_EASE_OUT", 2),
    ("EASE_IN_OUT", "Ease In-Out", "", "IPO_EASE_IN_OUT", 3),
    ("ELASTIC", "Elastic", "", "IPO_ELASTIC", 4),
    ("BOUNCE", "Bounce", "", "IPO_BOUNCE", 5),
    ("BACK", "Back", "", "IPO_BACK", 6),
    ("CUBIC", "Cubic", "", "IPO_CUBIC", 7),
    ("QUINT", "Quint", "", "IPO_QUINT", 8),
    ("SINE", "Sine", "", "IPO_SINE", 9),
    ("CIRCULAR", "Circular", "", "IPO_CIRC", 10),
    ("EXPO", "Expo", "", "IPO_EXPO", 11),
]

# --- 2. CLASE DE ACCESO GLOBAL ---
class TA_EasingLibrary:
    # curve = easing_curve
    preset = 'LINEAR'

# --- 3. SERIALIZACIÓN / EXPORTACIÓN ---
def serialize_curve(curve):
    points_data = []
    for pt in curve.curves[0].points:
        points_data.append({
            "location": list(pt.location),
            "handle_left": list(pt.handle_left),
            "handle_right": list(pt.handle_right)
        })
    return points_data

def deserialize_curve(curve, points_data):
    pts = curve.curves[0].points
    # Ajustar número de puntos
    while len(pts) > len(points_data):
        pts.remove(pts[-1])
    while len(pts) < len(points_data):
        loc = points_data[len(pts)]["location"]
        pts.new(loc[0], loc[1])
    for i, pt_data in enumerate(points_data):
        pt = pts[i]
        pt.location = pt_data["location"]
        pt.handle_left = pt_data["handle_left"]
        pt.handle_right = pt_data["handle_right"]
    curve.update()

# --- 4. PLANTILLAS DE PUNTOS PARA PRESETS ---
def set_easing_preset(preset_name):
    # curve = easing_curve.curves[0]
    # curve.points.clear()
    if preset_name == 'LINEAR':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'EASE_IN':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.5, 0.1)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'EASE_OUT':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.5, 0.9)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'EASE_IN_OUT':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.3, 0.05)
        # curve.points.new(0.7, 0.95)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'BOUNCE':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.3, 1.2)
        # curve.points.new(0.5, 0.8)
        # curve.points.new(0.7, 1.05)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'ELASTIC':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.2, -0.2)
        # curve.points.new(0.5, 1.2)
        # curve.points.new(0.8, 0.8)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'BACK':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.3, -0.2)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'CUBIC':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.4, 0.05)
        # curve.points.new(0.6, 0.95)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'QUINT':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.2, 0.02)
        # curve.points.new(0.8, 0.98)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'SINE':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.5, 0.5)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'CIRCULAR':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.5, 0.15)
        # curve.points.new(1.0, 1.0)
        pass
    elif preset_name == 'EXPO':
        # curve.points.new(0.0, 0.0)
        # curve.points.new(0.1, 0.02)
        # curve.points.new(0.9, 0.98)
        # curve.points.new(1.0, 1.0)
        pass
    else:
        # curve.points.new(0.0, 0.0)
        # curve.points.new(1.0, 1.0)
        pass
    # easing_curve.update()

def ensure_stage_properties(scene):
    props = getattr(scene, 'ta_letter_anim_props', None)
    if props:
        # Do not manually assign new TA_AnimStageProperties instances.
        # If you need to set defaults, do so on the existing instances, e.g.:
        # props.anim_stage_start.use_manual = False
        # props.anim_stage_middle.use_manual = False
        # props.anim_stage_end.use_manual = False
        pass

# === FUNCIONES MATEMÁTICAS DE EASING (SET COMPLETO) ===
def linear(t):
    return t

def ease_in_sine(t):
    return 1 - math.cos((t * math.pi) / 2)

def ease_out_sine(t):
    return math.sin((t * math.pi) / 2)

def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2

def ease_in_quad(t):
    return t * t

def ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)

def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

def ease_in_cubic(t):
    return t * t * t

def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)

def ease_in_out_cubic(t):
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def ease_in_quart(t):
    return t ** 4

def ease_out_quart(t):
    return 1 - pow(1 - t, 4)

def ease_in_out_quart(t):
    return 8 * t ** 4 if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2

def ease_in_quint(t):
    return t ** 5

def ease_out_quint(t):
    return 1 - pow(1 - t, 5)

def ease_in_out_quint(t):
    return 16 * t ** 5 if t < 0.5 else 1 - pow(-2 * t + 2, 5) / 2

def ease_in_expo(t):
    return 0 if t == 0 else pow(2, 10 * t - 10)

def ease_out_expo(t):
    return 1 if t == 1 else 1 - pow(2, -10 * t)

def ease_in_out_expo(t):
    if t == 0:
        return 0
    if t == 1:
        return 1
    return pow(2, 20 * t - 10) / 2 if t < 0.5 else (2 - pow(2, -20 * t + 10)) / 2

def ease_in_circ(t):
    return 1 - math.sqrt(1 - t * t)

def ease_out_circ(t):
    return math.sqrt(1 - pow(t - 1, 2))

def ease_in_out_circ(t):
    return (1 - math.sqrt(1 - 4 * t * t)) / 2 if t < 0.5 else (math.sqrt(1 - pow(-2 * t + 2, 2)) + 1) / 2

def ease_in_back(t, s=1.70158):
    return s * t * t * ((s + 1) * t - s)

def ease_out_back(t, s=1.70158):
    return 1 + s * pow(t - 1, 3) + s * pow(t - 1, 2)

def ease_in_out_back(t, s=1.70158):
    s *= 1.525
    return (pow(2 * t, 2) * ((s + 1) * 2 * t - s)) / 2 if t < 0.5 else (pow(2 * t - 2, 2) * ((s + 1) * (t * 2 - 2) + s) + 2) / 2

def ease_in_elastic(t, amplitude=1, period=0.3):
    if t == 0 or t == 1:
        return t
    s = period / (2 * math.pi) * math.asin(1 / amplitude) if amplitude >= 1 else period / 4
    return -(amplitude * pow(2, 10 * (t - 1)) * math.sin((t - 1 - s) * (2 * math.pi) / period))

def ease_out_elastic(t, amplitude=1, period=0.3):
    if t == 0 or t == 1:
        return t
    s = period / (2 * math.pi) * math.asin(1 / amplitude) if amplitude >= 1 else period / 4
    return amplitude * pow(2, -10 * t) * math.sin((t - s) * (2 * math.pi) / period) + 1

def ease_in_out_elastic(t, amplitude=1, period=0.45):
    if t == 0 or t == 1:
        return t
    s = period / (2 * math.pi) * math.asin(1 / amplitude) if amplitude >= 1 else period / 4
    if t < 0.5:
        return -0.5 * (amplitude * pow(2, 20 * t - 10) * math.sin((20 * t - 11.125) * (2 * math.pi) / period))
    else:
        return amplitude * pow(2, -20 * t + 10) * math.sin((20 * t - 11.125) * (2 * math.pi) / period) * 0.5 + 1

def ease_in_bounce(t):
    return 1 - ease_out_bounce(1 - t)

def ease_out_bounce(t):
    n1 = 7.5625
    d1 = 2.75
    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375

def ease_in_out_bounce(t):
    return (1 - ease_out_bounce(1 - 2 * t)) / 2 if t < 0.5 else (1 + ease_out_bounce(2 * t - 1)) / 2

# Polinomios de orden alto (sextic, septic, octic)
def ease_in_sextic(t):
    return t ** 6

def ease_out_sextic(t):
    return 1 - pow(1 - t, 6)

def ease_in_out_sextic(t):
    return 64 * t ** 6 if t < 0.5 else 1 - pow(-2 * t + 2, 6) / 2

def ease_in_septic(t):
    return t ** 7

def ease_out_septic(t):
    return 1 - pow(1 - t, 7)

def ease_in_out_septic(t):
    return 128 * t ** 7 if t < 0.5 else 1 - pow(-2 * t + 2, 7) / 2

def ease_in_octic(t):
    return t ** 8

def ease_out_octic(t):
    return 1 - pow(1 - t, 8)

def ease_in_out_octic(t):
    return 256 * t ** 8 if t < 0.5 else 1 - pow(-2 * t + 2, 8) / 2

# Diccionario de acceso rápido por nombre
easings = {
    'linear': linear,
    'ease_in_sine': ease_in_sine,
    'ease_out_sine': ease_out_sine,
    'ease_in_out_sine': ease_in_out_sine,
    'ease_in_quad': ease_in_quad,
    'ease_out_quad': ease_out_quad,
    'ease_in_out_quad': ease_in_out_quad,
    'ease_in_cubic': ease_in_cubic,
    'ease_out_cubic': ease_out_cubic,
    'ease_in_out_cubic': ease_in_out_cubic,
    'ease_in_quart': ease_in_quart,
    'ease_out_quart': ease_out_quart,
    'ease_in_out_quart': ease_in_out_quart,
    'ease_in_quint': ease_in_quint,
    'ease_out_quint': ease_out_quint,
    'ease_in_out_quint': ease_in_out_quint,
    'ease_in_expo': ease_in_expo,
    'ease_out_expo': ease_out_expo,
    'ease_in_out_expo': ease_in_out_expo,
    'ease_in_circ': ease_in_circ,
    'ease_out_circ': ease_out_circ,
    'ease_in_out_circ': ease_in_out_circ,
    'ease_in_back': ease_in_back,
    'ease_out_back': ease_out_back,
    'ease_in_out_back': ease_in_out_back,
    'ease_in_elastic': ease_in_elastic,
    'ease_out_elastic': ease_out_elastic,
    'ease_in_out_elastic': ease_in_out_elastic,
    'ease_in_bounce': ease_in_bounce,
    'ease_out_bounce': ease_out_bounce,
    'ease_in_out_bounce': ease_in_out_bounce,
    'ease_in_sextic': ease_in_sextic,
    'ease_out_sextic': ease_out_sextic,
    'ease_in_out_sextic': ease_in_out_sextic,
    'ease_in_septic': ease_in_septic,
    'ease_out_septic': ease_out_septic,
    'ease_in_out_septic': ease_in_out_septic,
    'ease_in_octic': ease_in_octic,
    'ease_out_octic': ease_out_octic,
    'ease_in_out_octic': ease_in_out_octic,
}
