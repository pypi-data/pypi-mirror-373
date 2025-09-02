import argparse
import os
import sys
import importlib.util
from mgi_alphatool.context import Context

def py2json():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Convert Python script to JSON.")
    parser.add_argument('-i', '--input', required=True, help='Input script path')
    parser.add_argument('-o', '--output', required=True, help='Output JSON path')
    args = parser.parse_args()

    # Get absolute paths
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    
    # Add script directory to Python path to ensure imports work correctly
    script_dir = os.path.dirname(input_path)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Use importlib to properly load the module with its imports
    module_name = os.path.basename(input_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, input_path)
    
    if spec is None:
        print(f"Error: Could not load file {input_path}")
        return
    
    module = importlib.util.module_from_spec(spec)
    
    # Add the output path to the module's namespace
    module.OUTPUT_PATH = output_path
    
    try:
        # Execute the module
        spec.loader.exec_module(module)
        
        # Find Context object in module's global namespace
        ctx = next((obj for var_name, obj in module.__dict__.items() 
                   if isinstance(obj, Context) and var_name != 'Context'), None)
        
        if not ctx:
            print("Context not found. Please initialize mgi_alphatool first.")
            print("Make sure your script creates a global mgi_alphatool Context object.")
        else:
            ctx.export(output_path)
            print(f"Successfully exported protocol to {output_path}")
    
    except Exception as e:
        print(f"Error executing script: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    py2json()