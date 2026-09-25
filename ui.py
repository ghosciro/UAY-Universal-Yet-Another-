import subprocess
import sys
from typing import List
from models import Package


def select_packages(
    packages: List[Package], prompt: str = "Seleziona > ", query: str = ""
) -> List[Package]:
    if not packages:
        return []
    lines = []

    NAME_WIDTH = 36  # leggermente più spazioso per contenere anche [Installato]

    for i, p in enumerate(packages):
        is_inst = getattr(p, "installed", False)
        status_tag = " [Installato]" if is_inst else ""
        name_str = f"{p.name}{status_tag}"

        # Tronca a larghezza fissa solo se eccede, così le colonne rimangono perfette
        if len(name_str) > NAME_WIDTH:
            disp_name = name_str[: NAME_WIDTH - 2] + ".."
        else:
            disp_name = name_str

        color = "\033[1;32m" if is_inst else "\033[1;31m"
        name_col = f"{color}{disp_name:<{NAME_WIDTH}}\033[0m"

        src = p.source.upper()
        if "APT" in src:
            src_col = f"\033[1;34m{src:<8}\033[0m"
        elif "FLATPAK" in src:
            src_col = f"\033[1;35m{src:<8}\033[0m"
        elif "PIPX" in src:
            src_col = f"\033[1;33m{src:<8}\033[0m"
        else:
            src_col = f"{src:<8}"

        desc = (p.desc or "").strip().replace("\t", " ").replace("\n", " ")
        display_line = f"{name_col} | {src_col} | {desc}"
        status_str = "Installato" if is_inst else "Non installato"

        # Nel campo 4 passiamo p.name completo (senza tagli) per l'anteprima
        lines.append(
            f"{i}\t{display_line}\t{p.id}\t{p.name}\t{src}\t{status_str}\t{desc}"
        )
    fzf_input = "\n".join(lines).encode("utf-8")

    preview_cmd = (
        'echo -e "\\033[1;36m=== PACKAGE DETAILS ===\\033[0m\\n" && '
        'echo -e "\\033[1mName:\\033[0m        {4}" && '
        'echo -e "\\033[1mID:\\033[0m          {3}" && '
        'echo -e "\\033[1mSource:\\033[0m      {5}" && '
        'echo -e "\\033[1mStatus:\\033[0m      {6}\\n" && '
        'echo -e "\\033[1;33mDescription:\\033[0m" && '
        'echo "{7}"'
    )

    fzf_cmd = [
            "fzf",
            "-m",
            "-e",
            "--ansi",
            "--delimiter=\t",
            "--with-nth=2",
            "--no-hscroll",
            "--tac",
            "--preview",
            preview_cmd,
            "--preview-window=right:50%:wrap",
            "--prompt",
            prompt,
            "--header",
            "TAB: multi-select | INVIO: conferma",
        ]
    if query:
        fzf_cmd.extend(["--query", query])

    try:
        process = subprocess.Popen(
            fzf_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
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
        print("Error: fzf is not installed or not found in PATH.", file=sys.stderr)
        return []