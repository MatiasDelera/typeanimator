"""
Script simple para probar las importaciones básicas del addon.
"""

import sys
import os

def test_basic_imports():
    """Probar importaciones básicas"""
    print("🔍 Probando importaciones básicas...")
    
    try:
        # Probar constants
        from constants import CURVE_NODE_GROUP_NAME, BLEND_WIDTH, PresetPriority
        print("✅ constants.py - OK")
    except Exception as e:
        print(f"❌ constants.py - Error: {e}")
        return False
    
    try:
        # Probar presets
        from presets import PresetItem, safe_json_load
        print("✅ presets.py - OK")
    except Exception as e:
        print(f"❌ presets.py - Error: {e}")
        return False
    
    try:
        # Probar preset_manager
        from preset_manager import PresetPriority
        print("✅ preset_manager.py - OK")
    except Exception as e:
        print(f"❌ preset_manager.py - Error: {e}")
        return False
    
    try:
        # Probar properties
        from properties import TA_LetterAnimProperties
        print("✅ properties.py - OK")
    except Exception as e:
        print(f"❌ properties.py - Error: {e}")
        return False
    
    try:
        # Probar preferences
        from preferences import TAAddonPreferences
        print("✅ preferences.py - OK")
    except Exception as e:
        print(f"❌ preferences.py - Error: {e}")
        return False
    
    try:
        # Probar settings_io
        from settings_io import save_last_settings, load_last_settings
        print("✅ settings_io.py - OK")
    except Exception as e:
        print(f"❌ settings_io.py - Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 PRUEBA DE IMPORTACIONES BÁSICAS")
    print("=" * 50)
    
    # Cambiar al directorio del addon
    addon_dir = os.path.dirname(__file__)
    os.chdir(addon_dir)
    
    # Probar importaciones
    success = test_basic_imports()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TODAS LAS IMPORTACIONES PASARON")
        print("✅ El addon debería registrarse correctamente")
    else:
        print("❌ HAY PROBLEMAS DE IMPORTACIÓN")
    
    return success 