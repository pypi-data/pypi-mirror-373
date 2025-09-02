"""Utilities for accessing PyInGraph examples after package installation."""

import os
import shutil
import pkg_resources
from pathlib import Path


def get_examples_path():
    """Get the path to the examples directory in the installed package.
    
    Returns:
        str: Path to the examples directory
    """
    try:
        # Try to get the examples path from the installed package
        examples_path = pkg_resources.resource_filename('pyingraph', 'examples')
        return examples_path
    except Exception:
        # Fallback: try to find examples relative to this file
        current_dir = Path(__file__).parent
        examples_path = current_dir / 'examples'
        if examples_path.exists():
            return str(examples_path)
        else:
            raise FileNotFoundError("Examples directory not found in the installed package")


def list_examples():
    """List all available examples.
    
    Returns:
        dict: Dictionary with example names and descriptions
    """
    examples_path = get_examples_path()
    examples = {}
    
    # Scan for Python demo files
    for file_path in Path(examples_path).glob('demo_*.py'):
        name = file_path.stem
        # Try to extract description from the first docstring
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple docstring extraction
                if '"""' in content:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    if end > start:
                        description = content[start:end].strip().split('\n')[0]
                    else:
                        description = "Demo script"
                else:
                    description = "Demo script"
        except Exception:
            description = "Demo script"
        
        examples[name] = {
            'file': str(file_path),
            'description': description
        }
    
    # Add JSON graph files
    for file_path in Path(examples_path).glob('*.json'):
        name = file_path.stem
        examples[name] = {
            'file': str(file_path),
            'description': "Graph configuration file"
        }
    
    return examples


def copy_examples(destination_dir, overwrite=False):
    """Copy all examples to a destination directory.
    
    Args:
        destination_dir (str): Directory where examples will be copied
        overwrite (bool): Whether to overwrite existing files
        
    Returns:
        str: Path to the copied examples directory
    """
    examples_path = get_examples_path()
    dest_path = Path(destination_dir) / 'pyingraph_examples'
    
    if dest_path.exists() and not overwrite:
        raise FileExistsError(f"Examples already exist at {dest_path}. Use overwrite=True to replace them.")
    
    if dest_path.exists() and overwrite:
        shutil.rmtree(dest_path)
    
    # Copy the entire examples directory
    shutil.copytree(examples_path, dest_path)
    
    print(f"Examples copied to: {dest_path}")
    print("\nAvailable examples:")
    examples = list_examples()
    for name, info in examples.items():
        print(f"  - {name}: {info['description']}")
    
    return str(dest_path)


def copy_example(example_name, destination_dir, overwrite=False):
    """Copy a specific example to a destination directory.
    
    Args:
        example_name (str): Name of the example to copy
        destination_dir (str): Directory where the example will be copied
        overwrite (bool): Whether to overwrite existing files
        
    Returns:
        str: Path to the copied example file
    """
    examples = list_examples()
    
    if example_name not in examples:
        available = ', '.join(examples.keys())
        raise ValueError(f"Example '{example_name}' not found. Available examples: {available}")
    
    source_file = Path(examples[example_name]['file'])
    dest_dir = Path(destination_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_file = dest_dir / source_file.name
    
    if dest_file.exists() and not overwrite:
        raise FileExistsError(f"File already exists at {dest_file}. Use overwrite=True to replace it.")
    
    shutil.copy2(source_file, dest_file)
    
    # If it's a demo script, also copy related files
    if example_name.startswith('demo_'):
        examples_path = Path(get_examples_path())
        
        # Copy JSON files that might be related
        for json_file in examples_path.glob('*.json'):
            dest_json = dest_dir / json_file.name
            if not dest_json.exists() or overwrite:
                shutil.copy2(json_file, dest_json)
        
        # Copy local_modules if it exists
        local_modules_src = examples_path / 'local_modules'
        if local_modules_src.exists():
            local_modules_dest = dest_dir / 'local_modules'
            if local_modules_dest.exists() and overwrite:
                shutil.rmtree(local_modules_dest)
            if not local_modules_dest.exists():
                shutil.copytree(local_modules_src, local_modules_dest)
    
    print(f"Example '{example_name}' copied to: {dest_file}")
    return str(dest_file)


def show_example_usage():
    """Show usage instructions for accessing examples."""
    print("PyInGraph Examples Usage:")
    print("========================")
    print()
    print("1. List available examples:")
    print("   from pyingraph import list_examples")
    print("   examples = list_examples()")
    print("   for name, info in examples.items():")
    print("       print(f'{name}: {info[\"description\"]}')")
    print()
    print("2. Copy all examples to current directory:")
    print("   from pyingraph import copy_examples")
    print("   copy_examples('.')")
    print()
    print("3. Copy a specific example:")
    print("   from pyingraph import copy_example")
    print("   copy_example('demo_simple_add', '.')")
    print()
    print("4. Get examples directory path:")
    print("   from pyingraph import get_examples_path")
    print("   path = get_examples_path()")
    print("   print(f'Examples located at: {path}')")


def _test_examples_utils():
    """Simple test function to verify examples utilities work correctly.
    
    This function can be run directly to test the basic functionality.
    It performs non-destructive tests that don't modify the file system.
    """
    print("Testing PyInGraph Examples Utilities...")
    print("=" * 40)
    
    try:
        # Test 1: Get examples path
        print("\n1. Testing get_examples_path()...")
        examples_path = get_examples_path()
        print(f"   ✓ Examples path found: {examples_path}")
        
        # Verify path exists
        if not Path(examples_path).exists():
            print(f"   ✗ Warning: Examples path does not exist: {examples_path}")
            return False
        
        # Test 2: List examples
        print("\n2. Testing list_examples()...")
        examples = list_examples()
        print(f"   ✓ Found {len(examples)} examples:")
        
        for name, info in examples.items():
            print(f"     - {name}: {info['description']}")
            # Verify file exists
            if not Path(info['file']).exists():
                print(f"   ✗ Warning: Example file does not exist: {info['file']}")
        
        if not examples:
            print("   ✗ Warning: No examples found")
            return False
        
        # Test 3: Verify example files are readable
        print("\n3. Testing example file accessibility...")
        demo_count = 0
        json_count = 0
        
        for name, info in examples.items():
            try:
                file_path = Path(info['file'])
                if file_path.suffix == '.py':
                    demo_count += 1
                elif file_path.suffix == '.json':
                    json_count += 1
                    
                # Try to read the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Read first 100 chars
                    if content:
                        print(f"   ✓ {name} is readable")
                    else:
                        print(f"   ✗ Warning: {name} appears to be empty")
                        
            except Exception as e:
                print(f"   ✗ Error reading {name}: {e}")
                return False
        
        print(f"\n   Summary: {demo_count} demo files, {json_count} JSON files")
        
        # Test 4: Test error handling
        print("\n4. Testing error handling...")
        try:
            # Test with non-existent example
            copy_example('non_existent_example', '/tmp')
            print("   ✗ Error: Should have raised ValueError for non-existent example")
            return False
        except ValueError as e:
            print(f"   ✓ Correctly raised ValueError: {str(e)[:50]}...")
        except Exception as e:
            print(f"   ✗ Unexpected error type: {type(e).__name__}: {e}")
            return False
        
        print("\n" + "=" * 40)
        print("✓ All tests passed! Examples utilities are working correctly.")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    """Run tests when this module is executed directly."""
    success = _test_examples_utils()
    if success:
        print("\nAll tests completed successfully!")
        print("You can now use the examples utilities with confidence.")
    else:
        print("\nSome tests failed. Please check the output above.")
        exit(1)