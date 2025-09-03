import argparse
import itertools
import typing
from collections.abc import Iterable
from typing import Sequence

import pydantic
import yaml

from grading_tools import mk_cli_program
from grading_tools.common.commands import CommandModule, CliProgram
from grading_tools.common.defaults import NamingDictionary, get_base_cfg

OptionsList = list[str]


class Flags(typing.TypedDict, total=False):
    options: OptionsList | None


CommandArgs = Flags
ModuleArgs = dict[str, CommandArgs]


class FileCFG(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra='allow')

    naming_dictionary: NamingDictionary = pydantic.Field(default_factory=NamingDictionary)
    arguments: CommandArgs | ModuleArgs = pydantic.Field(default_factory=dict)


def dig_dict(dic: dict, keys: Iterable[str]) -> dict:
    res = dic
    i = 0
    for k in keys:
        if k in res:
            i += 1
        res = res.get(k, {})
    return res


def expand_flag(flag: tuple[str, str | list[str]]) -> tuple[str, ...]:
    k, v = flag
    if v is None or v == 'null':
        return (k,)
    if isinstance(v, str):
        return k, v
    elif isinstance(v, list):
        return (k,) + tuple(v)
    else:
        return k, str(v)


def call(config_file: str = None, command: list[str] = None, path: list[list[str]] = None, remainder: list[str] = None,
         **config):
    cfg: FileCFG
    with open(config_file, 'r') as f:
        cfg = FileCFG.model_validate(yaml.full_load(f))

    if len(path) == 0:
        path = [[]]

    configured_arguments = {}
    for path_ in path:
        specific_args = dig_dict(cfg.arguments, itertools.chain(command, path_))

        if not specific_args:
            print(f'There is no config for {command} under path {path_} in the cfg file: {config_file}.')

        configured_arguments.update(specific_args)

    arg_list = list(command)

    if 'options' in configured_arguments:
        options = configured_arguments.pop('options')
        arg_list.extend(options)

    arg_list.extend(itertools.chain(*(expand_flag(flag) for flag in configured_arguments.items())))

    if remainder:
        arg_list.extend(remainder)

    merged_naming_dictionary = NamingDictionary(
        **get_base_cfg().get('naming_dictionary', {}).model_dump(exclude_defaults=True, exclude_unset=True))

    cli_program = mk_cli_program(default_config={'naming_dictionary': merged_naming_dictionary})

    cli_program.parse_and_run(arg_list)


def register_parser(parser: argparse.ArgumentParser, **defaults):
    parser.add_argument('-cfg', '--config-file', type=str, help='Path to the configuration file.', required=True)
    parser.add_argument('-cmd', '--command', type=str, help='The command to execute.', required=True, nargs='+')
    parser.add_argument('-p', '--path', type=str,
                        help='Optionally, a path to the specific config for the command. If this argument is used multiple times, the configs are applied in order, i.e., potentially overriding the previous ones. This allows creating shared base configs.',
                        required=False, nargs='+', default=[], action='append')
    # + 'remainder' which is set explicitly


class FromCfg(CommandModule):
    module_name = 'from-cfg'
    commands = [('from-cfg', register_parser, call)]


class CfgProgram(CliProgram):

    def parse_and_run(self, args: Sequence[str] | None = None) -> None:
        args, extra = self.make_parser().parse_known_args(args)
        args.remainder = extra
        args.func(args)


def mk_cfg_cli_program():
    return CfgProgram('from-cfg', FromCfg, *mk_cli_program().module_classes)


if __name__ == '__main__':
    mk_cfg_cli_program().parse_and_run()
