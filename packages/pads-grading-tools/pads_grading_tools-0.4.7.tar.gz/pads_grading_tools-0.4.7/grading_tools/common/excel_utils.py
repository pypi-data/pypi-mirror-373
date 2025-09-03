import pathlib
from os import PathLike
from typing import Callable

import pandas as pd


def write_table_helper(exwr: pd.ExcelWriter, df: pd.DataFrame, table_name: str, sheet_name: str | None = None,
                       additional_columns: list[dict] | None = None, include_index: bool = True, **kwargs):
    if sheet_name is None:
        sheet_name = table_name

    df.to_excel(exwr, startrow=1, sheet_name=sheet_name, index=include_index, header=False)
    column_definitions = ([{'header': c} for c in df.index.names] if include_index else []) + [{'header': c} for c in
                                                                                               df.columns]
    if additional_columns is not None:
        column_definitions.extend(additional_columns)
    sheet = exwr.sheets[sheet_name]
    sheet.add_table(0, 0, len(df), len(column_definitions) - 1,
                    {'name': table_name, 'columns': column_definitions} | kwargs)
    sheet.autofit()


def write_to_excel(output_file: str | PathLike[str], writer_func: Callable[[pd.ExcelWriter], None],
                   err_on_file_existence: bool = True, **exwr_kwargs):
    print(f'Writing to {output_file}.')
    path = pathlib.Path(output_file)
    if err_on_file_existence:
        if path.resolve().exists():
            raise Exception('FileWouldBeOverwritten')

    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_file, engine='xlsxwriter', engine_kwargs=dict(options=dict(use_future_functions=True)), **exwr_kwargs) as exwr:
        writer_func(exwr)


def write_table_to_excel(output_file: str | PathLike[str], table_name: str, df: pd.DataFrame,
                         sheet_name: str | None = None,
                         formula_columns: list[dict] | None = None,
                         additional_writer_func: Callable[[pd.ExcelWriter], None] = None,
                         writing_options: dict | None = None, **table_options):
    if writing_options is None:
        writing_options = {}
    if sheet_name is None:
        sheet_name = table_name

    def my_write(exwr):
        write_table_helper(exwr, df, table_name=table_name, sheet_name=sheet_name, additional_columns=formula_columns,
                           last_column=table_options.get('last_column', False))
        if additional_writer_func:
            additional_writer_func(exwr)

    write_to_excel(output_file, my_write, **writing_options)
