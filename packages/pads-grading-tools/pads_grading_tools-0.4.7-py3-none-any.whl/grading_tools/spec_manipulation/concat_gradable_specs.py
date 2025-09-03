import argparse
import glob
import itertools
import os
import pathlib
from collections import defaultdict
from typing import Any
import yaml
import jsonmerge

from grading_tools.common.commands import CommandModule
from grading_tools.common.gradable_spec import GradableSpecV1


def mk_merge_schema(depth: int):
    schema = {"type": "object",
              "properties": {
                  "tree-level-names": {
                      "items": {
                          "mergeStrategy": "override"
                      }
                  },
                  "tree": {
                      "properties": {}
                  }}}
    rec = schema["properties"]["tree"]
    for _ in range(depth):
        rec["properties"] = {}
        rec["properties"]["children"] = {
            "mergeStrategy": "append",  # Recursively merge nested objects
            "items": {

            }
        }
        rec = rec["properties"]["children"]["items"]
    return schema


def concat_specs(spec_files: list[str] = None, output_file: str = None, max_depth: int = None, **config):
    specs = []
    for spec_file in spec_files:
        with open(spec_file, 'r') as f:
            specs.append(yaml.load(f, yaml.FullLoader))

    merger = jsonmerge.Merger(mk_merge_schema(max_depth))
    head = specs[0]
    for s in specs[1:]:
        head = merger.merge(head, s)
    result = head

    if (dir_name := os.path.dirname(output_file)) != '':
        os.makedirs(dir_name, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(dict(result), f, sort_keys=False)


def register_parser_concat(parser: argparse.ArgumentParser, **defaults):
    parser.add_argument('-o', '--output', required=False, help='Filename of the output.', dest='output_file',
                        default=defaults['DEFAULT_OUTPUT_FILE'])
    parser.add_argument('-s', '--spec-files', type=str, required=True, nargs='+',
                        help='Path to the specs to concatenate.')
    parser.add_argument('-md', '--max-depth', type=int, required=False, help='Maximum depth to merge nodes at',
                        default=defaults['DEFAULT_MAX_DEPTH'])


class ConcatSpecs(CommandModule):
    module_name = 'concat-specs'
    commands = [('concat', register_parser_concat, concat_specs)]

    @property
    def additional_config(self) -> dict[str, Any]:
        nd = self.default_config['naming_dictionary']

        return {
            'DEFAULT_OUTPUT_FILE': 'specs-concat.yaml',
            'DEFAULT_TREE_LEVEL_NAMES': ['Assignment', 'Question', 'Subquestion', 'Grading Key'],
            'DEFAULT_MAX_DEPTH': 6
        }


if __name__ == '__main__':
    ConcatSpecs().as_program('gen').parse_and_run()
