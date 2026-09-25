import subprocess
import sys
from typing import List
from models import Package

def select_packages(packages: List[Package]) -> List[Package]:
    if not packages:
        return []

    lines = []
    for i, p in enumerate(packages):
        # 1. Colonna Nome visibile nella lista
        if getattr(p, "installed", False):
            name_col = f"\033[1;32m{p.name} [Installato]\033[0m"
        else:
            name_col = f"\033[1;31m{p.name}\033[0m"

        raw_name = f"{p.name} [Installato]" if getattr(p, "installed", False) else p.name
        pad = " " * max(1, 32 - len(raw_name))
        name_col += pad

        # 2. Origine
        src = p.source.upper()
        src_col = f"\033[1;34m{src:<8}\033[0m" if "APT" in src else f"\033[1;35m{src:<8}\033[0m"

        # 3. Descrizione breve
        desc = (p.desc or "").strip().replace("\t", " ").replace("\n", " ")

        # Campi FZF:
        # {1}: indice
        # {2}: riga visibile nella lista
        # {3}: id pacchetto
        # {4}: nome pulito
        # {5}: sorgente (APT/FLATPAK)
        # {6}: stato installato
        # {7}: descrizione completa
        status_str = "Installato" if getattr(p, "installed", False) else "Non installato"
        display_line = f"{name_col} | {src_col} | {desc}"
        lines.append(f"{i}\t{display_line}\t{p.id}\t{p.name}\t{src}\t{status_str}\t{desc}")

    fzf_input = "\n".join(lines).encode("utf-8")

    preview_cmd = (
        'echo -e "\\033[1;36m=== INFORMAZIONI PACCHETTO ===\\033[0m\\n" && '
        'echo -e "\\033[1mNome:\\033[0m        {4}" && '
        'echo -e "\\033[1mID:\\033[0m          {3}" && '
        'echo -e "\\033[1mOrigine:\\033[0m     {5}" && '
        'echo -e "\\033[1mStato:\\033[0m       {6}\\n" && '
        'echo -e "\\033[1;33mDescrizione:\\033[0m" && '
        'echo "{7}"'
    )

    try:
        process = subprocess.Popen(
            [
                "fzf",
                "-m",
                "--ansi",
                "--delimiter=\t",
                "--with-nth=2",
                "--preview", preview_cmd,
                "--preview-window=right:50%:wrap",
                "--prompt", "Seleziona > ",
                "--header", "TAB: seleziona multipli | INVIO: conferma"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr
        )
        stdout, _ = process.communicate(input=fzf_input)

        if process.returncode != 0:
            return []

        selected_indices = [
            int(line.split("\t")[0])
            for line in stdout.decode("utf-8").splitlines()
            if line.strip()
        ]

        return [packages[i] for i in selected_indices]

    except FileNotFoundError:
        print("Errore: fzf non è installato o non si trova nel PATH.", file=sys.stderr)
        return []