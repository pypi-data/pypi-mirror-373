import pandas as pd

from grading_tools.common.defaults import NamingDictionary


def stringify_scores_for_moodle(series: pd.Series, naming_dictionary: NamingDictionary):
    return series.apply(lambda x: f'{x:.2f}'.replace('.', naming_dictionary.MOODLE_CSV_DECIMAL_SEP))

def stringify_grades_for_rwthonline(series: pd.Series):
    return series.astype(str).str.replace('.', ',')