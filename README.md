# UAY (Universal Yet Another)

A unified Debian/Ubuntu wrapper inspired by `yay`, built to query and install packages simultaneously across both **APT** and **Flatpak** using an interactive **fzf** terminal interface.

---

## Prerequisites

Ensure the following system dependencies are installed:

- **Python 3.10+**
- **fzf**
- **pipx**

On Debian/Ubuntu systems, install them via:

```bash
sudo apt update
sudo apt install python3-pip pipx fzf
pipx ensurepath
```

*(If this is your first time setting up `pipx`, restart your terminal session or run `source ~/.bashrc` / `source ~/.zshrc`).*

---

## Installation

Choose one of the two installation methods:

### Method 1: Directly from GitHub (Recommended)

Install the latest build into an isolated environment via `pipx`:

```bash
pipx install git+[https://github.com/ghosciro/UAY-Universal-Yet-Another-.git](https://github.com/ghosciro/UAY-Universal-Yet-Another-.git)
```

To update later:

```bash
pipx upgrade uay
```

---

### Method 2: Via Pre-built Wheel (`.whl`)

1. Download the latest `.whl` asset from the [Releases](https://github.com/ghosciro/UAY-Universal-Yet-Another-/releases) page.
2. Install it locally:

```bash
pipx install ./uay-0.1.0-py3-none-any.whl
```

---

## Usage

Search for any software or library by passing a query:

```bash
uay <query>
```

Example:

```bash
uay whatsapp
```

### Keybindings

- **Type to filter**: Instant fuzzy search across returned package names and descriptions.
- **Up/Down arrows / Ctrl+j / Ctrl+k**: Navigate through entries.
- **TAB**: Toggle selection for multiple packages.
- **ENTER**: Confirm and proceed with installing selected items.
- **ESC / Ctrl+c**: Exit without making changes.

---

## Uninstallation

To remove `uay` from your environment:

```bash
pipx uninstall uay
```
