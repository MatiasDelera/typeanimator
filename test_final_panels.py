"""
Script para probar el registro final del addon con paneles.
"""

import sys
import os

def test_final_registration():
    """Probar el registro final del addon."""
    print("🔍 Probando registro final con paneles...")
    
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
            
            # Verificar que los paneles se registraron
            try:
                # Verificar panel principal
                if hasattr(bpy.types, 'VIEW3D_PT_ta_main_improved'):
                    print("✅ Panel principal registrado")
                else:
                    print("❌ Panel principal no registrado")
                
                # Verificar panel de fuentes
                if hasattr(bpy.types, 'VIEW3D_PT_font_manager'):
                    print("✅ Panel de fuentes registrado")
                else:
                    print("❌ Panel de fuentes no registrado")
                    
            except Exception as e:
                print(f"⚠️ Error verificando paneles: {e}")
            
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
    print("🚀 PRUEBA FINAL CON PANELES")
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
    
