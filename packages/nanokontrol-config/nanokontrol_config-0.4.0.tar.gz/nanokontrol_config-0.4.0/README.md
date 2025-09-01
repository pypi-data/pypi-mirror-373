# Korg™ nanoKONTROL Studio™ config tool

While there exists MIDI protocol specification for other Korg™ nano* products
like nanoKONTROL™ or nanoKONTROL2™, we have nothing for the more modern
nanoKONTROL Studio™ (and thus no tools like [Nano-Basket](https://github.com/royvegard/Nano-Basket)
for the nanoKONTROL Studio™

This project provides a CLI tool for reading and writing configuration from and
to YAML based config files plus a basis for future nanoKONTROL Studio™ based
projects which need to talk to the device using the proprietary MIDI based
protocol.


## Install and use

You can either install `nanokontrol-config` via `pipx`

```bash
# have pipx installed first
pipx install nanokontrol-config
nanokontrol-config ...
```

.. simply run it via `uvx` provided by the `uv` package
```bash
# have uv installed first
uvx nanokontrol-config ...
```

.. or checkout the project and run it via `uv run`
```bash
# have git and uv installed first
git clone https://github.com/frans-fuerst/nanokontrol-config.git
cd nanokontrol-config
uv run nanokontrol-config ...
```

If you are running into problems installing `python-rtmidi`, try to provide
`pkg-config` and `libasound2-dev` (or similar) before installing
`nanokontrol-config`.

With all approaches you get an entry point `nanokontrol-config` with the
following syntax:
```bash
nanokontrol-config [<global-opts>] <CMD> [<command-opts>]
```

### Exporting the config

Read the current config from your attached nanoKONTROL Studio™ device and save
it to a YAML file.

```bash
nanokontrol-config e[xport] [-o|--output current-config.yaml]
```

### Sending the config

Read a YAML file and push it to your (attached) device:

```bash
nanokontrol-config s[et] [-i|--input modified-config.yaml]
```

### Patching the config

**NOT YET IMPLEMENTED**

Read just a sparse config (only implementing the modifications you need) and
apply it to the configuration currently stored on your device:

```bash
nanokontrol-config p[atch] [-i|--input sparse-config.yaml]
```


## Disclaimer

I'm not affiliated in any way with Korg™ and this project is solely based on
reverse engineering MIDI I/O.

Of course using this tool is fully your own risk - I hereby refuse any
responsibility for any damages.


## License

See [License.md].


## Contribution

### Initialize

```bash
git clone https://github.com/frans-fuerst/nanokontrol-config.git
cd nanokontrol-config
uv run pre-commit install
```

### Manually run checks and fixes

```bash
# run all checks which would be executed on commit, but on unstaged stuff, too
uv run pre-commit run --hook-stage pre-commit --all-files
# run all type checking (mypy) on current (unstaged) state
uv run pre-commit run check-python-typing --all-files
uv run pre-commit run check-python-linting --all-files
uv run pre-commit run check-python-format --all-files
uv run pre-commit run check-python-isort --all-files
uv run pre-commit run check-python-unittest --all-files
uv run pre-commit run check-python-doctest --all-files
uv run pre-commit run check-yaml-linting --all-files

uv run pre-commit run fix-python-linting --hook-stage manual --all-files
uv run pre-commit run fix-python-format --hook-stage manual --all-files
uv run pre-commit run fix-python-isort --hook-stage manual --all-files
```

implement -> `uv run pytest` -> commit -> repeat

### Manually run checks and fixes

```bash
uv version --bump <patch|minor|major>
uv build
# manual tests
git push
uv publish --token <TOKEN>
```


## Missing for a v1.0

* `info` lists all devices and identifies Korg products
* `patch` implemented
* default values properly for all BaseModel instances implemented
* proper documentation and comments
* linter is satisfied


## Troubleshooting

* Reset to firmware defaults: SCENE + BACK + STOP + Turn on


## Future

* Graphical UI
* YAML import/export file config supports comments
* Support for importing/exporting the Korg™ proprietary configuration file format
* Support for other Korg™ nano* products
* Support for other MIDI controllers
* Availability for MicroPython (i.e. no dependency to `pydandtic` or `mido`)


## External sources

* [Nano-Basket: config tool for nanoKONTROL](https://github.com/royvegard/Nano-Basket)
* [nanoKONTROL2 MIDI Implementation (v1.00 / 2010.12.14)](
https://cdn.korg.com/us/support/download/files/aeb2862daf0cb7db826d8c62f51ec28d.txt?response-content-disposition=attachment%3Bfilename%2A%3DUTF-8%27%27nanoKONTROL2_MIDIimp.txt)
* [uv: Building and publishing a package](https://docs.astral.sh/uv/guides/package/#preparing-your-project-for-packaging)
* [korgforums: MIDI implementation docs for nanoKEY and nanoKONTROL Studio?](https://www.korgforums.com/forum/phpBB3/viewtopic.php?t=130754&hilit=%E5%A8%87+txt)
