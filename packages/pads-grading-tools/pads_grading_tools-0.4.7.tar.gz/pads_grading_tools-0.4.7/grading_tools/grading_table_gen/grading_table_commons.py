from __future__ import annotations

from typing import Sequence, Iterable

import pandas as pd

from grading_tools.common.defaults import NamingDictionary
from grading_tools.common.gradable_spec import GradableNode, GradableSpecV1
from grading_tools.common.utils import read_generic_table, read_rwthonline

COLUMN_NAME_LEVEL_START = 1
GK_INFO_TABLE_NAME = 'GKInfo'


def equalize(p: tuple, pad_to: int, trim_front: int = 0):
    if trim_front > 0:
        p = p[trim_front:]
    return p + (p[-1],) * max(pad_to - len(p), 0)


def mk_name(path: Sequence[str], start_depth: int = 1) -> str:
    return '-'.join(path[start_depth:])


def mk_node_name(n: GradableNode, start_depth: int = COLUMN_NAME_LEVEL_START) -> str:
    return mk_name(tuple(n.label for n in n.ancestry), start_depth)


def skip_in_formula(n: GradableNode) -> bool:
    return n.get_property('skip') or n.get_property('skip_in_formula')

def skip_in_total_calc(n: GradableNode) -> bool:
    return n.get_property('skip') or n.get_property('skip_in_total')

def mk_sum_formula_over_ranges(ranges: list[list[GradableNode]],
                               output_table: str,
                               max_points: float | None = None,
                               with_equals: bool = True,
                               upper_label_level: int = COLUMN_NAME_LEVEL_START, **config) -> tuple[str, bool]:
    formula = ''
    for i, local_range in enumerate(ranges):
        s, e = local_range[0], local_range[-1]
        if i > 0:
            formula += '+'
        formula += f'SUM([@[{mk_node_name(s, upper_label_level)}]:[{mk_node_name(e, upper_label_level)}]])'
    if max_points:
        formula = f'MIN({max_points},{formula})'
    if with_equals:
        formula = '=' + formula
    return formula, False


def mk_is_checked_formula(column: str, symbol: str, table: str | None = None):
    column_key = f'[@[{column}]]' if table is None else f'{table}[{column}]'
    # return  f'OR({column_key}="{symbol}",{column_key}="R{symbol}")'
    return f'ISNUMBER(SEARCH("{symbol}",{column_key}))'


def mk_is_checked_condition(column: str | tuple[str, str], symbol: str, table: str | None = None):
    if type(column) == tuple and len(column) == 2:
        column = f'{column[0]}]:[{column[1]}'
    column_key = f'[@[{column}]]' if table is None else f'{table}[{column}]'
    return column_key, f'"*{symbol}*"'


def mk_mandatory_col_disjunction(nodes: Iterable[GradableNode], upper_label_level: int = COLUMN_NAME_LEVEL_START,
                                 **config) -> str | None:
    s = ','.join(
        (mk_is_checked_formula(mk_node_name(n, upper_label_level), config["CHECKBOX_SYMBOL"]) for n in nodes if
         n.get_property('mandatory')))
    return f'OR({s})' if s else None


def mk_mandatory_col_condition(nodes: Iterable[Iterable[GradableNode]], **config) -> str | None:
    s = ','.join((dis for rng in nodes if (dis := mk_mandatory_col_disjunction(rng, **config))))
    return f'AND({s})' if s else None


def mk_marked_formula_over_ranges(ranges: list[list[GradableNode]],
                                  output_table: str, *,
                                  max_points: float | None = None,
                                  with_equals: bool = True,
                                  upper_label_level: int = COLUMN_NAME_LEVEL_START,
                                  naming_dictionary: NamingDictionary = None,
                                  **config) -> tuple[str, bool]:
    mandatory_col_groups: list[list[GradableNode]] = []
    sub_sums = []
    sub_formulas = []
    for i, local_range in enumerate(ranges):
        s, e = local_range[0], local_range[-1]
        start_col = mk_node_name(s, upper_label_level)
        end_col = mk_node_name(e, upper_label_level)
        # cancelled due to excel non-cooperation
        # this formula works if it is entered via the interface..
        # local_formula = f'SUMPRODUCT(IF(IFERROR(SEARCH("{config["CHECKBOX_SYMBOL"]}",[@[{start_col}]:[{end_col}]]),FALSE),1,0),INDEX({GK_INFO_TABLE_NAME}[[{start_col}]:[{end_col}]],1,0))'
        # local_formula = f'SUM(IFERROR(SEARCH("{config["CHECKBOX_SYMBOL"]}",[@[{start_col}]:[{end_col}]]),FALSE) * INDEX({GK_INFO_TABLE_NAME}[[{start_col}]:[{end_col}]],1,0))'
        rg, crit = mk_is_checked_condition((start_col, end_col), config["CHECKBOX_SYMBOL"])
        local_formula = f'SUMIF({rg},{crit},INDEX({naming_dictionary.GRADING_GKINFO_TABLE_NAME}[[{start_col}]:[{end_col}]],1,0))'
        sub_formulas.append(local_formula)
        cns = (mk_node_name(n, upper_label_level) for n in local_range)
        ifs = (
            f'IF({mk_is_checked_formula(c, config["CHECKBOX_SYMBOL"])},INDEX({naming_dictionary.GRADING_GKINFO_TABLE_NAME}[[{c}]],1),0)'
            for c in cns)
        sub_sums.extend(ifs)

        mandatory_col_options = [n for n in local_range if n.get_property('mandatory')]
        if len(mandatory_col_options) > 0:
            mandatory_col_groups.append(mandatory_col_options)

    formula = f'SUM({",".join(sub_formulas)})'
    if max_points:
        formula = f'MIN({max_points},{formula})'
    if len(mandatory_col_groups) > 0 and not config.get('use_simplified_formulas', False):
        s = mk_mandatory_col_condition(mandatory_col_groups, **config)
        if s:
            formula = f'IF({s},{formula},"")'
    if with_equals:
        formula = '=' + formula
    return formula, False


def mk_sum_formula_range(summary_range: Iterable[GradableNode]) -> tuple[list[list[GradableNode]], float]:
    local_max_pts = 0
    ranges = []
    range_start, range_end = (None, None)
    local_range = []
    gap = True
    for j, c in enumerate(summary_range):
        if not c.get_property('bonus') and not skip_in_total_calc(c):
            local_max_pts += c.pts

        if skip_in_formula(c):
            if not gap:
                assert local_range[0] == range_start
                assert local_range[-1] == range_end
                ranges.append(local_range)
            local_range = []
            range_start = None
            gap = True
        else:
            if gap:
                local_range = []
                range_start = c
                gap = False
        range_end = c
        local_range.append(c)
    if not gap:
        assert local_range[0] == range_start
        assert local_range[-1] == range_end
        ranges.append(local_range)
    return ranges, local_max_pts


def mk_header_info(spec: GradableSpecV1, cutoff_level: str | int | None = None, totals_level: str | int | None = None,
                   **config) -> tuple[
    pd.MultiIndex, list[str], list[float], list[tuple[str, ...]]]:
    if cutoff_level is not None:
        if type(cutoff_level) is str:
            cutoff_level = spec.tree_level_names.index(cutoff_level)
        spec = spec.cutoff(cutoff_level)
        if config['verbose']:
            print(f'Trimmed spec to depth {cutoff_level}')
            print(spec)

    point_tree = spec.tree  # assumed to be `complete()`
    if totals_level is not None:
        if type(totals_level) is str:
            totals_level = spec.tree_level_names.index(totals_level)
        point_tree.add_summaries(totals_level)

    max_pts = sum(n.pts for n in point_tree.leaves_iter() if not n.get_property('bonus') and not n.get_property('skip'))
    pts_list = list(map(lambda n: n.pts, point_tree.leaves_iter()))
    paths = list(point_tree.paths_iter(lambda n: n.label))
    depth = max(map(len, paths))
    paths_list = [equalize(p, depth) for p in paths]
    header_index = pd.MultiIndex.from_tuples(paths_list, names=spec.tree_level_names[:depth])
    column_names_list = [mk_node_name(n) for n in point_tree.leaves_iter()]
    return header_index, column_names_list, pts_list, paths_list


def mk_initialization_df(spec: GradableSpecV1, column_names_list: list[str], **config) -> pd.DataFrame:
    index_columns = config.get('index_columns', config['DEFAULT_INDEX_COLUMNS'])
    df = None
    if (data_df := config.get('data_df')) is not None:
        df = data_df
    elif (data_file := config.get('data_file')) is not None:
        df = read_generic_table(data_file, sheet_name=config.pop('data_sheet', None),
                                table_name=config.pop('data_table', None))
        df = df.set_index(index_columns, drop=True)
    if df is not None:
        keep = {mk_node_name(n) for n in spec.tree.leaves_iter() if not n.get_property('skip')}
        keep = [c for c in df.columns if c in keep]
        initialization_df = df[keep].reindex(columns=column_names_list)
    else:
        if index_file := config.get('index_file'):
            index_file_preset = config.get('index_file_preset', 'manual')
            if index_file_preset == 'rwthonline':
                df = read_rwthonline(index_file)
                nd: NamingDictionary = config.get('naming_dictionary', NamingDictionary())
                rwth_col_names = list(nd.RWTHONLINE_IDENTITY_COLS) + [nd.RWTHONLINE_MATR_COL]
                new_col_names = list(nd.IDENTITY_COLS) + [nd.MATR_COL]
                df = df[rwth_col_names]
                df.columns = new_col_names
            else:
                df = read_generic_table(index_file,
                                        columns=(index_columns if 'index_columns' in config else None),
                                        sheet_name=config.pop('index_sheet', None),
                                        table_name=config.pop('index_table', None))
            data_index = pd.MultiIndex.from_frame(df)
        else:
            data_index = pd.MultiIndex.from_tuples(
                [tuple(i for _ in index_columns) for i in range(config.get('placeholder_row_count', 1))],
                names=index_columns)
        initialization_df = pd.DataFrame(data=None, columns=column_names_list, dtype='Float64').reindex(data_index)
    return initialization_df
