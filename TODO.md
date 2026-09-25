
# ToDo

## APT

- [X] Implementare `AptBackend` (ricerca pacchetti e metadati)
- [X] Gestire recupero pacchetti installati (`dpkg-query` / `apt list --installed`)
- [X] Gestire installazione (`apt install`) e rimozione (`apt remove`)

## Flatpak

- [X] Implementare `FlatpakBackend` (ricerca su Flathub e repository configurati)
- [X] Gestire elenco applicazioni installate (`flatpak list`)
- [X] Gestire installazione (`flatpak install`) e disinstallazione (`flatpak uninstall`)

## PIPX

- [X] Implementare `PipxBackend` (ricerca, lista pacchetti Python isolati)
- [X] Gestire installazione (`pipx install`) e rimozione (`pipx uninstall`)

## Snap

- [ ] Implementare `SnapBackend` (ricerca con `snap find <query>` o via socket `/run/snapd.socket`)
- [ ] Gestire recupero pacchetti installati (`snap list`)
- [ ] Gestire installazione (`snap install`) e rimozione (`snap remove`)

## Homebrew

- [ ] Implementare `HomebrewBackend` (`brew search <query>`, parsing `brew info --json=v2`)
- [ ] Gestire elenco pacchetti installati (`brew list --formula --cask`)
- [ ] Gestire installazione (`brew install`) e rimozione (`brew uninstall`)

## Pacstall

- [ ] Implementare `PacstallBackend` (ricerca tramite `pacstall -S <query>`)
- [ ] Gestire lista pacchetti installati (`pacstall -L`)
- [ ] Gestire installazione (`pacstall -I`) e rimozione (`pacstall -R`)

## Cargo

- [ ] Implementare `CargoBackend` (interrogazione API `https://crates.io/api/v1/crates`)
- [ ] Gestire elenco binari installati localmente (`cargo install --list`)
- [ ] Gestire installazione (`cargo install`) e rimozione (`cargo uninstall`)

## Nix

- [ ] Implementare `NixBackend` (ricerca con `nix search nixpkgs <query> --json`)
- [ ] Gestire lista profili attivi (`nix profile list --json`)
- [ ] Gestire installazione (`nix profile install`) e rimozione (`nix profile remove`)

## AppImage

- [ ] Implementare `AppImageBackend` con catalogazione AppImageHub o feed release GitHub
- [ ] Gestire download file eseguibili e creazione collegamenti `.desktop` in `~/.local/bin`
- [ ] Gestire rimozione file `.AppImage` e pulizia scorciatoie
