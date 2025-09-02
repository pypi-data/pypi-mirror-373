# Readme for use on a Raspberry Pi 4/5

In order to use eric7 on a Raspberry Pi 4 or Pi 5 computer a Linux distribution
providing `Qt6` and `PyQt6` packages need to be installed. This recipe was tested on
__Ubuntu 24.10__ and __Manjaro ARM__.

This requirement is there because up to now no `PyQt6-QScintilla` wheel is available
for the aarch64 architecture (ARM computers) via the Python Packaging Index PyPI.

## 1. Step 1: Qt6 and PyQt6
Ensure the following `Qt6` and `PyQt6` packages are installed or install them.

### Ubuntu
    - designer-qt6
    - designer-qt6-plugins
    - libqscintilla2-qt6-15
    - libqscintilla2-qt6-l10n
    - libqt6charts6
    - libqt6core6t64
    - libqt6dbus6
    - libqt6designer6
    - libqt6designercomponents6
    - libqt6gui6
    - libqt6help6
    - libqt6multimedia6
    - libqt6multimediawidgets6
    - libqt6network6
    - libqt6opengl6
    - libqt6openglwidgets6
    - libqt6pdf6
    - libqt6pdfwidgets6
    - libqt6printsupport6
    - libqt6serialport6
    - libqt6sql6
    - libqt6sql6-sqlite
    - libqt6svg6
    - libqt6svgwidgets6
    - libqt6uitools6
    - libqt6webchannel6
    - libqt6webengine6-data
    - libqt6webenginecore6
    - libqt6webenginecore6-bin
    - libqt6webenginewidgets6
    - libqt6websockets6
    - libqt6widgets6
    - libqt6xml6
    - linguist-qt6
    - pyqt6-dev-tools
    - python3-pyqt6
    - python3-pyqt6.qsci
    - python3-pyqt6.qtcharts
    - python3-pyqt6.qthelp
    - python3-pyqt6.qtmultimedia
    - python3-pyqt6.qtpdf
    - python3-pyqt6.qtserialport
    - python3-pyqt6.qtsvg
    - python3-pyqt6.qtwebchannel
    - python3-pyqt6.qtwebengine
    - python3-pyqt6.qtwebsockets
    - python3-pyqt6.sip
    - qt6-documentation-tools
    - qt6-l10n-tools
    - qt6-translations-l10n


### Manjaro ARM
    - qt6-base
    - qt6-charts
    - qt6-doc
    - qt6-imageformats
    - qt6-multimedia
    - qt6-serialport
    - qt6-svg
    - qt6-tools
    - qt6-translations
    - qt6-webchannel
    - qt6-webengine
    - python-pyqt6
    - python-pyqt6-charts
    - python-pyqt6-sip
    - python-pyqt6-webengine
    - python-qscintilla-qt6
    - qscintilla-qt6


## 2. Step 2: Spell Checking
If spell checking is desired, ensure the following packages are installed.

- enchant
- python-enchant
- aspell
- any aspell language dictionary desired (suggested at least 'aspell-en')

## 3. Step 3: Prepare eric7 Installation
In order to install eric7 it is recommended to create a Python virtual environment in
order to isolate the eric7 execution environment as much as possible from the standard
installation. In order to create this environment execute the following in a terminal
window.

    python3 -m venv --system-site-packages eric7_env
    ~/eric7_env/bin/python3 -m pip install --upgrade pip

__Note:__ The switch `--system-site-packages` is necessary because there are is no
complete set of PyQt6/Qt6 packages available for the AArch64 (ARM) platform. This
necessitates the use of the packages provided by the distribution.

## 4. Step 4: Install eric7 (eric-ide)
Install eric7 into the created Python virtual environment by following these steps.

    ~/eric7_env/bin/python3 -m pip install --prefer-binary eric-ide
    ~/eric7_env/bin/eric7_post_install
