# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(security part).
"""

from PyQt6.QtCore import QCoreApplication

_securityMessages = {
    # assert used
    "S-101": QCoreApplication.translate(
        "Security",
        "Use of 'assert' detected. The enclosed code will be removed when"
        " compiling to optimised byte code.",
    ),
    # exec used
    "S-102": QCoreApplication.translate("Security", "Use of 'exec' detected."),
    # bad file permissions
    "S-103": QCoreApplication.translate(
        "Security", "'chmod' setting a permissive mask {0} on file ({1})."
    ),
    # bind to all interfaces
    "S-104": QCoreApplication.translate(
        "Security", "Possible binding to all interfaces."
    ),
    # hardcoded passwords
    "S-105": QCoreApplication.translate(
        "Security", "Possible hardcoded password: '{0}'"
    ),
    "S-106": QCoreApplication.translate(
        "Security", "Possible hardcoded password: '{0}'"
    ),
    "S-107": QCoreApplication.translate(
        "Security", "Possible hardcoded password: '{0}'"
    ),
    # hardcoded tmp directory
    "S-108": QCoreApplication.translate(
        "Security", "Probable insecure usage of temp file/directory."
    ),
    # try-except and contextlib.suppress
    "S-110": QCoreApplication.translate("Security", "Try, Except, Pass detected."),
    "S-112": QCoreApplication.translate("Security", "Try, Except, Continue detected."),
    "S-113": QCoreApplication.translate(
        "Security", "'contextlib.suppress()' detected."
    ),
    # request without timeout
    "S-114.1": QCoreApplication.translate("Security", "Call to {0} without timeout."),
    "S-114.2": QCoreApplication.translate(
        "Security",
        "Call to {0} with timeout set to None.",
    ),
    # flask app
    "S-201": QCoreApplication.translate(
        "Security",
        "A Flask app appears to be run with debug=True, which exposes the"
        " Werkzeug debugger and allows the execution of arbitrary code.",
    ),
    # tarfile.extractall
    "S-202.1": QCoreApplication.translate(
        "Security",
        "Usage of 'tarfile.extractall(members=function(tarfile))'. "
        "Make sure your function properly discards dangerous members ({0}).",
    ),
    "S-202.2": QCoreApplication.translate(
        "Security",
        "Found 'tarfile.extractall(members=?)' but couldn't identify the type of"
        " members. Check if the members were properly validated ({0}).",
    ),
    "S-202.3": QCoreApplication.translate(
        "Security",
        "'tarfile.extractall()' used without any validation. Please check and"
        " discard dangerous members.",
    ),
    # prohibited calls
    "S-301": QCoreApplication.translate(
        "Security",
        "Pickle and modules that wrap it can be unsafe when used to "
        "deserialize untrusted data, possible security issue.",
    ),
    "S-302": QCoreApplication.translate(
        "Security", "Deserialization with the marshal module is possibly dangerous."
    ),
    "S-303": QCoreApplication.translate(
        "Security", "Use of insecure MD2, MD4, MD5, or SHA1 hash function."
    ),
    "S-304": QCoreApplication.translate(
        "Security",
        "Use of insecure cipher '{0}'. Replace with a known secure cipher"
        " such as AES.",
    ),
    "S-305": QCoreApplication.translate(
        "Security", "Use of insecure cipher mode '{0}'."
    ),
    "S-306": QCoreApplication.translate(
        "Security", "Use of insecure and deprecated function (mktemp)."
    ),
    "S-307": QCoreApplication.translate(
        "Security",
        "Use of possibly insecure function - consider using safer ast.literal_eval.",
    ),
    "S-308": QCoreApplication.translate(
        "Security",
        "Use of mark_safe() may expose cross-site scripting vulnerabilities"
        " and should be reviewed.",
    ),
    "S-310": QCoreApplication.translate(
        "Security",
        "Audit url open for permitted schemes. Allowing use of file:/ or"
        " custom schemes is often unexpected.",
    ),
    "S-311": QCoreApplication.translate(
        "Security",
        "Standard pseudo-random generators are not suitable for"
        " security/cryptographic purposes.",
    ),
    "S-312": QCoreApplication.translate(
        "Security",
        "Telnet-related functions are being called. Telnet is considered"
        " insecure. Use SSH or some other encrypted protocol.",
    ),
    "S-313": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable to"
        " XML attacks. Replace '{0}' with its defusedxml equivalent function"
        " or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-314": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable to"
        " XML attacks. Replace '{0}' with its defusedxml equivalent function"
        " or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-315": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable to"
        " XML attacks. Replace '{0}' with its defusedxml equivalent function"
        " or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-316": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable to"
        " XML attacks. Replace '{0}' with its defusedxml equivalent function"
        " or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-317": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable to"
        " XML attacks. Replace '{0}' with its defusedxml equivalent function"
        " or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-318": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable to"
        " XML attacks. Replace '{0}' with its defusedxml equivalent function"
        " or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-319": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable to"
        " XML attacks. Replace '{0}' with its defusedxml equivalent function"
        " or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-321": QCoreApplication.translate(
        "Security",
        "FTP-related functions are being called. FTP is considered insecure."
        " Use SSH/SFTP/SCP or some other encrypted protocol.",
    ),
    "S-323": QCoreApplication.translate(
        "Security",
        "By default, Python will create a secure, verified SSL context for"
        " use in such classes as HTTPSConnection. However, it still allows"
        " using an insecure context via the _create_unverified_context that"
        " reverts to the previous behavior that does not validate"
        " certificates or perform hostname checks.",
    ),
    # hashlib functions
    "S-331": QCoreApplication.translate(
        "Security", "Use of insecure {0} hash function."
    ),
    "S-332": QCoreApplication.translate(
        "Security",
        "Use of insecure {0} hash for security. Consider 'usedforsecurity=False'.",
    ),
    # prohibited imports
    "S-401": QCoreApplication.translate(
        "Security",
        "A telnet-related module is being imported.  Telnet is considered"
        " insecure. Use SSH or some other encrypted protocol.",
    ),
    "S-402": QCoreApplication.translate(
        "Security",
        "A FTP-related module is being imported.  FTP is considered"
        " insecure. Use SSH/SFTP/SCP or some other encrypted protocol.",
    ),
    "S-403": QCoreApplication.translate(
        "Security",
        "Consider possible security implications associated with the '{0}' module.",
    ),
    "S-404": QCoreApplication.translate(
        "Security",
        "Consider possible security implications associated with the '{0}' module.",
    ),
    "S-405": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable"
        " to XML attacks. Replace '{0}' with the equivalent defusedxml"
        " package, or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-406": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable"
        " to XML attacks. Replace '{0}' with the equivalent defusedxml"
        " package, or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-407": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable"
        " to XML attacks. Replace '{0}' with the equivalent defusedxml"
        " package, or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-408": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable"
        " to XML attacks. Replace '{0}' with the equivalent defusedxml"
        " package, or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-409": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable"
        " to XML attacks. Replace '{0}' with the equivalent defusedxml"
        " package, or make sure defusedxml.defuse_stdlib() is called.",
    ),
    "S-411": QCoreApplication.translate(
        "Security",
        "Using '{0}' to parse untrusted XML data is known to be vulnerable"
        " to XML attacks. Use defusedxml.xmlrpc.monkey_patch() function to"
        " monkey-patch xmlrpclib and mitigate XML vulnerabilities.",
    ),
    "S-412": QCoreApplication.translate(
        "Security",
        "Consider possible security implications associated with '{0}' module.",
    ),
    "S-413": QCoreApplication.translate(
        "Security",
        "The pyCrypto library and its module '{0}' are no longer actively"
        " maintained and have been deprecated. Consider using"
        " pyca/cryptography library.",
    ),
    "S-414": QCoreApplication.translate(
        "Security",
        "An IPMI-related module is being imported. IPMI is considered "
        "insecure. Use an encrypted protocol.",
    ),
    # insecure certificate usage
    "S-501": QCoreApplication.translate(
        "Security",
        "'requests' call with verify=False disabling SSL certificate checks,"
        " security issue.",
    ),
    # insecure SSL/TLS protocol version
    "S-502.1": QCoreApplication.translate(
        "Security",
        "'ssl.wrap_socket' call with insecure SSL/TLS protocol version"
        " identified, security issue.",
    ),
    "S-502.2": QCoreApplication.translate(
        "Security",
        "'SSL.Context' call with insecure SSL/TLS protocol version identified,"
        " security issue.",
    ),
    "S-502.3": QCoreApplication.translate(
        "Security",
        "Function call with insecure SSL/TLS protocol version identified,"
        " security issue.",
    ),
    "S-503": QCoreApplication.translate(
        "Security",
        "Function definition identified with insecure SSL/TLS protocol"
        " version by default, possible security issue.",
    ),
    "S-504": QCoreApplication.translate(
        "Security",
        "'ssl.wrap_socket' call with no SSL/TLS protocol version specified,"
        " the default 'SSLv23' could be insecure, possible security issue.",
    ),
    # weak cryptographic keys
    "S-505": QCoreApplication.translate(
        "Security", "{0} key sizes below {1:d} bits are considered breakable."
    ),
    # YAML load
    "S-506": QCoreApplication.translate(
        "Security",
        "Use of unsafe 'yaml.load()'. Allows instantiation of arbitrary"
        " objects. Consider 'yaml.safe_load()'.",
    ),
    # SSH host key verification
    "S-507": QCoreApplication.translate(
        "Security",
        "Paramiko call with policy set to automatically trust the unknown host key.",
    ),
    # insecure SNMP
    "S-508": QCoreApplication.translate(
        "Security",
        "The use of SNMPv1 and SNMPv2 is insecure. You should use SNMPv3 if possible.",
    ),
    "S-509": QCoreApplication.translate(
        "Security",
        "You should not use SNMPv3 without encryption. noAuthNoPriv & authNoPriv is"
        " insecure.",
    ),
    # Shell injection
    "S-601": QCoreApplication.translate(
        "Security",
        "Possible shell injection via 'Paramiko' call, check inputs are"
        " properly sanitized.",
    ),
    "S-602.L": QCoreApplication.translate(
        "Security",
        "'subprocess' call with shell=True seems safe, but may be changed"
        " in the future, consider rewriting without shell",
    ),
    "S-602.H": QCoreApplication.translate(
        "Security", "'subprocess' call with shell=True identified, security issue."
    ),
    "S-603": QCoreApplication.translate(
        "Security", "'subprocess' call - check for execution of untrusted input."
    ),
    "S-604": QCoreApplication.translate(
        "Security",
        "Function call with shell=True parameter identified, possible"
        " security issue.",
    ),
    "S-605.L": QCoreApplication.translate(
        "Security",
        "Starting a process with a shell: Seems safe, but may be changed in"
        " the future, consider rewriting without shell",
    ),
    "S-605.H": QCoreApplication.translate(
        "Security",
        "Starting a process with a shell, possible injection detected,"
        " security issue.",
    ),
    "S-606": QCoreApplication.translate(
        "Security", "Starting a process without a shell."
    ),
    "S-607": QCoreApplication.translate(
        "Security", "Starting a process with a partial executable path."
    ),
    # SQL injection
    "S-608": QCoreApplication.translate(
        "Security",
        "Possible SQL injection vector through string-based query construction.",
    ),
    # Wildcard injection
    "S-609": QCoreApplication.translate(
        "Security", "Possible wildcard injection in call: {0}"
    ),
    # Django SQL injection
    "S-610": QCoreApplication.translate(
        "Security", "Use of 'extra()' opens a potential SQL attack vector."
    ),
    "S-611": QCoreApplication.translate(
        "Security", "Use of 'RawSQL()' opens a potential SQL attack vector."
    ),
    # insecure logging.config.listen()
    "S-612": QCoreApplication.translate(
        "Security",
        "Use of insecure logging.config.listen() detected.",
    ),
    # Trojan Source
    "S-613": QCoreApplication.translate(
        "Security",
        "The Python source file contains bidirectional control characters ({0}).",
    ),
    # PyTorch unsafe load or save
    "S-614": QCoreApplication.translate("Security", "Use of unsafe PyTorch load."),
    # unsafe huggingface download
    "S-615": QCoreApplication.translate(
        "Security",
        "Unsafe Hugging Face Hub download without revision pinning in '{0}'.",
    ),
    # Jinja2 templates
    "S-701.1": QCoreApplication.translate(
        "Security",
        "Using jinja2 templates with 'autoescape=False' is dangerous and can"
        " lead to XSS. Use 'autoescape=True' or use the 'select_autoescape'"
        " function to mitigate XSS vulnerabilities.",
    ),
    "S-701.2": QCoreApplication.translate(
        "Security",
        "By default, jinja2 sets 'autoescape' to False. Consider using"
        " 'autoescape=True' or use the 'select_autoescape' function to"
        " mitigate XSS vulnerabilities.",
    ),
    # Mako templates
    "S-702": QCoreApplication.translate(
        "Security",
        "Mako templates allow HTML/JS rendering by default and are inherently"
        " open to XSS attacks. Ensure variables in all templates are properly"
        " sanitized via the 'n', 'h' or 'x' flags (depending on context). For"
        " example, to HTML escape the variable 'data' do ${{ data |h }}.",
    ),
    # Django XSS vulnerability
    "S-703": QCoreApplication.translate(
        "Security", "Potential XSS on 'mark_safe()' function."
    ),
    # Markupsafe XSS vulnerability
    "S-704": QCoreApplication.translate(
        "Security",
        "Potential XSS with '{0}' detected. Do not use '{1}' on untrusted data.",
    ),
    # hardcoded AWS passwords
    "S-801": QCoreApplication.translate(
        "Security", "Possible hardcoded AWS access key ID: {0}"
    ),
    "S-802": QCoreApplication.translate(
        "Security", "Possible hardcoded AWS secret access key: {0}"
    ),
}

_securityMessagesSampleArgs = {
    "S-103": ["0o777", "testfile.txt"],
    "S-105": ["password"],
    "S-106": ["password"],
    "S-107": ["password"],
    "S-114.1": ["requests"],
    "S-114.2": ["httpx"],
    "S-202.1": ["members_filter(tar)"],
    "S-202.2": ["tar"],
    "S-304": ["Crypto.Cipher.DES"],
    "S-305": ["cryptography.hazmat.primitives.ciphers.modes.ECB"],
    "S-313": ["xml.etree.cElementTree.parse"],
    "S-314": ["xml.etree.ElementTree.parse"],
    "S-315": ["xml.sax.expatreader.create_parser"],
    "S-316": ["xml.dom.expatbuilder.parse"],
    "S-317": ["xml.sax.parse"],
    "S-318": ["xml.dom.minidom.parse"],
    "S-319": ["xml.dom.pulldom.parse"],
    "S-331": ["MD5"],
    "S-403": ["pickle"],
    "S-404": ["subprocess"],
    "S-405": ["xml.etree.ElementTree"],
    "S-406": ["xml.sax"],
    "S-407": ["xml.dom.expatbuilder"],
    "S-408": ["xml.dom.minidom"],
    "S-409": ["xml.dom.pulldom"],
    "S-411": ["xmlrpclib"],
    "S-412": ["wsgiref.handlers.CGIHandler"],
    "S-413": ["Crypto.Cipher"],
    "S-505": ["RSA", 2048],
    "S-609": ["os.system"],
    "S-613": [repr("\u202e")],
    "S-704": ["markupsafe.Markup", "Markup"],
    "S-801": ["A1B2C3D4E5F6G7H8I9J0"],  # secok
    "S-802": ["aA1bB2cC3dD4/eE5fF6gG7+hH8iI9jJ0=kKlLM+="],  # secok
}
