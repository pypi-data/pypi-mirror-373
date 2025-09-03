import argparse
from abc import abstractmethod, ABC
from collections.abc import Callable
from typing import Any, Sequence

from grading_tools.common.defaults import MinimalConfig, get_base_cfg, NamingDictionary

CommandName = str
CommandFunc = Callable[..., None]
ParserRegistration = Callable[[argparse.ArgumentParser, ...], None]


def merge_args(defaults: MinimalConfig, args: argparse.Namespace) -> MinimalConfig:
    nd = defaults['naming_dictionary']
    args_as_dict = vars(args)
    nd_dict = NamingDictionary.model_dump(nd, exclude_defaults=True, exclude_none=True)
    nd_dict.update({k: v for k, v in args_as_dict.items() if k in NamingDictionary.model_fields})
    return defaults | {'naming_dictionary': NamingDictionary.model_validate(nd_dict, strict=False)} | args_as_dict


class CommandModule(ABC):

    @property
    def additional_config(self) -> dict[str, Any]:
        return {}

    @property
    @abstractmethod
    def module_name(self) -> str:
        pass

    @property
    @abstractmethod
    def commands(self) -> list[tuple[CommandName, ParserRegistration, CommandFunc]]:
        pass

    @property
    def module_properties(self) -> dict[str, Any]:
        return {}

    def register_module(self, parser: argparse.ArgumentParser, **defaults) -> None:
        pass

    def register_command_base(self, parser: argparse.ArgumentParser, **defaults) -> None:
        pass

    def __init__(self, default_config: MinimalConfig | None = None) -> None:
        self.default_config: MinimalConfig = default_config if default_config is not None else get_base_cfg()

    def as_top_level(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(self.module_name)
        self.register(parser)
        return parser

    def register(self, parser: argparse.ArgumentParser):
        neat: bool = self.module_properties.get('neat', True)
        force_subparsers: bool = self.module_properties.get('force_subparsers', False)

        self.register_module(parser, **self.default_config)
        if len(self.commands) > 1 or force_subparsers or not neat:
            commands_parser = parser.add_subparsers(title='commands', dest='command', required=True)
            for name, register_command, command in self.commands:
                p = commands_parser.add_parser(name)
                self.register_command_base(p, **self.default_config)
                register_command(p, **self.default_config)

                def with_args(args: argparse.Namespace, cmd=command, cfg=dict(self.default_config)):
                    cmd(**merge_args(cfg, args))

                p.set_defaults(func=with_args)
        else:
            assert len(self.commands) == 1
            (name, register_command, command) = self.commands[0]
            self.register_command_base(parser, **self.default_config)
            register_command(parser, **self.default_config)
            parser.set_defaults(func=lambda args: command(**merge_args(self.default_config, args)))

    def as_program(self, name: str) -> 'CliProgram':
        return CliProgram(name, self.__class__)


class CliProgram:

    def __init__(self, program_name: str, *module_classes: type[CommandModule],
                 default_config: MinimalConfig | None = None):
        self.program_name: str = program_name
        self.module_classes: tuple[type[CommandModule], ...] = module_classes
        self.default_config: MinimalConfig = default_config if default_config is not None else get_base_cfg()

    def make_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(self.program_name)
        modules_parser = parser.add_subparsers(title='modules', dest='module', required=True)
        for module_cls in self.module_classes:
            module = module_cls(self.default_config)
            module.default_config |= module.additional_config
            module_parser = modules_parser.add_parser(module.module_name)
            module.register(module_parser)
        return parser

    def parse_and_run(self, args: Sequence[str] | None = None) -> None:
        args = self.make_parser().parse_args(args)
        args.func(args)
