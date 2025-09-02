# flinventory GUI

A GUI for the flinventory project/ data format.

Including a fuzzy search that prefers more exact matches and includes all alternative names and descriptions of things.

![Search screenshot](docs/search_small.png)

More screenshots for the edit mode can be found in the very basic [docs](docs/screenshots.md).

## Run

Getting code:
`git clone https://codeberg.org/flukx/flinventory-gui.git`

Getting prerequisites:
- ```commandline
  cd flinventory-gui
  nix-shell
  ```
- conda (not sure if that still works)
  ```commandline
  sudo apt install pdf2svg texlive-full
  # or
  sudo dnf install texlive-scheme-full pdf2svg
  # for actually needed LaTeX packages see shell.nix
  # or whatever package manager you use
  conda create -f environment.yml
  conda activate bikeparts-gui
  pip install flinventory-gui
  ```
- or virtualenv:
  ```commandline
  sudo apt install pdf2svg texlive-full
  # or
  sudo dnf install texlive-scheme-full pdf2svg
  # for actually needed LaTeX packages see shell.nix
  # or whatever package manager you use
  python -m venv .venv
  source .venv/bin/activate
  pip install -r flinventory-gui
  ```

Getting data: `git clone -b harzgerode-main https://codeberg.org/flukx/flings.git`

Run it:
```commandline
flinventory-webgui flings
```
It should open a browser with the search page. Otherwise, open [localhost:11111](http://localhost:11111)
in your browser.

To see all options run `python flinventory_gui/search.py --help` but note that many of them are inherited
from the underlying module `flinventory` and are not used.

## Rebuild during development
In the nix-shell, you can replace the flinventory-gui with the current version if you've changed something:
```commandline
pdm build
pip install dist/flinventory_gui-...py3-none-any.whl --upgrade
# run again
flinventory-webgui flings
```
or just (and get changes pick-uped immediately)
```commandline
python flinventory_gui/search.py flings
```

## Making website accessible in local network

It's nice to use the thing search on the computer where it is run but often it's more helpful to
use it on other mobile devices. Therefore, you can make the search page available in the local network
by opening the port (by default `11111` in the firewall.)

In Fedora KDE I opened "Firewall" and in the Configuration "Runtime" in Tab "Zones" in zone "public" in tab "Ports"
added `11111` for protocol `tcp`.

In NixOS KDE I typed ([for temporary access](https://discourse.nixos.org/t/how-to-temporarily-open-a-tcp-port-in-nixos/12306/10)):
```commandline
sudo iptables -A INPUT -p tcp --dport 11111 -j ACCEPT
sudo systemctl reload firewall
```
For permanent usage, use the `configuration.nix` with the line
`networking.firewall.allowedTCPPorts = [ 11111 ];`.

## Data
The data directory is given as a mandatory command-line argument.
Most of the content and structure of this data directory is described in the documentation of [flinventory](https://codeberg.org/flukx/flinventory.git).
**Optional** data that is not used by flinventory itself and therefore not described there, is:
- a directory `website_resources`
  - with a favicon named `favicon.ico`
  - and a directory `translatio` with translation files for the terms that are defined in the inventory
    and appear in the GUI, namely the level names in the schema. The file structure is that for the package
    [i18nice](https://github.com/solaluset/i18nice), that is:
    - `thing_editor.de.yml` (and with `en` or other languages):
      ```yaml
      de:
        room: Raum
        from-left: von links
        level: Regalbrett
        workshop: Werkstatt
      ```

## Development setup

### with `nix-shell`
Run `nix-shell` and a nix-shell with the necessary python packages is created based on the `shell.nix` file.
Note that NiceGUI is unfortunately not available via nix-packages and therefore installed in a virtual environment with pip.
This virtual environment has the advantage that you can use it as a local interpreter for your IDE.
At least in pycharm it can be used.

## Ideas for the future

- Somehow really make the search async. Since filtering the correct parts and displaying them
  has no waiting periods (with `await`) it cannot really be cancelled.
  - Also helpful: show only 10 best results.
- Add filter for search that shows a bike where you can click on parts. And then only parts that are
  "part_of" this are shown. When clicked on the brakes, it shows a list of brake types (sub categories)
  that you can click on again. [Interactive image](https://nicegui.io/documentation/interactive_image)
  could be helpful.
  - Make this filter keyboard accessible. Ctrl+F activates choice, then letter chooses something which is
    marked in the text on the bike picture.
- Figure out why sometimes the page reloads completely.
