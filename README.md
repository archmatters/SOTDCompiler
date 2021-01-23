# SOTDCompiler
r/Wetshaving SOTD scanner/compiler

Requires the 'praw' Reddit module for Python.

The program expects a praw.ini file with the client ID, secret, and user agent defined in a \[SOTDCompiler\] section.

Organization:

* main.py: the main scanner
* check.py: used to rescan saved data
* scanner.py: functions to walk comments and scan for SOTD information
* makers.py: soapmaker patterns
* scents.py: scent/product patterns
