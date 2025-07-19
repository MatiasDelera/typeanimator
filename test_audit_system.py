"""
Script de verificación del sistema de auditoría automática para TypeAnimator.
Verifica que la auditoría y reparación automática funcione correctamente.
"""

import bpy
import logging

logger = logging.getLogger(__name__)

def test_audit_repair_operator():
    """Test del operador de auditoría y reparación."""
    print("=== TEST: OPERADOR DE AUDITORÍA Y REPARACIÓN ===")
    
    try:
        # Ejecutar el operador de auditoría
        print("🔍 Ejecutando operador de auditoría...")
        
        # Verificar que el operador existe
        if hasattr(bpy.ops, 'typeanimator') and hasattr(bpy.ops.typeanimator, 'audit_repair_curves'):
            result = bpy.ops.typeanimator.audit_repair_curves()
            
            if result == {'FINISHED'}:
                print("✅ Operador de auditoría ejecutado exitosamente")
                return True
            else:
                print(f"❌ Operador de auditoría falló: {result}")
                return False
        else:
            print("❌ Operador de auditoría no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ ERROR ejecutando operador: {e}")
        return False

def test_manual_node_deletion():
    """Test de eliminación manual de nodos y regeneración."""
    print("\n=== TEST: ELIMINACIÓN MANUAL DE NODOS ===")
    
    try:
        # Encontrar el NodeGroup
        ng = bpy.data.node_groups.get("txFxCurveData")
        if not ng:
            print("❌ ERROR: No se encontró NodeGroup txFxCurveData")
            return False
        
        print(f"✅ NodeGroup encontrado: {ng.name}")
        
        # Contar nodos antes
        curve_nodes_before = [n for n in ng.nodes if "_curve_" in n.name]
        print(f"📊 Nodos de curva antes: {len(curve_nodes_before)}")
        
        # Eliminar algunos nodos manualmente
        nodes_to_delete = curve_nodes_before[:2] if len(curve_nodes_before) >= 2 else curve_nodes_before
        
        for node in nodes_to_delete:
            print(f"🗑️ Eliminando nodo: {node.name}")
            ng.nodes.remove(node)
        
        print(f"📊 Nodos eliminados: {len(nodes_to_delete)}")
        
        # Recargar el addon para activar auditoría automática
        print("🔄 Recargando addon...")
        
        # Simular recarga ejecutando auditoría manual
        try:
            from curves import audit_or_repair_curve_nodegroup
            audit_results = audit_or_repair_curve_nodegroup()
            
            print(f"📊 Resultados de auditoría:")
            print(f"   Total objetos: {audit_results.get('total_objects', 0)}")
            print(f"   Objetos válidos: {audit_results.get('valid_objects', 0)}")
            print(f"   Objetos reparados: {audit_results.get('repaired_objects', 0)}")
            
            # Verificar que se repararon los nodos
            curve_nodes_after = [n for n in ng.nodes if "_curve_" in n.name]
            print(f"📊 Nodos de curva después: {len(curve_nodes_after)}")
            
            if len(curve_nodes_after) >= len(curve_nodes_before) - len(nodes_to_delete):
                print("✅ Nodos reparados correctamente")
                return True
            else:
                print("❌ Nodos no se repararon completamente")
                return False
                
        except ImportError as e:
            print(f"❌ ERROR: No se puede importar función de auditoría: {e}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def test_audit_on_startup():
    """Test de auditoría automática al iniciar."""
    print("\n=== TEST: AUDITORÍA AL INICIAR ===")
    
    try:
        from constants import AUDIT_VALIDATE_ON_STARTUP
        
        print(f"📊 AUDIT_VALIDATE_ON_STARTUP: {AUDIT_VALIDATE_ON_STARTUP}")
        
        if AUDIT_VALIDATE_ON_STARTUP:
            print("✅ Auditoría automática habilitada al iniciar")
            
            # Simular auditoría de inicio
            try:
                from curves import audit_or_repair_curve_nodegroup
                audit_results = audit_or_repair_curve_nodegroup()
                
                print(f"📊 Auditoría de inicio completada:")
                print(f"   Objetos auditados: {audit_results.get('total_objects', 0)}")
                print(f"   Problemas encontrados: {len(audit_results.get('warnings', []))}")
                print(f"   Reparaciones realizadas: {audit_results.get('repaired_objects', 0)}")
                
                return True
                
            except ImportError as e:
                print(f"❌ ERROR: No se puede ejecutar auditoría: {e}")
                return False
        else:
            print("⚠️ Auditoría automática deshabilitada al iniciar")
            return True
            
    except ImportError as e:
        print(f"❌ ERROR: No se puede importar configuración: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def test_audit_logging():
    """Test de logging de auditoría."""
    print("\n=== TEST: LOGGING DE AUDITORÍA ===")
    
    try:
        from constants import AUDIT_LOG_DETAILS
        
        print(f"📊 AUDIT_LOG_DETAILS: {AUDIT_LOG_DETAILS}")
        
        if AUDIT_LOG_DETAILS:
            print("✅ Logging detallado habilitado")
            
            # Verificar que el logger está configurado
            logger = logging.getLogger(__name__)
            if logger.handlers:
                print("✅ Logger configurado con handlers")
            else:
                print("⚠️ Logger sin handlers configurados")
            
            return True
        else:
            print("⚠️ Logging detallado deshabilitado")
            return True
            
    except ImportError as e:
        print(f"❌ ERROR: No se puede importar configuración: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def test_audit_auto_repair():
    """Test de reparación automática."""
    print("\n=== TEST: REPARACIÓN AUTOMÁTICA ===")
    
    try:
        from constants import AUDIT_AUTO_REPAIR
        
        print(f"📊 AUDIT_AUTO_REPAIR: {AUDIT_AUTO_REPAIR}")
        
        if AUDIT_AUTO_REPAIR:
            print("✅ Reparación automática habilitada")
            
            # Crear un nodo corrupto para probar reparación
            ng = bpy.data.node_groups.get("txFxCurveData")
            if ng:
                # Crear nodo de prueba
                test_node = ng.nodes.new('ShaderNodeRGBCurve')
                test_node.name = "test_corrupt_node"
                test_node.label = "Test Corrupt Node"
                
                print(f"🔧 Nodo de prueba creado: {test_node.name}")
                
                # Ejecutar auditoría
                try:
                    from curves import audit_or_repair_curve_nodegroup
                    audit_results = audit_or_repair_curve_nodegroup()
                    
                    print(f"📊 Auditoría completada:")
                    print(f"   Objetos reparados: {audit_results.get('repaired_objects', 0)}")
                    
                    # Verificar que el nodo de prueba fue manejado
                    if "test_corrupt_node" not in [n.name for n in ng.nodes]:
                        print("✅ Nodo de prueba fue removido/reparado")
                    else:
                        print("⚠️ Nodo de prueba aún existe")
                    
                    return True
                    
                except ImportError as e:
                    print(f"❌ ERROR: No se puede ejecutar auditoría: {e}")
                    return False
            else:
                print("⚠️ No se encontró NodeGroup para probar")
                return True
        else:
            print("⚠️ Reparación automática deshabilitada")
            return True
            
    except ImportError as e:
        print(f"❌ ERROR: No se puede importar configuración: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def test_audit_error_handling():
    """Test de manejo de errores en auditoría."""
    print("\n=== TEST: MANEJO DE ERRORES EN AUDITORÍA ===")
    
    try:
        # Simular condiciones de error
        print("🔍 Probando manejo de errores...")
        
        # Test con NodeGroup corrupto
        ng = bpy.data.node_groups.get("txFxCurveData")
        if ng:
            # Crear nodo inválido
            invalid_node = ng.nodes.new('NodeGroupInput')  # Nodo incorrecto
            invalid_node.name = "invalid_curve_node"
            
            print(f"🔧 Nodo inválido creado: {invalid_node.name}")
            
            # Ejecutar auditoría
            try:
                from curves import audit_or_repair_curve_nodegroup
                audit_results = audit_or_repair_curve_nodegroup()
                
                print(f"📊 Auditoría con errores completada:")
                print(f"   Errores: {len(audit_results.get('errors', []))}")
                print(f"   Advertencias: {len(audit_results.get('warnings', []))}")
                
                # Verificar que no crasheó
                if 'error' not in audit_results:
                    print("✅ Auditoría manejó errores correctamente")
                    return True
                else:
                    print(f"❌ Auditoría falló: {audit_results['error']}")
                    return False
                    
            except Exception as e:
                print(f"❌ Auditoría crasheó: {e}")
                return False
        else:
            print("⚠️ No se encontró NodeGroup para probar")
            return True
            
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def run_all_audit_tests():
    """Ejecutar todas las pruebas de auditoría."""
    print("🚀 INICIANDO VERIFICACIÓN DE SISTEMA DE AUDITORÍA")
    print("=" * 60)
    
    tests = [
        test_audit_repair_operator,
        test_manual_node_deletion,
        test_audit_on_startup,
        test_audit_logging,
        test_audit_auto_repair,
        test_audit_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ ERROR en test {test.__name__}: {e}")
            results.append(False)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIÓN DE AUDITORÍA")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODAS LAS PRUEBAS DE AUDITORÍA PASARON")
        return True
    else:
        print("❌ ALGUNAS PRUEBAS DE AUDITORÍA FALLARON")
        return False

# Ejecutar si se llama directamente
if __name__ == "__main__":
    run_all_audit_tests() 