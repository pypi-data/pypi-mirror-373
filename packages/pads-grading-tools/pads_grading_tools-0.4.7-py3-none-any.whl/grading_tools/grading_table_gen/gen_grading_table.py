from __future__ import annotations

import argparse
import itertools
from typing import Literal

import pandas as pd

from grading_tools.common.commands import CommandModule
from grading_tools.common.defaults import NamingDictionary
from grading_tools.common.excel_utils import write_to_excel
from grading_tools.common.gradable_spec import *
from grading_tools.common.utils import complete_file_path
from grading_tools.grading_table_gen.grading_table_commons import mk_node_name, \
    mk_sum_formula_range, mk_header_info, mk_initialization_df, \
    mk_marked_formula_over_ranges, mk_sum_formula_over_ranges, mk_mandatory_col_condition, \
    mk_is_checked_condition, COLUMN_NAME_LEVEL_START

GradingStyle = Literal['numbers', 'checkboxes']


def merge_length(path: tuple[str, ...]) -> int | None:
    last_value = path[-1]
    last_index = None
    for i, n in enumerate(reversed(path[:-1])):
        if n != last_value:
            last_index = i
            break
    if last_index is None:
        return len(path)
    elif last_index > 0:
        return last_index
    else:
        return None


def add_visual_table_header(exwr: pd.ExcelWriter, output_sheet: str, output_table: str, startrow: int, startcol: int, *,
                            spec: GradableSpecV1, header_index: pd.Index, paths_list: list[tuple[str, ...]],
                            naming_dictionary: NamingDictionary, **config):
    header_height = header_index.nlevels
    pd.DataFrame(columns=header_index).to_excel(exwr, sheet_name=output_sheet, startrow=startrow, startcol=startcol)
    sheet = exwr.sheets[output_sheet]
    bold_merge_format = exwr.book.add_format({'align': 'center', 'bold': True, 'border': 1})
    merge_format = exwr.book.add_format({'align': 'center'})
    merge_format.set_align('vcenter')

    for i, p in enumerate(paths_list, start=1):
        if (j := merge_length(p)) is not None:
            sheet.merge_range(startrow + len(p) - 1 - j, startcol + i, startrow + len(p) - 1, startcol + i, p[-1],
                              bold_merge_format)
    if startcol > 0:
        for i, s in enumerate(header_index.names):
            sheet.merge_range(startrow + i, 0, startrow + i, startcol, s, merge_format)
    return header_height


def add_inline_aux_info(exwr: pd.ExcelWriter, output_sheet: str, output_table: str, startrow: int, startcol: int, *,
                        grading_style: GradingStyle, spec: GradableSpecV1, column_names_list: list[str],
                        pts_list: list[float], naming_dictionary: NamingDictionary, **config) -> int:
    if grading_style == 'numbers':
        pd.DataFrame(data=[pts_list], dtype='Float64', index=['Max Points']).to_excel(exwr,
                                                                                      startrow=startrow,
                                                                                      startcol=startcol,
                                                                                      sheet_name=output_sheet,
                                                                                      index=True,
                                                                                      header=False)
        return 1
    elif grading_style == 'checkboxes':
        book = exwr.book
        sheet = exwr.sheets[output_sheet]
        bold_format = book.add_format({'bold': True})
        bold_extra_format = book.add_format({'bold': True, 'bottom': 6})
        vert_format = book.add_format({'rotation': 90})
        merge_format = book.add_format({'align': 'center'})

        pd.DataFrame(data=[pts_list], dtype='Float64', index=['Max Points']).to_excel(exwr,
                                                                                      startrow=startrow + 1,
                                                                                      startcol=startcol + 1,
                                                                                      sheet_name=output_sheet,
                                                                                      index=False,
                                                                                      header=False)
        sheet.write(startrow + 1, startcol, 'Points')
        sheet.write(startrow + 2, startcol, 'Stats')
        sheet.write(startrow + 3, startcol, 'Text')
        for i, (c, n) in enumerate(zip(column_names_list, spec.tree.leaves_iter()), start=1):
            if not n.get_property('skip') and not n.get_property('skip_in_formula'):
                rg, crit = mk_is_checked_condition(c, config["CHECKBOX_SYMBOL"], table=output_table)
                sheet.write(startrow + 2, startcol + i,
                            f'=COUNTIF({rg},{crit})',
                            bold_format)
            elif n.get_property('summary'):
                sheet.write(startrow + 2, startcol + i,
                            f'=IF(COUNT({output_table}[{c}])>0,AVERAGE({output_table}[{c}]),"")', bold_extra_format)

            text = n.get_property('text')
            if not text:
                text = ''
            sheet.write(startrow + 3, startcol + i, text, vert_format)
        if startcol > 0:
            sheet.merge_range(startrow, 0, startrow + 3, startcol - 1, '', merge_format)

        excel_cols = [{'header': 'Info'}] + [{'header': c} for c in column_names_list]
        extra_options = {}
        sheet.add_table(startrow, startcol, startrow + 3, startcol + len(excel_cols) - 1,
                        {'name': naming_dictionary.GRADING_GKINFO_TABLE_NAME, 'columns': excel_cols} | extra_options)
        return 4
    else:
        return 0


def add_grading_table(exwr: pd.ExcelWriter, output_sheet: str, output_table: str, startrow: int, startcol: int, *,
                      spec: GradableSpecV1,
                      initialization_df: pd.DataFrame,
                      grading_style: GradingStyle = 'numbers',
                      utility_columns: bool | None = False,
                      cap_bonus_pts: bool = False,
                      naming_dictionary: NamingDictionary = None, **config):
    w_book = exwr.book
    regular_format = w_book.add_format({'align': 'center'})
    summary_format = w_book.add_format({'bold': True, 'align': 'center'})

    green_format = w_book.add_format({'bg_color': '#7df59f'})
    red_format = w_book.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    w_sheet_scores = exwr.sheets[output_sheet]

    initialization_df.to_excel(exwr, sheet_name=output_sheet, float_format='%.2f', index=True,
                               header=False,
                               startrow=startrow + 1, startcol=startcol, merge_cells=False)
    # pd.DataFrame(initialization_df.values).to_excel(exwr, sheet_name=output_sheet, float_format='%.2f', index=False,
    #                                          header=False,
    #                                          startcol=startcol + 1, startrow=current_row, merge_cells=False)
    # initialization_df.index.to_excel(exwr, sheet_name=output_sheet, index=False, header=False,
    #                                         startrow=current_row, startcol=0)

    (table_rows, table_cols) = initialization_df.shape
    # w_sheet_scores.set_column(1, max_col, 10)
    table_start = startrow
    sum_formula_func = mk_sum_formula_over_ranges if grading_style == 'numbers' else mk_marked_formula_over_ranges

    array_formulas = []
    bound_conditions = []
    equality_conditions = []
    excel_cols = [{'header': name if name else f'IndexCol-{i}'} for i, name in enumerate(initialization_df.index.names)]
    extra_options = {}
    for column_index, leaf in enumerate(spec.tree.leaves_iter(), start=len(excel_cols)):

        col = {'header': mk_node_name(leaf), 'format': regular_format}
        if leaf.get_property('summary'):
            summary_range = itertools.chain(
                *(c.leaves_iter() for c in leaf.left_siblings))

            local_ranges, local_max_pts = mk_sum_formula_range(summary_range)
            total_formula, is_arr_formula = sum_formula_func(local_ranges, output_table,
                                                             max_points=(local_max_pts if cap_bonus_pts else None),
                                                             naming_dictionary=naming_dictionary,
                                                             **config)
            if is_arr_formula:
                array_formulas.append((column_index, total_formula))
            else:
                col.update({'formula': total_formula})
            col.update({'format': summary_format})
            if grading_style == 'checkboxes':
                lb, ub = (leaf.pts, 0) if leaf.pts < 0 else (0, leaf.pts)
                bound_conditions.append((column_index, False, lb, ub))
        else:
            if grading_style == 'numbers':
                lb, ub = (leaf.pts, 0) if leaf.pts < 0 else (0, leaf.pts)
                bound_conditions.append((column_index, False, lb, ub))
        if leaf.get_property('mandatory'):
            equality_conditions.append((column_index, True, f'"{config["CHECKBOX_SYMBOL"]}"'))

        excel_cols.append(col)

    if utility_columns:
        all_ranges, total_max_pts = mk_sum_formula_range(spec.tree.leaves_iter())

        participation_formula = ''
        if grading_style == 'numbers':
            rng = f'[@[{excel_cols[0]["header"]}]:[{excel_cols[-1]["header"]}]]'
            participation_formula = f'COUNTA({rng})=COLUMNS({rng})'
        elif grading_style == 'checkboxes':
            id_col_rng = f'[@[{initialization_df.index.names[0]}]:[{initialization_df.index.names[-1]}]]'
            mandatory_cols = mk_mandatory_col_condition(all_ranges, **config)
            identity_cols = f'COUNTA({id_col_rng})=COLUMNS({id_col_rng})'
            participation_formula = f'AND({identity_cols}{("," + mandatory_cols) if mandatory_cols else ""})'
        excel_cols.append(
            {'header': naming_dictionary.PARTICIPATED_COL, 'formula': participation_formula})

        total_formula, is_arr_formula = sum_formula_func(all_ranges, output_table,
                                                         max_points=(total_max_pts if cap_bonus_pts else None),
                                                         with_equals=False,
                                                         naming_dictionary=naming_dictionary,
                                                         **config)
        total_formula = f'IF([@[{naming_dictionary.PARTICIPATED_COL}]], {total_formula}, "{config["FALLBACK_SCORE"]}")'
        total_col = {'header': naming_dictionary.GRADING_TOTAL_COL}
        if is_arr_formula:
            array_formulas.append((len(excel_cols), total_formula))
        else:
            total_col.update({'formula': total_formula})
        excel_cols.append(total_col)
        extra_options = {'last_column': True}

    w_sheet_scores.add_table(table_start, startcol, table_start + table_rows, startcol + len(excel_cols) - 1,
                             {'name': output_table,
                              'columns': excel_cols} | extra_options)
    for i, formula in array_formulas:
        w_sheet_scores.write_array_formula(table_start + 1, startcol + i, table_start + table_rows, startcol + i,
                                           '{' + formula + '}')

    if config['conditional_formatting']:
        for i, is_pos, lb, ub in bound_conditions:
            # conditional formatting is somehow broken
            w_sheet_scores.conditional_format(startrow + 1, startcol + i, startrow + table_rows, startcol + i,
                                              {'type': 'cell', 'criteria': 'between' if is_pos else 'not between',
                                               'minimum': lb,
                                               'maximum': ub, 'format': green_format if is_pos else red_format})
        for i, is_pos, equals in equality_conditions:
            condition = {'type': 'text', 'criteria': 'containing' if is_pos else 'not containing',
                         'value': equals[1:-1], 'format': green_format if is_pos else red_format}
            w_sheet_scores.conditional_format(startrow + 1, startcol + i, startrow + table_rows, startcol + i,
                                              condition)

    return len(initialization_df) + 1


def add_aux_sheet(exwr: pd.ExcelWriter, header_index: pd.Index, pts_list: list[float], **config):
    ## aux. sheet
    aux_sheet_name = config['AUX_SHEET_NAME']
    pts_df = pd.DataFrame(data={'Max Points': pts_list}, index=header_index, dtype='Float64')
    pts_df.to_excel(exwr, sheet_name=aux_sheet_name, float_format='%.2f')
    w_sheet_aux = exwr.sheets[aux_sheet_name]
    for i in range(header_index.nlevels + 1):
        w_sheet_aux.set_column(0, 1 + i, 15)


def save_grading_table(spec: GradableSpecV1,
                       output_sheet: str = None,
                       output_table: str = None,
                       verbose: bool = False,
                       cutoff_level: int | str | None = None,
                       totals_level: int | str | None = None,
                       **config):
    if verbose:
        print('Generating grading table for spec:')
        print(spec)

    header_index, column_names_list, pts_list, paths_list = mk_header_info(spec, cutoff_level, totals_level, **config)

    initialization_df = mk_initialization_df(spec, column_names_list, **config)

    extra_args = dict(spec=spec, header_index=header_index, column_names_list=column_names_list, pts_list=pts_list,
                      paths_list=paths_list,
                      initialization_df=initialization_df)  # , naming_dictionary=config.get('naming_dictionary')

    def my_write(exwr: pd.ExcelWriter):
        current_row = 0
        offset_startcol = initialization_df.index.nlevels - 1

        current_row += add_visual_table_header(exwr, output_sheet, output_table, current_row, offset_startcol,
                                               **extra_args, **config)

        # auxiliary inline table/info
        # has to return the number of rows written
        current_row += add_inline_aux_info(exwr, output_sheet, output_table, current_row, offset_startcol, **extra_args,
                                           **config)

        current_row += add_grading_table(exwr, output_sheet, output_table, current_row, 0, **extra_args, **config)

        if config['aux_sheet']:
            add_aux_sheet(exwr, **extra_args, **config)

    write_to_excel(
        complete_file_path(config['output_file'], default_file_name=config.pop('DEFAULT_GRADING_FILE_NAME', None)),
        my_write, err_on_file_existence=False)


def gen_grading_table(spec_file: str, cap_bonus_pts=False, **config):
    spec = load_spec(spec_file)

    root = spec.tree
    cap = sum(n.pts for n in root.leaves_iter() if
              not n.get_property('bonus') and not n.get_property('skip') and not n.get_property('skip_in_total'))
    bonus = sum(n.pts for n in root.leaves_iter() if n.get_property('bonus'))
    print(f'Points: {cap} + {bonus} (bonus) = {root.pts}')
    if cap_bonus_pts and bonus > 0:
        print(f'Points formula is capped to {cap} (MIN({cap},SUM(...))).')

    save_grading_table(spec, cap_bonus_pts=cap_bonus_pts, **config)


def register_gen_grading_table_options(parser: argparse.ArgumentParser, **defaults):
    parser.add_argument('-gs', '--grading-style', required=False, choices=['numbers', 'checkboxes'], default='numbers',
                        help='The grading style to use: "numbers" or "checkboxes". Note that these require different specification file properties.')

    parser.add_argument('-cl', '--cutoff-level', required=False, default=None, type=str,
                        help='Level up to which to include (sub^x) questions. E.g. choosing "Question" cuts off/aggregates subquestions.')
    parser.add_argument('-tl', '--totals-level', required=False, default=None, type=str,
                        help='Level up to which to introduce (sub^x) question totals columns. E.g. choosing "Question" introduces per-question totals.')

    parser.add_argument('-uc', '--utility-columns', required=False, action='store_false', default=True,
                        help='Whether to include utility columns.')
    parser.add_argument('-cf', '--conditional-formatting', required=False, action='store_false', default=True,
                        help='Whether to include add conditional formatting for some sanity checks.')
    parser.add_argument('-cap', '--cap-bonus-pts', required=False, action='store_true', default=False,
                        help='Whether to cap total pts to maximum without bonus.')
    parser.add_argument('-v', '--verbose', action='store_true', required=False, default=False,
                        help='Whether to print verbose output.')
    parser.add_argument('-aux', '--aux-sheet', required=False, action='store_true', default=False,
                        help='Whether to include an auxiliary sheet with reformatted information.')
    parser.add_argument('-sf', '--use-simplified-formulas', required=False, action='store_true', default=False,
                        help='Whether to use simplified formulas for the grading table. (in particular, for the checkboxes style, this means that the condition on the mandatory columns is omitted in the total formulas)')

def register_gen_grading_table(parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults):
    parser.add_argument('-s', '--spec-file', required=True, type=str, help='Path to spec file.')

    parser.add_argument('-o', '--output-file', required=False, type=str, help='Path to output file.',
                        default=defaults['DEFAULT_GRADING_FILE_NAME'])
    parser.add_argument('-ot', '--output-table', required=False, type=str, help='Name of the table to generate.',
                        default=defaults['DEFAULT_TABLE_NAME'])
    parser.add_argument('-osh', '--output-sheet', required=False, type=str,
                        help='Sheet where to put the generated table.',
                        default=defaults['DEFAULT_SHEET_NAME'])

    parser.add_argument('-df', '--data-file', required=False, type=str,
                        help='Path to (bootstrapping) data file. This file is used to prefill the grading table. If this option is used, the index information is ignored.')
    parser.add_argument('-dsh', '--data-sheet', required=False, type=str,
                        help='Optionally, an excel sheet that contains the data to use.',
                        default=naming_dictionary.GRADING_SHEET_NAME)
    parser.add_argument('-dt', '--data-table', required=False, type=str,
                        help='Optionally, an excel table that contains the data to use.',
                        default=naming_dictionary.GRADING_TABLE_NAME)

    parser.add_argument('-if', '--index-file', required=False, type=str,
                        help='Optionally, a file that contains an index to use. For example, a list of matriculation numbers.')
    parser.add_argument('-ift', '--index-file-preset', required=False, choices=('manual', 'rwthonline'), type=str,
                        default='manual',
                        help='Optionally, specify the a predefined index file handling to enable specific parsing, e.g., of RWTHOnline exam registrations. Overrides the other index options.')
    parser.add_argument('-ish', '--index-sheet', required=False, type=str,
                        help='Optionally, an excel sheet that contains the index to use.')
    parser.add_argument('-it', '--index-table', required=False, type=str,
                        help='Optionally, an excel table that contains the index to use.')
    parser.add_argument('-ic', '--index-columns', nargs='*', required=False,
                        help='Optionally, the column names of the index file to use as the index. If no file is provided, only the names are used.',
                        default=defaults['DEFAULT_INDEX_COLUMNS'])

    register_gen_grading_table_options(parser, **defaults)


class GenGradingTable(CommandModule):
    module_name = 'gen-grading'
    commands = [('grading', register_gen_grading_table, gen_grading_table)]

    @property
    def additional_config(self) -> dict[str, Any]:
        nd = self.default_config['naming_dictionary']
        return {
            'DEFAULT_GRADING_FILE_NAME': 'grading-empty.xlsx',
            'DEFAULT_INDEX_COLUMNS': list(nd.IDENTITY_COLS) + [nd.MATR_COL],
            'AUX_SHEET_NAME': 'Aux',
            'DEFAULT_SHEET_NAME': nd.GRADING_SHEET_NAME,
            'DEFAULT_TABLE_NAME': nd.GRADING_TABLE_NAME,
            'FALLBACK_SCORE': '',
            'CHECKBOX_SYMBOL': 'x',
            'placeholder_row_count': 10,
            'upper_label_level': COLUMN_NAME_LEVEL_START,
        }


if __name__ == '__main__':
    GenGradingTable().as_program('gen').parse_and_run()
