# Readme for ChromeOS usage

This Readme describes the steps to be performed to use eric on a
Chromebook with ChromeOS.

## 1. Preparation
Step 1: activate the Linux environment through the settings

Step 2: open a terminal window and execute these steps

    sudo apt update
    sudo apt upgrade
    sudo apt install libxkbfile1 libxcb-cursor0 libopengl0 python3-pip python3-venv

Step 3: modify environment to make Qt not use Wayland

As of ChromeOS 94 Qt6 is not yet compatible with the ChromeOS Wayland
implementation. In order to force Qt applications to use X11 modify
the "cros-garcon-override.conf" file.

    sudo vi /etc/systemd/user/cros-garcon.service.d/cros-garcon-override.conf

and add the line

    Environment="QT_QPA_PLATFORM=xcb"

After this change was performed close all Linux windows, log out and log back
in. This step is needed to restart the Linux VM and to make the above changes
effective.

__Note 1:__ This change seems to be not needed anymore on ChromeOS 102 with the
Bullseye based Linux environment.

__Note 2:__ If eric crashes showing completion lists, this change should be
applied in order to switch to use X11.

__Note 3:__ As of Qt 6.5.1 it is not compatible with Debian Bullseye in Wayland
mode. The above change needs to be implemented.

## 2. eric Installation
Installing eric7 is a simple process. There are various methods available.
Please choose the one best suited to your needs and skills. eric7 must be
used with Python 3, Qt6 and PyQt6.

### 2.1 Create a Python virtual environment for eric7
It is recommended to install eric7 into a Python virtual environment in order
to keep your Python distribution clean. In order to do that create it by
entering the following command in the terminal window.

    python3 -m venv eric7_venv
    ~/eric7_env/bin/python3 -m pip install --upgrade pip

Replace `eric7_venv` with the desired path to the directory for the virtual
environment. All further instructions will assume this environment name.

### 2.2 Installation via the Python Package Index PyPI
Enter the following command in the terminal window.

    ~/eric7_venv/bin/python3 -m pip install --upgrade --prefer-binary eric-ide

Once the installation is finished navigate to the executable directory of
the Python virtual environment and execute the `eric7_post_install` script.

    ~/eric7_venv/bin/eric7_post_install

### 2.3 Installation of Qt Tools via Qt online installer
In order to get the most out of eric7 it is recommended to install the Qt Tools
like `Qt Designer` or `Qt Linguist`. The recommended way is this.

1. Download the Qt online installer from the Qt download site.
2. Install Qt by executing the installer.
3. Configure the path to the Qt tools on the `Qt` configuration page of the
   eric7 configuration dialog.

## 3. Install optional packages for eric7 (for plug-ins)
eric7 provides an extension mechanism via plug-ins.  The plug-ins are
available via the Plugin Repository dialog from within eric7. Some plugins
require the installation of additional Python packages. This is done 
automatically during the plugin installation.
