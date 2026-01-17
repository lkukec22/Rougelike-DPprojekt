import os
import subprocess
import sys

def check_prolog():
    """Provjeri je li SWI-Prolog instaliran i dostupan u PATH-u."""
    try:
        result = subprocess.run(
            ["swipl", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"  -> Pronađen: {version}")
            return True
    except FileNotFoundError:
        pass
    
    print("  -> GREŠKA: SWI-Prolog nije pronađen!")
    print("     Molimo instalirajte SWI-Prolog s: https://www.swi-prolog.org/download/stable")
    print("     Nakon instalacije, provjerite da je 'swipl' dostupan u PATH-u.")
    return False

def setup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, 'venv')
    
    # Odredi Python executable i pip ovisno o OS-u
    if sys.platform == 'win32':
        python_exe = os.path.join(venv_dir, 'Scripts', 'python.exe')
        pip_exe = os.path.join(venv_dir, 'Scripts', 'pip.exe')
    else:
        python_exe = os.path.join(venv_dir, 'bin', 'python')
        pip_exe = os.path.join(venv_dir, 'bin', 'pip')
    
    # 1. Provjera SWI-Prolog instalacije
    print("\n[1/4] Provjeravam SWI-Prolog instalaciju...")
    if not check_prolog():
        sys.exit(1)
    
    # 2. Kreiranje virtualnog okruženja
    print("\n[2/4] Kreiram virtualno okruženje...")
    if not os.path.exists(venv_dir):
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        print(f"  -> Kreirano: {venv_dir}")
    else:
        print(f"  -> Već postoji: {venv_dir}")
    
    # 3. Instalacija paketa u venv
    print("\n[3/4] Instaliram potrebne pakete u virtualno okruženje...")
    requirements_path = os.path.join(base_dir, 'requirements.txt')
    subprocess.check_call([pip_exe, "install", "-r", requirements_path])
    
    # 4. Pokretanje igre
    print("\n[4/4] Pokrećem igru...")
    main_path = os.path.join(base_dir, 'src', 'main.py')
    subprocess.call([python_exe, main_path])

if __name__ == "__main__":
    setup()
