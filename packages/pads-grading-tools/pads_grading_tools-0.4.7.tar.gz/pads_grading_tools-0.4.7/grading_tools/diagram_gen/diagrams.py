import argparse
import os
import pathlib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from grading_tools.common.commands import CommandModule
from grading_tools.common.defaults import NamingDictionary
from grading_tools.common.gradable_spec import load_spec
from grading_tools.common.utils import read_generic_table, get_possible_grades
from grading_tools.grading_table_gen.grading_table_commons import (
    mk_node_name,
    skip_in_formula,
)


def save_plot(fig: go.Figure, name, **config):
    format_ = config["output_format"]
    _, ext = os.path.splitext(name)
    if not ext:
        name = f"{name}.{format_}"
    p = pathlib.Path(config["output"]).joinpath(name)
    if not p.parent.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    if format_ == "html":
        fig.write_html(p)
    else:
        fig.write_image(p, format=format_)


def gen_overview_figs(grades_file: str, naming_dictionary: NamingDictionary, **config):
    scores_plot_title = config["SCORES_TITLE"]
    grades_plot_title = config["GRADES_TITLE"]
    index_col = config["index_column"]
    df = read_generic_table(
        grades_file,
        table_name=config.pop("grades_table", None),
        sheet_name=config.pop("grades_sheet", None),
    )

    melted_scores = df.melt(
        id_vars=[index_col],
        value_vars=[
            naming_dictionary.ASSIGNMENT_SCORE_COL,
            naming_dictionary.EXAM_SCORE_COL,
            naming_dictionary.COURSE_SCORE_COL,
        ],
        var_name="Kind",
        value_name="Score",
    )

    fig_scores_a = px.histogram(
        melted_scores,
        x="Score",
        template="plotly_white",
        color="Kind",
        barmode="group",
        title=scores_plot_title,
        nbins=25,
        histnorm=config.get("histnorm"),
    )
    fig_scores_b = px.histogram(
        melted_scores,
        x="Score",
        template="plotly_white",
        facet_row="Kind",
        title=scores_plot_title,
        nbins=25,
        histnorm=config.get("histnorm"),
    )
    save_plot(fig_scores_a, f"scores-overview-a", **config)
    save_plot(fig_scores_b, f"scores-overview-b", **config)

    melted_grades = df.melt(
        id_vars=[index_col],
        value_vars=[
            naming_dictionary.EXAM_GRADE_COL,
            naming_dictionary.COURSE_GRADE_COL,
        ],
        var_name="Kind",
        value_name="Grade",
    )

    possible_grades = get_possible_grades(absent=False)
    # simply append the other statuses, e.g., "did not show"
    possible_grades.extend(
        (
            set(df[naming_dictionary.EXAM_GRADE_COL].unique())
            | set(df[naming_dictionary.COURSE_GRADE_COL].unique())
        )
        - set(possible_grades)
    )

    fig_grades_a = px.histogram(
        melted_grades,
        x="Grade",
        template="plotly_white",
        color="Kind",
        barmode="group",
        title=grades_plot_title,
        category_orders={"Grade": possible_grades},
        histnorm=config.get("histnorm"),
    )
    fig_grades_b = px.histogram(
        melted_grades,
        x="Grade",
        template="plotly_white",
        facet_row="Kind",
        title=grades_plot_title,
        category_orders={"Grade": possible_grades},
        histnorm=config.get("histnorm"),
    )

    return fig_grades_a, fig_grades_b


def gen_overview(**config):
    fig_grades_a, fig_grades_b = gen_overview_figs(**config)
    save_plot(fig_grades_a, f"grades-overview-a", **config)
    save_plot(fig_grades_b, f"grades-overview-b", **config)
    gen_pie(**config)

def gen_pie_fig(
    *,
    grades_file: str,
    index_column: str,
    naming_dictionary: NamingDictionary,
    **config,
):
    df = read_generic_table(
        grades_file,
        table_name=config.pop("grades_table", None),
        sheet_name=config.pop("grades_sheet", None),
    )
    melted_grades = df.melt(
        id_vars=[index_column],
        value_vars=[
            naming_dictionary.EXAM_GRADE_COL,
            naming_dictionary.COURSE_GRADE_COL,
        ],
        var_name="Kind",
        value_name="Grade",
    )
    melted_grades["Category"] = melted_grades["Grade"].map(
        {g: "passed" for g in get_possible_grades(absent=False)}
        | {"X": "no show", "5.0": "failed"}
    )
    return px.pie(
        melted_grades, facet_col="Kind", names="Category", title="Exam/Course Outcomes"
    )


def gen_pie(**config):
    f = gen_pie_fig(**config)
    save_plot(f, "outcomes-pie", **config)


def gen_per_question_fig(
    gradable_spec: str, grading_file: str, naming_dictionary: NamingDictionary, **config
):
    spec = load_spec(gradable_spec)
    points_df = read_generic_table(
        grading_file,
        table_name=config.pop("grading_table", None),
        sheet_name=config.pop("grading_sheet", None),
    )

    index_col = config["index_column"]

    facet_level = config["facet_level"]
    facet_level_index = spec.get_level_index(facet_level)

    if gl := config.get("groups_level"):
        groups_level = gl
    else:
        groups_level = spec.tree_level_names[facet_level_index - 1]
    groups_level_index = spec.get_level_index(groups_level)
    leaf_node_distinguishability_level_index = groups_level_index
    figs = {}
    group_level_nodes = spec.get_level(groups_level)
    # if there is only one group, the expected names do not need the group level prefix to be distinguishable,
    # since all leaves will be in that one singular group anyways
    if len(group_level_nodes) <= 1:
        leaf_node_distinguishability_level_index = facet_level_index
    for n in group_level_nodes:
        # fallback if there are no nodes on the intended facet level
        adapted_facet_level_index = facet_level_index
        faceted_cols = [
            c
            for c in n.iter_level(adapted_facet_level_index - groups_level_index)
            if not skip_in_formula(c)
        ]
        while (
            len(faceted_cols) == 0
            and adapted_facet_level_index >= leaf_node_distinguishability_level_index
        ):
            faceted_cols = [
                c
                for c in n.iter_level(adapted_facet_level_index - groups_level_index)
                if not skip_in_formula(c)
            ]
            adapted_facet_level_index -= 1
        #

        facet_rows = len(faceted_cols)
        titles = [
            mk_node_name(c, start_depth=adapted_facet_level_index) for c in faceted_cols
        ]

        if facet_rows > 0:
            fig = make_subplots(
                rows=facet_rows, subplot_titles=titles, x_title="Points"
            )
            for i, (facet_name, fn) in enumerate(zip(titles, faceted_cols), 1):
                leaves = [
                    mk_node_name(
                        leaf, start_depth=leaf_node_distinguishability_level_index
                    )
                    for leaf in fn.leaves_iter()
                    if not skip_in_formula(leaf)
                ]

                summarized_cols = [
                    col
                    for col in points_df.columns
                    if any(leaf in col for leaf in leaves)
                ]  # or startswith
                facet_totals = points_df.set_index(index_col)[summarized_cols].sum(
                    axis="columns"
                )
                facet_totals = facet_totals.dropna()
                g = go.Histogram(
                    x=facet_totals,
                    name=facet_name,
                    xbins=dict(start=-0.5, end=int(np.ceil(fn.pts + 0.5)), size=1),
                    histnorm=config.get("histnorm"),
                )
                fig.add_trace(g, row=i, col=1)
                fig.update_xaxes(range=[0, int(np.ceil(fn.pts))], tick0=0, row=i, col=1)
            fig.update_layout(
                height=facet_rows * 300,
                title_text=f"Points per {facet_level} in {n.label}",
                template="plotly_white",
            )
            figs[n.label] = fig

    return figs


def gen_per_question(**config):
    figs = gen_per_question_fig(**config)
    facet_level = config["facet_level"]
    for label, fig in figs.items():
        save_plot(fig, f"points-per-{facet_level.lower()}-in-{label.lower()}", **config)


def configure_parser_per_question(parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults):
    parser.add_argument(
        "-gs",
        "--gradable-spec",
        required=True,
        help="Path to the specification of this gradable.",
    )
    parser.add_argument(
        "-gp",
        "--grading-file",
        required=True,
        help="Path to grading file with per-question points.",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-gpsh",
        "--grading-sheet",
        required=False,
        help="Optionally, excel sheet within grading file.",
    )
    group.add_argument(
        "-gpt",
        "--grading-table",
        required=False,
        default=naming_dictionary.GRADING_TABLE_NAME,
        help="Optionally, excel table within grading file.",
    )
    parser.add_argument(
        "-fl",
        "--facet-level",
        required=False,
        default=defaults["facet_level"],
        help='The level in the gradable spec to create histograms for, e.g., "Question".',
    )
    parser.add_argument(
        "-gl",
        "--groups-level",
        required=False,
        help='The level in the gradable spec to create groups of histograms for, e.g., "Exam". By default, this level is the one above the facet_level.',
    )


def configure_parser_overview(
    parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults
) -> None:
    parser.add_argument(
        "-gr",
        "--grades-file",
        required=True,
        help="Path to the grades/scores file.",
        dest="grades_file",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-grsh",
        "--grades-sheet",
        required=False,
        help="Optionally, excel sheet within grades file.",
    )
    group.add_argument(
        "-grt",
        "--grades-table",
        required=False,
        help="Optionally, excel table within grades file.",
        default=naming_dictionary.OVERVIEW_TABLE_NAME,
    )

    parser.add_argument(
        "--assignment-score-column",
        required=False,
        help="Column with assignment score.",
        default=naming_dictionary.ASSIGNMENT_SCORE_COL,
        dest="ASSIGNMENT_SCORE_COL",
    )
    parser.add_argument(
        "--exam-score-column",
        required=False,
        help="Column with exam score.",
        default=naming_dictionary.EXAM_SCORE_COL,
        dest="EXAM_SCORE_COL",
    )
    parser.add_argument(
        "--course-score-column",
        required=False,
        help="Column with course total score.",
        default=naming_dictionary.COURSE_SCORE_COL,
        dest="COURSE_SCORE_COL",
    )
    parser.add_argument(
        "--exam-grade-column",
        required=False,
        help="Column with exam grade.",
        default=naming_dictionary.EXAM_GRADE_COL,
        dest="EXAM_GRADE_COL",
    )
    parser.add_argument(
        "--course-grade-column",
        required=False,
        help="Column with course grade.",
        default=naming_dictionary.COURSE_GRADE_COL,
        dest="COURSE_GRADE_COL",
    )


def configure_base_parser(
    parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults
) -> None:
    parser.add_argument(
        "-o", "--output", required=False, help="Path to output directory.", default="./"
    )
    parser.add_argument(
        "-of",
        "--output-format",
        required=False,
        choices=["png", "svg", "jpg", "pdf", "html"],
        help="Image file format to use.",
        default="png",
    )
    parser.add_argument(
        "-ic",
        "--index-column",
        required=False,
        type=str,
        default=naming_dictionary.MATR_COL,
        help="Column to use as index, e.g., Matr No or Group ID.",
    )
    parser.add_argument(
        "-hn",
        "--histnorm",
        help="Optionally, a non-default histogram normalization. (plotly argument)",
    )


def configure_all(
    parser: argparse.ArgumentParser, naming_dictionary: NamingDictionary, **defaults
) -> None:
    configure_parser_overview(parser, naming_dictionary=naming_dictionary, **defaults)
    configure_parser_per_question(
        parser, naming_dictionary=naming_dictionary, **defaults
    )


def gen_all(**config):
    gen_overview(**config)
    gen_per_question(**config)


class GenDiagram(CommandModule):
    module_name = "gen-diagrams"
    commands = [
        ("overview", configure_parser_overview, gen_overview),
        ("per-question", configure_parser_per_question, gen_per_question),
        ("all", configure_all, gen_all),
    ]
    additional_config = {
        "SCORES_TITLE": "Scores Overview",
        "GRADES_TITLE": "Grades Overview",
        "facet_level": "Question",
    }

    def register_command_base(self, parser: argparse.ArgumentParser, **defaults) -> None:
        configure_base_parser(parser, **defaults)


if __name__ == '__main__':
    GenDiagram().as_program('gen').parse_and_run()
