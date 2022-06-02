"""jc - JSON Convert `postconf -M` command output parser

Usage (cli):

    $ postconf -M | jc --postconf

    or

    $ jc postconf -M

Usage (module):

    import jc
    result = jc.parse('postconf', postconf_command_output)

Schema:

    [
      {
        "service_name":                     string,
        "service_type":                     string,
        "private":                          boolean/null,  # [0]
        "unprivileged":                     boolean/null,  # [0]
        "chroot":                           boolean/null,  # [0]
        "wake_up_time":                     integer,       # [1]
        "no_wake_up_before_first_use":      boolean/null,  # [2]
        "process_limit":                    integer,       # [1]
        "command":                          string
      }
    ]

    [0] '-' converted to null/None
    [1] '-' converted to -1
    [2] null/None if `wake_up_time` is null/None

Examples:

    $ postconf | jc --postconf -p
    []

    $ postconf | jc --postconf -p -r
    []
"""
from typing import List, Dict
import jc.utils
from jc.parsers.universal import simple_table_parse


class info():
    """Provides parser metadata (version, author, etc.)"""
    version = '1.0'
    description = '`postconf -M` command parser'
    author = 'Kelly Brazil'
    author_email = 'kellyjonbrazil@gmail.com'
    compatible = ['linux']
    magic_commands = ['postconf -M']


__version__ = info.version


def _process(proc_data: List[Dict]) -> List[Dict]:
    """
    Final processing to conform to the schema.

    Parameters:

        proc_data:   (List of Dictionaries) raw structured data to process

    Returns:

        List of Dictionaries. Structured to conform to the schema.
    """
    for item in proc_data:
        if item['private'] == '-':
            item['private'] = None
        else:
            item['private'] = jc.utils.convert_to_bool(item['private'])

        if item['unprivileged'] == '-':
            item['unprivileged'] = None
        else:
            item['unprivileged'] = jc.utils.convert_to_bool(item['unprivileged'])

        if item['chroot'] == '-':
            item['chroot'] = None
        else:
            item['chroot'] = jc.utils.convert_to_bool(item['chroot'])

        if item['wake_up_time'].endswith('?'):
            item['no_wake_up_before_first_use'] = True
        else:
            item['no_wake_up_before_first_use'] = False

        if item['wake_up_time'] == '-':
            item['wake_up_time'] = -1
        else:
            item['wake_up_time'] = jc.utils.convert_to_int(item['wake_up_time'])

        if item['process_limit'] == '-':
            item['process_limit'] = -1
        else:
            item['process_limit'] = jc.utils.convert_to_int(item['process_limit'])

    return proc_data


def parse(
    data: str,
    raw: bool = False,
    quiet: bool = False
) -> List[Dict]:
    """
    Main text parsing function

    Parameters:

        data:        (string)  text data to parse
        raw:         (boolean) unprocessed output if True
        quiet:       (boolean) suppress warning messages if True

    Returns:

        List of Dictionaries. Raw or processed structured data.
    """
    jc.utils.compatibility(__name__, info.compatible, quiet)
    jc.utils.input_type_check(data)

    raw_output: List = []

    if jc.utils.has_data(data):
        table = ['service_name service_type private unprivileged chroot wake_up_time process_limit command']
        data_list = list(filter(None, data.splitlines()))
        table.extend(data_list)
        raw_output = simple_table_parse(table)

    return raw_output if raw else _process(raw_output)
