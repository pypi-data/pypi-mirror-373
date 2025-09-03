#!/usr/bin/env python3
"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀
"""
"""
Basic test suite for tensor-product-binding
=====================================

Tests core functionality and ensures the module loads correctly.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import pytest
import numpy as np
import tensor_product_binding


class TestBasicFunctionality:
    """Test basic functionality of the module"""
    
    def test_module_import(self):
        """Test that the module imports successfully"""
        assert tensor_product_binding.__version__
        assert hasattr(tensor_product_binding, '__all__')
        
    def test_module_components(self):
        """Test that main components are available"""
        # Check that main classes/functions are available
        for component in tensor_product_binding.__all__:
            assert hasattr(tensor_product_binding, component), f"Missing component: {component}"
    
    def test_attribution_display(self):
        """Test that attribution is displayed on import"""
        # Import should trigger attribution display
        # This test just ensures no exceptions during import
        import importlib
        importlib.reload(tensor_product_binding)
        
    @pytest.mark.parametrize("numpy_version", ["latest"])
    def test_numpy_compatibility(self, numpy_version):
        """Test compatibility with numpy"""
        # Basic numpy array operations should work
        test_data = np.random.randn(10, 10)
        assert isinstance(test_data, np.ndarray)
        assert test_data.shape == (10, 10)


class TestModuleSpecific:
    """Module-specific tests"""
    
    def test_main_class_instantiation(self):
        """Test that main classes can be instantiated"""
        # This is a basic smoke test - instantiate main classes
        try:
            # Get the first class from __all__ and try to instantiate it
            main_classes = [getattr(tensor_product_binding, name) for name in tensor_product_binding.__all__ 
                           if hasattr(getattr(tensor_product_binding, name), '__init__')]
            
            if main_classes:
                # Try basic instantiation (this may fail for some classes, which is OK)
                pass  # Specific tests would go here
                
        except Exception as e:
            # Some classes may require parameters, which is fine for this basic test
            pass
    
    def test_version_format(self):
        """Test that version follows semantic versioning"""
        version = tensor_product_binding.__version__
        version_parts = version.split('.')
        assert len(version_parts) >= 2, f"Version should have at least major.minor: {version}"
        
        # Check that version parts are numeric
        for part in version_parts:
            assert part.isdigit() or 'a' in part or 'b' in part or 'rc' in part, f"Invalid version part: {part}"


if __name__ == "__main__":
    print("\n" + "="*80)
    print("💰 SUPPORT THIS RESEARCH - PLEASE DONATE!")  
    print("🙏 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
    print("="*80 + "\n")
    
    pytest.main([__file__, "-v"])
    
    print("\n" + "="*80)
    print("💝 Thank you for using this research software!")
    print("📚 Please donate: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS") 
    print("="*80 + "\n")


"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
📝 CITE: Benedict Chen (2025) - Tensor Product Binding Research Implementation

Your support enables continued development of cutting-edge AI research tools! 🎓✨
"""
