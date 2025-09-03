import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from grading_tools.common.commands import CommandModule
from grading_tools.common.defaults import *
from grading_tools.common.excel_utils import write_table_to_excel
from grading_tools.common.compat_utils import stringify_scores_for_moodle
from grading_tools.common.utils import read_moodle_csv, write_moodle_csv, read_generic_table


def print_rows_pretty(df, new_scores, naming_dictionary: NamingDictionary):
    print_df = pd.DataFrame(df[[naming_dictionary.MOODLE_MATR_COL] + list(naming_dictionary.MOODLE_IDENTITY_COLS)])
    print_df['OLD score'] = df[naming_dictionary.MOODLE_GRADING_COL]
    print_df['NEW score'] = new_scores
    print(print_df.reset_index(drop=True))


# misc


def join_moodle_and_scores(grading_file: str, moodle_grading_worksheet: str, group_name_fmt: str,
                           naming_dictionary: NamingDictionary, **config) -> tuple[pd.DataFrame, list[str]]:
    if config['verbose']:
        print('Configuration:')
        print(config)

    grading_column = config['grading_column']
    feedback_column = config['feedback_column']
    grading_df = read_generic_table(grading_file, sheet_name=config.pop('grading_sheet', None),
                                    table_name=config.pop('grading_table', None))
    moodle_df = read_moodle_csv(moodle_grading_worksheet)
    original_cols = moodle_df.columns

    # group id (number) vs. string wrangling
    formatted_group_names = pd.Series(
        grading_df[naming_dictionary.GRADING_GROUP_ID_COL].apply(lambda i: group_name_fmt.format(i)),
        name=naming_dictionary.MOODLE_GROUP_COL)
    group_scores_df = grading_df[[naming_dictionary.GRADING_GROUP_ID_COL, grading_column] + (
        [feedback_column] if feedback_column else [])].set_index(formatted_group_names)

    merged_df = moodle_df.merge(group_scores_df, on=naming_dictionary.MOODLE_GROUP_COL, how='left')
    merged_df[naming_dictionary.GRADING_GROUP_ID_COL] = merged_df[naming_dictionary.GRADING_GROUP_ID_COL].astype(
        pd.Int64Dtype())

    rows_with_total_score = merged_df[grading_column].notna()

    return merged_df.loc[rows_with_total_score], original_cols


# unused
def join_and_create_overview(output_file: str, naming_dictionary: NamingDictionary, **config):
    updated_df, _ = join_moodle_and_scores(naming_dictionary=naming_dictionary, **config)
    write_table_to_excel(output_file, naming_dictionary.OVERVIEW_TABLE_NAME, updated_df)


def join_and_export(output_file: str, grading_column: str, feedback_column: str, naming_dictionary: NamingDictionary,
                    **config):
    updated_df, original_cols = join_moodle_and_scores(grading_column=grading_column, feedback_column=feedback_column,
                                        naming_dictionary=naming_dictionary, **config)

    # decimal representation wrangling

    stringified_scores_col = stringify_scores_for_moodle(updated_df[grading_column], naming_dictionary)

    changed_rows_idx = updated_df[naming_dictionary.MOODLE_GRADING_COL] != stringified_scores_col

    overridden_rows_idx = changed_rows_idx & updated_df[naming_dictionary.MOODLE_GRADING_COL].notna()

    changed_rows = updated_df.loc[changed_rows_idx]
    if len(changed_rows) > 0:
        if config['verbose']:
            print('Listing changed rows:')
            print_rows_pretty(changed_rows, stringified_scores_col.loc[changed_rows_idx],
                              naming_dictionary=naming_dictionary)
        if config['export_diffs']:
            changed_rows_file = Path(output_file).parent.joinpath('changed_rows.csv').resolve()
            changed_rows.to_csv(changed_rows_file)

    overwritten_rows = updated_df.loc[overridden_rows_idx]
    if len(overwritten_rows) > 0:
        if config['verbose']:
            print('Listing overwritten rows:')
            print_rows_pretty(overwritten_rows, stringified_scores_col.loc[overridden_rows_idx],
                              naming_dictionary=naming_dictionary)

        if config['export_diffs']:
            overwritten_rows_file = Path(output_file).parent.joinpath('overwritten_rows.csv').resolve()
            overwritten_rows.to_csv(overwritten_rows_file)

    # update
    updated_df[naming_dictionary.MOODLE_GRADING_COL] = stringified_scores_col
    if feedback_column:
        updated_df[naming_dictionary.MOODLE_FEEDBACK_COL] = updated_df[feedback_column]

    # select the columns for final export
    if config.get('allow_column_cleaning'):
        export_df = updated_df[[naming_dictionary.MOODLE_MATR_COL] + list(naming_dictionary.MOODLE_IDENTITY_COLS) + [
            naming_dictionary.MOODLE_GRADING_COL, naming_dictionary.MOODLE_FEEDBACK_COL]]
    else:
        export_df = updated_df[original_cols]

    write_moodle_csv(export_df, output_file)
    print(f'Exported {len(changed_rows)} scores into {output_file} ({len(overwritten_rows)} overwritten).')


def configure_parser(parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults):
    parser.add_argument('-o', '--output', required=False, help='Path to output csv file.', dest='output_file',
                        default=defaults['DEFAULT_OUTPUT_FILE_NAME'])
    parser.add_argument('-m', '--moodle-grading-worksheet', required=True, help='Path to moodle grading im/export worksheet (a csv file).')
    parser.add_argument('-mgc', '--moodle-grading-column', required=False,
                        help='Name of the grading aspect column in the moodle file.', dest='MOODLE_GRADING_COL',
                        default=naming_dictionary.MOODLE_GRADING_COL)
    parser.add_argument('-mfc', '--moodle-feedback-column', required=False,
                        help='Name of the feedback column in the moodle file.', dest='MOODLE_FEEDBACK_COL',
                        default=naming_dictionary.MOODLE_FEEDBACK_COL)

    parser.add_argument('-g', '--grading-file', required=True, help='Path to grading file with group scores.')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-sh', '--grading-sheet', required=False, help='Optionally, excel sheet within grading file.')
    group.add_argument('-t', '--grading-table', required=False, help='Optionally, excel table within grading file.',
                       default=naming_dictionary.GRADING_TABLE_NAME)

    parser.add_argument('-gc', '--grading-column', required=False,
                        help='Name of the grading aspect column in the grading/scores file.',
                        default=naming_dictionary.GRADING_TOTAL_COL)
    parser.add_argument('-gfc', '--feedback-column', required=False,
                        help='Name of the feedback column in the grading/scores file.', default=None)

    parser.add_argument('-gfmt', '--group-name-fmt', required=True,
                        help='Format str to recreate the group names used in moodle group creation (in Python style, e.g., "Group A1 {:02}").')

    parser.add_argument('-acc', '--allow-column-cleaning', required=False, action='store_true', default=False,
                        help='Whether the exported table can be cleaned up. By default, the original columns of the moodle file are preserved, to not support the upload in the grading table upload in the, e.g., assignment activity itself.')
    parser.add_argument('-v', '--verbose', required=False, action='store_true', default=False,
                        help='Whether to produce more verbose output.')
    parser.add_argument('-exd', '--export-diffs', required=False,
                        help='Whether to export tables of changed/overwritten scores (includes initially unset scores).')


class GenGroupUpload(CommandModule):
    module_name = 'gen-group-upload'
    commands = [('scores', configure_parser, join_and_export)]

    @property
    def additional_config(self) -> dict[str, Any]:
        return {'USED_JOIN_COL': 'MOODLE_GROUP_COL',
                'DEFAULT_OUTPUT_FILE_NAME': f'moodle_upload_{datetime.now().strftime("%Y_%m_%d_%H_%M")}.csv'}


if __name__ == '__main__':
    GenGroupUpload().as_program('gen').parse_and_run()
