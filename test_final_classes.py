"""
Script para probar el registro final del addon con clases.
"""

import sys
import os

def test_final_registration():
    """Probar el registro final del addon."""
    print("🔍 Probando registro final con clases...")
    
    try:
        # Simular el entorno de Blender
        import bpy
        
        # Importar el módulo principal
        from registration import register, unregister
        
        print("✅ Módulos importados correctamente")
        
        # Intentar registrar
        try:
            register()
            print("✅ Registro exitoso")
            
            # Verificar que las clases se registraron
            try:
                # Verificar clases de presets
                if hasattr(bpy.types, 'PresetItem'):
                    print("✅ PresetItem registrado")
                else:
                    print("❌ PresetItem no registrado")
                
                # Verificar clases de fonts
                if hasattr(bpy.types, 'FavoriteFontItem'):
                    print("✅ FavoriteFontItem registrado")
                else:
                    print("❌ FavoriteFontItem no registrado")
                
                if hasattr(bpy.types, 'FontManagerProperties'):
                    print("✅ FontManagerProperties registrado")
                else:
                    print("❌ FontManagerProperties no registrado")
                    
            except Exception as e:
                print(f"⚠️ Error verificando clases: {e}")
            
            # Intentar desregistrar
            try:
                unregister()
                print("✅ Desregistro exitoso")
                return True
            except Exception as e:
                print(f"❌ Error en desregistro: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error en registro: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error importando módulos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA FINAL CON CLASES")
    print("=" * 50)
    
    # Cambiar al directorio del addon
    addon_dir = os.path.dirname(__file__)
    os.chdir(addon_dir)
    
    # Probar registro
    success = test_final_registration()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ REGISTRO EXITOSO")
        print("✅ El addon debería funcionar correctamente en Blender")
    else:
        print("❌ HAY PROBLEMAS DE REGISTRO")
    
