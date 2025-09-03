import argparse
import itertools
import os.path
from typing import Any

import pandas as pd

from grading_tools.common.commands import CommandModule
from grading_tools.common.defaults import NamingDictionary
from grading_tools.common.gradable_spec import load_spec
from grading_tools.common.utils import read_generic_table
from grading_tools.grading_table_gen.gen_grading_table import save_grading_table, \
    register_gen_grading_table_options
from grading_tools.grading_table_gen.grading_table_commons import mk_node_name


def read_stripped_df(file_name: str, index_columns: list[str], question_columns: list[str],
                     naming_dictionary: NamingDictionary) -> pd.DataFrame:
    df = read_generic_table(file_name, table_name=naming_dictionary.GRADING_TABLE_NAME)
    filtered_columns = [c for c in df.columns if c in set(question_columns)]
    df = df.set_index(index_columns, drop=True)
    df = df[filtered_columns]  # .astype('Float64')
    stripped = df.dropna(axis='columns', how='all').dropna(axis='rows', how='all')
    return stripped


def read_merge_pattern(merge_pattern: str) -> list[list[int]]:
    pattern = [[int(s.strip()) for s in row.split(' ')] for row in merge_pattern.split('/')]
    assert all(len(row) > 0 for row in pattern)
    return pattern


def merge_dfs(df_table: list[list[pd.DataFrame]]) -> pd.DataFrame:
    merged_row_dfs = []
    for row in df_table:
        merged_row_df = pd.concat(row, axis='columns', join='outer', verify_integrity=True)
        merged_row_dfs.append(merged_row_df)
    merged_df = pd.concat(merged_row_dfs, axis='index', verify_integrity=True)
    return merged_df


def assert_non_overlapping(df_table: list[list[pd.DataFrame]]):
    idx_sets = []
    for row in df_table:
        sets = [set(df.columns) for df in row]
        # mutually disjoint
        assert all(set.isdisjoint(a, b) for a, b in itertools.combinations(sets,
                                                                           2)), 'The columns of the individual grading table columns within a merged row must be disjoint. This is to ensure no values are accidentally overwritten.'
        idx_sets.append(set.union(*(set(df.index) for df in row)))
    assert all(set.isdisjoint(a, b) for a, b in itertools.combinations(idx_sets,
                                                                       2)), 'The indices of the individual grading table rows must be disjoint. This is to ensure no values are accidentally overwritten.'


def apply_pattern(dfs: list[pd.DataFrame], pattern: list[list[int]]) -> list[list[pd.DataFrame]]:
    return [[dfs[i] for i in row] for row in pattern]


def merge_grading(merge_pattern: str = None, files: list[str] = None, spec_file: str = None,
                  index_columns: list[str] = None,
                  naming_dictionary: NamingDictionary = None, **config):
    spec = load_spec(spec_file)

    # the condition skips any skippable, e.g., total/summary nodes
    question_columns = [mk_node_name(n) for n in spec.tree.leaves_iter() if not n.get_property('skip')]

    pattern = read_merge_pattern(merge_pattern)
    dfs = [read_stripped_df(f, index_columns, question_columns, naming_dictionary) for f in files]
    df_table = apply_pattern(dfs, pattern)

    assert_non_overlapping(df_table)
    merged_df = merge_dfs(df_table)

    if config['verbose']:
        print('Merged DF')
        print(merged_df)

    save_grading_table(spec, data_df=merged_df, output_sheet=naming_dictionary.GRADING_SHEET_NAME,
                       output_table=naming_dictionary.GRADING_TABLE_NAME, naming_dictionary=naming_dictionary, **config)


def update_grading(spec_file: str = None, grading_file: str = None, **config):
    if not config.get('output_file'):
        config['output_file'] = os.path.splitext(grading_file)[0] + '-updated.xlsx'
    merge_grading(merge_pattern='0', spec_file=spec_file, files=[grading_file], **config)


MERGE_PATTERN_REGEX = r'(\d+)(\s+(\d+))*(\/(\d+)(\s+(\d+))*)*'


def register_parser_merge(parser: argparse.ArgumentParser, **defaults):
    parser.add_argument('-o', '--output', required=False, help='Filename of the output.', dest='output_file')
    parser.add_argument('-s', '--spec-file', type=str, required=True,
                        help='Path to the specification of the resulting gradable.')
    parser.add_argument('-f', '--files', type=str, nargs='+', required=True, help='Paths to the files to merge.')
    parser.add_argument('-mp', '--merge-pattern', required=True,
                        help=f'String specifying the merge pattern. Format: "{MERGE_PATTERN_REGEX}", e.g., "1 0 2/3" will merge the files with indices 1, 0 and 2 horizontally, i.e., join them, and then merge file 3 onto the result vertically, i.e., by row concatenation.',
                        default=defaults['DEFAULT_MERGE_PATTERN'])

    parser.add_argument('-ic', '--index-columns', nargs='*', required=False,
                        help='The column names to use as the index. Used for joining, as well as creation of the resulting grading table.',
                        default=defaults['DEFAULT_INDEX_COLUMNS'])

    register_gen_grading_table_options(parser, **defaults)


def register_parser_update(parser: argparse.ArgumentParser, **defaults):
    parser.add_argument('-o', '--output', required=False, help='Filename of the output.', dest='output_file')
    parser.add_argument('-s', '--spec-file', type=str, required=True,
                        help='Path to the updated specification of this gradable.')
    parser.add_argument('-g', '--grading-file', required=True, help='Path to the grading file to update.')

    parser.add_argument('-ic', '--index-columns', nargs='*', required=False,
                        help='The column names to use as the index. Used for joining, as well as creation of the resulting grading table.',
                        default=defaults['DEFAULT_INDEX_COLUMNS'])

    register_gen_grading_table_options(parser, **defaults)


class EditGradingTable(CommandModule):
    module_name = 'edit-grading'
    commands = [('merge', register_parser_merge, merge_grading), ('update', register_parser_update, update_grading)]

    @property
    def additional_config(self) -> dict[str, Any]:
        nd = self.default_config['naming_dictionary']
        return {'DEFAULT_MERGE_PATTERN': '0', 'DEFAULT_INDEX_COLUMNS': list(nd.IDENTITY_COLS) + [nd.MATR_COL]} | {
            'DEFAULT_OUTPUT_FILENAME': ''}


if __name__ == '__main__':
    EditGradingTable().as_program('edit-grading').parse_and_run()
