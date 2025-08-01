"""
Script final para probar el registro del addon sin errores de contexto.
"""

import sys
import os

def test_registration():
    """Probar el registro del addon."""
    print("🔍 Probando registro del addon...")
    
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
    print("🚀 PRUEBA FINAL DE REGISTRO")
    print("=" * 50)
    
    # Cambiar al directorio del addon
    addon_dir = os.path.dirname(__file__)
    os.chdir(addon_dir)
    
    # Probar registro
    success = test_registration()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ REGISTRO EXITOSO")
        print("✅ El addon debería funcionar correctamente en Blender")
    else:
        print("❌ HAY PROBLEMAS DE REGISTRO")
    
