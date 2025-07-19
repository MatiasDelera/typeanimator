"""
Script simple para verificar el estado del addon TypeAnimator.
"""

import os

def check_addon():
    """Verificar el estado del addon"""
    print("🔍 VERIFICACIÓN SIMPLE DEL ADDON")
    print("=" * 40)
    
    addon_path = os.path.dirname(__file__)
    folder_name = os.path.basename(addon_path)
    
    print(f"1. Carpeta: {folder_name}")
    print(f"2. Ruta: {addon_path}")
    
    # Verificar archivos críticos
    critical_files = [
        "__init__.py",
        "registration.py",
        "constants.py", 
        "curves.py",
        "operators.py",
        "ui.py",
        "properties.py"
    ]
    
    print("\n3. Archivos críticos:")
    all_exist = True
    for file in critical_files:
        exists = os.path.exists(os.path.join(addon_path, file))
        status = "✅" if exists else "❌"
        print(f"   {file}: {status}")
        if not exists:
            all_exist = False
    
    # Verificar bl_info
    try:
        with open(os.path.join(addon_path, "__init__.py"), "r") as f:
            content = f.read()
            has_bl_info = "bl_info" in content
            has_register = "register()" in content
            print(f"\n4. bl_info: {'✅' if has_bl_info else '❌'}")
            print(f"5. register(): {'✅' if has_register else '❌'}")
    except Exception as e:
        print(f"\n4. Error leyendo __init__.py: {e}")
        all_exist = False
    
    # Verificar constantes
    try:
        with open(os.path.join(addon_path, "constants.py"), "r") as f:
            content = f.read()
            has_constants = "CURVE_NODE_GROUP_NAME" in content
            print(f"6. Constantes: {'✅' if has_constants else '❌'}")
    except Exception as e:
        print(f"6. Error leyendo constants.py: {e}")
        all_exist = False
    
    print("\n" + "=" * 40)
    if all_exist:
        print("✅ ADDON LISTO PARA USAR")
        print("✅ Estructura básica correcta")
    else:
        print("❌ PROBLEMAS DETECTADOS")
        print("❌ Verificar archivos faltantes")
    
    return all_exist

if __name__ == "__main__":
    check_addon() 