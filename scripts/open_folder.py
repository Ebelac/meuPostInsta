#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abre uma pasta no gerenciador de arquivos nativo do sistema:
- macOS: Finder
- Windows: Explorer
- Linux: gerenciador padrao via xdg-open

Uso:
    python3 scripts/open_folder.py <caminho>

Exemplo:
    python3 scripts/open_folder.py assets/generated_carousels
"""
import os
import platform
import subprocess
import sys


def open_folder(path: str) -> bool:
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        print(f"❌ Pasta nao encontrada: {abs_path}")
        return False

    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", abs_path], check=True)
            print(f"✅ Aberto no Finder: {abs_path}")
        elif system == "Windows":
            subprocess.run(["explorer", abs_path], check=False)
            print(f"✅ Aberto no Explorer: {abs_path}")
        else:  # Linux
            subprocess.run(["xdg-open", abs_path], check=True)
            print(f"✅ Aberto no gerenciador padrao: {abs_path}")
        return True
    except FileNotFoundError:
        print(f"⚠️ Comando de abrir pasta nao disponivel neste sistema ({system})")
        print(f"   Acesse manualmente: {abs_path}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Falha ao abrir pasta: {e}")
        print(f"   Acesse manualmente: {abs_path}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scripts/open_folder.py <caminho>")
        sys.exit(1)
    ok = open_folder(sys.argv[1])
    sys.exit(0 if ok else 1)
