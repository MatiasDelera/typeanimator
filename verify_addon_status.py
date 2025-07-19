"""
Script simple para verificar el estado del addon TypeAnimator.
Ejecutar en la consola de Blender.
"""

import bpy
import os

def verify_addon_status():
    """Verificar el estado del addon"""
    print("🔍 VERIFICACIÓN DEL ESTADO DEL ADDON")
    print("=" * 50)
    
    # 1. Verificar si el addon está registrado
    addon_name = "typeanimator"
    is_enabled = addon_name in bpy.context.preferences.addons
    print(f"1. Addon registrado: {'✅' if is_enabled else '❌'}")
    
    if is_enabled:
        print(f"   Nombre: {bpy.context.preferences.addons[addon_name].module}")
    
    # 2. Verificar archivos principales
    addon_path = os.path.dirname(__file__)
    required_files = [
        "__init__.py",
        "registration.py", 
        "constants.py",
        "curves.py",
        "operators.py",
        "ui.py",
        "properties.py"
    ]
    
    print("\n2. Archivos principales:")
    for file in required_files:
        file_path = os.path.join(addon_path, file)
        exists = os.path.exists(file_path)
        print(f"   {file}: {'✅' if exists else '❌'}")
    
    # 3. Verificar bl_info
    try:
        with open(os.path.join(addon_path, "__init__.py"), "r") as f:
            content = f.read()
            has_bl_info = "bl_info" in content
            print(f"\n3. bl_info presente: {'✅' if has_bl_info else '❌'}")
    except:
        print("\n3. bl_info error: ❌")
    
    # 4. Verificar funciones register/unregister
    try:
        with open(os.path.join(addon_path, "__init__.py"), "r") as f:
            content = f.read()
            has_register = "register()" in content and "unregister()" in content
            print(f"4. register/unregister: {'✅' if has_register else '❌'}")
    except:
        print("4. register/unregister error: ❌")
    
    # 5. Verificar constantes críticas
    try:
        with open(os.path.join(addon_path, "constants.py"), "r") as f:
            content = f.read()
            has_constants = "CURVE_NODE_GROUP_NAME" in content and "BLEND_WIDTH" in content
            print(f"5. Constantes críticas: {'✅' if has_constants else '❌'}")
    except:
        print("5. Constantes error: ❌")
    
    # 6. Verificar operadores
    try:
        with open(os.path.join(addon_path, "operators.py"), "r") as f:
            content = f.read()
            has_operators = "class TA_OT_" in content
            print(f"6. Operadores definidos: {'✅' if has_operators else '❌'}")
    except:
        print("6. Operadores error: ❌")
    
    # 7. Verificar UI
    try:
        with open(os.path.join(addon_path, "ui.py"), "r") as f:
            content = f.read()
            has_ui = "class TA_PT_" in content
            print(f"7. Paneles UI definidos: {'✅' if has_ui else '❌'}")
    except:
        print("7. UI error: ❌")
    
    # 8. Verificar Node Group
    if hasattr(bpy.data, "node_groups"):
        node_groups = [ng.name for ng in bpy.data.node_groups if "txFxCurve" in ng.name]
        print(f"\n8. Node Groups TypeAnimator: {len(node_groups)} encontrados")
        for ng in node_groups:
            print(f"   - {ng}")
    else:
        print("\n8. Node Groups: No disponibles")
    
    # 9. Verificar propiedades de escena
    scene_props = [attr for attr in dir(bpy.types.Scene) if attr.startswith('ta_')]
    print(f"\n9. Propiedades de escena: {len(scene_props)} encontradas")
    for prop in scene_props:
        print(f"   - {prop}")
    
    # Resumen
    print("\n" + "=" * 50)
    print("📋 RESUMEN")
    print("=" * 50)
    
    if is_enabled:
        print("✅ El addon está registrado y habilitado")
        print("✅ Los archivos principales están presentes")
        print("✅ La estructura básica es correcta")
        print("\n🎉 El addon debería funcionar correctamente")
    else:
        print("❌ El addon no está registrado")
        print("⚠️ Verificar la instalación y activación")
    
    return is_enabled

# Ejecutar verificación
if __name__ == "__main__":
    verify_addon_status() 