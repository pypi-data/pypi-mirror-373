"""
Performance and Functionality Comparison

This script compares the original monolithic SOM implementation with the 
new modular version to ensure equivalent performance and results.
"""

import numpy as np
import time
import sys
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Import original implementation
sys.path.insert(0, os.path.dirname(__file__))
from self_organizing_map import SelfOrganizingMap as OriginalSOM

# Import modular implementation  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'self_organizing_maps'))
from self_organizing_maps import SelfOrganizingMap as ModularSOM

def create_test_data():
    """Create consistent test data"""
    np.random.seed(42)
    n_samples = 1000
    
    # 2D Gaussian clusters
    cluster1 = np.random.multivariate_normal([2, 2], [[0.5, 0.2], [0.2, 0.5]], n_samples//3)
    cluster2 = np.random.multivariate_normal([-1, 3], [[0.3, -0.1], [-0.1, 0.4]], n_samples//3) 
    cluster3 = np.random.multivariate_normal([1, -2], [[0.4, 0.1], [0.1, 0.3]], n_samples//3)
    
    return np.vstack([cluster1, cluster2, cluster3])

def compare_basic_training():
    """Compare basic training results between implementations"""
    print("🔄 Comparing Basic Training Results")
    print("=" * 50)
    
    data = create_test_data()
    
    # Configuration for both implementations
    config = {
        'map_size': (15, 15),
        'input_dim': 2,
        'initial_learning_rate': 0.5,
        'topology': 'rectangular',
        'neighborhood_function': 'gaussian',
        'parameter_schedule': 'exponential',
        'random_seed': 42
    }
    
    # Original implementation
    print("📊 Original Implementation:")
    np.random.seed(42)
    original_som = OriginalSOM(**config)
    start_time = time.time()
    original_results = original_som.train(data, n_iterations=1000, verbose=False)
    original_time = time.time() - start_time
    
    print(f"   Training time: {original_time:.2f} seconds")
    print(f"   Final QE: {original_results['final_quantization_error']:.4f}")
    print(f"   Final TE: {original_results['final_topographic_error']:.4f}")
    
    # Modular implementation
    print("\n🧩 Modular Implementation:")
    np.random.seed(42)
    modular_som = ModularSOM(**config)
    start_time = time.time()
    modular_results = modular_som.train(data, n_iterations=1000, verbose=False)
    modular_time = time.time() - start_time
    
    print(f"   Training time: {modular_time:.2f} seconds")
    print(f"   Final QE: {modular_results['final_quantization_error']:.4f}")
    print(f"   Final TE: {modular_results['final_topographic_error']:.4f}")
    
    # Performance comparison
    time_ratio = modular_time / original_time
    qe_diff = abs(original_results['final_quantization_error'] - modular_results['final_quantization_error'])
    te_diff = abs(original_results['final_topographic_error'] - modular_results['final_topographic_error'])
    
    print(f"\n📈 Performance Comparison:")
    print(f"   Time ratio (modular/original): {time_ratio:.2f}x")
    print(f"   QE difference: {qe_diff:.6f}")
    print(f"   TE difference: {te_diff:.6f}")
    
    # Success criteria
    success = (
        time_ratio < 2.0 and  # Modular shouldn't be more than 2x slower
        qe_diff < 0.01 and    # Quality should be very similar
        te_diff < 0.01
    )
    
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"   Overall: {status}")
    
    return success

def compare_weight_initialization():
    """Compare weight initialization between implementations"""
    print("\n🎲 Comparing Weight Initialization")
    print("=" * 50)
    
    config = {
        'map_size': (10, 10),
        'input_dim': 3,
        'random_seed': 123
    }
    
    # Compare random initialization
    np.random.seed(123)
    original_som = OriginalSOM(**config)
    original_weights = original_som.get_neuron_weights()
    
    np.random.seed(123)
    modular_som = ModularSOM(**config)
    modular_weights = modular_som.get_neuron_weights()
    
    # Check if weights are similar (allowing for small floating point differences)
    weight_diff = np.mean(np.abs(original_weights - modular_weights))
    print(f"   Random init weight difference: {weight_diff:.8f}")
    
    # Test linear initialization
    config['initialization'] = 'linear'
    
    np.random.seed(123)
    original_som = OriginalSOM(**config)
    original_linear = original_som.get_neuron_weights()
    
    np.random.seed(123)
    modular_som = ModularSOM(**config)
    modular_linear = modular_som.get_neuron_weights()
    
    linear_diff = np.mean(np.abs(original_linear - modular_linear))
    print(f"   Linear init weight difference: {linear_diff:.8f}")
    
    success = weight_diff < 1e-6 and linear_diff < 1e-6
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"   Status: {status}")
    
    return success

def compare_bmu_finding():
    """Compare BMU finding between implementations"""
    print("\n🎯 Comparing BMU Finding")
    print("=" * 50)
    
    data = create_test_data()[:100]  # Use smaller dataset for detailed comparison
    
    config = {
        'map_size': (8, 8),
        'input_dim': 2,
        'random_seed': 42
    }
    
    # Initialize both SOMs with same configuration
    np.random.seed(42)
    original_som = OriginalSOM(**config)
    
    np.random.seed(42) 
    modular_som = ModularSOM(**config)
    
    # Compare BMU positions for test inputs
    different_bmus = 0
    for i, input_vector in enumerate(data):
        original_bmu = original_som.map_input(input_vector)
        modular_bmu = modular_som.map_input(input_vector)
        
        if original_bmu != modular_bmu:
            different_bmus += 1
    
    print(f"   Different BMUs: {different_bmus}/{len(data)}")
    
    success = different_bmus == 0
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"   Status: {status}")
    
    return success

def compare_sklearn_interface():
    """Compare sklearn interface compatibility"""
    print("\n🔬 Comparing Sklearn Interface")
    print("=" * 50)
    
    data = create_test_data()[:200]
    
    config = {
        'map_size': (8, 8),
        'input_dim': 2,
        'random_seed': 42
    }
    
    # Test fit/predict interface
    np.random.seed(42)
    original_som = OriginalSOM(**config)
    original_pred = original_som.fit_predict(data)
    
    np.random.seed(42)
    modular_som = ModularSOM(**config)
    modular_pred = modular_som.fit_predict(data)
    
    # Check if predictions are identical
    pred_identical = np.array_equal(original_pred, modular_pred)
    print(f"   Predictions identical: {pred_identical}")
    
    # Test transform method
    np.random.seed(42)
    original_som = OriginalSOM(**config)
    original_som.fit(data)
    original_transform = original_som.transform(data[:10])
    
    np.random.seed(42)
    modular_som = ModularSOM(**config) 
    modular_som.fit(data)
    modular_transform = modular_som.transform(data[:10])
    
    transform_identical = np.array_equal(original_transform, modular_transform)
    print(f"   Transforms identical: {transform_identical}")
    
    success = pred_identical and transform_identical
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"   Status: {status}")
    
    return success

def run_comparison():
    """Run comprehensive comparison"""
    print("🔍 SOM Implementation Comparison")
    print("=" * 60)
    print("Comparing original monolithic vs modular implementation")
    
    tests = [
        compare_basic_training,
        compare_weight_initialization,
        compare_bmu_finding,
        compare_sklearn_interface
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎯 Comparison Results")
    print("=" * 50)
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Compatibility: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 Perfect compatibility! Modularization preserves all functionality.")
        return True
    else:
        print("⚠️  Some compatibility issues found.")
        return False

if __name__ == "__main__":
    success = run_comparison()
    sys.exit(0 if success else 1)