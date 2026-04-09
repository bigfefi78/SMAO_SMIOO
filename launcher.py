"""
Launcher per Qt Designer (PyQt5)
Carica automaticamente i plugin custom
"""

import subprocess
import sys
import os
from pathlib import Path


def find_designer():
    """Trova l'eseguibile di Qt Designer"""

    print("🔍 Ricerca Qt Designer...")

    possible_paths = []

    # 1. pyqt5-tools
    try:
        import pyqt5_tools

        try:
            designer_path = Path(pyqt5_tools.QT_BIN_DIR) / "designer.exe"
            possible_paths.append(str(designer_path))
        except AttributeError:
            pass

        pyqt5_tools_dir = os.path.dirname(pyqt5_tools.__file__)
        possible_paths.append(
            os.path.join(pyqt5_tools_dir, "Qt", "bin", "designer.exe")
        )

    except ImportError:
        print("   pyqt5-tools non installato")

    # 2. Nel venv Scripts (IMPORTANTE: cerca pyqt5-tools.exe)
    venv_scripts = os.path.dirname(sys.executable)
    possible_paths.extend(
        [
            os.path.join(venv_scripts, "pyqt5-tools.exe"),  # Wrapper
            os.path.join(venv_scripts, "designer.exe"),
        ]
    )

    # 3. In site-packages
    try:
        import site

        for site_dir in site.getsitepackages():
            possible_paths.extend(
                [
                    os.path.join(
                        site_dir, "qt5_applications", "Qt", "bin", "designer.exe"
                    ),
                    os.path.join(site_dir, "pyqt5_tools", "Qt", "bin", "designer.exe"),
                ]
            )
    except Exception:
        pass

    # 4. Designer standalone
    possible_paths.extend(
        [
            r"C:\QtDesigner\designer.exe",
            r"C:\Program Files\Qt Designer\designer.exe",
        ]
    )

    # Cerca il primo che esiste
    for path in possible_paths:
        if path and os.path.exists(path):
            print(f"   ✓ Trovato: {path}")
            # Ritorna info: (path, is_wrapper)
            is_wrapper = path.endswith("pyqt5-tools.exe")
            return (path, is_wrapper)

    print("   ✗ Designer non trovato")
    return (None, False)


def main():
    print("=" * 70)
    print("🚀 Qt Designer Launcher (PyQt5)")
    print("=" * 70)

    # Info sistema
    print(f"\nPython: {sys.version.split()[0]}")
    print(f"Executable: {sys.executable}")
    print(
        f"Venv: {'Sì' if hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix else 'No'}"
    )

    # Verifica PyQt5
    try:
        import PyQt5

        pyqt_dir = os.path.dirname(PyQt5.__file__)
        print(f"\n✓ PyQt5: {pyqt_dir}")
        print("✓ QtDesigner: Disponibile (plugin supportati!)")

    except ImportError as e:
        print("\n❌ PyQt5 non installato correttamente!")
        print(f"   Errore: {e}")
        print("\n   Installa con:")
        print(f"   {sys.executable} -m pip install PyQt5 pyqt5-tools")
        return 1

    # Trova Designer
    designer_info = find_designer()
    designer_path, is_wrapper = designer_info

    if not designer_path:
        print("\n" + "=" * 70)
        print("❌ SOLUZIONI:")
        print("=" * 70)
        print("\n1️⃣  Installa pyqt5-tools:")
        print(f"   {sys.executable} -m pip install pyqt5-tools==5.15.4.3.2")
        print("\n2️⃣  Oppure avvia Designer manualmente:")
        print("   .venv\\Scripts\\pyqt5-tools.exe designer")
        print("=" * 70)
        return 1

    print(f"✓ Designer: {designer_path}")
    if is_wrapper:
        print("  (Usando wrapper pyqt5-tools)")

    # Path progetto e plugin
    project_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.join(project_dir, "designer_plugins")

    if not os.path.exists(plugin_dir):
        print(f"\n⚠️  Cartella plugin non trovata: {plugin_dir}")
    else:
        print(f"✓ Plugin dir: {plugin_dir}")

        # Verifica plugin
        plugins = [
            "blue_button_plugin.py",
            "toggle_button_plugin.py",
            "displacement_indicator_plugin.py",
        ]
        for plugin_file in plugins:
            full_path = os.path.join(plugin_dir, plugin_file)
            if os.path.exists(full_path):
                print(f"  ✓ {plugin_file}")
            else:
                print(f"  ⚠️  {plugin_file} NON TROVATO")

    # Setup environment
    env = os.environ.copy()

    # CRITICO: Variabile per plugin PyQt5
    env["PYQTDESIGNERPATH"] = plugin_dir
    print(f"\n\n\n\n\n\n\n\n✓ PYQTDESIGNERPATH: {env['PYQTDESIGNERPATH']}")

    # Aggiungi progetto al PYTHONPATH
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = project_dir + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = project_dir

    print("\n" + "=" * 70)
    print("📌 Widget disponibili in Designer:")
    print("   Gruppo 'Custom Buttons':     BlueButton")
    print("   Gruppo 'Industrial Controls': ToggleButton, DisplacementIndicator")
    print("=" * 70)
    print("\nAvvio Designer...\n")

    # Cambia directory
    os.chdir(project_dir)

    # Avvia Designer
    try:
        if is_wrapper:
            # Se è pyqt5-tools.exe, passa 'designer' come argomento
            cmd = [designer_path, "designer"]
        else:
            # Se è designer.exe diretto, non serve argomento
            cmd = [designer_path]

        print(f"Comando: {' '.join(cmd)}\n")

        result = subprocess.run(cmd, env=env)
        return result.returncode

    except KeyboardInterrupt:
        print("\n👋 Designer chiuso")
        return 0

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
