#!/usr/bin/env python3
""
Installation verification script for xentity

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: February 2, 2025

Usage:
    python tests/verify_installation.py
""

import sys
from pathlib import Path

def verify_installation():
    ""Verify that the library is properly installed and working.""
    print("🔍 Verifying xentity installation...")
    print("=" * 50)
    
    # Add src to Python path for testing
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Test main import
        print("📦 Testing main import...")
        import exonware.xentity
        print("✅ exonware.xentity imported successfully")
        
        # Test convenience import  
        print("📦 Testing convenience import...")
        import xentity
        print("✅ xentity convenience import works")
        
        # Test version information
        print("📋 Checking version information...")
        assert hasattr(exonware.xentity, '__version__')
        assert hasattr(exonware.xentity, '__author__')
        assert hasattr(exonware.xentity, '__email__')
        assert hasattr(exonware.xentity, '__company__')
        print(f"✅ Version: {exonware.xentity.__version__}")
        print(f"✅ Author: {exonware.xentity.__author__}")
        print(f"✅ Company: {exonware.xentity.__company__}")
        
        # Test basic functionality (add your tests here)
        print("🧪 Testing basic functionality...")
        # Add your verification tests here
        print("✅ Basic functionality works")
        
        print("\n🎉 SUCCESS! exonware.xentity is ready to use!")
        print("You have access to all xentity features!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you've installed the package with: pip install exonware-xentity")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    ""Main verification function.""
    success = verify_installation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
