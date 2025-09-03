import argparse
import os
import zipfile
from typing import Any

import pandas as pd

from grading_tools.common.commands import CommandModule
from grading_tools.common.compat_utils import stringify_scores_for_moodle
from grading_tools.common.defaults import NamingDictionary
from grading_tools.common.utils import read_generic_table


def generate_feedback(grading_file: str, gk_info_file: str, naming_dictionary: NamingDictionary, **config) -> tuple[
    dict[int, str], pd.DataFrame]:
    grading_df = read_generic_table(grading_file, sheet_name=config.pop('grading_sheet', None),
                                    table_name=config.pop('grading_table', None))
    gk_info_df = read_generic_table(gk_info_file, sheet_name=config.pop('gk_info_sheet', None),
                                    table_name=config.pop('gk_info_table', None))
    gk_info_df = gk_info_df.set_index('Info')
    gk_info_df_t = gk_info_df.T.convert_dtypes(convert_string=True, convert_floating=True)

    grading_df = grading_df.set_index(naming_dictionary.GRADING_GROUP_ID_COL)
    gk_text = gk_info_df_t['Text']
    gk_pts = gk_info_df_t['Points']

    bitmask = grading_df[gk_info_df_t.index].map(lambda x: x and type(x) is str and ('x' in x or 'X' in x)).astype(bool)

    if config.get('verbose', False):
        print(gk_info_df)
        print(grading_df)
        print(bitmask)
        print(bitmask.sum(axis=1))

    feedbacks = {}
    for group_id in bitmask.index:
        row = bitmask.loc[group_id].to_numpy()
        qs = gk_info_df_t.index[row]
        strs = gk_text.iloc[row]
        pts = gk_pts.iloc[row]

        def fmt_q(q: str):
            return '-'.join(q.split('-')[:-1])

        def fmt_t(t: str | None):
            return t + ' ' if pd.notna(t) else ''

        txt = f'Feedback Group {group_id}\n'
        txt += '\n'.join((f'{fmt_q(q)}: {fmt_t(t)}({p})' for q, t, p in zip(qs, strs, pts)))
        feedbacks[group_id] = txt

    data = {'total': stringify_scores_for_moodle(grading_df[naming_dictionary.GRADING_TOTAL_COL], naming_dictionary),
            'feedback': [feedbacks[gid] for gid in grading_df.index]}  # feedbacks.values() should also work
    feedback_df = pd.DataFrame(data, index=pd.Index(grading_df.index, name=naming_dictionary.GRADING_GROUP_ID_COL))

    return feedbacks, feedback_df


def zip_round_trip(feedbacks: dict[int, str], output_zip: str, submissions_file: str, group_name_fmt: str, **config):
    dirname = os.path.dirname(output_zip)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with zipfile.ZipFile(submissions_file, 'r', zipfile.ZIP_DEFLATED) as sz:
        submission_names = {(fn[:i] if (i := fn.find('/')) > 0 else fn) for fn in sz.namelist()}

        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as fz:
            for group_id, txt in feedbacks.items():
                group_name = group_name_fmt.format(group_id)
                matching_submissions = {sn for sn in submission_names if group_name in sn}
                if config.get('verbose', False):
                    if len(matching_submissions) > 1:
                        print(f'Multiple submission folders match the group name {group_name} for id {group_id}.')
                    if len(matching_submissions) < 1:
                        print(f'No submission folders match the group name {group_name} for id {group_id}.')
                if len(matching_submissions) == 1:
                    submission_name = matching_submissions.pop()
                    fz.writestr(os.path.join(submission_name, 'feedback.txt'), txt)


def export_feedback_folder(output_dir: str, grading_file: str, gk_info_file: str, naming_dictionary: NamingDictionary,
                           **config):
    feedbacks, feedback_df = generate_feedback(grading_file, gk_info_file, naming_dictionary, **config)

    os.makedirs(output_dir, exist_ok=True)
    for group_id, txt in feedbacks.items():
        with open(os.path.join(output_dir, f'feedback-{group_id}.txt'), 'w') as f:
            f.write(txt)
    feedback_df.to_csv(os.path.join(output_dir, 'all-feedback.csv'))


def export_feedback_zip(moodle_output: str, submissions_zip: str, grading_file: str, gk_info_file: str,
                        naming_dictionary: NamingDictionary, **config):
    feedbacks, feedback_df = generate_feedback(grading_file, gk_info_file, naming_dictionary, **config)
    zip_round_trip(feedbacks, moodle_output, submissions_zip, **config)


def export_feedback(**config):
    if 'output_dir' in config:
        export_feedback_folder(**config)
    if 'moodle_output' in config:
        export_feedback_zip(**config)


def configure_parser(parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults):
    parser.add_argument('-o', '--output', required=False, help='Path to output directory.', dest='output_dir',
                        default=defaults['DEFAULT_OUTPUT_DIR_NAME'])

    parser.add_argument('-g', '--grading-file', required=True, help='Path to grading file with group scores.')
    parser.add_argument('-gk', '--gk-info-file', required=True, help='Path to grading key info.',
                        dest='gk_info_file')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-sh', '--grading-sheet', required=False, help='Optionally, excel sheet within grading file.')
    group.add_argument('-t', '--grading-table', required=False, help='Optionally, excel table within grading file.',
                       default=naming_dictionary.GRADING_TABLE_NAME)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-gksh', '--gk-info-sheet', required=False,
                       help='Optionally, gk info excel sheet within grading file.')
    group.add_argument('-gkt', '--gk-info-table', required=False,
                       help='Optionally, gk info excel table within grading file.',
                       default=naming_dictionary.GRADING_GKINFO_TABLE_NAME)

    parser.add_argument('-v', '--verbose', required=False, action='store_true', default=False,
                        help='Whether to produce more verbose output.')


def configure_parser_moodle(parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults):
    configure_parser(parser, naming_dictionary, **defaults)
    parser.add_argument('-mo', '--moodle-output', required=False, help='Path to moodle output zip.',
                        default=defaults['DEFAULT_MOODLE_OUTPUT_NAME'])

    parser.add_argument('-szip', '--submissions-zip', required=True,
                        help='Path to submissions zip file as downloaded from moodle.')
    parser.add_argument('-gfmt', '--group-name-fmt', required=True,
                        help='Format str to recreate the group names used in moodle group creation (in Python style, e.g., "Group A1 {:02}").')


class ComposeFeedback(CommandModule):
    module_name = 'gen-group-feedback'
    commands = [('basic', configure_parser, export_feedback_folder),
                ('moodle', configure_parser_moodle, export_feedback_zip)]

    @property
    def additional_config(self) -> dict[str, Any]:
        return {'DEFAULT_OUTPUT_DIR_NAME': 'feedback/', 'DEFAULT_MOODLE_OUTPUT_NAME': 'moodle-feedback.zip'}


if __name__ == '__main__':
    ComposeFeedback().as_program('group-feedback').parse_and_run()
