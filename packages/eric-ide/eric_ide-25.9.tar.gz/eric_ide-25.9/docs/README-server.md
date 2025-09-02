# README for the eric-ide Server

## 0. What is eric-ide-server?
eric-ide-server is an extension for the eric7 IDE. It allows remote editing
and debugging of Python scripts and projects. By having the eric7_server
script installed and running on a remote computer the eric7 IDE will be able
to connect to it for loading and saving files and run a debug session. This
works for simple (single) scripts as well as complete eric-ide projects.
For more details see
[https://eric-ide.python-projects.org](https://eric-ide.python-projects.org)

## 1. Installation
Installing eric7_server is a simple process. It is recommended to run the
server in its own Python virtual environment in order to not mess with your
system. Installation should be done using the package provided via PyPI. The
steps are shown below.

### 1.1 Create a Python virtual environment for eric7_server
In order to create that environment execute the following command in a terminal
window.

__Linux, macOS__

    python3 -m venv eric7_server_venv

__Windows__

    python.exe -m venv eric7_server_venv

Replace `eric7_server_venv` with the desired path to the directory for the virtual
environment. All further instructions will assume this environment name.

### 1.2 Installation via the Python Package Index PyPI

Enter the following command in a terminal window.

__Linux, macOS__

    ~/eric7_server_venv/bin/python3 -m pip install --upgrade --prefer-binary eric-ide-server

__Windows__

    eric7_server_venv\Scripts\python.exe -m pip install --upgrade --prefer-binary eric-ide-server

## 2. Usage
In order to use the eric-ide server on a remote host just login to this host (preferable
via ssh) and start the server. When serving files via the eric-ide server file dialog,
the current directory (i.e. the one the server was started in) will be shown first. Some
aspects of the server may be changed via command line switches. The supported switches
are

- -h, --help  
    Show some help message giving the supported switches and exit.
- -p PORT, --port PORT  
    Listen on the given port for connections from an eric IDE (default 42024).
- -6, --with-ipv6  
    Listen on IPv6 interfaces as well, if the system supports the creation of TCP
    sockets, which can handle both IPv4 and IPv6.
- -V, --version  
    Show version information and exit.

## 3. License
eric7 (and the eric7 tools) is released under the conditions of the GPLv3. See 
separate license file `LICENSE.GPL3` for more details. Third party software
included in eric7 is released under their respective license and contained in
the eric7 distribution for convenience. 

## 4. Bugs and other reports
Please send bug reports, feature requests or contributions to eric bugs
address. Just send an email to
[eric-bugs@eric-ide.python-projects.org](mailto:eric-bugs@eric-ide.python-projects.org).
To request a new feature send an email to
[eric-featurerequest@eric-ide.python-projects.org](mailto:eric-featurerequest@eric-ide.python-projects.org).

Alternatively bugs may be reported or features requested via the eric7 issue tracker
at 
[https://tracker.die-offenbachs.homelinux.org/](https://tracker.die-offenbachs.homelinux.org/).
