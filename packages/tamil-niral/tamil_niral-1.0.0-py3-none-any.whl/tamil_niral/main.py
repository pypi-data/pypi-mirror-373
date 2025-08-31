import sys
import subprocess

# Set your language's version
__version__ = "1.0.0"

def main_func():
    """Handles command-line arguments in Tamil."""
    args = sys.argv[1:]

    if not args:
        print("Usage: niral <command> or niral <filename.tn>")
        return

    # Command: "niral நிறுவு தமிழ் நிரல்" (Install/Update Tamil Niral)
    if args == ['நிறுவு', 'தமிழ்', 'நிரல்']:
        print("Updating Tamil Niral to the latest version...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'tamil-niral'])

    # Command: "niral சோதிப்பு தமிழ் நிரல்" (Check Tamil Niral version)
    elif args == ['சோதிப்பு', 'தமிழ்', 'நிரல்']:
        print(f"Tamil Niral version: {__version__}")

    # Command: "niral நிறுவு நூலகம் <library_name>" (Install a library)
    elif len(args) == 3 and args[:2] == ['நிறுவு', 'நூலகம்']:
        lib_name = args[2]
        package_name = f"tamil-niral-{lib_name}" # Assumes libraries are named like 'tamil-niral-kadigaram'
        print(f"Installing library: {lib_name}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', package_name])

    # Default action: Run an interpreter file
    else:
        try:
            file_path = args[0]
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                # Replace 'run_interpreter' with your interpreter's main function
                # from .interpreter import run_interpreter 
                # run_interpreter(code)
                print(f"Executing file: {file_path}") # Placeholder
        except FileNotFoundError:
            print(f"Error: File '{args[0]}' not found.")