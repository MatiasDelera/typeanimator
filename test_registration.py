"""
Script simple para probar el registro del addon TypeAnimator.
"""

import sys
import os

def test_imports():
    """Probar las importaciones básicas"""
    print("🔍 Probando importaciones...")
    
    try:
        # Probar importación de constants
        from constants import CURVE_NODE_GROUP_NAME, BLEND_WIDTH
        print("✅ constants.py - OK")
    except Exception as e:
        print(f"❌ constants.py - Error: {e}")
        return False
    
    try:
        # Probar importación de curves
        from curves import get_or_create_curve_node
        print("✅ curves.py - OK")
    except Exception as e:
        print(f"❌ curves.py - Error: {e}")
        return False
    
    try:
        # Probar importación de properties
        from properties import TA_LetterAnimProperties
        print("✅ properties.py - OK")
    except Exception as e:
        print(f"❌ properties.py - Error: {e}")
        return False
    
    try:
        # Probar importación de presets
        from presets import PresetItem
        print("✅ presets.py - OK")
    except Exception as e:
        print(f"❌ presets.py - Error: {e}")
        return False
    
    try:
        # Probar importación de operators
        from operators import TA_OT_copy_curve_between_stages
        print("✅ operators.py - OK")
    except Exception as e:
        print(f"❌ operators.py - Error: {e}")
        return False
    
    try:
        # Probar importación de registration
        from registration import register, unregister
        print("✅ registration.py - OK")
    except Exception as e:
        print(f"❌ registration.py - Error: {e}")
        return False
    
    return True

def test_syntax():
    """Probar sintaxis de archivos Python"""
    print("\n🔍 Probando sintaxis...")
    
    files_to_test = [
        "constants.py",
        "curves.py", 
        "properties.py",
        "presets.py",
        "operators.py",
        "registration.py",
        "handlers.py"
    ]
    
    all_ok = True
    for file in files_to_test:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"✅ {file} - Sintaxis OK")
        except Exception as e:
            print(f"❌ {file} - Error de sintaxis: {e}")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("🚀 PRUEBA DE REGISTRO DEL ADDON")
    print("=" * 50)
    
    # Cambiar al directorio del addon
    addon_dir = os.path.dirname(__file__)
    os.chdir(addon_dir)
    
    # Probar sintaxis
    syntax_ok = test_syntax()
    
    # Probar importaciones
    imports_ok = test_imports()
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN")
    print("=" * 50)
    
    if syntax_ok and imports_ok:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("✅ El addon está listo para registrar en Blender")
    else:
        print("❌ HAY PROBLEMAS QUE CORREGIR")
        if not syntax_ok:
            print("   - Errores de sintaxis detectados")
        if not imports_ok:
            print("   - Errores de importación detectados")
    
