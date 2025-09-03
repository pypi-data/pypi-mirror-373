import argparse
import pathlib
from typing import Any

import pandas as pd

from grading_tools.common.commands import CommandModule
from grading_tools.common.defaults import NamingDictionary
from grading_tools.common.excel_utils import write_to_excel, write_table_helper
from grading_tools.common.utils import read_moodle_students_csv


def find_group_index(full_groups_lists_df: pd.DataFrame, group_name: str) -> int:
    matching_cols = full_groups_lists_df[full_groups_lists_df == group_name]
    return matching_cols.index[0] if len(matching_cols) > 0 else pd.NA


def gen_group_info_table(output_file: str, moodle_students_list: str, group_formats: list[str],
                         naming_dictionary: NamingDictionary, grouping_names: list[str] | None = None, **config):
    moodle_df = read_moodle_students_csv(moodle_students_list)

    moodle_df['GroupsList'] = moodle_df[naming_dictionary.MOODLE_GROUPS_GROUPS_COL].map(
        lambda s: [str.strip(g) for g in s.split(',')],
        na_action='ignore')
    exploded = moodle_df.explode('GroupsList', ignore_index=True)

    groupings = list(
        zip(grouping_names, group_formats) if grouping_names is not None else ((f'Grouping {i}', f) for i, f in
                                                                               enumerate(group_formats,
                                                                                         start=1)))
    full_groups_lists_df = pd.DataFrame(
        {g: [str.format(f, j) for j in range(0, 1000)] for g, f in groupings},
        index=range(0, 1000))

    grouping_info_cols = []
    for grouping in full_groups_lists_df.columns:
        all_groups_in_grouping = full_groups_lists_df[grouping]
        exploded[grouping] = exploded['GroupsList'].where(exploded['GroupsList'].isin(all_groups_in_grouping),
                                                          inplace=False)
        exploded[grouping + ' ID'] = exploded[grouping].map(lambda v: find_group_index(all_groups_in_grouping, v))
        grouping_info_cols.extend([grouping, grouping + ' ID'])

    # joining back together

    tables = [
        moodle_df.set_index(naming_dictionary.MOODLE_GROUPS_MATR_COL)[
            list(naming_dictionary.MOODLE_GROUPS_IDENTITY_COLS)]]
    for grouping in full_groups_lists_df.columns:
        tables.append(
            exploded.loc[exploded[grouping].notna(), [naming_dictionary.MOODLE_GROUPS_MATR_COL, grouping,
                                                      grouping + ' ID']].set_index(
                naming_dictionary.MOODLE_GROUPS_MATR_COL))
    group_info_df = pd.concat(tables, axis='columns', ignore_index=False).reset_index(drop=False)
    group_info_df.index.name = 'No'
    group_info_df.columns = [naming_dictionary.MATR_COL, naming_dictionary.FIRST_NAME_COL,
                             naming_dictionary.LAST_NAME_COL] + grouping_info_cols
    group_info_df = pd.DataFrame(group_info_df, columns=list(naming_dictionary.IDENTITY_COLS) + [
        naming_dictionary.MATR_COL] + grouping_info_cols)

    def my_write(exwr: pd.ExcelWriter):
        group_info_table_name = naming_dictionary.GROUPS_INFO_TABLE_NAME
        if config['verbose']:
            print(group_info_df)
        write_table_helper(exwr, group_info_df, group_info_table_name)

        for grouping, _ in groupings:
            grouping_table = group_info_df[group_info_df[grouping].notna()][
                list(naming_dictionary.IDENTITY_COLS) + [naming_dictionary.MATR_COL] + [grouping,
                                                                                        grouping + ' ID']].reset_index(
                drop=True)
            grouping_table.columns = list(naming_dictionary.IDENTITY_COLS) + [naming_dictionary.MATR_COL] + [
                naming_dictionary.GRADING_GROUP_NAME_COL, naming_dictionary.GRADING_GROUP_ID_COL]
            grouping_table.index.name = 'No'
            grouping_table_name = grouping.replace(' ', '_')
            if config['verbose']:
                print(grouping_table)
            write_table_helper(exwr, grouping_table, grouping_table_name)

            groups_df = grouping_table[
                [naming_dictionary.GRADING_GROUP_NAME_COL, naming_dictionary.GRADING_GROUP_ID_COL]]
            groups_df = groups_df.groupby(
                [naming_dictionary.GRADING_GROUP_NAME_COL, naming_dictionary.GRADING_GROUP_ID_COL],
                group_keys=True).agg(**{'Member Count': pd.NamedAgg(naming_dictionary.GRADING_GROUP_NAME_COL, 'count')})
            groups_df = groups_df.reset_index(drop=False).sort_values(naming_dictionary.GRADING_GROUP_ID_COL,
                                                                      ascending=True)
            groups_df.index.name = 'No'
            grouping_group_list_table_name = 'Groups_' + grouping.replace(' ', '_')
            if config['verbose']:
                print(groups_df)
            write_table_helper(exwr, groups_df, grouping_group_list_table_name)

    path = pathlib.Path(output_file)
    if path.is_dir():
        print(path)
        path = path.joinpath(config['DEFAULT_GROUPS_FILE_NAME'])
    write_to_excel(path, my_write, err_on_file_existence=False)


def register_gen_group_info(parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults):
    parser.add_argument('-o', '--output-file', required=True, default=defaults['DEFAULT_GROUPS_FILE_NAME'])
    parser.add_argument('-m', '--moodle-students-list', required=True,
                        help='The list of all students with their group memberships as exported by moodle.', type=str)
    parser.add_argument('-gfmts', '--group-formats', required=False,
                        help='The format strings of the group names used in grouping creation. For example, "Group A1 {:02}" which corresponds to names with 2-padded group ids, e.g., "Group A1 01".',
                        type=str, nargs='+', default=defaults['DEFAULT_GROUP_FORMATS'])
    parser.add_argument('-gns', '--grouping-names', required=False,
                        help='The names of the groupings. For example, "Assignment Part 1" "Assignment Part 2".',
                        type=str, nargs='+', default=defaults['DEFAULT_GROUPING_NAMES'])
    parser.add_argument('-v', '--verbose', required=False, default=False, action='store_true')


class GenMiscTable(CommandModule):
    module_name = 'gen-misc'
    commands = [('groups-info', register_gen_group_info, gen_group_info_table)]

    @property
    def module_properties(self) -> dict[str, Any]:
        return {
            'force_subparsers': True
        }

    @property
    def additional_config(self) -> dict[str, Any]:
        nd = self.default_config['naming_dictionary']
        return {
            'DEFAULT_GROUP_FORMATS': ['Group A1 {:03}', 'Group A2 {:03}'],
            'DEFAULT_GROUPS_FILE_NAME': 'moodle-groups-info.xlsx',
            'DEFAULT_GROUPING_NAMES': ['Assignment Part 1', 'Assignment Part 2'],
        }


if __name__ == '__main__':
    GenMiscTable().as_program('gen').parse_and_run()
