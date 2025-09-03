from collections.abc import Sequence
from typing import TypedDict

import pydantic


# @dataclasses.dataclass(frozen=True)
class NamingDictionary(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    # moodle

    ## csv

    ## csv structure
    MOODLE_CSV_SEP: str = ','
    MOODLE_CSV_DECIMAL_SEP: str = ','
    MOODLE_QUOTE_CHAR: str = '"'
    MOODLE_NA_CHAR: str = '-'

    ### csv grading table of moodle activity with group submissions

    MOODLE_ID_COL: str = 'ID'
    MOODLE_MATR_COL: str = 'Matrikelnummer'
    MOODLE_FULL_NAME_COL: str = 'Vollständiger Name'
    MOODLE_IDENTITY_COLS: Sequence[str] = ('Vollständiger Name',)
    MOODLE_GROUP_COL: str = 'Gruppe'
    MOODLE_GRADING_COL: str = 'Bewertung'
    MOODLE_FEEDBACK_COL: str = 'Feedback als Kommentar'

    ### csv export of students with group memberships

    MOODLE_GROUPS_CSV_SEP: str = ';'
    MOODLE_GROUPS_QUOTE_CHAR: str = '"'

    MOODLE_GROUPS_IDENTITY_COLS: Sequence[str] = ('Vorname', 'Nachname')
    MOODLE_GROUPS_MATR_COL: str = 'Matrikelnummer'
    MOODLE_GROUPS_GROUPS_COL: str = 'Gruppen'

    ## excel

    ### excel grading table export

    MOODLE_EXCEL_ID_COL: str = 'LMS-ID'
    MOODLE_EXCEL_MATR_COL: str = 'Matrikelnummer'
    MOODLE_EXCEL_IDENTITY_COLS: Sequence[str] = ('Nachname', 'Vorname')

    # rwth online

    ## csv structure

    RWTHONLINE_CSV_SEP: str = ';'
    # unsure here
    # RWTHONLINE_DECIMAL_SEP = ','
    RWTHONLINE_QUOTE_CHAR: str = '"'

    ### exam registrations table

    RWTHONLINE_MATR_COL: str = 'REGISTRATION_NUMBER'
    RWTHONLINE_IDENTITY_COLS: Sequence[str] = ('FAMILY_NAME_OF_STUDENT', 'FIRST_NAME_OF_STUDENT')
    RWTHONLINE_GRADE_COL: str = 'GRADE'

    # exam management

    MATR_COL: str = 'Matr No'
    FIRST_NAME_COL: str = 'First Name'
    LAST_NAME_COL: str = 'Last Name'
    FULL_NAME_COL: str = 'Full Name'
    IDENTITY_COLS: Sequence[str] = (LAST_NAME_COL, FIRST_NAME_COL)
    PARTICIPATED_COL: str = 'Participated'

    ## grading table

    GRADING_SHEET_NAME: str = 'GradingTable'
    GRADING_TABLE_NAME: str = 'GradingTable'
    GRADING_GKINFO_TABLE_NAME: str = 'GKInfo'
    GRADING_INDIVIDUAL_ID_COL: str = MATR_COL
    GRADING_GROUP_ID_COL: str = 'Group ID'
    GRADING_GROUP_NAME_COL: str = 'Group Name'
    GRADING_TOTAL_COL: str = 'Final Points'

    ## overview table

    OVERVIEW_TABLE_NAME: str = 'Overview'
    ADMISSION_COL: str = 'Admitted'
    PASSED_COL: str = 'Passed'
    ASSIGNMENT_SCORE_COL: str = 'Assignment Score'
    EXAM_SCORE_COL: str = 'Exam Score'
    COURSE_SCORE_COL: str = 'Course Score'
    EXAM_GRADE_COL: str = 'Exam Grade'
    COURSE_GRADE_COL: str = 'Course Grade'

    ## moodle groups table

    GROUPS_INFO_TABLE_NAME: str = 'GroupsInfo'

    ### grade calculation
    # TODO maybe move elsewhere
    GRADE_FALLBACK_VALUE: str = 'X'  # did not show


class BaseConfig(pydantic.BaseModel):
    naming_dictionary: NamingDictionary = NamingDictionary()


class MinimalConfig(TypedDict, total=False):
    naming_dictionary: NamingDictionary


def get_base_cfg() -> MinimalConfig:
    return MinimalConfig(naming_dictionary=NamingDictionary())
