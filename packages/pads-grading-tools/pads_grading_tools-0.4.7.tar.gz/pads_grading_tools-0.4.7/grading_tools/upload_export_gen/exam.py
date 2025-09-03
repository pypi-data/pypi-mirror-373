import argparse
from datetime import datetime
from pathlib import Path
from typing import Literal, Any

import pandas as pd

from grading_tools.common.commands import CommandModule
from grading_tools.common.defaults import NamingDictionary
from grading_tools.common.compat_utils import stringify_grades_for_rwthonline
from grading_tools.common.utils import (
    read_generic_table,
    write_moodle_csv,
    write_rwthonline_csv,
    read_rwthonline,
    read_moodle_excel,
    get_possible_grades,
    complete_file_path,
)

OLD_RWTHONLINE_GRADE = "OLD_RWTHONLINE_GRADE"


def project(
    df: pd.DataFrame,
    extra: list[str] = None,
    naming_dictionary: NamingDictionary = None,
) -> pd.DataFrame:
    if naming_dictionary is None:
        naming_dictionary = NamingDictionary()
    cols = list(naming_dictionary.IDENTITY_COLS)
    if extra:
        cols.extend(extra)
    else:
        cols.extend(
            [
                naming_dictionary.EXAM_SCORE_COL,
                naming_dictionary.COURSE_SCORE_COL,
                naming_dictionary.COURSE_GRADE_COL,
            ]
        )
    return df[cols]


def gen_both(output_file: str, **config):
    grades_df = read_grades_df(**config)
    rwth_export_file = output_file.rsplit(".csv")[0] + "-rwth.csv"
    moodle_export_file = output_file.rsplit(".csv")[0] + "-moodle.csv"
    rwth_export, considered_grades = create_rwthonline_export(
        grades_df, rwth_file=config.pop("rwth_file", None), **config
    )
    write_rwthonline_csv(rwth_export, rwth_export_file)
    moodle_export, _ = create_moodle_export(
        considered_grades, moodle_file=config.pop("moodle_file", None), **config
    )
    write_moodle_csv(moodle_export, moodle_export_file)


def gen_generic(output_file: str, **config):
    considered_grades = read_grades_df(**config)
    moodle_export, _ = create_generic_export(considered_grades, **config)
    write_moodle_csv(
        moodle_export,
        complete_file_path(
            output_file, default_file_name=config.pop("DEFAULT_OUTPUT_FILE_NAME", None)
        ),
    )


def gen_rwth(output_file: str, **config):
    grades_df = read_grades_df(**config)
    rwth_export, _ = create_rwthonline_export(
        grades_df, rwth_file=config.pop("rwth_file", None), **config
    )
    write_rwthonline_csv(
        rwth_export,
        complete_file_path(
            output_file, default_file_name=config.pop("DEFAULT_OUTPUT_FILE_NAME", None)
        ),
    )


def gen_moodle(output_file: str, **config):
    considered_grades = read_grades_df(**config)
    moodle_export, _ = create_moodle_export(
        considered_grades, moodle_file=config.pop("moodle_file", None), **config
    )
    write_moodle_csv(
        moodle_export,
        complete_file_path(
            output_file, default_file_name=config.pop("DEFAULT_OUTPUT_FILE_NAME", None)
        ),
    )


def read_grades_df(
    grades_file: str, naming_dictionary: NamingDictionary, **config
) -> pd.DataFrame:
    grades_df = read_generic_table(
        grades_file,
        sheet_name=config.pop("grades_sheet", None),
        table_name=config.pop("grades_table", None),
    )
    grades_df = grades_df.set_index(naming_dictionary.MATR_COL, drop=False)
    grades_df.index.name = "INDEX"

    # only keep not NA scores
    return grades_df[grades_df[naming_dictionary.COURSE_GRADE_COL].notna()]


def create_generic_export(
    scores_df: pd.DataFrame,
    export_columns: list[str] = None,
    naming_dictionary: NamingDictionary = NamingDictionary(),
    **config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if (rwth_file := config.pop("rwth_file", None)) is not None:
        _, considered_grades = create_rwthonline_export(scores_df, rwth_file, **config)
    else:
        considered_grades = scores_df

    export_df = considered_grades[
        list(naming_dictionary.IDENTITY_COLS) + [naming_dictionary.MATR_COL] + list(export_columns)
    ]

    return export_df, considered_grades


def create_moodle_export(
    scores_df: pd.DataFrame,
    moodle_file: str = None,
    used_grading_column: str = None,
    used_feedback_column: str = None,
    moodle_grading_column: str = None,
    moodle_feedback_column: str = None,
    naming_dictionary: NamingDictionary = NamingDictionary(),
    **config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if (rwth_file := config.pop("rwth_file", None)) is not None:
        _, considered_grades = create_rwthonline_export(scores_df, rwth_file, **config)
    else:
        considered_grades = scores_df

    moodle_df = read_moodle_excel(moodle_file)
    moodle_df[naming_dictionary.MOODLE_EXCEL_MATR_COL] = pd.to_numeric(
        moodle_df[naming_dictionary.MOODLE_EXCEL_MATR_COL], errors="coerce"
    )
    moodle_df = moodle_df.dropna(subset=[naming_dictionary.MOODLE_EXCEL_MATR_COL])

    use_feedback = (moodle_feedback_column in moodle_df.columns) and (
        used_feedback_column in considered_grades.columns
    )
    exported_cols = (
        [moodle_grading_column, moodle_feedback_column]
        if use_feedback
        else [moodle_grading_column]
    )

    # only students listed on moodle can receive a grade there
    moodle_export = pd.merge(
        considered_grades,
        moodle_df[
            list(naming_dictionary.MOODLE_EXCEL_IDENTITY_COLS)
            + [
                naming_dictionary.MOODLE_EXCEL_MATR_COL,
                naming_dictionary.MOODLE_EXCEL_ID_COL,
            ]
            + exported_cols
        ],
        how="inner",
        left_on=naming_dictionary.MATR_COL,
        right_on=naming_dictionary.MOODLE_EXCEL_MATR_COL,
    )

    moodle_export[used_feedback_column] = moodle_export[used_feedback_column].astype(
        str
    )
    moodle_changed_rows_idx = (
        moodle_export[moodle_grading_column] != moodle_export[used_grading_column]
    )
    if use_feedback:
        moodle_changed_rows_idx |= (
            moodle_export[moodle_feedback_column] != moodle_export[used_feedback_column]
        )
    proj_cols = [used_grading_column, moodle_grading_column]
    if use_feedback:
        proj_cols += [used_feedback_column, moodle_feedback_column]
    moodle_changed_rows = project(
        moodle_export.loc[moodle_changed_rows_idx],
        proj_cols,
        naming_dictionary=naming_dictionary,
    )

    if config["verbose"] and len(moodle_changed_rows) > 0:
        print(
            "The following rows differ in grading value or feedback text (includes initially unset values)"
        )
        print(moodle_changed_rows)

    notna_entries = moodle_export[moodle_grading_column].notna()
    if use_feedback:
        notna_entries |= moodle_export[moodle_feedback_column].notna()

    moodle_overwritten_rows = moodle_export.loc[moodle_changed_rows_idx & notna_entries]
    moodle_overwritten_rows = project(
        moodle_overwritten_rows, proj_cols, naming_dictionary=naming_dictionary
    )
    if len(moodle_overwritten_rows) > 0:
        print("The following rows have overwritten grading value or feedback text")
        print(moodle_overwritten_rows)
        if config["export_diffs"]:
            moodle_diffs_file = (
                Path(config["output_file"])
                .parent.joinpath("moodle_overwritten_rows.csv")
                .resolve()
            )
            moodle_overwritten_rows.to_csv(moodle_diffs_file)

    moodle_export[moodle_grading_column] = moodle_export[used_grading_column]
    if used_feedback_column in moodle_export.columns:
        moodle_export[moodle_feedback_column] = moodle_export[used_feedback_column]
    moodle_export = moodle_export[
        [naming_dictionary.MOODLE_EXCEL_ID_COL, naming_dictionary.MATR_COL]
        + list(naming_dictionary.MOODLE_EXCEL_IDENTITY_COLS)
        + exported_cols
    ]

    return moodle_export, considered_grades


## https://wiki-intern.rwth-aachen.de/display/RD/Notenskala+und+Notenvermerke
# X - nicht erschienen
# NZ - nicht zugelassen
# PA - Prüfung abgebrochen
# U - Ungültig/Täuschung
# Die Titel der Spalten "GRADE", "ECTS_GRADE", "REMARK", "DB_Primary_Key_Of_Candidate" und "DB_Primary_Key_Of_Exam" dürfen weder gelöscht, noch umbenannt werden.
#
# Achten Sie darauf, in den Spalten "DB_Primary_Key_Of_Candidate" und "DB_Primary_Key_Of_Exam" keine Einträge zu verändern oder zu löschen.
#
# May be edited:
# DATE_OF_ASSESMENT
# GRADE
# REMARK
def create_rwthonline_export(
    scores_df: pd.DataFrame,
    rwth_file: str = None,
    naming_dictionary: NamingDictionary = NamingDictionary(),
    **config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rwth_df = read_rwthonline(rwth_file)

    original_rwth_cols = list(rwth_df.columns)
    rwth_df = rwth_df.set_index(naming_dictionary.RWTHONLINE_MATR_COL, drop=False)
    rwth_df.index.name = "INDEX"
    rwth_df[OLD_RWTHONLINE_GRADE] = rwth_df[naming_dictionary.RWTHONLINE_GRADE_COL]
    rwth_df = rwth_df.drop(naming_dictionary.RWTHONLINE_GRADE_COL, axis="columns")

    non_registered_students_with_grade = scores_df.loc[
        list(
            set(scores_df[naming_dictionary.MATR_COL])
            - set(rwth_df[naming_dictionary.RWTHONLINE_MATR_COL])
        )
    ]
    if len(non_registered_students_with_grade) > 0:
        print(
            f"The following students are not registered according to the RWTH Online list but received a grade (will{'' if config['skip_rwthonline_registration_filter'] else ' not'} be included in output)"
        )
        print(
            project(
                non_registered_students_with_grade, naming_dictionary=naming_dictionary
            )
        )
    registered_students_without_grade = rwth_df.loc[
        list(
            set(rwth_df[naming_dictionary.RWTHONLINE_MATR_COL])
            - set(scores_df[naming_dictionary.MATR_COL])
        )
    ]
    if len(registered_students_without_grade) > 0:
        print(
            "The following students are registered according to the RWTH Online list but are not in the scores table"
        )
        print(registered_students_without_grade)

    # ensure that only students who are registered according to rwth online can receive a grade, unless this is overridden
    how: Literal["inner", "left"] = (
        "inner" if not config["skip_rwthonline_registration_filter"] else "left"
    )
    considered_grades = scores_df.join(rwth_df, how=how)

    existing_rwthonline_grades = considered_grades[OLD_RWTHONLINE_GRADE].notna()
    non_matching_grades_rwth = considered_grades.loc[
        existing_rwthonline_grades
        & (
            considered_grades[OLD_RWTHONLINE_GRADE]
            != considered_grades[naming_dictionary.COURSE_GRADE_COL]
        )
    ]
    if len(non_matching_grades_rwth) > 0:
        print(
            "The following grades differ between the RWTH Online list and provided scores table"
        )
        rwthonline_diffs = project(
            non_matching_grades_rwth,
            [OLD_RWTHONLINE_GRADE, naming_dictionary.COURSE_GRADE_COL],
            naming_dictionary=naming_dictionary,
        )
        print(rwthonline_diffs)
        if config["export_diffs"]:
            rwthonline_diffs_file = (
                Path(config["output_file"])
                .parent.joinpath("rwthonline_overwritten_rows.csv")
                .resolve()
            )
            rwthonline_diffs.to_csv(rwthonline_diffs_file)

    if config["override_grade_with_rwthonline"]:
        overwritten_grades = considered_grades.loc[existing_rwthonline_grades]
        if len(existing_rwthonline_grades) > 0:
            print(
                "Overwriting the following grades from the score table with rwthonline entries"
            )
            print(
                project(
                    overwritten_grades,
                    [OLD_RWTHONLINE_GRADE],
                    naming_dictionary=naming_dictionary,
                )
            )
            considered_grades.loc[
                existing_rwthonline_grades, naming_dictionary.COURSE_GRADE_COL
            ] = considered_grades.loc[existing_rwthonline_grades, OLD_RWTHONLINE_GRADE]

    rwth_export = rwth_df.join(
        considered_grades[naming_dictionary.COURSE_GRADE_COL], how="left"
    )
    stringified_grades = stringify_grades_for_rwthonline(
        rwth_export[naming_dictionary.COURSE_GRADE_COL]
    )
    assert set(stringified_grades) <= set(
        get_possible_grades(symbols=True, decimal_sep=",")
    )
    rwth_export[naming_dictionary.RWTHONLINE_GRADE_COL] = stringified_grades
    rwth_export = rwth_export[original_rwth_cols]

    return rwth_export, considered_grades


def register_generic(
    parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults
):
    parser.add_argument(
        "-ec",
        "--export-columns",
        required=False,
        nargs="+",
        help="The columns to export. If not specified, the default columns are used.",
        default=defaults["DEFAULT_EXPORT_COLUMNS"],
        dest="export_columns",
    )
    parser.add_argument(
        "-r",
        "--rwth",
        required=False,
        help="Path to rwth online exam registrations file.",
        dest="rwth_file",
    )
    parser.add_argument(
        "--skip-rwthonline-registration-filter",
        required=False,
        action="store_true",
        default=False,
        help="Whether to keep scores from students who do not appear in the rwthonline table.",
    )
    parser.add_argument(
        "--override-grade-with-rwthonline",
        required=False,
        action="store_true",
        default=True,
        help="Whether to override grades from the scores table with grades from rwthonline.",
    )


def register_moodle(
    parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults
):
    parser.add_argument(
        "-m",
        "--moodle",
        required=True,
        help="Path to moodle excel file.",
        dest="moodle_file",
    )
    parser.add_argument(
        "-ugc",
        "--used-grading-column",
        required=False,
        default=defaults["DEFAULT_USED_GRADING_COL_NAME"],
        help="The column in the scores table to use for the moodle grading aspect.",
    )
    parser.add_argument(
        "-ufc",
        "--used-feedback-column",
        required=False,
        default=defaults["DEFAULT_USED_FEEDBACK_COL_NAME"],
        help="The column in the scores table to use for the feedback of the moodle grading aspect.",
    )
    parser.add_argument(
        "-mgc",
        "--moodle-grading-column",
        required=False,
        help="The name of the grading column in the moodle export.",
        default=defaults["DEFAULT_MOODLE_GRADING_COL_NAME"],
    )
    parser.add_argument(
        "-mfc",
        "--moodle-feedback-column",
        required=False,
        help="The name of the feedback column in the moodle export.",
        default=defaults["DEFAULT_MOODLE_FEEDBACK_COL_NAME"],
    )


def register_rwth(
    parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults
):
    parser.add_argument(
        "-r",
        "--rwth",
        required=True,
        help="Path to rwth online exam registrations file.",
        dest="rwth_file",
    )
    parser.add_argument(
        "--skip-rwthonline-registration-filter",
        required=False,
        action="store_true",
        default=False,
        help="Whether to keep scores from students who do not appear in the rwthonline table.",
    )
    parser.add_argument(
        "--override-grade-with-rwthonline",
        required=False,
        action="store_true",
        default=True,
        help="Whether to override grades from the scores table with grades from rwthonline.",
    )


def register_base(
    parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults
) -> None:
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Path to output csv file.",
        dest="output_file",
        default=defaults["DEFAULT_OUTPUT_FILE_NAME"],
        type=str,
    )

    parser.add_argument(
        "-g",
        "--grades",
        required=True,
        help="Path to the grade file.",
        dest="grades_file",
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-sh",
        "--grades-sheet",
        required=False,
        help="Optionally, excel sheet within scores file.",
    )
    group.add_argument(
        "-t",
        "--grades-table",
        required=False,
        help="Optionally, excel table within scores file.",
        default=naming_dictionary.OVERVIEW_TABLE_NAME,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        required=False,
        action="store_true",
        default=False,
        help="Whether to produce more verbose output.",
    )
    parser.add_argument(
        "-exd",
        "--export-diffs",
        required=False,
        help="Whether to export tables of changed/overwritten scores (includes initially unset scores).",
    )


def register_both(*args, **kwargs):
    register_moodle(*args, **kwargs)
    register_rwth(*args, **kwargs)


class GenGradeUpload(CommandModule):
    module_name = "gen-grade-upload"
    commands = [
        ("rwth", register_rwth, gen_rwth),
        ("moodle", register_moodle, gen_moodle),
        ("generic", register_generic, gen_generic),
        ("both", register_both, gen_both),
    ]

    def register_command_base(
        self, parser: argparse.ArgumentParser, **defaults
    ) -> None:
        register_base(parser, **defaults)

    @property
    def additional_config(self) -> dict[str, Any]:
        nd = self.default_config["naming_dictionary"]
        return {
            "DEFAULT_MOODLE_GRADING_COL_NAME": nd.MOODLE_GRADING_COL,
            "DEFAULT_MOODLE_FEEDBACK_COL_NAME": nd.MOODLE_FEEDBACK_COL,
            "DEFAULT_USED_GRADING_COL_NAME": nd.EXAM_SCORE_COL,
            "DEFAULT_USED_FEEDBACK_COL_NAME": nd.COURSE_GRADE_COL,
            "DEFAULT_EXPORT_COLUMNS": (
                nd.EXAM_SCORE_COL,
                nd.COURSE_SCORE_COL,
                nd.COURSE_GRADE_COL,
            ),
            "DEFAULT_OUTPUT_FILE_NAME": f"upload_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.csv",
        }


if __name__ == '__main__':
    GenGradeUpload().as_program('gen-grade-upload').parse_and_run()
