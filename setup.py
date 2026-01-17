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

    # 1. Provjera SWI-Prolog instalacije
    print("\n[1/3] Provjeravam SWI-Prolog instalaciju...")
    if not check_prolog():
        sys.exit(1)
    
    # 2. Instalacija paketa iz requirements.txt
    print("\n[2/3] Instaliram potrebne pakete...")
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    
    print("\n[3/3] Pokrećem igru...")
    
    # 3. Pokretanje igre
    main_path = os.path.join(os.path.dirname(__file__), 'src', 'main.py')
    subprocess.call([sys.executable, main_path])

if __name__ == "__main__":
    setup()
