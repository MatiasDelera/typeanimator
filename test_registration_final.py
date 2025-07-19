"""
Script final para probar el registro completo del addon.
"""

import sys
import os
import importlib

def test_module_registration():
    """Probar que todos los módulos tienen funciones register/unregister."""
    print("🔍 Probando funciones de registro...")
    
    modules_to_test = [
        'constants',
        'presets', 
        'preset_manager',
        'properties',
        'preferences',
        'settings_io',
        'utils',
        'operators',
        'ui',
        'fonts',
        'styles',
        'core',
        'preview',
        'icon_loader'
    ]
    
    missing_functions = []
    
    for module_name in modules_to_test:
        try:
            module = importlib.import_module(f'.{module_name}', package='typeanimator')
            
            has_register = hasattr(module, 'register')
            has_unregister = hasattr(module, 'unregister')
            
            if not has_register:
                missing_functions.append(f"{module_name}.register")
            if not has_unregister:
                missing_functions.append(f"{module_name}.unregister")
                
            print(f"✅ {module_name}: register={has_register}, unregister={has_unregister}")
            
        except Exception as e:
            print(f"❌ {module_name}: Error - {e}")
            return False
    
    if missing_functions:
        print(f"\n❌ Funciones faltantes: {missing_functions}")
        return False
    
    return True

def test_main_registration():
    """Probar el registro principal."""
    print("\n🔍 Probando registro principal...")
    
    try:
        from registration import register, unregister
        print("✅ Funciones register/unregister encontradas en registration.py")
        return True
    except Exception as e:
        print(f"❌ Error en registro principal: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA FINAL DE REGISTRO")
    print("=" * 50)
    
    # Cambiar al directorio del addon
    addon_dir = os.path.dirname(__file__)
    os.chdir(addon_dir)
    
    # Agregar el directorio actual al path
    sys.path.insert(0, addon_dir)
    
    # Probar módulos
    modules_ok = test_module_registration()
    
    # Probar registro principal
    main_ok = test_main_registration()
    
    print("\n" + "=" * 50)
    if modules_ok and main_ok:
        print("✅ TODAS LAS PRUEBAS PASARON")
        print("✅ El addon debería registrarse correctamente en Blender")
    else:
        print("❌ HAY PROBLEMAS DE REGISTRO")
    
    return modules_ok and main_ok 