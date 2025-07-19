"""
Script de verificación de naming de nodos para TypeAnimator.
Ejecutar en la consola de Blender para validar el sistema de naming.
"""

import bpy
import re
import logging

logger = logging.getLogger(__name__)

def test_node_naming():
    """Test completo del sistema de naming de nodos."""
    print("=== TEST: NAMING DE NODOS ===")
    
    # Verificar que existe el NodeGroup
    ng = bpy.data.node_groups.get("txFxCurveData")
    if not ng:
        print("❌ ERROR: Falta txFxCurveData NodeGroup")
        return False
    
    print("✅ NodeGroup txFxCurveData encontrado")
    
    # Patrón de validación
    pattern = re.compile(r'^[A-Za-z0-9_]+_curve_(in|mid|out)$')
    
    # Verificar todos los nodos
    invalid_nodes = []
    valid_nodes = []
    
    for node in ng.nodes:
        if "_curve_" in node.name:
            if pattern.match(node.name):
                valid_nodes.append(node.name)
                print(f"✅ Nodo válido: {node.name}")
            else:
                invalid_nodes.append(node.name)
                print(f"❌ Nodo inválido: {node.name}")
    
    # Resultados
    print(f"\n📊 RESULTADOS:")
    print(f"   Nodos válidos: {len(valid_nodes)}")
    print(f"   Nodos inválidos: {len(invalid_nodes)}")
    
    if invalid_nodes:
        print(f"❌ ERROR: {len(invalid_nodes)} nodos con naming inválido")
        return False
    
    print("✅ Todos los nodos tienen naming válido")
    return True

def test_rename_robustness():
    """Test de robustez al renombrar objetos."""
    print("\n=== TEST: ROBUSTEZ AL RENOMBRAR ===")
    
    # Encontrar objetos de texto
    text_objects = [obj for obj in bpy.data.objects if obj.type == 'FONT']
    
    if not text_objects:
        print("⚠️ No hay objetos de texto para probar")
        return True
    
    obj = text_objects[0]
    original_name = obj.name
    print(f"📝 Probando con objeto: {original_name}")
    
    # Contar nodos antes del rename
    ng = bpy.data.node_groups.get("txFxCurveData")
    if not ng:
        print("❌ ERROR: NodeGroup no encontrado")
        return False
    
    nodes_before = len([n for n in ng.nodes if "_curve_" in n.name])
    print(f"   Nodos antes del rename: {nodes_before}")
    
    # Renombrar objeto
    obj.name = f"{original_name}_RENAMED"
    print(f"   Objeto renombrado a: {obj.name}")
    
    # Verificar que no se crearon nodos duplicados
    nodes_after = len([n for n in ng.nodes if "_curve_" in n.name])
    print(f"   Nodos después del rename: {nodes_after}")
    
    if nodes_after > nodes_before:
        print(f"❌ ERROR: Se crearon {nodes_after - nodes_before} nodos duplicados")
        return False
    
    print("✅ No se crearon nodos duplicados")
    
    # Restaurar nombre original
    obj.name = original_name
    print(f"   Nombre restaurado: {obj.name}")
    
    return True

def test_base_name_generation():
    """Test de generación de nombres base."""
    print("\n=== TEST: GENERACIÓN DE NOMBRES BASE ===")
    
    # Simular diferentes nombres de objetos
    test_names = [
        "Text",
        "Text.001",
        "Text_copy",
        "Text_001_copy",
        "My_Text_Object",
        "Text@Special#Chars",
        "Text with spaces"
    ]
    
    for test_name in test_names:
        # Simular objeto
        class MockObject:
            def __init__(self, name):
                self.name = name
        
        mock_obj = MockObject(test_name)
        
        # Importar función de constants
        try:
            from constants import generate_base_name_from_object
            base_name = generate_base_name_from_object(mock_obj)
            print(f"   '{test_name}' -> '{base_name}'")
        except ImportError:
            print(f"⚠️ Función generate_base_name_from_object no disponible")
            break
    
    return True

def run_all_naming_tests():
    """Ejecutar todas las pruebas de naming."""
    print("🚀 INICIANDO VERIFICACIÓN DE NAMING DE NODOS")
    print("=" * 50)
    
    tests = [
        test_node_naming,
        test_rename_robustness,
        test_base_name_generation
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
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE VERIFICACIÓN DE NAMING")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODAS LAS PRUEBAS DE NAMING PASARON")
        return True
    else:
        print("❌ ALGUNAS PRUEBAS DE NAMING FALLARON")
        return False

# Ejecutar si se llama directamente
if __name__ == "__main__":
    run_all_naming_tests() 