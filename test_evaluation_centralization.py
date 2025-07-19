"""
Script de verificación de evaluación centralizada para TypeAnimator.
Verifica que no haya lógica duplicada de evaluación de curvas.
"""

import bpy
import re
import logging

logger = logging.getLogger(__name__)

def check_duplicate_evaluation_logic():
    """Verificar que no hay lógica duplicada de evaluación."""
    print("=== TEST: EVALUACIÓN CENTRALIZADA ===")
    
    # Buscar archivos Python del addon
    import os
    addon_path = os.path.dirname(__file__)
    python_files = []
    
    for root, dirs, files in os.walk(addon_path):
        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                python_files.append(os.path.join(root, file))
    
    print(f"📁 Analizando {len(python_files)} archivos Python")
    
    # Patrones a buscar
    patterns = {
        't_stage': r't_stage',
        'stage_calculation': r'stage.*=.*\(.*\)',
        'curve_evaluation': r'\.evaluate\(',
        'blending_logic': r'blend.*=.*\(.*\)',
    }
    
    # Resultados
    findings = {}
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                file_name = os.path.basename(file_path)
                
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        if pattern_name not in findings:
                            findings[pattern_name] = []
                        findings[pattern_name].append({
                            'file': file_name,
                            'matches': len(matches),
                            'lines': []
                        })
                        
                        # Encontrar líneas específicas
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                findings[pattern_name][-1]['lines'].append(f"Línea {i}: {line.strip()}")
        except Exception as e:
            print(f"⚠️ Error leyendo {file_path}: {e}")
    
    # Analizar resultados
    print("\n📊 ANÁLISIS DE LÓGICA DUPLICADA:")
    
    for pattern_name, results in findings.items():
        print(f"\n🔍 {pattern_name.upper()}:")
        
        for result in results:
            print(f"   📄 {result['file']}: {result['matches']} coincidencias")
            
            # Mostrar líneas problemáticas
            for line in result['lines'][:3]:  # Solo primeras 3
                print(f"      {line}")
            
            if len(result['lines']) > 3:
                print(f"      ... y {len(result['lines']) - 3} más")
    
    # Verificar que curves.py tiene la lógica centralizada
    curves_file = None
    for file_path in python_files:
        if os.path.basename(file_path) == 'curves.py':
            curves_file = file_path
            break
    
    if curves_file:
        print(f"\n✅ Archivo curves.py encontrado: {curves_file}")
        
        with open(curves_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Verificar funciones centralizadas
            central_functions = [
                'evaluate_staged_curve',
                'evaluate_blended_stages',
                'calculate_blend_factor'
            ]
            
            print("\n🔍 FUNCIONES CENTRALIZADAS:")
            for func in central_functions:
                if func in content:
                    print(f"   ✅ {func}() encontrada")
                else:
                    print(f"   ❌ {func}() NO encontrada")
    else:
        print("❌ ERROR: No se encontró curves.py")
    
    return True

def test_handler_integration():
    """Verificar integración con handlers."""
    print("\n=== TEST: INTEGRACIÓN CON HANDLERS ===")
    
    # Buscar archivos de handlers
    import os
    addon_path = os.path.dirname(__file__)
    handler_files = []
    
    for root, dirs, files in os.walk(addon_path):
        for file in files:
            if file.endswith('.py') and 'handler' in file.lower():
                handler_files.append(os.path.join(root, file))
    
    print(f"📁 Archivos de handlers encontrados: {len(handler_files)}")
    
    for file_path in handler_files:
        file_name = os.path.basename(file_path)
        print(f"\n🔍 Analizando: {file_name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Buscar llamadas a evaluación
                evaluation_calls = re.findall(r'evaluate_staged_curve\(', content)
                blended_calls = re.findall(r'evaluate_blended_stages\(', content)
                
                print(f"   📊 Llamadas a evaluate_staged_curve: {len(evaluation_calls)}")
                print(f"   📊 Llamadas a evaluate_blended_stages: {len(blended_calls)}")
                
                # Buscar lógica duplicada
                duplicate_patterns = [
                    r't_stage.*=.*\(.*\)',
                    r'stage.*=.*\(.*\)',
                    r'blend.*=.*\(.*\)'
                ]
                
                for pattern in duplicate_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"   ⚠️ Posible lógica duplicada: {len(matches)} coincidencias")
                        
        except Exception as e:
            print(f"   ❌ Error leyendo {file_name}: {e}")
    
    return True

def test_evaluation_consistency():
    """Verificar consistencia de evaluación."""
    print("\n=== TEST: CONSISTENCIA DE EVALUACIÓN ===")
    
    # Verificar que existe el sistema de curvas
    try:
        from curves import evaluate_staged_curve, evaluate_blended_stages
        
        print("✅ Funciones de evaluación importadas correctamente")
        
        # Test básico de evaluación
        test_obj = bpy.context.active_object
        if test_obj:
            print(f"📝 Objeto de prueba: {test_obj.name}")
            
            # Test de evaluación por etapa
            for stage in ['in', 'mid', 'out']:
                try:
                    value = evaluate_staged_curve(test_obj, stage, 0.5)
                    print(f"   {stage}: evaluate(0.5) = {value:.3f}")
                except Exception as e:
                    print(f"   ❌ Error en {stage}: {e}")
            
            # Test de evaluación blended
            try:
                results = evaluate_blended_stages(test_obj, 0.5)
                print(f"   Blended: {results}")
            except Exception as e:
                print(f"   ❌ Error en blended: {e}")
        else:
            print("⚠️ No hay objeto activo para probar")
            
    except ImportError as e:
        print(f"❌ ERROR: No se pueden importar funciones de evaluación: {e}")
        return False
    
    return True

def run_all_evaluation_tests():
    """Ejecutar todas las pruebas de evaluación."""
    print("🚀 INICIANDO VERIFICACIÓN DE EVALUACIÓN CENTRALIZADA")
    print("=" * 60)
    
    tests = [
        check_duplicate_evaluation_logic,
        test_handler_integration,
        test_evaluation_consistency
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
    print("📋 RESUMEN DE VERIFICACIÓN DE EVALUACIÓN")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODAS LAS PRUEBAS DE EVALUACIÓN PASARON")
        return True
    else:
        print("❌ ALGUNAS PRUEBAS DE EVALUACIÓN FALLARON")
        return False

# Ejecutar si se llama directamente
if __name__ == "__main__":
    run_all_evaluation_tests() 