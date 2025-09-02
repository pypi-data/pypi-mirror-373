# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(pathlib part).
"""

from PyQt6.QtCore import QCoreApplication

_pathlibMessages = {
    "P-101": QCoreApplication.translate(
        "PathlibChecker",
        "os.chmod('foo', 0o444) should be replaced by foo_path.chmod(0o444)",
    ),
    "P-102": QCoreApplication.translate(
        "PathlibChecker", "os.mkdir('foo') should be replaced by foo_path.mkdir()"
    ),
    "P-103": QCoreApplication.translate(
        "PathlibChecker",
        "os.makedirs('foo/bar') should be replaced by bar_path.mkdir(parents=True)",
    ),
    "P-104": QCoreApplication.translate(
        "PathlibChecker",
        "os.rename('foo', 'bar') should be replaced by foo_path.rename(Path('bar'))",
    ),
    "P-105": QCoreApplication.translate(
        "PathlibChecker",
        "os.replace('foo', 'bar') should be replaced by "
        "foo_path.replace(Path('bar'))",
    ),
    "P-106": QCoreApplication.translate(
        "PathlibChecker", "os.rmdir('foo') should be replaced by foo_path.rmdir()"
    ),
    "P-107": QCoreApplication.translate(
        "PathlibChecker", "os.remove('foo') should be replaced by foo_path.unlink()"
    ),
    "P-108": QCoreApplication.translate(
        "PathlibChecker", "os.unlink('foo'') should be replaced by foo_path.unlink()"
    ),
    "P-109": QCoreApplication.translate(
        "PathlibChecker", "os.getcwd() should be replaced by Path.cwd()"
    ),
    "P-110": QCoreApplication.translate(
        "PathlibChecker", "os.readlink('foo') should be replaced by foo_path.readlink()"
    ),
    "P-111": QCoreApplication.translate(
        "PathlibChecker",
        "os.stat('foo') should be replaced by foo_path.stat() or "
        "foo_path.owner() or foo_path.group()",
    ),
    "P-112": QCoreApplication.translate(
        "PathlibChecker",
        "os.listdir(path='foo') should be replaced by foo_path.iterdir()",
    ),
    "P-113": QCoreApplication.translate(
        "PathlibChecker",
        "os.link('bar', 'foo') should be replaced by foo_path.hardlink_to('bar')",
    ),
    "P-114": QCoreApplication.translate(
        "PathlibChecker",
        "os.symlink('bar', 'foo') should be replaced by foo_path.symlink_to('bar')",
    ),
    "P-201": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.abspath('foo') should be replaced by foo_path.resolve()",
    ),
    "P-202": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.exists('foo') should be replaced by foo_path.exists()",
    ),
    "P-203": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.expanduser('~/foo') should be replaced by foo_path.expanduser()",
    ),
    "P-204": QCoreApplication.translate(
        "PathlibChecker", "os.path.isdir('foo') should be replaced by foo_path.is_dir()"
    ),
    "P-205": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.isfile('foo') should be replaced by foo_path.is_file()",
    ),
    "P-206": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.islink('foo') should be replaced by foo_path.is_symlink()",
    ),
    "P-207": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.isabs('foo') should be replaced by foo_path.is_absolute()",
    ),
    "P-208": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.join('foo', 'bar') should be replaced by foo_path / 'bar'",
    ),
    "P-209": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.basename('foo/bar') should be replaced by bar_path.name",
    ),
    "P-210": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.dirname('foo/bar') should be replaced by bar_path.parent",
    ),
    "P-211": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.samefile('foo', 'bar') should be replaced by "
        "foo_path.samefile(bar_path)",
    ),
    "P-212": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.splitext('foo.bar') should be replaced by foo_path.stem and"
        " foo_path.suffix",
    ),
    "P-213": QCoreApplication.translate(
        "PathlibChecker",
        "os.path.relpath('/bar/foo', start='bar') should be replaced by "
        "foo_path.relative_to('/bar')",
    ),
    "P-301": QCoreApplication.translate(
        "PathlibChecker", "open('foo') should be replaced by Path('foo').open()"
    ),
    "P-401": QCoreApplication.translate(
        "PathlibChecker", "py.path.local is in maintenance mode, use pathlib instead"
    ),
}
