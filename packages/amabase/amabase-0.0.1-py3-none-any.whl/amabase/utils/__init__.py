from __future__ import annotations

import argparse
import json
import logging
import logging.config
import os
import re
import secrets
import socket
import struct
import subprocess
import sys
from contextlib import AbstractContextManager
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from enum import Enum, Flag
from importlib import import_module
from io import BytesIO, StringIO, UnsupportedOperation
from pathlib import Path
from textwrap import dedent
from types import ModuleType
from typing import IO, Any, Callable, Iterator, Sequence
from uuid import UUID

_logger = logging.getLogger(__name__)

#region Color

class Color:
    RESET = '\033[0m'

    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    GRAY = LIGHT_BLACK = '\033[0;90m'
    BG_RED = '\033[0;41m'

    # Disable coloring if environment variable NO_COLORS is set to 1 or if stderr is piped/redirected
    NO_COLORS = False
    if os.environ.get('NO_COLORS', '').lower() in {'1', 'yes', 'true', 'on'} or not sys.stderr.isatty():
        NO_COLORS = True
        for _ in dir():
            if isinstance(_, str) and _[0] != '_' and _ not in ['NO_COLORS']:
                locals()[_] = ''

    # Set Windows console in VT mode
    if not NO_COLORS and sys.platform == 'win32':
        import ctypes
        _kernel32 = ctypes.windll.kernel32
        _kernel32.SetConsoleMode(_kernel32.GetStdHandle(-11), 7)
        del _kernel32

#endregion


#region Secrets

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def get_random_string(length: int, *, allowed_chars=RANDOM_STRING_CHARS):
    """
    Return a securely generated random string.

    The bit length of the returned value can be calculated with the formula:
        log_2(len(allowed_chars)^length)

    For example, with default `allowed_chars` (26+26+10), this gives:
      * length: 12, bit length =~ 71 bits
      * length: 22, bit length =~ 131 bits
    """
    return "".join(secrets.choice(allowed_chars) for _ in range(length))

#endregion


#region Datetime

def datetime_from_utc_timestamp(value: int|float|tuple[int|float,...]) -> datetime:
    if isinstance(value, tuple):
        value = value[0]
    if value is None:
        return None # pyright: ignore[reportReturnType]
    return datetime.fromtimestamp(value, tz=timezone.utc).astimezone() # pyright: ignore[reportArgumentType]


def is_iso_datetime(value: str|None):
    """
    Recognize if the given string value may be parsed as ISO datetime.
    
    This is used to handle datetime values (typically coming from APIs with JSON-encoded data) as datetimes, notably to perform CSV and JSON parsing and timezone handling.
    """
    return value is not None and re.match(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d{3,6})?(?:Z|[\+\-]\d{2}(?::?\d{2})?)?$', value)


def get_duration_str(duration: timedelta) -> str:
    # Adapted from: django.utils.duration.duration_iso_string
    if duration < timedelta(0):
        sign = "-"
        duration *= -1
    else:
        sign = ""

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = ".{:06d}".format(microseconds) if microseconds else ""
    return "{}P{}DT{:02d}H{:02d}M{:02d}{}S".format(
        sign, days, hours, minutes, seconds, ms
    )


def _get_duration_components(duration: timedelta):
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return days, hours, minutes, seconds, microseconds

#endregion


#region Sequence

def decode_sequence(value: str) -> list[str]:
    """
    Parse a sequence literal (expressed using PostgreSQL array syntax or JSON syntax) into a list.
    
    For PostgreSQL format, see https://www.postgresql.org/docs/current/arrays.html#ARRAYS-INPUT.
    """
    if not isinstance(value, str):
        raise TypeError(f"value: {type(value.__name__)}")

    if len(value) == 0:
        raise ValueError(f"Invalid sequence literal: empty string")
    elif value[0] == '[' and value[-1] == ']':
        return decode_json(value)
    elif not (value[0] == '{' and value[-1] == '}'):
        raise ValueError(f"Invalid sequence literal '{value}': must either start end end with square brackets (JSON syntax) or with accolades (PG syntax)")
        
    # From now on, we assume `value` is a PG literal

    def split(text: str):
        pos = 0

        def get_quoted_part(start_pos: int):
            nonlocal pos
            pos = start_pos
            while True:
                try:
                    next_pos = text.index('"', pos + 1)
                except ValueError:
                    raise ValueError(f"Unclosed quote from position {pos}: {text[pos:]}")
                
                pos = next_pos
                if text[pos - 1] == '\\' and (pos <= 2 or text[pos - 2] != '\\'): # escaped quote
                    pos += 1 # will search next quote
                else:
                    value = text[start_pos+1:pos]
                    pos += 1
                    if pos == len(text): # end
                        pass
                    else:
                        if text[pos] != ',':
                            raise ValueError(f"Quoted part \"{value}\" is followed by \"{text[pos]}\", expected a comma")
                        pos += 1
                    return value

        def get_unquoted_part(start_pos: int):
            nonlocal pos
            try:
                pos = text.index(',', start_pos)
                value = text[start_pos:pos]
                pos += 1
            except ValueError:
                pos = len(text) # end
                value = text[start_pos:]

            if value.lower() == 'null':
                return None
            return value

        def unescape(part: str|None):
            if part is None:
                return part
            return part.replace('\\"', '"').replace('\\\\', '\\')
        
        parts: list[str] = []
        while pos < len(text):
            char = text[pos]
            if char == ',':
                part = ''
                pos += 1
            elif char == '"':
                part = get_quoted_part(pos)
            elif char == '{':
                raise NotImplementedError("Cannot parse PostgreSQL sub array literals")
            else:
                part = get_unquoted_part(pos)
            parts.append(unescape(part)) # type: ignore (part not None so unescape cannot be None)

        return parts

    return split(value[1:-1])


def encode_sequence(values: list[Any]|tuple[Any]|set[Any]) -> str:
    """
    Convert a list, tuple or set into a string using PostgreSQL array syntax.
    
    For PostgreSQL format, see https://www.postgresql.org/docs/current/arrays.html#ARRAYS-INPUT.
    """    
    escaped: list[str] = []
    for value in values:
        if value is None:
            value = "null"
        elif isinstance(value, (list,tuple)):
            value = encode_sequence(value)
        else:
            if not isinstance(value, str):
                value = str(value)
            if value.lower() == "null":
                value = f'"{value}"'
            elif ',' in value or '"' in value or '\\' in value or '{' in value or '}' in value:
                value = '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
        escaped.append(value)

    return '{' + ','.join(escaped) + '}'

#endregion


#region JSON

class ExtendedJSONEncoder(json.JSONEncoder):
    """
    Adapted from: django.core.serializers.json.DjangoJSONEncoder
    
    Usage example: json.dumps(data, indent=4, cls=ExtendedJSONEncoder)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def default(self, o):
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:23] + r[26:]
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if o.tzinfo is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond and o.microsecond % 1000 == 0:
                r = r[:12]
            return f'T{r}'
        elif isinstance(o, timedelta):
            return get_duration_str(o)
        elif isinstance(o, (Decimal, UUID)):
            return str(o)
        else:
            try:
                from django.utils.functional import Promise  # type: ignore (optional dependency)
                if isinstance(o, Promise):
                    return str(o)
            except ModuleNotFoundError:
                pass

            if isinstance(o, (Enum,Flag)):
                return o.value
            elif isinstance(o, bytes):
                return str(o)
            elif not isinstance(o, type) and hasattr(o, 'to_jsondict'):
                result = o.to_jsondict() # pyright: ignore[reportAttributeAccessIssue]
                if not isinstance(result, dict):
                    raise TypeError(f"{type(o).__name__}.to_jsondict() method returned {type(result).__name__}, expected dict")
                return result
            else:
                return super().default(o)


class ExtendedJSONDecoder(json.JSONDecoder):
    def __init__(self, *, object_hook = None, **options):
        super().__init__(object_hook=object_hook or self._object_hook, **options)

    def _object_hook(self, data: dict):        
        for key, value in data.items():
            if isinstance(value, str) and is_iso_datetime(value):
                data[key] = datetime.fromisoformat(value)
        
        return data


def dump_json(data: Any, file: str|os.PathLike|IO[str], *, indent: int|None = None, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder] = ExtendedJSONEncoder, encoding = 'utf-8'):
    if cls is None:
        cls = ExtendedJSONEncoder

    _file_manager: AbstractContextManager[IO[str]]|None
    _file: IO[str]
    if isinstance(file, (str, os.PathLike)):
        parent = os.path.dirname(file)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        _file_manager = open(file, 'w', encoding=encoding)
        _file = _file_manager.__enter__()
    else:
        _file_manager = None # managed externally
        _file = file

    try:
        json.dump(data, _file, ensure_ascii=ensure_ascii, indent=None if indent == 0 else indent, sort_keys=sort_keys, cls=cls)
        if _file == sys.stdout or _file == sys.stderr:
            _file.write('\n')
    finally:
        if _file_manager:
            _file_manager.__exit__(None, None, None)


def load_json(file: str|os.PathLike|IO, *, encoding = 'utf-8', cls: type[json.JSONDecoder] = ExtendedJSONDecoder) -> Any:
    _file_manager: AbstractContextManager[IO]|None
    _file: IO
    if isinstance(file, (str, os.PathLike)):
        _file_manager = open(file, 'r', encoding=encoding)
        _file = _file_manager.__enter__()
    else:
        _file_manager = None # managed externally
        _file = file

    try:
        skip_utf8_bom(_file)
        return json.load(_file, cls=cls)
    finally:
        if _file_manager:
            _file_manager.__exit__(None, None, None)


def encode_json(data: Any, *, indent: int|None = None, sort_keys = False, ensure_ascii = False, cls: type[json.JSONEncoder] = ExtendedJSONEncoder) -> str:
    with StringIO() as fp:
        dump_json(data, fp, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii, cls=cls)
        return fp.getvalue()


def decode_json(data: str|bytes, *, cls: type[json.JSONDecoder] = ExtendedJSONDecoder) -> Any:
    with StringIO(data) if isinstance(data, str) else BytesIO(data) as fp:
        return load_json(fp, cls=cls)

#endregion


#region Tabulate

def tabulate(rows: Sequence[tuple|list], columns: list[str], sep: str = '  ') -> str:
    """Format a list of rows as a table.

    Each row is a tuple or list of values. The columns parameter is a list of column names.
    The sep parameter is the string used to separate columns (default: two spaces).
    """
    if not rows:
        return ''
    
    # Compute column widths
    col_widths = [len(col) for col in columns]
    for row in rows:
        for i, value in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(value)) if value is not None else 0)
    
    # Prepare format string
    fmt = sep.join(f'{{:{w}}}' for w in col_widths)

    # Prepare output
    output = []
    output.append(fmt.format(*columns))
    output.append(fmt.format(*['-' * w for w in col_widths]))
    for row in rows:
        output.append(fmt.format(*(str(v) if v is not None else '' for v in row)))
    
    return '\n'.join(output)

#endregion


#region Encoding

UTF8_BOM = '\ufeff'
UTF8_BOM_BINARY = UTF8_BOM.encode('utf-8')

SURROGATE_MIN_ORD = ord('\uDC80')
SURROGATE_MAX_ORD = ord('\uDCFF')


def skip_utf8_bom(fp: IO, encoding: str|None = None):
    """
    Skip UTF8 byte order mark, if any.
    - `fp`: open file pointer.
    - `encoding`: if given, do nothing unless encoding is utf-8 or alike.
    """
    if encoding and not encoding in {'utf8', 'utf-8', 'utf-8-sig'}:
        return False

    try:
        start_pos = fp.tell()
    except UnsupportedOperation: # e.g. empty file
        start_pos = 0

    try:
        data = fp.read(1)
    except UnsupportedOperation: # e.g. empty file
        return False
    
    if isinstance(data, str): # text mode
        if len(data) >= 1 and data[0] == UTF8_BOM:
            return True
        
    elif isinstance(data, bytes): # binary mode
        if len(data) >= 1 and data[0] == UTF8_BOM_BINARY[0]:
            data += fp.read(2) # type: ignore (data bytes => fp reads bytes)
            if data[0:3] == UTF8_BOM_BINARY:
                return True
    
    fp.seek(start_pos)
    return False

#endregion


#region Dotenv

def load_dotenv(path: os.PathLike|str|None = None, *, encoding = 'utf-8', override = False, parents = False) -> str|None:
    """
    Load `.env` from the given or current directory (or the given file if any) to environment variables.    
    If the given file is a directory, search `.env` in this directory.
    If `parents` is True, also search if parent directories until a `.env` file is found.

    Usage example:

    ```
    # Load configuration files
    load_dotenv() # load `.env` in the current working directory
    load_dotenv(os.path.dirname(__file__), parents=True) # load `.env` in the Python module installation directory or its parents
    load_dotenv(f'C:\\ProgramData\\my-app\\my-app.env' if sys.platform == 'win32' else f'/etc/my-app/my-app.env') # load `.env` in the system configuration directory
    ```
    """
    if not path:
        path = find_to_root('.env') if parents else '.env'
    elif os.path.isdir(path):
        path = find_to_root('.env', path) if parents else os.path.join(path, '.env')
    elif not os.path.isfile(path) and parents:
        path = find_to_root(os.path.basename(path), os.path.dirname(path))
        if not path: # not found
            return None
    elif isinstance(path, os.PathLike):
        path = str(path)
    elif not isinstance(path, str):
        raise TypeError('path')
    
    if not path or not os.path.isfile(path):
        return None # does not exist
        
    with open(path, 'r', encoding=encoding, newline=None) as fp:
        skip_utf8_bom(fp, encoding=encoding)
        for name, value in parse_properties(fp.read()):
            if not override:
                if name in os.environ:
                    continue
            os.environ[name] = value

    return path


def find_to_root(name: str, start_dir: str|os.PathLike|None = None) -> str|None:
    """
    Find the given file name from the given start directory (or current working directory if none given), up to the root.

    Return None if not found.
    """    
    if start_dir:            
        if not os.path.exists(start_dir):
            raise IOError('Starting directory not found')
        elif not os.path.isdir(start_dir):
            start_dir = os.path.dirname(start_dir)
    else:
        start_dir = os.getcwd()

    last_dir = None
    current_dir = os.path.abspath(start_dir)
    while last_dir != current_dir:
        path = os.path.join(current_dir, name)
        if os.path.exists(path):
            return path
        parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
        last_dir, current_dir = current_dir, parent_dir

    return None


def parse_properties(content: str) -> Iterator[tuple[str,str]]:
    """
    Parse properties/ini/env file content.
    """
    def find_nonspace_on_same_line(start: int):
        pos = start
        while pos < len(content):
            c = content[pos]
            if c == '\n' or not c.isspace():
                return pos
            else:
                pos += 1
        return None

    def find_closing_quote(start: int):
        """ Return the unquoted value and the next position """
        pos = content.find('"', start)
        if pos == -1:
            return content[start:], None
        elif pos+1 < len(content) and content[pos+1] == '"': # escaped
            begining_content = content[start:pos+1]
            remaining_content, remaining_pos = find_closing_quote(pos+2)
            return begining_content + remaining_content, remaining_pos
        else:
            return content[start:pos], pos

    name = None
    value = '' # value being build (or name being build if variable `name` is None)
    i = find_nonspace_on_same_line(0)
    while i is not None and i < len(content):
        c = content[i]
        if c == '"':
            unquoted, end = find_closing_quote(i+1)
            value += unquoted
            if end is None:
                return
            i = end + 1
        elif c == '=' and name is None:
            name = value
            value = ''
            i += 1
        elif c == '\n':
            if name or value:
                yield (name, value) if name is not None else (value, '')
            name = None
            value = ''
            i += 1            
        elif c == '#': # start of comment
            if name or value:
                yield (name, value) if name is not None else (value, '')
            name = None
            value = ''
            pos = content.find('\n', i+1)
            if pos == -1:
                return
            else:
                i = pos + 1
        elif c.isspace(): # start of whitespace
            end = find_nonspace_on_same_line(i+1)
            if value:
                if end is None or content[end] in ({'#', '\n', '='} if name is None else {'#', '\n'}):
                    pass # strip end
                else:
                    value += content[i:end]
            i = end
        else:
            value += c
            i += 1

    if name or value:
        yield (name, value) if name is not None else (value, '')

#endregion


#region Logging

def get_logging_config(*, level: str|None = None, names: bool|None = None):
    if level:
        level = level.upper()
    else:
        level = (os.environ.get('LOG_LEVEL') or 'INFO').upper()

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'without_names': { 'format': '%(levelname)s %(message)s' },
            'with_names': { 'format': f'%(levelname)s {Color.GRAY}[%(name)s]{Color.RESET} %(message)s' },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'with_names' if names else 'without_names',
                'level': level,
            },
        },
        'root': {
            'handlers': ['console'],
            'level': level,
        },
        'loggers': {
            'django': { 'level': 'INFO', 'propagate': False },
            'daphne': { 'level': 'INFO', 'propagate': False },
            'asyncio': { 'level': 'INFO', 'propagate': False },
            'urllib3': { 'level': 'INFO', 'propagate': False },
            'botocore': { 'level': 'INFO', 'propagate': False },
            'boto3': { 'level': 'INFO', 'propagate': False },
            's3transfer': { 'level': 'INFO', 'propagate': False },
            'PIL': { 'level': 'INFO', 'propagate': False },
            'celery.utils.functional': { 'level': 'INFO', 'propagate': False },
            'smbprotocol': { 'level': 'WARNING', 'propagate': False },
        },
    }


def configure_logging(config: dict|None = None, *, level: str|None, names: bool|None = False):
    if config is None:
        config = get_logging_config(level=level, names=names)
    elif not isinstance(config, dict):
        raise TypeError(f"Logging config: {type(config)} (expected a dict)")
    elif not 'root' in config:
        raise ValueError(f"Logging config: missing 'root' key")
    elif not 'handlers' in config:
        raise ValueError(f"Logging config: missing 'handlers' key")
        
    if level is not None:
        level = level.upper()
        config['root']['level'] = level
        if 'console' in config['handlers']:
            config['handlers']['console']['level'] = level

    if names is not None:
        if not 'console' in config['handlers']:
            raise ValueError("Logging config: cannot change console formatter: no 'handlers.console' key")
        if names:
            formatter = 'with_names'
        else:
            formatter = 'without_names'
        if not 'formatters' in config or not formatter in config:
            raise ValueError(f"Logging config: formatter: '{formatter}' not found")
        config['handlers']['console']['formatter'] = config['formatters'][formatter]

    logging.config.dictConfig(config)

    if not Color.NO_COLORS:
        logging.addLevelName(logging.DEBUG, f'{Color.GRAY}DEBU{Color.RESET}')
        logging.addLevelName(logging.INFO, f'{Color.CYAN}INFO{Color.RESET}')
        logging.addLevelName(logging.WARNING, f'{Color.YELLOW}WARN{Color.RESET}')
        logging.addLevelName(logging.ERROR, f'{Color.RED}ERRO{Color.RESET}')
        logging.addLevelName(logging.CRITICAL, f'{Color.BG_RED}CRIT{Color.RESET}')

    return config

#endregion


#region Commands

def add_command(subparsers: argparse._SubParsersAction, handle: Callable|ModuleType|type[object], *, name: str|None = None, add_arguments: Callable[[argparse.ArgumentParser],Any]|None = None, doc: str|None = None):
    # Prepare parameters
    if isinstance(handle, ModuleType):
        module = handle

        try:
            handle = getattr(handle, 'handle')
        except AttributeError:
            handle = getattr(handle, '_handle')

        if not name:
            parts = module.__name__.split('.')
            if len(parts) >= 2 and parts[-1] in {'command', 'commands'}:
                name = parts[-2].lower()
            else:
                name = parts[-1].lower()
                    
        if not add_arguments:
            add_arguments = getattr(handle, 'add_arguments', None)
            if not add_arguments:
                add_arguments = getattr(module, 'add_arguments', None)
    
        if not doc:
            doc = handle.__doc__
            if not doc:
                doc = module.__doc__
    
    elif isinstance(handle, type) and issubclass(handle, object):
        command_cls = handle
        command_instance = handle()
        handle = command_instance.handle # pyright: ignore[reportAttributeAccessIssue]
        
        if not name:
            name = command_cls.__name__.lower()
            name = name.removesuffix('command')
            if not name:
                parts = command_cls.__module__.split('.')
                if len(parts) >= 2 and parts[-1] in {'command', 'commands'}:
                    name = parts[-2].lower()
                else:
                    name = parts[-1].lower()
                    
        if not add_arguments:
            add_arguments = getattr(command_instance, 'add_arguments', None)
    
        if not doc:
            doc = handle.__doc__
            if not doc:
                doc = getattr(command_cls, 'help', command_cls.__doc__)

    else:
        if not name:
            name = handle.__name__.lower()

        if not add_arguments:
            add_arguments = getattr(handle, 'add_arguments', None)
    
        if not doc:
            doc = handle.__doc__

    # Register command
    cmdparser = subparsers.add_parser(name, help=get_help_text(doc), description=get_description_text(doc), formatter_class=argparse.RawTextHelpFormatter)
    if add_arguments:
        add_arguments(cmdparser)
    cmdparser.set_defaults(handle=handle)


def get_help_text(doc: str|None):
    if doc is None:
        return None
    
    doc = doc.strip()
    try:
        return doc[0:doc.index('\n')].strip()
    except:
        return doc
    

def get_description_text(doc: str|None):
    if doc is None:
        return None
    
    return dedent(doc)


def use_default_subparser(parser: argparse.ArgumentParser, name: str, args: Sequence[str]|None = None) -> Sequence[str]:
    """
    Add the given `name` as a default subparser if no subparse is selected in `args`.

    The result may be passed to `parse_args`.
    """
    if args is None:
        args = sys.argv[1:]

    help_option_strings = []
    option_string_nargs: dict[str,int|str|None] = {}
    subparser_names = []
    for action in parser._subparsers._actions: # type: ignore
        if isinstance(action, argparse._HelpAction):
            help_option_strings = action.option_strings
        elif isinstance(action, argparse._SubParsersAction):
            for sp_name in action._name_parser_map.keys():
                subparser_names.append(sp_name)
        else:
            for op_name in action.option_strings:
                option_string_nargs[op_name] = action.nargs

    target_args = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in help_option_strings:
            # Help: modify nothing
            return args
        
        elif arg in option_string_nargs:
            target_args.append(arg)            
            nargs = option_string_nargs[arg]
            if isinstance(nargs, int):
                for _ in range(nargs):
                    i += 1
                    arg = args[i]
                    target_args.append(arg)
            else:
                # Special option: modify nothing
                return args
            
        elif arg in subparser_names:
            # A subparser is given: modify nothing
            return args
        
        else:
            # Use default subparser
            target_args.append(name)
            while i < len(args):
                target_args.append(args[i])
                i += 1
            break

        i += 1

    return target_args

#endregion


#region Dependencies

def ensure_pip_dependency(modules: str|list[str]|dict[str,str|None], *, yes = False):
    if isinstance(modules, dict):
        _modules = modules
    elif isinstance(modules, str):
        _modules = {modules: None}
    else:
        _modules = {module: None for module in modules}

    missing_packages = []
    for module in _modules:
        try:
            import_module(module)
        except ModuleNotFoundError:
            package = _modules.get(module) or module.replace('_', '-')
            missing_packages.append(package)

    if not missing_packages:
        return False

    missing_packages_str = ' '.join(missing_packages)
    in_str = os.path.dirname(os.path.dirname(sys.executable))
    if not yes:
        response = input(f"Confirm installation of {Color.YELLOW}%s{Color.RESET} in %s? (y/N) " % (missing_packages_str, in_str))
        if response.lower() != 'y':
            sys.exit(1)

    _logger.info(f"Install %s in %s", missing_packages_str, in_str)
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
    return True

#endregion


#region Paths

def get_data_dir(prog: str, base_dir: str|os.PathLike|None = None, *, system = True) -> Path:
    # Use environment variable DATA_DIR if set
    if value := os.environ.get('DATA_DIR'):
        return Path(value).expanduser()

    # Use `data` subdirectory of BASE_DIR if it is not 'site-packages' (we then assume the application is not installed using PyPI: might be a source repository) 
    if base_dir:
        if not isinstance(base_dir, Path):
            base_dir = Path(base_dir)

        if base_dir.name != 'site-packages':
            return base_dir.joinpath('data')
    
    # Use system directory if possible
    if system:
        if sys.platform == 'win32':
            parent_dir = Path(f"{os.environ.get('SYSTEMDRIVE') or 'C'}:\\ProgramData")
        else:
            parent_dir = Path('/var/local/')
        
        if os.access(parent_dir, os.W_OK):
            return Path(parent_dir).joinpath(prog)
        
    # Use user directory otherwise
    parent_dir = Path(os.environ.get('APPDATA') or '~/.local/var').expanduser()
    return Path(parent_dir).joinpath(prog)

#endregion


#region Network

def get_linux_default_gateway_ip(iface: str|None = None):
    with open("/proc/net/route") as fp:
        for line in fp:
            fields = line.strip().split()
            
            if iface and fields[0] != iface:
                continue

            if fields[1] != '00000000' or not int(fields[3], 16) & 2: # if not default route or not RTF_GATEWAY, skip it
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

#endregion
