# Change Log

### Version 25.9
- bug fixes
- General
    - Made the code compatible with Python 3.14.
- Code Style Checker
    - Updated these checkers.
        - Security to `bandit` v1.8.6.
    - Added these new checkers.
        - Checker based on `flake8_no_nested_comprehensions` v1.0.0 to detect
          comprehensions with multiple generators.
- Editor
    - Added an information pane informing the user when an editor file is changed
      externally. It gives the option to activate the editor automatic reload
      capability, to reload the modified file, to ignore the current external
      modification and all further ones and to show a dialog with the differences
      between the externally modified file and the current editor text.
- MicroPython
    - Added the capability to clear the graph and delete the recorded raw data to
      the graph view.
    - Migrated the graph widget to the QtGraphs package because the QtCharts package
      is deprecated. The wheel will therefore install PyQt6 ≥ 6.8.0. Using the provided
      install script, eric-ide can be used with older PyQt6 versions as well.
    - Added an action button to stop the running script.
    - Extended the file manager widget to deal with multi selection of files.
    - Updated the list of known CircuitPython boards.
    - Updated the list of known UF2 capable boards.
- Third Party packages
    - Upgraded `eradicate` to version 3.0.0.
    - Upgraded `pycodestyle` to version 2.14.0.
    - Upgraded `pyflakes` to version 3.4.0.

### Version 25.8
- bug fixes
- Editor
    - Changed mouse button actions for undo/redo to Ctrl-XButton1/Ctrl-XButton2
      to allow history movement with XButton1/XButton2.
    - Added the 'soft keywords' to the list of default keywords for Python3.
    - Added configuration capability to disable auto-completions in comment and/or
      string areas (default True).
- Project
    - Added the capability to load the data of a 'pyproject.toml' file into the
      project properties dialog.
- Toolbar Manager
    - Added a button to the dialog to insert a separator item.
- View Manager
    - Added capability to move within the navigation history with mouse buttons
      XButton1 and XButton2 ('Back' and 'Forward' mouse buttons).

### Version 25.7
- bug fixes
- Editor and File Browser
    - Added capability to detect and show the Python metadata entries of a Python
      script.
- View Manager
    - Added capability to navigate to previously visited editor locations via backward
      and forward movements like in web browsers.

### Version 25.6
- bug fixes
- Code Style Checker
    - Updated these checkers.
        - Annotations to `flake8-annotations-complexity` v0.1.0
        - Security to `bandit` v1.8.3
    - Added these new checkers.
        - Checker based on `flake8-constants` v0.0.3 to detect modifications of
          constants.
- conda Manager
    - Removed the conda interface and changed it to a plug-in available via the
      plug-in repository.
- Cooperation
    - Removed the Cooperation interface and changed it to a plug-in available via the
      plug-in repository.
- CycloneDX Interface
    - Changed the interface to work with newer CycloneDX releases.
- MicroPython
    - Added support for IPv6 for WiFi and Ethernet enabled devices (MPy ≥ 1.24.0).
    - Updated the list of known CircuitPython boards
    - Updated the list of known UF2 capable boards.
- Virtual Environments
    - Added the capability to set an environment to unavailable.
- Third Party Packages
    - Upgraded `pycodestyle` to version 2.13.0.
    - Upgraded `pyflakes` to version 3.3.2.

### Version 25.5
- bug fixes
- General
    - Modified the display of the crash session dialog to show the time stamp
      of the found crash session file and the path of the
      project file (if a project was open) (see issue584).
    - Modified the display of the crash session dialog to allow the removal
      of crash session files.
- IRC
    - Removed the IRC interface and changed it to a plug-in available via the
      plug-in repository.
- Project
    - Removed support for `pyqt5` project type.
    - Removed support for `pyside2` project type.
- Virtual Environments
    - Prepared the virtual environments support for being expanded via plugins.

### Version 25.4
- bug fixes
- MicroPython
    - Added the capability to show the sha256 hash of a device file.

### Version 25.3
- bug fixes
- Code Style Checker
    - Updated these checkers.
        - Imports to `flake8-tidy-imports` v4.11.0
        - Logging to `flake8-logging` v1.7.0
        - Miscellaneous to `flake8-bugbear` v24.12.12
        - Miscellaneous to `flake8-comprehensions` v3.16.0
        - Security to `bandit` v1.8.2
    - Added these checkers to support more case.
        - 'Structural Pattern Matching' based on `flake8-spm` v0.0.1
        - Nested f-strings based on `flake8-nested-fstrings` v1.1.0
        - `pydantic` and `dataclass` related topics based on `flake8-pydantic` v0.4.0
- MicroPython
    - Added support for NRF52 based devices which support the UF2 standard.
    - Updated the list of known UF2 capable boards.
- pip Interface
    - Added a field to search for packages in the dependencies list.

### Version 25.2
- bug fixes
- MicroPython
    - Updated the list of known CircuitPython boards for CPy 9.2.3.
    - Updated the list of known UF2 capable boards.

### Version 25.1
- bug fixes
- General
    - Made the code compatible with Qt/PyQt 6.8.
- Mercurial Interface
    - Removed support for the `strip` extension (does not exist anymore).
    - Moved `purge` and `shelve` extensions to the `Other Functions` menu
      because they are builtin functions.
    - Added support for the `fastexport` extension.
    - Added support for the `uncommit` extension.
- pip Interface
    - Added an action button to clean up the site-packages directory of
      the selected environment.
    - Changed the package search function to open an external web browser
      with the package search term (PyPI does not support programmatic
      search anymore).
- Plugin Repository
    - Added a status label for 'Upgrade Available' that includes a copy of
      the the upgradable plugin entries.

### Version 24.12
- bug fixes
- Debugger
    - Added a configuration option to not stop at the first executable statement
      when debugging in passive mode.
- Find In Files
    - Added the capability to filter the list of files to be searched.
- IDE Server
    - Extended the eric-ide server to be able to check, if received messages have
      been sent by a valid eric IDE.
- MicroPython
    - Added support for ESP-C2, ESP32-C6, ESP32-H2, ESP32-P4 and ESP8684.
    - Extended the list of known VID/PID of ESP32 devices.
    - Added an entry to the ESP32 menu to show some device security information.
    - Improved the device detection of the UF2 Flash dialog to suppress devices not
      seen on the USB bus (happens when devices have identical BOOT volume names).
- Project Type 'Eric7 Plugin'
    - Added code to ensure, that compiled form files get recreated before
      they are written to the plugin archive.

### Version 24.11
**Note:** As Python 3.8 is EOL this eric-ide release will be the last one
supporting this Python version.

- bug fixes
- General
    - Made the code compatible with Python 3.13.
- Code Style Checker
    - Updated these checkers.
        - Miscellaneous to `flake8-bugbear` v24.8.19
        - Security to `bandit` v1.7.10
- IDE Server
    - Extended the eric-ide server integration in the file browser.
- MicroPython
    - Updated the list of known CircuitPython boards for CPy 9.2.0.
    - Updated the list of known UF2 capable boards.
- Third Party Packages
    - Upgraded `pycodestyle` to version 2.12.1.

### Version 24.10
- bug fixes
- Debugger
    - Added a configuration option to make 'Show only' the default for the
      global and local variables viewer.
- MicroPython
    - Added MicroPython support for RP2350 based controllers.
    - Updated the list of known CircuitPython boards for CPy 9.2.0-alpha.2351.
    - Updated the list of known UF2 capable boards.
    - Extended the file manager widget context menus.

### Version 24.9
- bug fixes
- Code Style Checker
    - Updated these checkers.
        - Security to `bandit` v1.7.9
        - Miscellaneous to `flake8-comprehensions` v3.15.0
- Third Party Packages
    - Upgraded `pip-licenses` to version 5.0.0.
    - Upgraded `pycodestyle` to version 2.12.0.

### Version 24.8
- bug fixes
- General
    - Improved the handling of crash sessions.
- Editor
    - Added the capability to sort the entries in the code outline by occurrence
      or alphabetically. Configure this on the `Editor => General` page.
    - Changed the editor layout to use a splitter between editor and code layout
      to enhance the flexibility.
- MicroPython
    - Updated the list of known CircuitPython boards for CPy 9.1.0.
    - Updated the list of known UF2 capable boards.
- Project Viewer
    - Added the context menu actions `New file...` and `New directory...` to the
      `Others` project viewer to give a more concise way to create a new files
      and directories.
- Security Key Management
    - Added a tool to manage FIDO2 security keys.
- Web Browser
    - Added support for `Passkeys` (for Qt >= 6.7.0).

### Version 24.7.1
- bug fixes

### Version 24.7
- bug fixes
- General
    - Improved the internal debug logging system.
- Code Style Checker
    - Updated these checkers.
        - Annotations to `flake8-annotations` v3.1.1
        - Miscellaneous to `flake8-bugbear` v24.4.26
        - Logging to `flake8-logging` v1.6.0
- IDE Server
    - Added functionality to work with remote files and projects via
      an `eric-ide Server` on a remote computer. All communication to
      this server is done through a single socket (port 42024 by default).
- MicroPython
    - Added a few boards to the list of know MicroPython boards.
- pip Interface
    - Added a configuration option to not include global environments in
      the selector list.
- Third Party Packages
    - Upgraded `pip-licenses` to version 4.4.0.

### Version 24.6
- bug fixes
- Editor
    - Added a key event handler to make the keypad ',' always insert a '.'
      character because that is what is needed in programming.
- General
    - Added a `Help` menu entry to generate some version information and copy
      that to the clipboard (see issue 562).
- Web Browser
    - Added the capability to enable the rendering of all web pages using a
      dark theme (PyQt/Qt >= 6.7.0).

### Version 24.5
- bug fixes
- General
    - Changed code from using `QFileSystemWatcher` to our own implementation
      (`EricFileSystemWatcher`) based on the `watchdog` Python package in order
      to get more fine grained control over the reported changes.
- Editor
    - Added the capability to reload the current editor via its context menu or
      the main `File` menu (see issue 556).
    - Added basic support for Jenkins pipeline files (and Groovy source files)
      (see issue 558).
- Editor Outline
    - Improved the navigation capability by respecting the column offset when
      placing the cursor of the editor (see issue 554).
- File Browser
    - Improved the navigation capability by respecting the column offset when
      placing the cursor of the editor (see issue 554).
- Project Browser
    - Improved the navigation capability by respecting the column offset when
      placing the cursor of the editor (see issue 554).
- Symbols Viewer
    - Completed the list of selectable code blocks.

### Version 24.4
- bug fixes
- Code Style Checker
    - Updated these checkers.
        - Security to `bandit` v1.7.8
        - Miscellaneous to `flake8-bugbear` v24.2.6
        - Logging to `flake8-logging` v1.5.0
- MicroPython
    - Updated the list of known CircuitPython boards.
    - Updated the list of known UF2 capable boards.
- pip Interface
    - Added the capability to install packages given in the `project.dependencies`
      section of a `pyproject.toml` file.
- Project
    - Added an action to the `Other Tools` menu to clear the byte code caches
      of the project.
- Shell
    - Added a context menu action to open an editor for a file at a line of an
      exception shown in the console window.
- Snapshot
    - Disabled the snapshot functionality for Wayland based desktops.
- Third Party Packages
    - Upgraded `pip-licenses` to version 4.3.4.

### Version 24.3
- bug fixes
- General
    - Removed support for the deprecated eric-ide specific XML file formats.
    - Removed the Oxygen based icons.

### Version 24.2.1
- bug fixes

### Version 24.2
**Important Note:** Before upgrading to this release, all plug-ins installed
via the plug-in repository must be at the most recent release in order to
prevent failures of some plug-ins.

- bug fixes
- Code Style Checker
    - Updated these checkers to support more cases.
        - Miscellaneous
        - Security
- Editor
    - Added an Edit menu entry tp convert tabs to spaces manually.
    - Added the capability to show local variables in the outline view.
    - Added code to show the indicator margin messages when the mouse hovers
      over a syntax error or warning indicator.
- File Browser
    - Added the capability to show local variables of functions and methods.
- Find In Files
    - Changed the filter entry to a filter selector with associated edit
      capability to define a list of filter entries.
- Log Viewer
    - Added code to show an indicator for the log viewer icon, if new messages
      were added and the "Autoshow" option is deactivated.
- MicroPython
    - Added an entry to the file manager's local and device context menu to
      rename a file.
    - Added a standalone application of the built-in MicroPython interface (
      `eric7_mpy`).
    - Enhanced the MicroPython file manager widget.
- Plugin Repository
    - Added a label to show the number of selected entries.
- Project Browser
    - Added the capability to show local variables of functions and methods.
- Third Party packages
    - Upgraded `pyflakes` to version 3.2.0.
    - Upgraded `jquery.js` to version 3.7.1.

### Version 24.1
- bug fixes
- General
    - Changed debug logging to be directed to a debug log file `eric7_debug.txt` in
      the `.eric7` directory.
- Code Style Checker
    - Updated these checkers to support more cases.
        - Logging
        - Miscellaneous
        - Simplify
    - Extended the documentation style checker to check the tag sequence and the use
      of deprecated tags (eric doc style).
- Editor
    - Added the capability to comment/uncomment/toggle comment for languages
      that do not support single line comments (e.g. HTML uses `<!--` and
      `-->`.
    - Added the capability to search & replace strings containing escape codes
      (like `\n`).
    - Introduced a configurable timeout after which the quick search text occurrences
      are highlighted (if this function is activated).
- File Browser
    - Added context menu entries to show the directory path of an item in an
      external file manager.
- Find In Files
    - Added the capability to search & replace strings containing escape codes
      (like `\n`).
- Multiproject
    - Added the capability to indicate externally removed projects and actions
      to clear them out.
- Project Browser
    - Added context menu entries to show the directory path of an item in an
      external file manager.
    - Added an entry to the background context menu to show the project
      directory in an external file manager.
- Testing
    - Extended the testing dialog to allow filtering of the result list
      based on the result status.
    - Extended the testing dialog to allow to perform a discovery run only and
      just perform selected test cases of this list.
    - Extended the testing dialog to allow to perform the test with debugger
      support (only if the dialog was started from within eric IDE).
- Viewmanager
    - Added `Close Tabs to the Left` and `Close Tabs to the Right` context
      menu entries to the tabview view manager.
    - Added `Close Editors Above` and `Close Editors Below` context menu
      entries to the listspace view manager.
- Virtual Environments
    - Added the capability to search for unregistered Python interpreters in
      order to create an environment entry for those selected by the user.
- Third Party packages
    - Upgraded pip-licenses to version 4.3.3.
    - Upgraded pycodestyle to version 2.11.1.

### Version 23.12
- bug fixes
- General
    - Improved platform support for FreeBSD.
- Debugger
    - Added a configuration option to select whether call trace optimization
      shall be enabled (this requires no function/method definition on the
      first line of a module).
    - Improved the configuration for remote debugging (global and project
      specific).
    - Changed the Python debugger code such, that unhandled exceptions are
      reported always and handled exception only, if the specifically
      requested in the `Start Debugging` dialog.
- Diff Dialog
    - Extended the functionality to accept two files to be diffed via the
      command line.
- Editor
    - Changed the `Auto Save` interval to be in seconds instead of minutes.
      __Note__: The `Auto Save` interval has to be reconfigured!
    - Added the capability to save a modified file automatically when the
      editor looses the focus.
    - Added a button to format underline text of HTML documents.
- Icons
    - Added a configuration option to override the style dependent icon size
      of the tool bars.
- Plugin Repository Dialog
    - Introduced categories to improve the presentation of the list of available
      plugins.
- Syntax Checker
    - Added code to show some per file and overall statistics of the check.
    - Re-introduced the JavaScript syntax checker. This time it is based on
      the `esprima` package.

### Version 23.11
- bug fixes
- General
    - Added the capability to select list entries with a configurable action
      (system default, double click, single click) (see `Interface => Interface`
      configuration page)
- Editor
    - Enhanced the print capability with the configuration of the print
      color mode (e.g. to print an editor with a dark background).
- Project Viewer
    - Added the context menu action "New source file..." to give a more concise
      way to create a new source file.

### Version 23.10
- bug fixes
- General
    - Made the code compatible with Python 3.12.
- Editor
    - Added a typing completer for TOML files.
    - Enhanced the existing completers slightly.
    - Enhanced the 'Search & Replace' widget to allow a mode switching using
      a mode switch button and keyboard shortcuts (see issue 511)
- Mercurial Interface
    - Added the capability to select the branches to be shown to the Log Browser
      window.
- MicroPython
    - Updated the list of known CircuitPython boards.
- pip Interface
    - Added capability to disable display of vulnerability data (e.g. if system
      does not support HTTPS protocol).
- Shell
    - Added some more special commands (% commands). Type `%help` to get a dialog
      listing these commands.
- Syntax Checker
    - Added code to the Python syntax checker to report Python Warnings.
- Third Party packages
    - Upgraded eradicate to version 2.3.0.
    - Upgraded pip-licenses to version 4.3.2.

### Version 23.9
- bug fixes
- MicroPython
    - Added support to set the host name of the device (WiFi and Ethernet).
    - Added support to set the WiFi country code (where supported by the device
      and the installed firmware).
- Project
    - Added capability to configure the project sources directory (e.g. if the
      project uses the 'src' directory layout schema).
- Third Party packages
    - Upgraded pyflakes to version 3.1.0.
    - Upgraded pycodestyle to version 2.11.0.

### Version 23.8
- bug fixes
- General
    - Removed support for Python 3.7 because that is EOL.
- Code Style Checker
    - Added these checkers to support more case.
        - use of sync functions in async functions
- MicroPython
    - Updated the list of known CircuitPython boards.
    - Updated the list of known UF2 capable boards.
- pip Interface
    - Added the capability to repair all dependencies with one button click.
- Shell Window
    - Added more pages to the Shell window configuration dialog.

### Version 23.7
- bug fixes
- Code Style Checker
    - Added these checkers to support more case.
        - property decorator usage
        - PEP-604 style union type annotations
        - deprecated 'typing' symbols (PEP 585)
- MicroPython
    - Added support for Bluetooth for RP2040 based boards (e.g. Pi Pico W).
- pip Interface
    - Added a standalone application for Python package management with `pip`.

### Version 23.6
- bug fixes
- Code Style Checker
    - Updated these checkers to support more cases.
        - Annotations
        - Miscellaneous
        - Name Order
        - Simplify
    - Added these checkers to support more case.
        - unused arguments
        - unused global variables
- MicroPython
    - Added support of th WebREPL device interface available on some boards with
      builtin network capability.
    - Added the capability to enable/disable the WebREPL via the WiFi menu.
- Third Party packages
    - Upgraded pipdeptree to version 2.7.1.
    - Upgraded pip-licenses to version 4.3.1.

### Version 23.5
- bug fixes
- JavaScript Support
    - Removed JavaScript functionality depending on the `jasy` package because it
      has not been maintained for years.
- MicroPython
    - Added support for STLink based devices.
    - Added the capability to select the device path manually in case it could not
      be detected (e.g. because the device does not have a volume name).
    - Added the capability to install the `mpy-cross` compiler from the MicroPython
      page of the configuration dialog.
    - Added a package installer for devices lacking network connectivity and the `mip`
      package manager.
- Plugin Repository
    - Added the capability to enforce the download of plugin packages using the
      `http://` protocol (in case of missing/non-functional system `SSL` libraries).
- Translator
    - Added support for the LibreTranslate translator (see
      https://github.com/LibreTranslate/LibreTranslate).
- Web Browser
    - Added the capability to enforce the download of spell check dictionaries using
      the `http://` protocol (in case of missing/non-functional system `SSL` libraries).

### Version 23.4.2
- bug fixes

### Version 23.4.1
- bug fixes

### Version 23.4
- bug fixes
- Editor
    - Added capability to highlight the area used by a text search (if it is not the
      whole document).
- MicroPython
    - Updated the list of known CircuitPython boards.
    - Updated the list of known UF2 capable boards.
    - Added functionality to search for known boot volumes in the UF2 flash dialog.
    - Added functionality to install packages using `mip` or `upip`.
    - Added support for WiFi enabled boards.
    - Added support for Bluetooth enabled boards.
    - Added support for Ethernet enabled boards.
    - Added support for synchronizing the board time via NTP for network enabled
      boards.
    - Added a dialog to enter the parameters to convert a .hex or .bin firmware
      file to UF2.
- Mini Editor
    - Added capability to highlight the area used by a text search (if it is not the
      whole document).
- Syntax Checker
    - Added the capability to define names to be treated as builtin names by the
      `pyflakes` checker globally (see configuration dialog `Editor => Code Checkers`
      page and on a per project basis (see `Project-Tools => Check => Syntax`).
- Third Party packages
    - Upgraded eradicate to version 2.2.0.
    - Upgraded pipdeptree to version 2.5.2.
    - Upgraded pip-licenses to version 4.1.0.

### Version 23.3
- bug fixes
- MicroPython
    - Updated the list of known CircuitPython boards.
    - Updated the list of known UF2 capable boards.
    - Some smaller enhancements for CircuitPython devices.
    - Added functionality to update modules of CircuitPython devices with `circup`
      (adapted for use within eric-ide).
    - Added functionality to show the installed firmware version and the version
      available on Github (for all boards except 'Calliope mini').
    - Added support for Teensy 4.0 and 4.1 devices with MicroPython.
    - Extended the file manager to be able to load device files into an editor and
      save them back to the device.
- PDF Viewer
    - Added a tool based on `QtPdf` and `QtPdfWidgets` to show the contents of PDF
      files.

### Version 23.2
- bug fixes
- Human Machine Interfaces
    - Changed code to use the default tab bar icon size.
- Debug Client - Python
    - Removed the internal copy of the 'coverage' package and made it a dependency.
- pip Interface
    - Added code to show the full text of security advisories in the package details
      dialog.
    - Added a tab to show the defined project URLs to the package details dialog.
    - Changed the package details dialog to show just those tabs, that contain some
      data.
- Help Viewer
    - Added a configuration option to disable the search for new QtHelp documents
      on startup.
- Web Browser
    - Updated the included 'jquery.js' and 'jquery-ui.js' needed by the Speeddial page
      and adapted this page to the new/changed functions.

### Version 23.1.1
- bug fixes

### Version 23.1
- bug fixes
- Class Browsers
    - Removed the IDL and Protobuf class browsers to include them in their respective
      plugin.
- Code Formatting
    - Added an option to configure the 'known first party' packages to the isort
      configuration dialog.
- Editor
    - Changed the handling of files whose type cannot be determined by the Python
      mimetypes module to check against a list of known text file patterns and
      ultimately asking the user, if the file in question is a text file (see
      `Mimetypes` configuration page).
    - Added a configuration option to disable the source navigator (selector boxes above
      the editor or code outline right of the editor). This is useful e.g. on very small
      screens.
    - Added support for multiple cursor paste.
- Find In Files
    - Added context menu entries in Replace mode to select/deselect all entries
      (e.g. useful for checking big replacement lists for validity).
- MicroPython
    - Updated the list of known CircuitPython boards.
    - Updated the list of known UF2 capable boards.
- Project
    - Extended the list of default file type associations.
    - Added the capability to edit the file type associations from within the
      project properties dialog.
- Project Viewer
    - Removed the CORBA and Protobuf viewers to make them available as plugins.
    - Added a `Collapse all files` entry to the Project Sources viewer.
- Version Control Systems - git
    - Changed git interface code to work with `git worktrees`.
    - Added a dialog to manage worktrees ( `git worktree` commands).
- Third Party packages
    - Upgraded pipdeptree to version 2.3.3.
    - Upgraded pip-licenses to version 4.0.2.
    - Upgraded pycodestyle to version 2.10.0.
    - Upgraded pyflakes to version 3.0.1.

### Version 22.12
- bug fixes
- Code Formatting
    - added an interface to resort the import statements of Python source files with
      the 'isort' utility
- Code Style Checker
    - added a few imports style options and added a sorting function iaw. the 'isort'
      utility
- CycloneDX Interface
    - addad capability to generate readable (prettified) output
- Debugger
    - increased the configuration possibilities for the network interface the debug
      server listens on
    - added the capability to configure the debug server of the IDE to listen at a
      fixed network port (default 35000)
    - added a stack frame selector to the global variables viewer (synchronized with
      the one of the local variables viewer)
- MicroPython
    - introduced a configuration option to enable manual selection of devices
      (e.g. for unknown devices or inside the Linux container of ChromeOS)
- Previewers
    - added a button to copy the contents of the HTML previewer to the clipboard
- Project
    - added capability to reload the current project
- Qt Tools
    - added a configuration option for the path of the 'qhelpgenerator' tool
      (it is installed differently by various Linux distributions)
- Web Browser
    - added bookmark importer entries for
        - Falkon
        - Microsoft Edge
        - Opera (Chromium based)
        - Vivaldi

### Version 22.11.1
- bug fixes

### Version 22.11
- bug fixes
- Debugger
    - added the capability to apply the current selection of the `Variable Types Filter`
      to see its effect
    - added the capability to add a positive (`Show Only`) or negative (`Don't Show`)
      variables filter to the global and local variables viewers
- Editor
    - added a configuration option to reject the loading of a file that exceeds the
      configured size
    - opening a file that is not a text file will be rejected
- Git Interface
    - added support for `git blame --ignore-revs-file` including an action to create
      such a skip list file
- Mercurial Interface
    - added support for `hg annotate --skip` including an action to create a file
      for the commit IDs to be skipped (one per line)
- Project
    - refined the embedded environment handling
    - added a topic to the project properties to define the sources start path within
      the project ('Translations Properties Dialog')
- Scripts
    - renamed 'eric7.py' to 'eric7_ide.py' in order to remove the ambiguity between the
      main script and the package
- Styles and Themes
    - added a style sheet for the dark gray theme
- Translator
    - added the command line switch `--no-multimedia` to forcefully disable the
      pronounce function of the translator widget (in case Qt aborts the application
      start process)
- Various
    - changed the Gmail interface to use the Google API packages for authentication
      (OAuth2) and sending of emails
- Virtual Environments
    - added the capability to enter a descriptive text for a virtual environment
- Third Party packages
    - upgraded coverage to version 6.5.0
    - upgraded pycodestyle to version 2.9.1
    - upgraded pyflakes to version 2.5.0

### Version 22.10
- bug fixes
- API files
    - added API files for the Adafruit CircuitPython Library Bundle
    - updated the CircuitPython API file
- Code Formatting
    - added a Project menu entry to just configure the formatting parameters
    - added the capability to format the source code after a diff or check
      run from within the results dialog
- Code Style Checker
    - added some more security related checks
    - extended the list of miscellaneous checks
- pip Interface
    - changed the pip licenses dialog to show the count of each individual license
- Project
    - added capability to use a virtual Python environment named `.venv` embedded
      within the project directory
    - added a configuration option to save the project automatically whenever it changes
- Testing
    - extended the testing dialog to allow test case filtering on markers (pytest only)
    - extended the testing dialog to allow test case filtering by a list of test name
      patterns (unittest) or test name expression (pytest)
- Translator
    - added support for 'Ukrainian' to the DeepL translator interface
- install scripts
    - modified install.py script to differentiate between optional and required
      dependencies
    - modified the install script such, that the qt6-applications package is only
      installed upon request (--with-tools)
    - extended the install-dependencies.py script to differentiate between optional and
      required dependencies. Invoke it with
      `python3 install-dependencies.py --all | --optional | --required`.

### Version 22.9
- bug fixes
- Code Style Checker
    - extended the Naming style checker to be more PEP8 compliant
    - updated imports checker to support banned module patterns
    - updated the annotations checker to support more cases
    - updated the simplifications checker to support more cases
- Debugger
    - added capability to suppress reporting of unhandled exceptions
- Editor
    - extended the Pygments based lexer to support the various comment variants
- Interface
    - added capability to expand or shrink the sidebar by clicking on the empty
      part of the icon bar
- MicroPython
    - added capability to connect to devices for which only the serial port name
      is available

### Version 22.8
- bug fixes
- API Generator
    - added capability to configure a start directory for the API generation
      process
- Code Documentation Generator
    - added capability to configure a start directory for the documentation
      generation process
- Code Formatting
    - added an interface to reformat Python source code with the 'Black' utility
- Eric Widgets
    - extended EricPathPicker to offer a pathlib.Path based interface
    - extended EricFileDialog to offer a pathlib.Path based interface
    - extended the EricFileDialog Wizard to create the pathlib.Path based methods
- MicroPython
    - updated the list of known CircuitPython boards
    - updated the list of known UF2 capable boards
- pip Interface
    - included a copy of pipdeptree and patched it to work with Python 3.11+
    - added capability to repair dependency issues
    - added capability to generate text for a 'constraints.txt' file
- setup Wizard
    - added support for `project_urls`
    - added support for `entry_points`
    - added a variant to create a `setup.cfg` file
    - added a variant to create a `pyproject.toml` file
- Third Party packages
    - upgraded coverage to version 6.4.2
    - upgraded eradicate to version 2.1.0

### Version 22.7
- bug fixes
- Code Style Checker
    - introduced an additional documentation style type for eric and blacked
      code (i.e. code formatted by the 'Black' tool)
- CycloneDX Interface
    - added capability to create a Software Bill of Materials (SBOM) file in
      CycloneDX format
- pip Interface
    - added SBOM capability
- Project
    - added SBOM capability
    - added License to project properties
- Styles and Themes
    - added a style and theme with a dark gray background
- Translator
    - changed DeepL support to the v2 API and added support for the Free API
      next to the Pro API
    - removed the interface to Glosbe as they don't provide an API anymore
    - removed the interface to PROMT as they don't provide a free API anymore
    - upgraded the interfaces to the Google V2 and Microsoft translators
- Virtual Environments
    - added the capability to upgrade a virtual environment

### Version 22.6
- bug fixes
- Dataview Coverage
    - added support to write coverage reports as HTML, JSON or LCOV files
    - removed the support for writing annotated sources
      (deprecated in coverage.py)
- Mercurial Interface
    - added configuration option to override the automatic search for the hg
      executable
- MicroPython
    - updated the list of known CircuitPython boards
    - updated the list of known UF2 capable boards
- pip Interface
    - added a filter to the package licenses dialog
- Syntax Checker
    - changed the TOML syntax checker to use 'tomlkit' because 'toml' is no
      longer maintained
- Testing
    - reworked the former unittest interface to allow to support testing
      frameworks other than "unittest"
    - implemented support for the "unittest" and "pytest" frameworks
- Wizards
    - extended the QInputDialog wizard to support the `getMultiLineText()`
      function
- Third Party packages
    - upgraded pip-licenses to version 3.5.4
    - upgraded coverage to version 6.4.0

### Version 22.5
- bug fixes
- General
    - added configuration options to disable the embedded `Find/Replace In
      Files` and `Find File` tools and use dialog based variants instead
- Mercurial Interface
    - added capability to enter a revset expression when defining a revision
      to operate on
- pip Interface
    - added the capability to save the licenses overview as a CSV file

### Version 22.4
- bug fixes
- General
    - added capability to upgrade PyQt packages eric depends on from within eric
    - added capability to upgrade eric from within eric
- pip Interface
    - added a vulnerability check for installed packages based on "Safety DB"
    - added a widget to show a package dependency tree
    - added a button to search for more packages (i.e. one more page of results)
- Third Party packages
    - upgraded coverage to version 6.3.2
    - upgraded mccabe to version 0.7.0

### Version 22.3
- bug fixes
- General
    - performance improvements
    - added a `__main__.py` script to allow starting eric7 with
      `python3 -m eric7`
- MicroPython
    - enhanced support for ESP32 devices
    - updated the list of known UF2 capable boards

### Version 22.2
- bug fixes
- General
    - dropped support for Python 3.6 because that is end-of-life
- File Browser
    - added capability to open SVG files in the text editor
- Help Viewer
    - added bookmarks to the internal help viewer
- MicroPython
    - updated the list of known CircuitPython boards
    - updated the list of known UF2 capable boards
    - added support for ESP32-C3, ESP32-S2 and ESP32-S3 chips
    - added a dialog to show information for a connected board
- Project Browser
    - added capability to open SVG files in the text editor to the Project
      Others Browser
- Styles and Themes
    - added a dark blueish style (QSS and Highlighters) and an associated theme
      (`dark_blue.ethj` and `dark_blue_with_stylesheet.ethj`)
- Third Party packages
    - upgraded coverage to version 6.2.0

### Version 22.1.1
- bug fix

### Version 22.1
- bug fixes
- Code Style Checker
    - added a checker for various import statement topics
- Color Themes
    - added capability to import and export ALL colors
- Mini Editor
    - added configuration capability
- QSS Previewer
    - added disabled widgets in order to show their colors as well
- Styles and Themes
    - added a dark greenish style (QSS and Highlighters) and an associated theme
      (`dark_green.ethj` and `dark_green_with_stylesheet.ethj`)

### Version 21.12
- bug fixes
- first release of eric7 (i.e. the PyQt6 port of eric6)
- General
    - rearranged the interface and modernized the sidebars layout
    - integrated some dialogs into the sidebars
- Debugger
    - added code to remember the list of recently used breakpoint conditions
      in the editor and the breakpoint viewer
    - added code to enter the script to be run/debugged/... in the start dialog
- Editor
    - added the capability to suppress syntax highlighting by associating
      the file type 'Text'
    - added code to move a breakpoint to a line actually creating some byte code
      (Python only)
    - added mouse button capability to perform undo/redo actions (Extra
      Buttons 1 and 2)
    - added support for 'multi cursor editing' (additional cursors with
      Meta+Alt+Left Click, Esc to end it)
- Find In Files
    - integrated the dialog into the right sidebar
- Help Viewer
    - added an internal help viewer based on QTextBrowser or QWebEngine
- Jedi
    - integrated the Assistant Jedi plugin as a fixed part of eric
    - added code to jump to references when clicked on a definition
    - added support for mouse hover help
    - added support for simple refactorings to the editor context menu
- Plugin Repository
    - added an integrated plugin repository viewer (right side)
- Plugin Uninstall Dialog
    - added capability to uninstall several plugins with one invocation of the
      dialog
- Project
    - added a 'Start' context sub menu to the project sources browser
- Shell
    - added capability to save the contents of the shell window into a file
- Unit Test
    - added capability to remember the most recently used test data
- Viewmanager
    - added a 'Start' sub menu to the tabview and listspace view managers
      context menu
- Virtual Environments
    - integrated the Virtual Environments Manager window into the right side bar
    - added a standalone variant of the Virtual Environments Manager
- Third Party packages
    - upgraded coverage to version 6.1.2
    - upgraded pycodestyle to version 2.8.0
    - upgraded mccabe to version 0.6.1
    - upgraded pyflakes to version 2.4.0
