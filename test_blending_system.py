"""
Script de verificación del sistema de blending para TypeAnimator.
Verifica que el blending entre etapas funcione correctamente sin saltos.
"""

import bpy
import time
import logging

logger = logging.getLogger(__name__)

def test_blending_continuity():
    """Test de continuidad en blending con BLEND_WIDTH grande."""
    print("=== TEST: CONTINUIDAD DE BLENDING ===")
    
    # Configurar BLEND_WIDTH grande para prueba
    from constants import BLEND_WIDTH
    print(f"📊 BLEND_WIDTH actual: {BLEND_WIDTH}")
    
    # Ajustar temporalmente a un valor grande para prueba
    original_blend_width = BLEND_WIDTH
    
    try:
        # Importar funciones de evaluación
        from curves import evaluate_blended_stages, evaluate_staged_curve
        
        # Encontrar objeto de prueba
        test_obj = bpy.context.active_object
        if not test_obj:
            print("⚠️ No hay objeto activo para probar")
            return False
        
        print(f"📝 Objeto de prueba: {test_obj.name}")
        
        # Obtener propiedades de timing
        props = bpy.context.scene.ta_letter_anim_props
        if not props:
            print("⚠️ No hay propiedades de animación")
            return False
        
        timing = props.timing
        start_frame = timing.start_frame
        duration = timing.duration
        
        print(f"📊 Timing: start={start_frame}, duration={duration}")
        
        # Test de continuidad en timeline
        print("\n🔍 Verificando continuidad en timeline...")
        
        # Puntos de prueba en zonas de blending
        test_frames = []
        
        # Generar frames de prueba
        step = max(1, duration // 20)  # 20 puntos de prueba
        for f in range(start_frame, start_frame + duration + 1, step):
            test_frames.append(f)
        
        # Añadir frames específicos en zonas de blending
        blend_zones = [
            start_frame + duration // 3,  # Transición IN->MID
            start_frame + 2 * duration // 3  # Transición MID->OUT
        ]
        
        for zone in blend_zones:
            for offset in range(-2, 3):
                test_frames.append(zone + offset)
        
        test_frames = sorted(list(set(test_frames)))
        
        print(f"📊 Frames de prueba: {len(test_frames)} frames")
        
        # Evaluar en cada frame
        previous_values = None
        jumps_detected = 0
        max_jump = 0.0
        
        for frame in test_frames:
            # Establecer frame
            bpy.context.scene.frame_set(frame)
            
            # Calcular tiempo normalizado
            t = (frame - start_frame) / duration
            t = max(0.0, min(1.0, t))
            
            # Evaluar blending
            try:
                results = evaluate_blended_stages(test_obj, t, props)
                
                # Calcular valor combinado (promedio ponderado)
                combined_value = sum(results.values()) / len(results)
                
                # Verificar saltos
                if previous_values is not None:
                    jump = abs(combined_value - previous_values['combined'])
                    if jump > 0.1:  # Umbral de salto
                        jumps_detected += 1
                        max_jump = max(max_jump, jump)
                        print(f"   ⚠️ Salto detectado en frame {frame}: {jump:.3f}")
                
                previous_values = {
                    'combined': combined_value,
                    'stages': results
                }
                
                # Mostrar algunos valores para verificación
                if frame % 10 == 0:
                    print(f"   Frame {frame:3d}: t={t:.2f}, combined={combined_value:.3f}, stages={results}")
                
            except Exception as e:
                print(f"   ❌ Error en frame {frame}: {e}")
        
        # Resultados
        print(f"\n📊 RESULTADOS DE CONTINUIDAD:")
        print(f"   Frames evaluados: {len(test_frames)}")
        print(f"   Saltos detectados: {jumps_detected}")
        print(f"   Salto máximo: {max_jump:.3f}")
        
        if jumps_detected == 0:
            print("✅ No se detectaron saltos - blending suave")
        else:
            print(f"⚠️ Se detectaron {jumps_detected} saltos")
        
        return jumps_detected == 0
        
    except ImportError as e:
        print(f"❌ ERROR: No se pueden importar funciones: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def test_blend_modes():
    """Test de diferentes modos de blending."""
    print("\n=== TEST: MODOS DE BLENDING ===")
    
    try:
        from curves import calculate_blend_factor, smooth_step
        from constants import BLEND_MODE
        
        print(f"📊 BLEND_MODE actual: {BLEND_MODE}")
        
        # Test de smooth_step
        print("\n🔍 Test de smooth_step:")
        test_points = [0.0, 0.25, 0.5, 0.75, 1.0]
        for x in test_points:
            result = smooth_step(x)
            print(f"   smooth_step({x:.2f}) = {result:.3f}")
        
        # Test de calculate_blend_factor
        print("\n🔍 Test de calculate_blend_factor:")
        stage_start = 0.0
        stage_end = 1.0
        blend_width = 0.1
        
        test_times = [0.0, 0.05, 0.1, 0.5, 0.9, 0.95, 1.0]
        for t in test_times:
            factor = calculate_blend_factor(t, stage_start, stage_end, blend_width)
            print(f"   blend_factor(t={t:.2f}) = {factor:.3f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ ERROR: No se pueden importar funciones: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def test_blending_visualization():
    """Test de visualización de blending."""
    print("\n=== TEST: VISUALIZACIÓN DE BLENDING ===")
    
    try:
        from curves import evaluate_blended_stages
        
        # Encontrar objeto de prueba
        test_obj = bpy.context.active_object
        if not test_obj:
            print("⚠️ No hay objeto activo para probar")
            return False
        
        # Crear gráfico de valores
        print("\n📊 Gráfico de valores de blending:")
        print("   t    | IN    | MID   | OUT   | Combined")
        print("   -----|-------|-------|-------|---------")
        
        for i in range(11):
            t = i / 10.0
            
            try:
                results = evaluate_blended_stages(test_obj, t)
                combined = sum(results.values()) / len(results)
                
                print(f"   {t:.1f}   | {results['in']:.3f} | {results['mid']:.3f} | {results['out']:.3f} | {combined:.3f}")
                
            except Exception as e:
                print(f"   {t:.1f}   | ERROR: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ ERROR: No se pueden importar funciones: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def test_blending_performance():
    """Test de performance del blending."""
    print("\n=== TEST: PERFORMANCE DE BLENDING ===")
    
    try:
        from curves import evaluate_blended_stages
        
        # Encontrar objeto de prueba
        test_obj = bpy.context.active_object
        if not test_obj:
            print("⚠️ No hay objeto activo para probar")
            return False
        
        # Test de performance
        iterations = 1000
        print(f"📊 Ejecutando {iterations} evaluaciones de blending...")
        
        start_time = time.perf_counter()
        
        for i in range(iterations):
            t = i / iterations
            try:
                results = evaluate_blended_stages(test_obj, t)
            except Exception:
                pass
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        print(f"📊 Resultados de performance:")
        print(f"   Tiempo total: {duration:.3f} segundos")
        print(f"   Evaluaciones por segundo: {iterations / duration:.0f}")
        print(f"   Tiempo por evaluación: {duration / iterations * 1000:.3f} ms")
        
        # Verificar que es razonablemente rápido
        if duration < 1.0:  # Menos de 1 segundo para 1000 evaluaciones
            print("✅ Performance aceptable")
            return True
        else:
            print("⚠️ Performance lenta")
            return False
        
    except ImportError as e:
        print(f"❌ ERROR: No se pueden importar funciones: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False

def run_all_blending_tests():
    """Ejecutar todas las pruebas de blending."""
    print("🚀 INICIANDO VERIFICACIÓN DE SISTEMA DE BLENDING")
    print("=" * 60)
    
    tests = [
        test_blending_continuity,
        test_blend_modes,
        test_blending_visualization,
        test_blending_performance
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
    print("📋 RESUMEN DE VERIFICACIÓN DE BLENDING")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODAS LAS PRUEBAS DE BLENDING PASARON")
        return True
    else:
        print("❌ ALGUNAS PRUEBAS DE BLENDING FALLARON")
        return False

# Ejecutar si se llama directamente
if __name__ == "__main__":
    run_all_blending_tests() 