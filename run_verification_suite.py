"""
Script principal de verificación completa para TypeAnimator.
Ejecuta todas las pruebas de verificación por bloques.
"""

import bpy
import time
import logging

logger = logging.getLogger(__name__)

def run_naming_verification():
    """Ejecutar verificación de naming de nodos."""
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN 1: NAMING DE NODOS")
    print("=" * 80)
    
    try:
        # Importar y ejecutar test de naming
        exec(open("test_naming_validation.py").read())
        
        # Ejecutar función principal
        from test_naming_validation import run_all_naming_tests
        return run_all_naming_tests()
        
    except Exception as e:
        print(f"❌ ERROR en verificación de naming: {e}")
        return False

def run_evaluation_verification():
    """Ejecutar verificación de evaluación centralizada."""
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN 2: EVALUACIÓN CENTRALIZADA")
    print("=" * 80)
    
    try:
        # Importar y ejecutar test de evaluación
        exec(open("test_evaluation_centralization.py").read())
        
        # Ejecutar función principal
        from test_evaluation_centralization import run_all_evaluation_tests
        return run_all_evaluation_tests()
        
    except Exception as e:
        print(f"❌ ERROR en verificación de evaluación: {e}")
        return False

def run_blending_verification():
    """Ejecutar verificación de sistema de blending."""
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN 3: SISTEMA DE BLENDING")
    print("=" * 80)
    
    try:
        # Importar y ejecutar test de blending
        exec(open("test_blending_system.py").read())
        
        # Ejecutar función principal
        from test_blending_system import run_all_blending_tests
        return run_all_blending_tests()
        
    except Exception as e:
        print(f"❌ ERROR en verificación de blending: {e}")
        return False

def run_audit_verification():
    """Ejecutar verificación de sistema de auditoría."""
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN 4: SISTEMA DE AUDITORÍA")
    print("=" * 80)
    
    try:
        # Importar y ejecutar test de auditoría
        exec(open("test_audit_system.py").read())
        
        # Ejecutar función principal
        from test_audit_system import run_all_audit_tests
        return run_all_audit_tests()
        
    except Exception as e:
        print(f"❌ ERROR en verificación de auditoría: {e}")
        return False

def run_quick_verification():
    """Ejecutar verificaciones rápidas adicionales."""
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN 5: PRUEBAS RÁPIDAS ADICIONALES")
    print("=" * 80)
    
    results = []
    
    # Test 1: Verificar que existen los operadores
    print("\n📋 Test 1: Verificación de operadores")
    try:
        required_operators = [
            'typeanimator.copy_curve_between_stages',
            'typeanimator.reset_all_curves',
            'typeanimator.debug_evaluate_curves',
            'typeanimator.audit_repair_curves',
            'typeanimator.toggle_live_preview'
        ]
        
        missing_operators = []
        for op_name in required_operators:
            if not hasattr(bpy.ops, op_name.replace('.', '_')):
                missing_operators.append(op_name)
        
        if missing_operators:
            print(f"❌ Operadores faltantes: {missing_operators}")
            results.append(False)
        else:
            print("✅ Todos los operadores están disponibles")
            results.append(True)
            
    except Exception as e:
        print(f"❌ ERROR verificando operadores: {e}")
        results.append(False)
    
    # Test 2: Verificar configuración de overshoot
    print("\n📋 Test 2: Configuración de overshoot")
    try:
        from constants import OVERSHOOT_ENABLED, OVERSHOOT_LIMIT
        
        print(f"   OVERSHOOT_ENABLED: {OVERSHOOT_ENABLED}")
        print(f"   OVERSHOOT_LIMIT: {OVERSHOOT_LIMIT}")
        
        if OVERSHOOT_LIMIT > 1.0:
            print("✅ Configuración de overshoot correcta")
            results.append(True)
        else:
            print("⚠️ OVERSHOOT_LIMIT muy bajo")
            results.append(False)
            
    except ImportError as e:
        print(f"❌ ERROR: No se puede importar configuración: {e}")
        results.append(False)
    
    # Test 3: Verificar live preview
    print("\n📋 Test 3: Configuración de live preview")
    try:
        from constants import LIVE_PREVIEW_ENABLED, LIVE_PREVIEW_UPDATE_RATE
        
        print(f"   LIVE_PREVIEW_ENABLED: {LIVE_PREVIEW_ENABLED}")
        print(f"   LIVE_PREVIEW_UPDATE_RATE: {LIVE_PREVIEW_UPDATE_RATE}")
        
        if LIVE_PREVIEW_UPDATE_RATE > 0:
            print("✅ Configuración de live preview correcta")
            results.append(True)
        else:
            print("⚠️ LIVE_PREVIEW_UPDATE_RATE inválido")
            results.append(False)
            
    except ImportError as e:
        print(f"❌ ERROR: No se puede importar configuración: {e}")
        results.append(False)
    
    # Test 4: Verificar NodeGroup
    print("\n📋 Test 4: Verificación de NodeGroup")
    try:
        ng = bpy.data.node_groups.get("txFxCurveData")
        if ng:
            curve_nodes = [n for n in ng.nodes if "_curve_" in n.name]
            print(f"   NodeGroup encontrado: {ng.name}")
            print(f"   Nodos de curva: {len(curve_nodes)}")
            
            if len(curve_nodes) > 0:
                print("✅ NodeGroup configurado correctamente")
                results.append(True)
            else:
                print("⚠️ No hay nodos de curva en el NodeGroup")
                results.append(False)
        else:
            print("❌ NodeGroup txFxCurveData no encontrado")
            results.append(False)
            
    except Exception as e:
        print(f"❌ ERROR verificando NodeGroup: {e}")
        results.append(False)
    
    return all(results)

def run_performance_test():
    """Ejecutar test de performance básico."""
    print("\n" + "=" * 80)
    print("🔍 VERIFICACIÓN 6: TEST DE PERFORMANCE")
    print("=" * 80)
    
    try:
        # Crear texto de prueba con 200 caracteres
        test_text = "Test " * 40  # 200 caracteres aproximadamente
        
        print(f"📝 Creando texto de prueba: {len(test_text)} caracteres")
        
        # Crear objeto de texto
        bpy.ops.object.text_add(location=(0, 0, 0))
        text_obj = bpy.context.active_object
        text_obj.data.body = test_text
        
        print(f"✅ Objeto de texto creado: {text_obj.name}")
        
        # Separar letras
        print("🔧 Separando letras...")
        bpy.ops.typeanimator.separate_letters()
        
        # Contar letras separadas
        letters = [obj for obj in bpy.data.objects if hasattr(obj, 'ta_letter_index')]
        print(f"📊 Letras separadas: {len(letters)}")
        
        # Test de performance en timeline
        print("🎬 Probando performance en timeline...")
        
        start_frame = 1
        end_frame = 60
        start_time = time.perf_counter()
        
        for frame in range(start_frame, end_frame + 1):
            bpy.context.scene.frame_set(frame)
            # Forzar actualización
            bpy.context.view_layer.update()
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        fps = (end_frame - start_frame + 1) / duration
        
        print(f"📊 Resultados de performance:")
        print(f"   Tiempo total: {duration:.3f} segundos")
        print(f"   FPS promedio: {fps:.1f}")
        
        if fps >= 24:
            print("✅ Performance aceptable (≥24 FPS)")
            return True
        else:
            print("⚠️ Performance lenta (<24 FPS)")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en test de performance: {e}")
        return False

def run_complete_verification():
    """Ejecutar verificación completa del sistema."""
    print("🚀 INICIANDO VERIFICACIÓN COMPLETA DE TYPEANIMATOR")
    print("=" * 80)
    print("📋 Este script ejecutará todas las verificaciones por bloques")
    print("📋 Asegúrate de tener un objeto de texto activo para las pruebas")
    print("=" * 80)
    
    start_time = time.perf_counter()
    
    # Lista de verificaciones
    verifications = [
        ("Naming de Nodos", run_naming_verification),
        ("Evaluación Centralizada", run_evaluation_verification),
        ("Sistema de Blending", run_blending_verification),
        ("Sistema de Auditoría", run_audit_verification),
        ("Pruebas Rápidas", run_quick_verification),
        ("Test de Performance", run_performance_test)
    ]
    
    results = {}
    
    for name, verification_func in verifications:
        print(f"\n🔄 Ejecutando: {name}")
        try:
            result = verification_func()
            results[name] = result
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"   {status}: {name}")
        except Exception as e:
            print(f"   ❌ ERROR: {name} - {e}")
            results[name] = False
    
    # Resumen final
    end_time = time.perf_counter()
    total_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print("📋 RESUMEN FINAL DE VERIFICACIÓN")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"⏱️ Tiempo total: {total_time:.2f} segundos")
    print(f"📊 Verificaciones pasadas: {passed}/{total}")
    print(f"📈 Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    print("\n📋 DETALLE POR VERIFICACIÓN:")
    for name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {status}: {name}")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS VERIFICACIONES PASARON!")
        print("🎉 El sistema TypeAnimator está funcionando correctamente")
        return True
    else:
        print(f"\n⚠️ {total - passed} VERIFICACIONES FALLARON")
        print("⚠️ Revisa los errores específicos arriba")
        return False

# Ejecutar si se llama directamente
if __name__ == "__main__":
    run_complete_verification() 