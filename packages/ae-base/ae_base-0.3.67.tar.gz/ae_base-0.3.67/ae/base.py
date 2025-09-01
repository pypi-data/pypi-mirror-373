"""
basic constants, helper functions and context managers
======================================================

this module is pure python, has no external dependencies, and provides a comprehensive toolkit of base constants,
common helper functions, useful classes, and context managers for a wide variety of programming tasks.

.. note::
    on import, this module checks if it is running on the Android OS. if so, it will monkey patch the
    :mod:`shutil` module to ensure functions like ``copy`` and ``move`` work correctly. to prevent
    permission-related errors, this module should be one of the first imports in your Android app's main module.


string manipulation
-------------------

functions for converting, cleaning, normalizing, and formatting strings.

* :func:`camel_to_snake`: converts a string from CamelCase to snake_case.
* :func:`snake_to_camel`: converts a string from snake_case to CamelCase.
* :func:`norm_name`: normalizes a string to be a valid identifier (e.g., for variable-, method-, or file-names).
* :func:`norm_line_sep`: converts all line separator combinations (CRLF, CR) in a string to a single newline (LF).
* :func:`defuse`: converts special characters in string to Unicode alternatives, making it safe for use as
  a URL slug, path or filename.
* :func:`dedefuse`: reverses the operation of :func:`defuse`, restoring the original string.
* :func:`force_encoding`: ensures text is in a specific encoding without raising errors, replacing characters as needed.
* :func:`to_ascii`: converts a Unicode string into its closest ASCII representation by removing accents and diacritics.
* :func:`ascii_str`: encodes a Unicode string into a reversible 7-bit ASCII representation, useful for transport
  protocols like HTTP headers.
* :func:`str_ascii`: decodes a string created by :func:`ascii_str` back to its original Unicode form.
* :func:`format_given`: a replacement for `str.format_map` that formats a string but leaves placeholders intact if they
  are not found in the provided mapping.


system & environment
--------------------

inspect the operating system and manage environment variables.

.. hint::
    the :mod:`ae.core` portion is providing more OS-specific constants and helper functions, like e.g.
    :func:`~ae.core.start_app_service` and :func:`~ae.core.request_app_permissions`.

OS information
~~~~~~~~~~~~~~

* :data:`os_platform`: a string identifying the operating system (e.g., 'linux', 'win32', 'android', 'ios').
* :data:`os_device_id`: a string with the ID/name of the device.
* :func:`os_host_name`: determines the operating system's host/machine name.
* :func:`os_local_ip`: determines the local IP address of the machine.
* :func:`os_user_name`: determines the current logged-in user's name.
* :func:`sys_env_dict`: returns a dictionary containing key Python runtime environment values.
* :func:`sys_env_text`: compiles a formatted text block with system environment information, useful for logging.

environment variables & `.env` files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* :func:`env_str`: retrieves the string value of an OS environment variable, with an option to automatically convert the
  variable name to the conventional format.
* :func:`parse_dotenv`: parses a `.env` file and returns its key-value pairs as a dictionary.
* :func:`load_env_var_defaults`: recursively searches parent directories for `.env` files and loads any undeclared
  variables.
* :func:`load_dotenvs`: detects and loads all relevant `.env` files from the current working directory and optional
  also from the main module's path.


data structure utilities
------------------------

helpers for working with lists, dictionaries, and other data structures.

* :func:`evaluate_literal`: replacement for :func:`ast.literal_eval` that also interprets/recognizes unquoted strings
  as `str` type.
* :func:`duplicates`: returns a list of all duplicate items found in any type of iterable.
* :func:`deep_dict_update`: recursively updates a dictionary in-place with values from another dictionary.
* :func:`mask_secrets`: hides sensitive string values (e.g., passwords, API keys) in deeply nested data structures,
  useful for logging.


application & project helpers
-----------------------------

functions to aid in application setup, configuration, and build introspection.

* :func:`app_name_guess`: attempts to determine the name of the currently running application from its environment.
* :func:`build_config_variable_values`: reads variable values from a `buildozer.spec` file.
* :func:`instantiate_config_parser`: returns a `ConfigParser` instance pre-configured for case-sensitive keys and
  extended interpolation.
* :func:`project_main_file`: determines the absolute path to the main module file of a project package (where the
  `__version__` of the app|package is defined).
* :func:`main_file_paths_parts`: returns a tuple of possible main/version file path names combinations of any project.


modules and call stack inspection
---------------------------------

dynamically inspect modules, execution frames, and variables on the call stack.

* :func:`import_module`: dynamically imports a Python module from a path without adding it to `sys.modules`.
* :func:`module_attr`: dynamically gets a reference to a module or any attribute (variable, function, class) within it.
* :func:`module_file_path`: determines the absolute file path of the module from which it is called.
* :func:`module_name`: finds the name of the first module in the call stack that is not in a predefined skip list.
* :func:`stack_frames`: a generator that yields frames from the call stack, starting at a specified depth.
* :func:`stack_var`: finds the value of a specific variable by searching up the call stack.
* :func:`stack_vars`: returns the global and local variables from a specific frame in the call stack.
* :func:`full_stack_trace`: generates a complete, detailed string representation of an exception's stack trace.

.. hint::
    the :class:`~ae.core.AppBase` class uses these helper functions to determine the
    :attr:`version <ae.core.AppBase.app_version>` and :attr:`title <ae.core.AppBase.app_title>` of an application,
    if these values are not specified in the instance initializer.


networking utilities
--------------------

* :func:`url_failure`: determines if and why a HTTP|FTP target is unavailable.
* :func:`mask_url`: hides or replaces the password/token portion of a URL for safe logging.


general utilities & helpers
---------------------------

a collection of miscellaneous mathematical, date/time, and other standalone helper functions.

mathematical
~~~~~~~~~~~~

* :func:`sign`: returns the sign of a number (-1 for negative, 0 for zero, 1 for positive).
* :func:`round_traditional`: rounds a float value using traditional rounding rules (e.g., `0.5` rounds up).

date & time
~~~~~~~~~~~
* :func:`utc_datetime`: Returns the current date and time as a timezone-naive `datetime` object in UTC.
* :func:`now_str`: creates a compact, sortable timestamp string from the current UTC time.

miscellaneous
~~~~~~~~~~~~~
* :func:`dummy_function`: a null function that accepts any arguments and returns `None`.


types, classes & mixins
-----------------------

* :class:`UnsetType`: the class for the :data:`UNSET` singleton object, useful as a sentinel value when `None` is a
  valid input.
* :class:`ErrorMsgMixin`: a mixin class that provides any class with a sophisticated error message handling and
  logging property.
* :class:`UnformattedValue`: a helper class for :func:`format_given` to represent a placeholder that was not found in
  the formatting map.
* :class:`GivenFormatter`: a helper class for :func:`format_given` that overrides default formatting behavior to keep
  missing placeholders.


base constants
--------------

predefined constants for project structure, file conventions, and default settings.

project & file structure
~~~~~~~~~~~~~~~~~~~~~~~~

* :data:`DOCS_FOLDER`: default name for a project's documentation folder ('docs').
* :data:`TESTS_FOLDER`: default name for a project's tests folder ('tests').
* :data:`TEMPLATES_FOLDER`: default name for a folder containing file templates ('templates').
* :data:`BUILD_CONFIG_FILE`: default name for a build configuration file ('buildozer.spec').
* :data:`DEF_PROJECT_PARENT_FOLDER`: default directory name for grouping source code projects ('src').
* :data:`PY_CACHE_FOLDER`: default name for Python's cache folder ('__pycache__').
* :data:`PY_EXT`: file extension for Python modules ('.py').
* :data:`PY_INIT`: the filename for a Python package initializer ('__init__.py').
* :data:`PY_MAIN`: the filename for a Python executable's main module ('__main__.py').
* :data:`CFG_EXT`: file extension for CFG configuration files ('.cfg').
* :data:`INI_EXT`: file extension for INI configuration files ('.ini').
* :data:`DOTENV_FILE_NAME`: default name for environment variable files ('.env').
* :data:`PACKAGE_INCLUDE_FILES_PREFIX`: prefix for files/folders to be included in setup package data (used by
  :mod:`ae.updater` and :mod:`aedev.project_manager`)

formats & default settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

* :data:`DATE_ISO`: ISO format string for dates ("%Y-%m-%d").
* :data:`DATE_TIME_ISO`: ISO format string for :mod:`datetime.datetime` dates ("%Y-%m-%d %H:%M:%S.%f").
* :data:`NOW_STR_FORMAT`: the datetime format string, used e.g. by :func:`now_str` for creating timestamps.
* :data:`NAME_PARTS_SEP`: the character used as a separator in name conversions ('_').
* :data:`DEF_ENCODING`: the default encoding used for string operations ('ascii').
* :data:`DEF_ENCODE_ERRORS`: the default error handling strategy for encoding ('backslashreplace').
* :data:`SKIPPED_MODULES`: a tuple of module names to be ignored by stack inspection functions.
* :data:`UNSET`: a singleton instance of :class:`UnsetType`, used where `None` is a valid data value.


file, path & I/O operations
---------------------------

simplify file system interactions with wrappers and context managers.

* :func:`read_file`: reads the entire content of a text or binary file into a string or bytes object.
* :func:`write_file`: writes a string or bytes object to a file, overwriting existing content.
* :func:`norm_path`: normalizes a path by expanding user home directories (`~`), resolving `.`, `..`, symbolic links,
  and converting between absolute and relative paths.
* :func:`in_wd`: a context manager that temporarily switches the current working directory.

os.path shortcuts
~~~~~~~~~~~~~~~~~

the following are direct references to functions in the :mod:`os.path` module for convenient and quicker access:

* :data:`os_path_abspath`: :func:`os.path.abspath`
* :data:`os_path_basename`: :func:`os.path.basename`
* :data:`os_path_dirname`: :func:`os.path.dirname`
* :data:`os_path_expanduser`: :func:`os.path.expanduser`
* :data:`os_path_isdir`: :func:`os.path.isdir`
* :data:`os_path_isfile`: :func:`os.path.isfile`
* :data:`os_path_join`: :func:`os.path.join`
* :data:`os_path_normpath`: :func:`os.path.normpath`
* :data:`os_path_realpath`: :func:`os.path.realpath`
* :data:`os_path_relpath`: :func:`os.path.relpath`
* :data:`os_path_sep`: :data:`os.path.sep`
* :data:`os_path_splitext`: :func:`os.path.splitext`
"""
# pylint: disable=too-many-lines
import datetime
import getpass
import importlib.abc
import importlib.util
import os
import platform
import re
import shutil
import socket
import ssl
import string
import sys
import unicodedata
import warnings

from ast import literal_eval
from configparser import ConfigParser, ExtendedInterpolation
from contextlib import contextmanager
from importlib.machinery import ModuleSpec
from inspect import getinnerframes, getouterframes, getsourcefile
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen
from types import ModuleType
from typing import Any, Callable, Generator, Iterable, MutableMapping, Optional, Union, cast


__version__ = '0.3.67'


os_path_abspath = os.path.abspath
os_path_basename = os.path.basename
os_path_dirname = os.path.dirname
os_path_expanduser = os.path.expanduser
os_path_isdir = os.path.isdir
os_path_isfile = os.path.isfile
os_path_join = os.path.join
os_path_normpath = os.path.normpath
os_path_realpath = os.path.realpath
os_path_relpath = os.path.relpath
os_path_sep = os.path.sep                       # pylint: disable=invalid-name
os_path_splitext = os.path.splitext


DOCS_FOLDER = 'docs'                            #: project documentation root folder name
TESTS_FOLDER = 'tests'                          #: name of project folder to store unit/integration tests
TEMPLATES_FOLDER = 'templates'
""" template folder name, used in template and namespace root projects to maintain and provide common file templates """

BUILD_CONFIG_FILE = 'buildozer.spec'            #: gui app build config file
PACKAGE_INCLUDE_FILES_PREFIX = 'ae_'            #: file/folder names prefix included in setup package_data/ae_updater

PY_CACHE_FOLDER = '__pycache__'                 #: python cache folder name
PY_EXT = '.py'                                  #: file extension for modules and hooks
PY_INIT = '__init__' + PY_EXT                   #: init-module file name of a python package
PY_MAIN = '__main__' + PY_EXT                   #: main-module file name of a python executable

CFG_EXT = '.cfg'                                #: CFG config file extension
INI_EXT = '.ini'                                #: INI config file extension

DATE_ISO = "%Y-%m-%d"                           #: ISO string format for date values (e.g. in config files/variables)
DATE_TIME_ISO = "%Y-%m-%d %H:%M:%S.%f"          #: ISO string format for datetime values

DEF_PROJECT_PARENT_FOLDER = 'src'               #: default directory name to put code project roots underneath of it

DEF_ENCODE_ERRORS = 'backslashreplace'          #: default encode error handling for UnicodeEncodeErrors
DEF_ENCODING = 'ascii'
""" encoding for :func:`force_encoding` that will always work independent from destination (console, file sys, ...).
"""

DOTENV_FILE_NAME = '.env'                       #: name of the file containing console/shell environment variables
_env_line = re.compile(r"""
    ^
    (?:export\s+)?      # optional export
    ([\w.]+)            # key
    (?:\s*=\s*|:\s+?)   # separator
    (                   # optional value begin
        '(?:\'|[^'])*'  #   single quoted value
        |               #   or
        "(?:\"|[^"])*"  #   double quoted value
        |               #   or
        [^#\n]+         #   unquoted value
    )?                  # value end
    (?:\s*\#.*)?        # optional comment
    $
    """, re.VERBOSE)
_env_variable = re.compile(r"""
    (\\)?               # is it escaped with a backslash?
    (\$)                # literal $
    (                   # collect braces with var for sub
        \{?             #   allow brace wrapping
        ([A-Z0-9_]+)    #   match the variable
        }?              #   closing brace
    )                   # braces end
    """, re.IGNORECASE | re.VERBOSE)


NAME_PARTS_SEP = '_'                                #: name parts separator character, e.g. for :func:`norm_name`

NOW_STR_FORMAT = "{sep}%Y%m%d{sep}%H%M%S{sep}%f"    #: timestamp format of :func:`now_str`

SKIPPED_MODULES = ('ae.base', 'ae.paths', 'ae.dynamicod', 'ae.core', 'ae.console',
                   'ae.gui', 'ae.gui.app', 'ae.gui.tours', 'ae.gui.utils',
                   'ae.kivy', 'ae.kivy.apps', 'ae.kivy.behaviors', 'ae.kivy.i18n', 'ae.kivy.tours', 'ae.kivy.widgets',
                   'ae.enaml_app', 'ae.beeware_app', 'ae.pyglet_app', 'ae.pygobject_app', 'ae.dabo_app',
                   'ae.qpython_app', 'ae.appjar_app', 'importlib._bootstrap', 'importlib._bootstrap_external')
""" skipped modules used as default by :func:`module_name`, :func:`stack_var` and :func:`stack_vars` """


# using only object() does not provide a proper representation string
class UnsetType:
    """ (singleton) UNSET (type) object class. """
    def __bool__(self):
        """ ensure to be evaluated as False, like None. """
        return False

    def __len__(self):
        """ ensure to be evaluated as empty. """
        return 0


UNSET = UnsetType()     #: pseudo value used for attributes/arguments if ``None`` is needed as a valid value


def app_name_guess() -> str:
    """ guess/try to determine the name of the currently running app (w/o assessing not yet initialized app instance).

    :return:                    application name/id or "unguessable" if not guessable.
    """
    app_name = build_config_variable_values(('package.name', ""))[0]
    if not app_name:
        unspecified_app_names = ('ae_base', 'app', '_jb_pytest_runner', 'main', '__main__', 'pydevconsole', 'src')
        path = sys.argv[0]
        app_name = os_path_splitext(os_path_basename(path))[0]
        if app_name.lower() in unspecified_app_names:
            path = os.getcwd()
            app_name = os_path_basename(path)
            if app_name.lower() in unspecified_app_names:
                app_name = "unguessable"
    return defuse(app_name)


def ascii_str(unicode_str: str) -> str:
    """ convert non-ASCII chars to a revertible 7-bit/ASCII representation, e.g., to put in an http header.

    :param unicode_str:         string to encode/convert.
    :return:                    revertible representation of the specified string, using only ASCII characters.
    """
    return repr(unicode_str.encode())


def str_ascii(encoded_str: str) -> str:
    """ convert non-ASCII chars in str object encoded with :func:`ascii_str` back to their corresponding Unicode chars.

    :param encoded_str:         string to decode (covert contained ASCII-encoded characters back Unicode chars).
    :return:                    decoded string.
    """
    return literal_eval(encoded_str).decode()


def build_config_variable_values(*names_defaults: tuple[str, Any], section: str = 'app') -> tuple[Any, ...]:
    """ determine build config variable values from the ``buildozer.spec`` file in the current directory.

    :param names_defaults:      tuple of tuples of build config variable names and default values.
    :param section:             name of the spec file section, using 'app' as default.
    :return:                    tuple of build config variable values (using the passed default value if not specified
                                in the :data:`BUILD_CONFIG_FILE` spec file or if the spec file does not exist in cwd).
    """
    if not os_path_isfile(BUILD_CONFIG_FILE):
        return tuple(def_val for name, def_val in names_defaults)

    config = instantiate_config_parser()
    config.read(BUILD_CONFIG_FILE, 'utf-8')

    return tuple(config.get(section, name, fallback=def_val) for name, def_val in names_defaults)


def camel_to_snake(name: str) -> str:
    """ convert a name from CamelCase to snake_case.

    :param name:                name string in CamelCaseFormat.
    :return:                    name in snake_case_format.
    """
    str_parts = []
    for char in name:
        if char.isupper():
            str_parts.append(NAME_PARTS_SEP + char)
        else:
            str_parts.append(char)
    return "".join(str_parts)


def deep_dict_update(data: dict, update: dict, overwrite: bool = True):
    """ update the optionally nested data dict in-place with the items and subitems from the update dict.

    :param data:                dict to be updated/extended. non-existing keys of dict-subitems will be added.
    :param update:              dict with the [sub-]items to update in the :paramref:`~deep_dict_update.data` dict.
    :param overwrite:           pass False to not overwrite an already existing value.

    .. hint:: see the module/portion :mod:`ae.deep` for more deep update helper functions.
    """
    for upd_key, upd_val in update.items():
        if isinstance(upd_val, dict):
            if upd_key not in data:
                data[upd_key] = {}
            deep_dict_update(data[upd_key], upd_val, overwrite=overwrite)
        elif overwrite or upd_key not in data:
            data[upd_key] = upd_val


URI_SEP_CHAR = '⫻'  # U+2AFB: TRIPLE SOLIDUS BINARY RELATION
# noinspection GrazieInspection
ASCII_UNICODE = (
    ('/', '⁄'),     # U+2044: Fraction Slash; '∕' U+2215: Division Slash; '⧸' U+29F8: Big Solidus;
                    # '╱' U+FF0F: Fullwidth Solidus; '╱' U+2571: Box Drawings Light Diagonal Upper Right to Lower Left
    ('|', '।'),     # U+0964: Devanagari Danda
    ('\\', '﹨'),    # U+FE68: SMALL REVERSE SOLIDUS; '⑊' U+244A OCR DOUBLE BACKSLASH; '⧵' U+29F5 REV. SOLIDUS OPERATOR
    (':', '﹕'),     # U+FE55: Small Colon
    ('*', '﹡'),     # U+FE61: Small Asterisk
    ('?', '﹖'),     # U+FE56: Small Question Mark
    ('"', '＂'),     # U+FF02: Fullwidth Quotation Mark
    ("'", '‘'),     # U+2018: Left Single; '’' U+2019: Right Single; '‛' U+201B: Single High-Reversed-9 Quotation Mark
    ('<', '⟨'),     # U+27E8: LEFT ANGLE BRACKET; '‹' U+2039: Single Left-Pointing Angle Quotation Mark
    ('>', '⟩'),     # U+27E9: RIGHT ANGLE BRACKET; '›' U+203A: Single Right-Pointing Angle Quotation Mark
    ('(', '⟮'),     # U+27EE: MATHEMATICAL LEFT FLATTENED PARENTHESIS
    (')', '⟯'),     # U+27EF: MATHEMATICAL RIGHT FLATTENED PARENTHESIS
    ('[', '⟦'),     # U+27E6: MATHEMATICAL LEFT WHITE SQUARE BRACKET
    (']', '⟧'),     # U+27E7: MATHEMATICAL RIGHT WHITE SQUARE BRACKET
    ('{', '﹛'),     # U+FE5B: Small Left Curly Bracket
    ('}', '﹜'),     # U+FE5C: Small Right Curly Bracket
    ('#', '﹟'),     # U+FE5F: Small Number Sign
    (';', '﹔'),     # U+FE54: Small Semicolon
    ('@', '﹫'),     # U+FE6B: Small Commercial At
    ('&', '﹠'),     # U+FE60: Small Ampersand
    ('=', '﹦'),     # U+FE66: Small Equals Sign
    ('+', '﹢'),     # U+FE62: Small Plus Sign
    ('$', '﹩'),     # U+FE69: Small Dollar Sign
    ('%', '﹪'),     # U+FE6A: Small Percent Sign
    ('^', '＾'),     # U+FF3E: Fullwidth Circumflex Accent
    (',', '﹐'),     # U+FE50: Small Comma
    (' ', '␣'),     # U+2423: Open Box; more see underneath and https://unicode-explorer.com/articles/space-characters:
                    # ' ' U+00A0: No-Break Space (NBSP); ' ' U+1680 Ogham Space Mark; ' ' U+2000 En Quad;
                    # ' ' U+2001 Em Quad; ' ' U+2002 En Space; ' ' U+2003 Em Space; ' ' U+2004 Three-Per-Em
                    # ' ' U+2005 Four-Per-Em; ' ' U+2006 Six-Per-Em; ' ' U+2007 Figure Space;
                    # ' ' U+2008 Punctuation Space; ' ' U+2009 Thin; ' ' U+200A Hair Space;
                    # ' ' U+202F: Narrow No-Break Space (NNBSP); ' ' U+205F Medium Mathematical Space;
                    # '␠' U+2420 symbol for space; '␣' U+2423 Open Box; '　' U+3000: Ideographic Space
    (chr(127), '␡'),  # U+2421: DELETE SYMBOL
    # ('_', '𛲖'), # U+1BC96: Duployan Affix Low Line; '＿' U+FF3F Fullwidth Low Line
)
""" transformation table of special ASCII to Unicode alternative character,
see https://www.compart.com/en/unicode/category/Po and https://xahlee.info/comp/unicode_naming_slash.html (http!) """

ASCII_TO_UNICODE = dict(ASCII_UNICODE)  #: map to convert ASCII to an alternative defused Unicode character
UNICODE_TO_ASCII = {unicode_char: ascii_char for ascii_char, unicode_char in ASCII_UNICODE}     #: Unicode to ASCII map


def dedefuse(value: str) -> str:
    """ convert a string that got defused with :func:`defuse` back to its original form.

    :param value:               string defused with the function :func:`defuse`.
    :return:                    re-activated form of the string (with all ASCII special characters recovered).
    """
    original = ""
    for char in value:
        if char in UNICODE_TO_ASCII:
            char = UNICODE_TO_ASCII[char]
        elif 0x2400 <= (code := ord(char)) <= 0x241F:
            char = chr(code - 0x2400)
        original += char

    return original.replace(URI_SEP_CHAR, '://')


def defuse(value: str) -> str:
    """ convert a file path or a URI into a defused/presentational form to be usable as URL slug or file/folder name.

    :param value:               any string to defuse (replace special chars with Unicode alternatives).
    :return:                    string with its special characters replaced by its pure presentational alternatives.

    the ASCII character range 0..31 gets converted to the Unicode range U+2400 + ord(char): 0==U+2400 ... 31==U+241F.

    in most unix variants only the slash and the ASCII 0 characters are not allowed in file names.

    in MS Windows are not allowed: ASCII 0..31 / | \\ : * ? ” % < > ( ). some blogs recommend also not allowing
    (convert) the characters `#` and `'`.

    only old POSIX seems to be even more restricted (only allowing alphanumeric characters plus . - and _).

    more on allowed characters in file names in the answers of RedGrittyBrick on https://superuser.com/questions/358855
    and of Christopher Oezbek on https://stackoverflow.com/questions/1976007.

    file name length is not restricted/shortened by this function, although the maximum is 255 characters on most OSs.

    .. hint:: use the :func:`dedefuse` function to convert the defused string back to the corresponding URI/file-path.

    """
    defused = ""
    value = value.replace('://', URI_SEP_CHAR)  # make URIs shorter
    for char in value:
        if char in ASCII_TO_UNICODE:
            char = ASCII_TO_UNICODE[char]
        elif (code := ord(char)) <= 31:
            char = chr(0x2400 + code)
        defused += char
    return defused


def dummy_function(*_args, **_kwargs):
    """ null function accepting any arguments and returning None.

    :param _args:               ignored positional arguments.
    :param _kwargs:             ignored keyword arguments.
    :return:                    always None.
    """


def duplicates(values: Iterable) -> list:
    """ determine all duplicates in the iterable specified in the :paramref:`~duplicates.values` argument.

    inspired by Ritesh Kumars answer to https://stackoverflow.com/questions/9835762.

    :param values:              iterable (list, tuple, str, ...) to search for duplicate items.
    :return:                    list of the duplicate items found (can contain the same duplicate multiple times).
    """
    seen_set: set = set()
    seen_add = seen_set.add
    dup_list: list = []
    dup_add = dup_list.append
    for item in values:
        if item in seen_set:
            dup_add(item)
        else:
            seen_add(item)
    return dup_list


def env_str(name: str, convert_name: bool = False) -> Optional[str]:
    """ determine the string value of an OS environment variable, optionally preventing invalid variable name.

    :param name:                name of an OS environment variable.
    :param convert_name:        pass True to prevent invalid variable names by converting
                                CamelCase names into SNAKE_CASE, lower-case into
                                upper-case and all non-alpha-numeric characters into underscore characters.
    :return:                    string value of OS environment variable if found, else None.
    """
    if convert_name:
        name = norm_name(camel_to_snake(name)).upper()
    return os.environ.get(name)


def evaluate_literal(literal_string: str
                     ) -> Optional[Union[bool, bytes, dict, complex, float, int, list, set, str, tuple]]:
    """ evaluates a Python expression while accepting unquoted strings as str type.

    :param literal_string:      any literal of the base types (like dict, list, set, tuple) which are recognized
                                by :func:`ast.literal_eval`.
    :return:                    an instance of the data type or the specified string, even if it is not quoted with high
                                comma characters. `None` will be returned if the specified literal is the string "None".
    """
    try:
        return literal_eval(literal_string)
    except (IndentationError, SyntaxError, TypeError, ValueError):
        return literal_string


def force_encoding(text: Union[str, bytes], encoding: str = DEF_ENCODING, errors: str = DEF_ENCODE_ERRORS) -> str:
    """ force/ensure the encoding of text (str or bytes) without any UnicodeDecodeError/UnicodeEncodeError.

    :param text:                text as str/bytes.
    :param encoding:            encoding (def= :data:`DEF_ENCODING`).
    :param errors:              encode error handling (def= :data:`DEF_ENCODE_ERRORS`).

    :return:                    text as str (with all characters checked/converted/replaced to be encode-able).
    """
    enc_str: bytes = text.encode(encoding=encoding, errors=errors) if isinstance(text, str) else text
    return enc_str.decode(encoding=encoding)


class UnformattedValue:                     # pylint: disable=too-few-public-methods
    """ helper class for :func:`~ae.base.format_given` to keep placeholder with format unchanged if not found. """
    def __init__(self, key: str):
        self.key = key

    def __format__(self, format_spec: str):
        """ overriding Python object class method to return placeholder unchanged, including the curly brackets. """
        # pylint: disable=consider-using-f-string
        return "{{{}{}}}".format(self.key, ":" + format_spec if format_spec else "")


class GivenFormatter(string.Formatter):
    """ helper class for :func:`~ae.base.format_given` to keep placeholder with format unchanged if not found. """
    def get_value(self, key, args, kwargs):
        """ overriding to keep placeholder unchanged if not found """
        try:
            return super().get_value(key, args, kwargs)
        except KeyError:
            return UnformattedValue(key)


def format_given(text: str, placeholder_map: dict[str, Any], strict: bool = False):
    """ replacement for Python's str.format_map(), keeping intact placeholders that are not in the specified mapping.

    :param text:                text/template in which the given/specified placeholders will get replaced. in contrary
                                to :func:`str.format_map`, no KeyError will be raised for placeholders not specified in
                                :paramref:`~format_given.placeholder_map`.
    :param placeholder_map:     dict with placeholder keys to be replaced in :paramref:`~format_given.text` argument.
    :param strict:              pass True to raise an error for text templates containing unpaired curly brackets.
    :return:                    the specified :paramref:`~format_given.text` with only the placeholders specified in
                                :paramref:`~format_given.placeholder_map` replaced with their respective map value.

    inspired by the answer of CodeManX in `https://stackoverflow.com/questions/3536303`__
    """
    formatter = GivenFormatter()
    try:
        return formatter.vformat(text, (), placeholder_map)
    except (ValueError, Exception) as ex:                           # pylint: disable=broad-except
        if strict:
            raise ex
        return text


def full_stack_trace(ex: Exception) -> str:
    """ get a full stack trace from an exception.

    :param ex:                  exception instance.
    :return:                    str with stack trace info.
    """
    ret = f"Exception {ex!r}. Traceback:" + os.linesep
    trace_back = sys.exc_info()[2]
    if trace_back:
        def ext_ret(item):
            """ process traceback frame and add as str to ret """
            nonlocal ret
            ret += f'File "{item[1]}", line {item[2]}, in {item[3]}' + os.linesep
            lines = item[4]  # mypy does not detect item[]
            if lines:
                for line in lines:
                    ret += ' ' * 4 + line.lstrip()

        for frame in reversed(getouterframes(trace_back.tb_frame)[1:]):
            ext_ret(frame)
        for frame in getinnerframes(trace_back):
            ext_ret(frame)
    return ret


def import_module(import_name: str, path: Optional[Union[str, UnsetType]] = UNSET) -> Optional[ModuleType]:
    """ search, import and execute a Python module dynamically without adding it to sys.modules.

    :param import_name:         dot-name of the module to import.
    :param path:                optional file path of the module to import. if this arg is not specified or has the
                                default value (:data:`UNSET`), then the path will be determined from the import name.
                                specify ``None`` to prevent the module search.
    :return:                    a reference to the loaded module or ``None`` if the module could not be imported.
    """
    if path is UNSET:
        path = import_name.replace('.', os_path_sep)
        path += PY_EXT if os_path_isfile(path + PY_EXT) else os_path_sep + PY_INIT
    mod_ref = None

    spec = importlib.util.spec_from_file_location(import_name, path)    # type: ignore # silly mypy
    if isinstance(spec, ModuleSpec):
        mod_ref = importlib.util.module_from_spec(spec)
        # added isinstance and imported importlib.abc to suppress PyCharm+mypy inspections
        if isinstance(spec.loader, importlib.abc.Loader):
            try:
                spec.loader.exec_module(mod_ref)
            except FileNotFoundError:
                mod_ref = None

    return mod_ref


def instantiate_config_parser() -> ConfigParser:
    """ instantiate and prepare config file parser.

    ensures that the :class:`~configparser.ConfigParser` instance is correctly configured, e.g., to support
    case-sensitive config variable names and to use :class:`ExtendedInterpolation` as the interpolation argument.
    """
    cfg_parser = ConfigParser(allow_no_value=True, interpolation=ExtendedInterpolation())
    # set optionxform to have case-sensitive var names (or use 'lambda option: option')
    # mypy V 0.740 bug - see mypy issue #5062: adding pragma "type: ignore" breaks PyCharm (showing
    # inspection warning "Non-self attribute could not be type-hinted"), but
    # also cast(Callable[[Arg(str, 'option')], str], str) and # type: ... is not working
    # (because Arg is not available in plain mypy, only in the extra mypy_extensions package)
    setattr(cfg_parser, 'optionxform', str)
    return cfg_parser


@contextmanager
def in_wd(new_cwd: str) -> Generator[None, None, None]:
    """ context manager to temporarily switch the current working directory / cwd.

    :param new_cwd:             path to the directory to switch to (within the context/with block).
                                an empty string gets interpreted as the current working directory.

    the following example demonstrates a typical usage, together with a temporary path, created with the help of Pythons
    :class:`~tempfile.TemporaryDirectory` class::

        with tempfile.TemporaryDirectory() as tmp_dir, in_wd(tmp_dir):
            # within the context the tmp_dir is set as the current working directory
            assert os.getcwd() == tmp_dir
        # here the current working directory got set back to the original path and the temporary directory got removed

    """
    cur_dir = os.getcwd()
    try:
        if new_cwd:         # empty new_cwd results in the current working folder (no dir change needed/prevent error)
            os.chdir(new_cwd)
        yield
    finally:
        os.chdir(cur_dir)


def load_dotenvs(from_module_path: bool = False):
    """ detect and load not defined OS environment variables from ``.env`` files.

    :param from_module_path:    pass True to load OS environment variables (that are not already loaded from ``.env``
                                files situated in or above the current working directory) also from/above the folder of
                                the first module in the call stack that gets not excluded/skipped by :func:`stack_var`.

                                in order to also load ``.env`` files in/above the project folder.
                                call this function from the main module of project/app.

    .. note::
        only variables that are not already defined in the OS environment variables mapping :data:`os.environ` will be
        loaded/added. variables will be loaded first from the first ``.env`` file found in or above the current working
        directory, while the variable values in the deeper situated files are overwriting the values defined in the
        ``.env`` files situated in the above folders.
    """
    env_vars = os.environ
    load_env_var_defaults(os.getcwd(), env_vars)

    if from_module_path and (file_name := stack_var('__file__')):
        load_env_var_defaults(os_path_dirname(os_path_abspath(file_name)), env_vars)


def load_env_var_defaults(start_dir: str, env_vars: MutableMapping[str, str]) -> MutableMapping[str, str]:
    """ load undeclared env var defaults from a chain of ``.env`` files starting in the specified folder or its parent.

    :param start_dir:           folder to start search of an ``.env`` file, if not found, then also checks the parent
                                folder. if an ``.env `` file got found, then put their shell environment variable values
                                into the  specified :paramref:`~load_env_var_defaults.env_vars` mapping if they are not
                                already there. after processing the first ``.env`` file, it repeats to check for
                                further ``.env`` files in the parent folder to load them too, until either detecting
                                a folder without an ``.env`` file or until an ``.env`` got loaded from the root folder.
    :param env_vars:            environment variables mapping to be amended with env variable values from any
                                found ``.env`` file. pass Python's :data:`os.environ` to amend this mapping directly
                                with all the already not declared environment variables.
    :return:                    dict with the loaded env var names (keys) and values.
    """
    start_dir = norm_path(start_dir)
    file_path = os_path_join(start_dir, DOTENV_FILE_NAME)
    if not os_path_isfile(file_path):
        file_path = os_path_join(os_path_dirname(start_dir), DOTENV_FILE_NAME)

    loaded_vars = {}
    while os_path_isfile(file_path):
        for var_nam, var_val in parse_dotenv(file_path).items():
            if var_nam not in env_vars:
                env_vars[var_nam] = loaded_vars[var_nam] = var_val

        if os.sep not in file_path:
            break           # pragma: no cover # prevent endless-loop for ``.env`` file in root dir (os.sep == '/')
        file_path = os_path_join(os_path_dirname(os_path_dirname(file_path)), DOTENV_FILE_NAME)

    return loaded_vars


def main_file_paths_parts(portion_name: str) -> tuple[tuple[str, ...], ...]:
    """ determine tuple of supported main/version file name path part tuples.

    :param portion_name:        portion or package name.
    :return:                    tuple of tuples of main/version file name path parts.
    """
    return (
        ('main' + PY_EXT, ),
        (PY_MAIN, ),
        (PY_INIT, ),
        ('main', PY_INIT),          # django main project
        (portion_name + PY_EXT, ),
        (portion_name, PY_INIT),
    )


def mask_secrets(data: Union[dict, Iterable], fragments: Iterable[str] = ('password', 'pwd')) -> Union[dict, Iterable]:
    """ partially-hide secret string values like passwords/credit-card-numbers in deeply nestable data structures.

    :param data:                iterable deep data structure wherein its item values get masked if their related dict
                                item key contains one of the fragments specified in :paramref:`~mask_secrets.fragments`.
    :param fragments:           dict key string fragments of which the related value will be masked. each fragment has
                                to be specified with lower case chars! defaults to ('password', 'pwd') if not passed.
    :return:                    specified data structure with the secrets masked (¡in-place!).
    """
    is_dict = isinstance(data, dict)

    for idx, val in tuple(data.items()) if is_dict else enumerate(data):    # type: ignore # silly mypy not sees is_dict
        val_is_str = isinstance(val, str)
        if not val_is_str and isinstance(val, Iterable):
            mask_secrets(val, fragments=fragments)
        elif is_dict and val_is_str and isinstance(idx, str):
            idx_lower = idx.lower()
            if any(_frag in idx_lower for _frag in fragments):
                data[idx] = val[:3] + "*" * 9                               # type: ignore # silly mypy not sees is_dict

    return data


def mask_url(url: str, replacement: str = "¿¿¿") -> str:
    """ hide|replace the password/token in a URL.

    :param url:                 URL in which an optional password|token will be searched and replaced.
    :param replacement:         optional replacement string, if not specified then the default value will be used.
    :return:                    URL with the credentials masked/replaced.
    """
    parts = urlparse(url)
    if parts.password is None:
        return url
    # manually split out the netloc, because using parts.hostname/,port would have to be checked for None&hostname.lower
    parts = parts._replace(netloc=f"{parts.username}:{replacement}@{parts.netloc.rpartition('@')[-1]}")
    # noinspection PyTypeChecker
    return urlunparse(parts)


def module_attr(import_name: str, attr_name: str = "") -> Optional[Any]:
    """ determine dynamically a reference to a module or to any attribute (variable/func/class) declared in the module.

    :param import_name:         import-/dot-name of the distribution/module/package to load/import.
    :param attr_name:           name of the attribute declared within the module. do not specify or pass an empty
                                string to get/return a reference to the imported module instance.
    :return:                    module instance or module attribute value
                                or None if the module got not found
                                or UNSET if the module attribute doesn't exist.

    .. note:: a previously not imported module will *not* be added to `sys.modules` by this function.

    """
    mod_ref = sys.modules.get(import_name, None) or import_module(import_name)
    return getattr(mod_ref, attr_name, UNSET) if mod_ref and attr_name else mod_ref


def module_file_path(local_object: Optional[Callable] = None) -> str:
    """ determine the absolute path of the module from which this function got called.

    :param local_object:        optional local module, class, method, function, traceback, frame, or code object of the
                                calling module (passing `lambda: 0` also works). omit this argument in order to use
                                the `__file__` module variable (which will not work if the module is frozen by
                                ``py2exe`` or ``PyInstaller``).
    :return:                    module path (inclusive module file name) or empty string if not found/determinable.
    """
    if local_object:
        file_path = getsourcefile(local_object)
        if file_path:
            return norm_path(file_path)

    file_path = stack_var('__file__')
    if not file_path:                                   # pragma: no cover
        try:
            # noinspection PyProtectedMember,PyUnresolvedReferences
            file_path = sys._getframe().f_back.f_code.co_filename   # type: ignore # pylint: disable=protected-access
        except (AttributeError, Exception):                         # pylint: disable=broad-except # pragma: no cover
            file_path = ""
    return file_path


def module_name(*skip_modules: str, depth: int = 0) -> Optional[str]:
    """ find the first module in the call stack that is *not* in :paramref:`~module_name.skip_modules`.

    :param skip_modules:        module names to skip (def=this and other core modules, see :data:`SKIPPED_MODULES`).
    :param depth:               the calling level from which on to search. the default value 0 refers to the frame and
                                the module of the caller of this function.
                                pass 1 or an even higher value if you want to get the module name of a function/method
                                in a deeper level in the call stack.
    :return:                    the module name of the call stack level, specified by :paramref:`~module_name.depth`.
    """
    if not skip_modules:
        skip_modules = SKIPPED_MODULES
    return stack_var('__name__', *skip_modules, depth=depth + 1)


def norm_line_sep(text: str) -> str:
    # noinspection GrazieInspection
    """ convert any combination of line separators in the :paramref:`~norm_line_sep.text` arg to new-line characters.

        :param text:                string containing any combination of line separators ('\\\\r\\\\n' or '\\\\r').
        :return:                    normalized/converted string with only new-line ('\\\\n') line separator characters.
        """
    return text.replace('\r\n', '\n').replace('\r', '\n')


def norm_name(name: str, allow_num_prefix: bool = False) -> str:
    """ normalize name to start with a letter/alphabetic/underscore and to contain only alphanumeric/underscore chars.

    :param name:                any string to be converted into a valid variable/method/file/... name.
    :param allow_num_prefix:    pass True to allow leading digits in the returned normalized name.
    :return:                    cleaned/normalized/converted name string (e.g., for a variable-/method-/file-name).
    """
    str_parts: list[str] = []
    for char in name:
        if char.isalpha() or char.isalnum() and (allow_num_prefix or str_parts):
            str_parts.append(char)
        else:
            str_parts.append('_')
    return "".join(str_parts)


def norm_path(path: str, make_absolute: bool = True, remove_base_path: str = "", remove_dots: bool = True,
              resolve_sym_links: bool = True) -> str:
    """ normalize a path, replacing `..`/`.` parts or the tilde character (home folder) and transform to relative/abs.

    :param path:                path string to normalize/transform.
    :param make_absolute:       pass False to not convert the returned path to an absolute path.
    :param remove_base_path:    pass a valid base path to return a relative path, even if the argument values of
                                :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links` are
                                `True`.
    :param remove_dots:         pass False to not replace/remove the `.` and `..` placeholders.
    :param resolve_sym_links:   pass False to not resolve symbolic links, passing True implies a `True` value also for
                                the :paramref:`~norm_path.make_absolute` argument.
    :return:                    normalized path string: absolute if :paramref:`~norm_path.remove_base_path` is empty and
                                either :paramref:`~norm_path.make_absolute` or :paramref:`~norm_path.resolve_sym_links`
                                is `True`; relative if :paramref:`~norm_path.remove_base_path` is a base path of
                                :paramref:`~norm_path.path` or if :paramref:`~norm_path.path` got specified as a
                                relative path and neither :paramref:`~norm_path.make_absolute` nor
                                :paramref:`~norm_path.resolve_sym_links` is `True`.

    .. hint:: the :func:`~ae.paths.normalize` function additionally replaces :data:`~ae.paths.PATH_PLACEHOLDERS`.

    """
    path = path or "."
    if path[0] == "~":
        path = os_path_expanduser(path)

    if remove_dots:
        path = os_path_normpath(path)

    if resolve_sym_links:
        path = os_path_realpath(path)
    elif make_absolute:
        path = os_path_abspath(path)

    if remove_base_path:
        if remove_base_path[0] == "~":
            remove_base_path = os_path_expanduser(remove_base_path)
        path = os_path_relpath(path, remove_base_path)

    return path


def now_str(sep: str = "") -> str:
    """ return the current UTC timestamp as string (to use as suffix for file and variable/attribute names).

    :param sep:                 optional prefix and separator character (separating date from time and in time part
                                the seconds from the microseconds).
    :return:                    naive UTC timestamp (without timezone info) as string (length=20 + 3 * len(sep)).
    """
    return utc_datetime().strftime(NOW_STR_FORMAT.format(sep=sep))


def os_host_name() -> str:
    """ determine the operating system host/machine name.

    :return:                    machine name string.
    """
    return defuse(platform.node()) or "indeterminableHostName"


# noinspection PyTypeChecker
def os_local_ip() -> str:
    """ determine ip address of this system/machine in the local network (LAN or WLAN).

    inspired by answers of SO users @dml and @fatal_error to the question: https://stackoverflow.com/questions/166506.

    :return:                    ip address of this machine in the local network (WLAN or LAN/ethernet)
                                or empty string if this machine is not connected to any network.
    """
    socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_address = ""
    try:
        socket1.connect(('10.255.255.255', 1))                      # doesn't even have to be reachable
        ip_address = socket1.getsockname()[0]
    except (OSError, IOError, Exception):                           # pylint: disable=broad-except # pragma: no cover
        # ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError inherit from OSError
        socket2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            socket2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket2.connect(('<broadcast>', 0))
            ip_address = socket2.getsockname()[0]
        except (OSError, IOError, Exception):                       # pylint: disable=broad-except
            pass
        finally:
            socket2.close()
    finally:
        socket1.close()

    return ip_address


def _os_platform() -> str:
    """ determine the operating system where this code is running (used to initialize the :data:`os_platform` variable).

    :return:                    operating system (extension) as string. extending Python's :func:`sys.platform`
                                for mobile platforms like Android and iOS:

                                * `'android'` for all Android systems.
                                * `'cygwin'` for MS Windows with an installed Cygwin extension.
                                * `'darwin'` for all Apple Mac OS X systems.
                                * `'freebsd'` for all other BSD-based unix systems.
                                * `'ios'` for all Apple iOS systems.
                                * `'linux'` for all other unix systems (like Arch, Debian/Ubuntu, Suse, ...).
                                * `'win32'` for MS Windows systems (w/o the Cygwin extension).

    """
    if env_str('ANDROID_ARGUMENT') is not None:     # p4a env variable; alternatively use ANDROID_PRIVATE
        return 'android'
    return env_str('KIVY_BUILD') or sys.platform    # KIVY_BUILD == 'android'/'ios' on Android/iOS


os_platform = _os_platform()
""" operating system / platform string (see :func:`_os_platform`).

this string value gets determined for most of the operating systems with the help of Python's :func:`sys.platform`
function and additionally detects the operating systems iOS and Android (currently not fully supported by Python).
"""


def os_user_name() -> str:
    """ determine the operating system username.

    :return:                    username string.
    """
    return getpass.getuser()


def parse_dotenv(file_path: str) -> dict[str, str]:
    """ parse ``.env`` file content and return environment variable names as dict keys and values as dict values.

    :param file_path:           string with the name/path of an existing ``.env``/:data:`DOTENV_FILE_NAME` file.
    :return:                    dict with environment variable names and values
    """
    env_vars: dict[str, str] = {}
    for line in cast(str, read_file(file_path)).splitlines():
        match = _env_line.search(line)
        if not match:
            if not re.search(r'^\s*(?:#.*)?$', line):  # not comment or blank
                warnings.warn(f"'{line!r}' in '{file_path}' doesn't match {DOTENV_FILE_NAME} format", SyntaxWarning)
            continue

        var_nam, var_val = match.groups()
        var_val = "" if var_val is None else var_val.strip()

        # remove surrounding quotes, unescape all chars except $ so variables can be escaped properly
        match = re.match(r'^([\'"])(.*)\1$', var_val)
        if match:
            delimiter, var_val = match.groups()
            if delimiter == '"':
                var_val = re.sub(r'\\([^$])', r'\1', var_val)
        else:
            delimiter = None
        if delimiter != "'":
            for parts in _env_variable.findall(var_val):
                # substitute env variables in a value with its value, if declared and not escaped
                if parts[0] == '\\' or (replace := env_vars.get(parts[-1], os.environ.get(parts[-1], UNSET))) is UNSET:
                    replace = "".join(parts[1:-1])  # don't replace escaped/undeclared vars to prevent value cut at '$'

                var_val = var_val.replace("".join(parts[0:-1]), cast(str, replace))

        env_vars[var_nam] = var_val

    return env_vars


def project_main_file(import_name: str, project_path: str = "") -> str:
    """ determine the main module file path of a project package containing the project __version__ module variable.

    :param import_name:         name of the module/package (including namespace prefixes, separated with dots).
    :param project_path:        optional path where the project of the package/module is situated. not needed if the
                                current working directory is the root folder of either the import_name project or of a
                                sister project (under the same project parent folder).
    :return:                    absolute file path of the main module or empty string if no main/version file is found.
    """
    *namespace_dirs, portion_name = import_name.split('.')
    project_name = ('_'.join(namespace_dirs) + '_' if namespace_dirs else "") + portion_name
    paths_parts = main_file_paths_parts(portion_name)

    project_path = norm_path(project_path)
    module_paths = []
    if os_path_basename(project_path) != project_name:
        module_paths.append(os_path_join(os_path_dirname(project_path), project_name, *namespace_dirs))
    if namespace_dirs:
        module_paths.append(os_path_join(project_path, *namespace_dirs))
    module_paths.append(project_path)

    for module_path in module_paths:
        for path_parts in paths_parts:
            main_file = os_path_join(module_path, *path_parts)
            if os_path_isfile(main_file):
                # noinspection PyTypeChecker
                return main_file
    return ""


def read_file(file_path: str, extra_mode: str = "", encoding: Optional[str] = None, error_handling: str = 'ignore'
              ) -> Union[str, bytes]:
    """ returning content of the text/binary file specified by file_path argument as string.

    :param file_path:           path/name of the file to load the content from.
    :param extra_mode:          extra open mode flag characters appended to "r" onto the :func:`open` mode argument.
                                pass "b" to read the content of a binary file returned of the type `bytes`. in binary
                                mode the argument passed in :paramref:`~read_file.error_handling` will be ignored.
    :param encoding:            encoding used to load and convert/interpret the file content.
    :param error_handling:      for files opened in text mode, pass `'strict'` or ``None`` to return ``None`` (instead
                                of an empty string) for the cases where either a decoding `ValueError` exception or any
                                `OSError`, `FileNotFoundError` or `PermissionError` exception got raised.
                                the default value `'ignore'` will ignore any decoding errors (missing some characters)
                                and will return an empty string on any file/os exception. this parameter will be ignored
                                if the :paramref:`~read_file.extra_mode` argument contains the 'b' character (to read
                                the file content as binary/bytes-array).
    :return:                    file content string or bytes array.
    :raises FileNotFoundError:  if the file to read from does not exist.
    :raises OSError:            if :paramref:`~read_file.file_path` is misspelled or contains invalid characters.
    :raises PermissionError:    if the current OS user account lacks permissions to read the file content.
    :raises ValueError:         on decoding errors.
    """
    extra_kwargs = {} if "b" in extra_mode else {'errors': error_handling}
    with open(file_path, "r" + extra_mode, encoding=encoding, **extra_kwargs) as file_handle:           # type: ignore
        return file_handle.read()


def round_traditional(num_value: float, num_digits: int = 0) -> float:
    """ round numeric value traditional.

    needed because python round() is working differently, e.g., round(0.075, 2) == 0.07 instead of 0.08
    inspired by https://stackoverflow.com/questions/31818050/python-2-7-round-number-to-nearest-integer.

    :param num_value:           float value to be round.
    :param num_digits:          number of digits to be round (def=0 - rounds to an integer value).

    :return:                    rounded value.
    """
    return round(num_value + 10 ** (-len(str(num_value)) - 1), num_digits)


def sign(number: float) -> int:
    """ return ths sign (-1, 0, 1) of a number.

    :param number:              any number of type float or int.
    :return:                    -1 if the number is negative, 0 if it is zero, or 1 if it is positive.
    """
    return (number > 0) - (number < 0)


def snake_to_camel(name: str, back_convertible: bool = False) -> str:
    """ convert name from snake_case to CamelCase.

    :param name:                name string composed of parts separated by an underscore character
                                (:data:`NAME_PARTS_SEP`).
    :param back_convertible:    pass `True` to get the first character of the returned name in lower-case
                                if the snake name has no leading underscore character (and to allow
                                the conversion between snake and camel case without information loss).
    :return:                    name in camel case.
    """
    ret = "".join(part.capitalize() for part in name.split(NAME_PARTS_SEP))
    if back_convertible and name[0] != NAME_PARTS_SEP:
        ret = ret[0].lower() + ret[1:]
    return ret


def stack_frames(depth: int = 1) -> Generator:  # Generator[frame, None, None]
    """ generator returning the call stack frame from the level given in :paramref:`~stack_frames.depth`.

    :param depth:               the stack level to start; the first returned frame by this generator. the default value
                                (1) refers to the next deeper stack frame, respectively the one of the caller of this
                                function. pass 2 or a higher value if you want to start with an even deeper frame/level.
    :return:                    generated frames of the call stack.
    """
    try:
        while True:
            depth += 1
            # noinspection PyProtectedMember,PyUnresolvedReferences
            yield sys._getframe(depth)          # pylint: disable=protected-access
    except (TypeError, AttributeError, ValueError):
        pass


def stack_var(name: str, *skip_modules: str, scope: str = '', depth: int = 1) -> Optional[Any]:
    """ determine variable value in calling stack/frames.

    :param name:                variable name to search in the calling stack frames.
    :param skip_modules:        module names to skip (def=see :data:`SKIPPED_MODULES` module constant).
    :param scope:               pass 'locals' to only check for local variables (ignoring globals) or
                                'globals' to only check for global variables (ignoring locals). the default value (an
                                empty string) will not restrict the scope, returning either a local or global value.
    :param depth:               the calling level from which on to search. the default value (1) refers to the next
                                deeper stack frame, which is the caller of the function. pass 2 or an even higher
                                value if you want to start the variable search from a deeper level in the call stack.
    :return:                    the variable value of a deeper level within the call stack or UNSET if the variable was
                                not found.
    """
    glo, loc, _deep = stack_vars(*skip_modules, find_name=name, min_depth=depth + 1, scope=scope)
    variables = glo if name in glo and scope != 'locals' else loc
    return variables.get(name, UNSET)


def stack_vars(*skip_modules: str,
               find_name: str = '', min_depth: int = 1, max_depth: int = 0, scope: str = ''
               ) -> tuple[dict[str, Any], dict[str, Any], int]:
    """ determine all global and local variables in a calling stack/frames.

    :param skip_modules:        module names to skip (def=see :data:`SKIPPED_MODULES` module constant).
    :param find_name:           if passed, then the returned stack frame must contain a variable with the passed name.
    :param scope:               scope to search the variable name passed via :paramref:`~stack_vars.find_name`. pass
                                'locals' to only search for local variables (ignoring globals) or 'globals' to only
                                check for global variables (ignoring locals). passing an empty string will find the
                                variable within either locals or globals.
    :param min_depth:           the call stack level from which on to search. the default value (1) refers the next
                                deeper stack frame, respectively, to the caller of this function. pass 2 or a higher
                                value if you want to get the variables from a deeper level in the call stack.
    :param max_depth:           the maximum depth in the call stack from which to return the variables. if the specified
                                argument is not zero and no :paramref:`~stack_vars.skip_modules` are specified, then the
                                first deeper stack frame that is not within the default :data:`SKIPPED_MODULES` will be
                                returned. if this argument and :paramref:`~stack_vars.find_name` get not passed,
                                then the variables of the top stack frame will be returned.
    :return:                    tuple of the global and local variable dicts and the depth in the call stack.
    """
    if not skip_modules:
        skip_modules = SKIPPED_MODULES
    glo = loc = {}
    depth = min_depth + 1   # +1 for stack_frames()
    for frame in stack_frames(depth=depth):
        depth += 1
        glo, loc = frame.f_globals, frame.f_locals

        if glo.get('__name__') in skip_modules:
            continue
        if find_name and (find_name in glo and scope != 'locals' or find_name in loc and scope != 'globals'):
            break
        if max_depth and depth > max_depth:
            break
    # experienced strange overwrites of locals (e.g., self) when returning f_locals directly (adding .copy() fixed it)
    # check if f_locals is a dict (because enaml is using their DynamicScope object, which is missing a copy method)
    if isinstance(loc, dict):
        loc = loc.copy()
    return glo.copy(), loc, depth - 1


def sys_env_dict() -> dict[str, Any]:
    """ returns dict with python system run-time environment values.

    :return:                    python system run-time environment values like python_ver, argv, cwd, executable,
                                frozen and bundle_dir (if bundled with pyinstaller).

    .. hint:: see also https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
    """
    sed: dict[str, Any] = {
        'python ver': sys.version.replace('\n', ' '),
        'platform': os_platform,
        'argv': sys.argv,
        'executable': sys.executable,
        'cwd': os.getcwd(),
        'frozen': getattr(sys, 'frozen', False),
        'user name': os_user_name(),
        'host name': os_host_name(),
        'device id': os_device_id,
        'app_name_guess': app_name_guess(),
        'os env': mask_secrets(os.environ.copy()),
    }

    if sed['frozen']:
        sed['bundle_dir'] = getattr(sys, '_MEIPASS', '*#ERR#*')

    return sed


def sys_env_text(ind_ch: str = " ", ind_len: int = 12, key_ch: str = "=", key_len: int = 15,
                 extra_sys_env_dict: Optional[dict[str, str]] = None) -> str:
    """ compile a formatted text block with system environment info.

    :param ind_ch:              indent character (defaults to " ").
    :param ind_len:             indent depths (default=12 characters).
    :param key_ch:              key-value separator character (default="=").
    :param key_len:             key-name minimum length (default=15 characters).
    :param extra_sys_env_dict:  dict with additional system info items.
    :return:                    text block with system environment info.
    """
    sed = sys_env_dict()
    if extra_sys_env_dict:
        sed.update(extra_sys_env_dict)
    key_len = max([key_len] + [len(key) + 1 for key in sed])

    ind = ""
    text = "\n".join([f"{ind:{ind_ch}>{ind_len}}{key:{key_ch}<{key_len}}{val}" for key, val in sed.items()])

    return text


def to_ascii(unicode_str: str) -> str:
    """ converts Unicode string into ascii representation.

    useful for fuzzy string compare; inspired by MiniQuark's answer
    in: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string

    :param unicode_str:         string to convert.
    :return:                    converted string (replaced accents, diacritics, ... into normal ascii characters).
    """
    nfkd_form = unicodedata.normalize('NFKD', unicode_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).replace('ß', "ss").replace('€', "Euro")


def url_failure(url: str, timeout: Optional[float] = None) -> str:  # pylint: disable=too-many-return-statements
    """ determine if and why an FTP or HTTP[S] target is not available via a GET request.

    :param url:                 URL of an target|page|file to check (not downloaded, fetching only the header).
    :param timeout:             connection timeout in seconds (see :func:`urllib.request.urlopen`).
    :return:                    empty string if target header is available, else an error description. if an
                                FTP|HTTP response error occurred then the error/status code
                                will be returned in the first 3 characters.
    """
    # noinspection PyBroadException
    try:
        with urlopen(url, timeout=timeout) as response:             # open connection and read header
            status = response.getcode()                             # no need to call response.read()
            return "" if 200 <= status < 300 else f"{status} {mask_url(url)} {response.reason=}"

    except HTTPError as exception:
        return f"{exception.code} {mask_url(url)} raised HTTPError {exception.reason=}"

    except URLError as exception:
        err_prefix = f"996 {mask_url(url)} raised {exception.errno=} {exception.reason=};"
        if isinstance(exception.reason, socket.gaierror):
            return f"{err_prefix} could not resolve hostname"
        if isinstance(exception.reason, socket.timeout):
            return f"{err_prefix} connection timed out after {timeout} seconds"
        if isinstance(exception.reason, ssl.SSLCertVerificationError):
            return f"{err_prefix} SSL certificate verification failed"
        return f"{err_prefix} could not reach the server"

    except Exception:                                               # pylint: disable=broad-exception-caught
        return f"999 {mask_url(url)} raised unexpected exception"   # NOT put str(_exception) because contains password


def utc_datetime() -> datetime.datetime:
    """ return the current UTC timestamp as string (to use as suffix for file and variable/attribute names).

    :return:                    timestamp string of the actual UTC date and time.
    """
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def write_file(file_path: str, content: Union[str, bytes],
               extra_mode: str = "", encoding: Optional[str] = None, make_dirs: bool = False):
    """ (over)write the file specified by :paramref:`~write_file.file_path` with text or binary/bytes content.

    :param file_path:           file path/name to write the passed content into (overwriting any previous content!).
    :param content:             new file content passed either as string or as `bytes`. if a byte array gets passed,
                                then this method will automatically write the content as binary.
    :param extra_mode:          additional open mode flag characters. passed to the `mode` argument of :func:`open` if
                                this argument starts with 'a' or 'w', else this argument value will be appended to 'w'
                                before it gets passed to the `mode` argument of :func:`open`.
                                if the :paramref:`~write_file.content` is of the `bytes` type, then a 'b' character will
                                be automatically added to the `mode` argument of :func:`open` (if not already specified
                                in this argument).
    :param encoding:            encoding used to write/convert/interpret the file content to write.
    :param make_dirs:           pass True to automatically create not existing folders specified in
                                :paramref:`~write_file.file_path`.
    :raises FileExistsError:    if the file to write to exists already and is write-protected.
    :raises FileNotFoundError:  if parts of the file path do not exist.
    :raises OSError:            if :paramref:`~write_file.file_path` is misspelled or contains invalid characters.
    :raises PermissionError:    if the current OS user account lacks permissions to read the file content.
    :raises ValueError:         on decoding errors.

    to extend this function for Android 14+, see `<https://github.com/beeware/toga/pull/1158#issuecomment-2254564657>`__
    and `<https://gist.github.com/neonankiti/05922cf0a44108a2e2732671ed9ef386>`__
    Yes, to use ACTION_CREATE_DOCUMENT, you don't supply a URI in the intent. You wait for the intent result, and that
    will contain a URI which you can write to.
    See #1158 (comment - `<https://github.com/beeware/toga/pull/1158#issuecomment-2254564657>`__) for a link to a Java
    example, and #1158 (comment - `<https://github.com/beeware/toga/pull/1158#issuecomment-1446196973>`__) for how to
    wait for an intent result.
    Related german docs: `<https://developer.android.com/training/data-storage/shared/media?hl=de>`__
    """
    if make_dirs and (dir_path := os_path_dirname(file_path)):
        os.makedirs(dir_path, exist_ok=True)

    if isinstance(content, bytes) and 'b' not in extra_mode:
        extra_mode += 'b'

    if extra_mode == '' or extra_mode[0] not in ('a', 'w'):
        extra_mode = 'w' + extra_mode

    with open(file_path, mode=extra_mode, encoding=encoding) as file_handle:
        file_handle.write(content)


class ErrorMsgMixin:                                                # pylint: disable=too-few-public-methods
    """ mixin class providing sophisticated error message handling. """
    _err_msg: str = ""
    main_app = None
    po = dpo = vpo = print

    def __init__(self):
        try:
            from ae.core import main_app_instance       # type: ignore # pylint: disable=import-outside-toplevel

            self.main_app = main_app = main_app_instance()
            assert main_app is not None, f"{self.__class__.__name__}.__init__() called too early; main app instance not"

            self.po = main_app.po
            self.dpo = main_app.dpo
            self.vpo = main_app.vpo

        except (ImportError, AssertionError, Exception) as exc:                 # pylint: disable=broad-except
            print(f"{self.__class__.__name__}.__init__() raised {exc}; using print() instead of main app error loggers")

            # self.main_app = None
            # self.po = self.dpo = self.vpo = print

    @property
    def error_message(self) -> str:
        """ error message string if an error occurred or an empty string if not.

        :getter:                return the accumulated error message of the recently occurred error(s).
        :setter:                any assigned error message will be accumulated to recent error messages.
                                pass an empty string to reset the error message.
        """
        return self._err_msg

    @error_message.setter
    def error_message(self, next_err_msg: str):
        if next_err_msg:
            if "WARNING" in next_err_msg.upper():
                self.vpo(f" .::. {next_err_msg}")
            else:
                self.dpo(f" .::. {next_err_msg}")
            self._err_msg += ("\n\n" if self._err_msg else "") + next_err_msg
        else:
            self._err_msg = ""


# platform-specific patches
os_device_id = os_host_name()
""" user-definable id/name of the device, defaults to os_host_name() on most platforms, alternatives are:

on Android (check with adb shell 'settings get global device_name' and adb shell 'settings list global'):
    - Settings.Global.DEVICE_NAME (Settings.Global.getString(context.getContentResolver(), "device_name"))
    - android.os.Build.DEVICE/.MANUFACTURER/.BRAND/.HOST
    - DeviceName.getDeviceName()
on MS Windows:
    - os.environ['COMPUTERNAME']
on all other platforms:
    - socket.gethostname()
"""
if os_platform == 'android':                                        # pragma: no cover
    # determine Android device id because os_host_name() returns mostly 'localhost' and not the user-definable device id
    from jnius import autoclass                                     # type: ignore

    # noinspection PyBroadException
    try:
        Settings = autoclass('android.provider.Settings$Global')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        # mActivity inherits from Context so no need to cast('android.content.Context',..) neither get app context
        # _Context = autoclass('android.content.Context')
        # context = cast('android.content.Context', PythonActivity.mActivity)
        # context = PythonActivity.mActivity.getApplicationContext()
        context = PythonActivity.mActivity
        if _dev_id := Settings.getString(context.getContentResolver(), 'device_name'):
            os_device_id = defuse(_dev_id)

    except Exception:                                               # pylint: disable=broad-except
        pass

    # monkey patches the :func:`shutil.copystat` and :func:`shutil.copymode` helper functions, which are crashing on
    # 'android' (see # `<https://bugs.python.org/issue28141>`__ and `<https://bugs.python.org/issue32073>`__). these
    # functions are used by shutil.copy2/copy/copytree/move to copy OS-specific file attributes.
    # although shutil.copytree() and shutil.move() are copying/moving the files correctly when the copy_function
    # arg is set to :func:`shutil.copyfile`, they will finally also crash afterward when they try to set the attributes
    # on the destination root directory.
    shutil.copymode = dummy_function
    shutil.copystat = dummy_function


elif os_platform in ('win32', 'cygwin'):                            # pragma: no cover
    if _dev_id := os.environ.get('COMPUTERNAME'):
        os_device_id = defuse(_dev_id)
