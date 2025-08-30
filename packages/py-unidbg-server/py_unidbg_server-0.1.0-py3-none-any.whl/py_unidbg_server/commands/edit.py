from pathlib import Path
import sys

def run():
    base = Path(__file__).parent.parent  # py_unidbg_server
    template_file = base / "unidbg_server.py"
    
    target_dir = Path.cwd()
    target_file = target_dir / "unidbg_server.py"

    if target_file.exists():
        print(f"Target file already exists: {target_file}")
        sys.exit(1)
    else:
        # Read the template file
        template_code = template_file.read_text(encoding='utf-8')
        # Write the modified code to the target directory
        target_file.write_text(template_code, encoding='utf-8')
        print(f"File has been copied to: {target_file}")
