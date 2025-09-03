# grading-tools

This is a collection of some grading tools.
The current state is that not all functionality is functional.

This resource is made up of three major components: a pair of Excel templates, a python package with a CLI (command line interface), and an extensive usage example.
Only the python package is available on PyPI.

### Usage Example

Please refer to `examples/example-apm-25/README.md`.
This example could also be used for testing purposes when developing new features or fixing old ones. 

### Excel Templates

In the subfolder [excel-templates](excel-templates/), there is an overview template for exams and one for assignments.
The templates are supposed to be usable as-is via configuration and power queries to external Excel/csv files that conform to particular naming conventions (see [defaults.py](grading_tools/common/defaults.py)).
Importantly, the templates are called _overview_ because no data should be entered into them: they simply join and transform the task-specific (generated) files.
To update the contents, e.g., after review, edit/replace the source file(s) and click "recompute connections".

#### exam-overview

This is intended to combine the data from
- RWTHOnline registrations,
- per-student assignment scores, and
- a grading table.  

It contains an overview table with exam admissibility (using the assignment scores), calculated grades (the course score calculation and grade ranges are configurable) and lists of exam participants with room assignments for attendance sheets.  

#### assignment-overview

This is intended to combine data from,
- a moodle group info table (functionality described in a later section), and
- group-based grading tables for the first and second part of an assignment.  

It contains an overview table with joined (group -> individual student) assignment scores and exam admissibility.
Furthermore, it is supposed to be used as a source for the exam-overview. 

### Grading Tools Functionality

The grading tool collection is realized as a CLI python package that can be built into an `.exe` (or platform equivalent) using `PyInstaller`.
It is supposed to be easily extensible with new commands using the `CommandModule` class.
All commands and options are documented in the CLI, so the detailed functionality and configuration can be explored using the `--help` (`-h`) option.  
Some of the following command names/arguments may be outdated, so please reference the `-h` printouts.

#### Generating Grading Tables

This tool uses a json/yaml-based specification of a "gradable", e.g., assignment or exam, that defines the structure and number of points of (sub)questions.

Consider the following partial example. It defines an exam that is made up of four questions, some with (sub)(sub)questions.

```yaml
version: v1
tree-level-names:
  - Exam
  - Question
  - Subquestion
  - Subsubquestion
tree:
  label: exam-1
  children:
    - label: Q1
      children:
        - label: a
          pts: 4
        - label: b
          pts: 3
        - label: c
          pts: 6
        - label: d
          children:
            - label: i
              pts: 2
            - label: ii
              pts: 4  
```

The entire structure is a tree with each node being either intermediate (having a list of children), e.g., _Q1_, or a leaf node, e.g., _Q1 a_.
Each leaf has to have a specification of the number of achievable points.
Using this, appropriate (sub) total columns can be generated in a grading table.
Currently, the following are the considered properties.
- `summary`: used to mark a placeholder total column that sums its preceding ancestors (this generates a formula column)
- `bonus`: a task marked as bonus is not counted in the total number of achievable points
- `mandatory` (only applicable in checkbox-based grading): the total of a task is only calculated if one of its mandatory columns is checked
- `skip`: combines both sub-options below
  - `skip_in_total`: the task is skipped in total calculation (e.g., used in deduction-based grading)
  - `skip_in_formula`: the task is skipped in total formulas (used for formula columns themselves, e.g., sub-totals)  

Each path of this tree corresponds to a column in a generated grading table.
For example, for _Q1_, there would be columns _Q1-a_, _Q1-b_, _Q1-b_, _Q1-c_ and _Q1-d-i_ and _Q1-d-ii_.
By default, also some summary columns are generated, e.g., _Q1-d-Total_.

It is possible to automatically add summary/total columns up to a specified level in the tree via the `--totals-level` flag.
For example, the below command would introduce sub-total columns for each question, and each level above, i.e., usually the whole exam/assignment.
`python -m grading_tools.main gen-grading -s gradable-specification.yaml -o output.xlsx  -tl "Question" --aux --index-columns "Group ID"`

By default, some additional formula columns are generated, including a _Participated_ and _Final Points_ column.
The latter is supposed to be used as the value for grade calculation, uploading, etc.

```
python -m grading_tools.main gen-grading
  --spec gradable-specification.yaml
  --index-file exam-overview.xlsx 
  --index-table Registrations 
  --output output.xlsx
  --totals-level "Question"
  --aux
  --utility-columns
```

There is also support for "checkbox" based grading, i.e., where instead of entering the number of achieved points in the cells of the table, instead, cells are either checked with an "x" or left unchecked, and the achieved points are calculated from specified grading key.
The option `--grading-style [checkboxes|numbers]` (short: `-gs`) determines which style is used.
To properly make use of _checkbox_ grading, the gradable specification needs to encode the all possible deductions within a task, or alternatively, all possible achievable partial points.
The generated grading sheet contains some sanity checking formulas and highlighting.
For example, a grading key aspect can be marked as _mandatory_ to specify that it needs to have a checkmark ("x") for its (sub)question total to be calculated.
Multiple mandatory sibling nodes are placed in a disjunction, i.e., either of them needs to be ticked for the task to count. 
In deduction based grading, this is useful to differentiate whether a task has not been worked on by the student at all or whether it has not been graded yet.
The following are example definitions of a checkbox-graded task with a grading key.

```yaml
version: v1
tree-level-names:
  - Assignment
  - Question
  - Subquestion
  - Grading Key
tree:
  label: assignment-part-1
  children:
    - label: Q1
      children:
        - label: a
          children:
            - label: did
              pts: 1
              mandatory: True
            - label: didnot
              pts: 0
              mandatory: True
            - label: doc-minor
              text: "documentation error"
              pts: -0.25
              skip_in_total: True
            - label: doc-medium
              text: "documentation error"
              pts: -1
              skip_in_total: True
```

```yaml
version: v0
Q1:
  - a:
      - did:
          text: worked on task
          pts: 5
          mandatory: True
      - didnot:
          text: skipped task
          pts: 0
          mandatory: True
      - gk1:
          text: did not do X
          pts: -2
          skip_in_total: True
      - gk2:
          text: did not do Y
          pts: -3
          skip_in_total: True
      - gk3:
          text: X and Y not done properly
          pts: -3
          skip_in_total: True
  - b:
      - gk1:
          text: did do X
          pts: 2
      - gk2:
          text: did do Y
          pts: 3
```

Subquestion `a` uses a deduction-based style, where `did` determines the max achievable points, and `gk1`, `gk2` and `gk3` define possible deductions.
Note that `gk` `1` and `2` are independent/disjoint, while `gk3` overlaps with both of them and, i.e., has to be mutually exclusive with the aforementioned to guarantee non-negative points.  
It would be ideal to avoid such "entangled" gk elements, as they complicate "outsourced" grading.
Including `did` and `didnot` as alternative mandatory nodes may seem redundant, however, note how this allows distinguishing between an ungraded task and one that the student did not work on (as mentioned before).
Subquestion `b` uses "additive grading", i.e., when a `gk` element applies, the student gets points for it.
It's also possible to have overlapping/mutually exclusive entries here, but same as before, it may be best to avoid them.
In this scenario, it would also necessitate the usage of `skip_in_total` declarations as the total number of points of `b` would not simply be the sum of all `gk` elements anymore.  
The tool currently has no special treatment of overlapping/mutually exclusive grading key entries.

To support grading table merging and grading key changes, table generation can be "seeded" with existing data via the `--data-file` (short: `-df`), `--data-sheet` and `--data-table` flags.
`python.exe -m grading_tools.main gen-grading -s example.yaml -tl Question -gs checkboxes -o test-new.xlsx -df test.xlsx`

Group-based grading should use the groups as index instead of the default one row per student.  
```
python -m grading_tools.main gen-grading 
    -s .\sandbox\raw\apm-ass-pt-1.yaml 
    --index-file .\sandbox\moodle-groups-info.xlsx 
    -it "Groups_Assignment_Part_1" 
    -o .\sandbox\ 
    -ic "Group Name" "Group ID"
```  
It is recommended to first generate an index via the `gen-excel groups-info` command.

#### Merging Grading Tables

To support parallel/distributed grading, there is functionality for merging individual grading tables.
It is possible to perform both joins on the columns (_horizontal_) as well as the rows (_vertical_), i.e., when grading is split by questions (columns) or by students (rows).
Arbitrary combinations of the two can be merged at once to produce a new canonical "single source of truth" via the combined grading table. 
Consider `tests/merging` for a simple example of a 3-way merge.

The merging operation is specified via a _merge pattern_.
```
python -m grading_tools.main edit-grading merge 
    --spec example.yaml
    --output merged.xlsx
    --files a.xlsx b.xlsx c.xlsx d.xlsx
    --merge-pattern "0/1/2 3"
```
Given the four Excel files a-d, the merge pattern "0/1/2 3" specifies that the result will be made up of three groups of rows: `a.xlsx`, `b.xlsx`, and the join of `c.xlsx` and `d.xlsx` (files are referred to by their indices).  
This requires that `c.xlsx` and `d.xlsx` only overlap on their index columns (e.g., matriculation number), as a doubly defined grading column may indicate an error.
For this purpose only columns that contain at least one value are considered, i.e., in theory `c.xlsx` and `d.xlsx` can use the same table structure and just have to leave the columns (questions) of the other file untouched.
Importantly however, both these files should have an exactly matching index, e.g., contain scores for precisely the same students/groups.
Otherwise, the implicit outer join will generate empty cells.
Lastly, symmetrically to within-group column disjointness, each group of rows must not have overlapping row indices, as otherwise the scores of a student/group would be overwritten.
Analogously, empty rows are not considered, so, in theory, all joined grading tables could use the same generated grading table.
However, it is highly recommended to at least split the horizontal (by question) distribution into different grading tables via manually splitting the overall gradable spec into parts.
This way, the individual grading tables need less horizontal space and are easier to use.

#### Generating a Moodle Group Info Table

To more easily handle group based grading of moodle based assignments, a _group info_ table can be generated from the exported students list.
This simplifies joins over group numbers + rows and makes it easier to consider all students, not just those who have joined a group; particularly due to the two part nature of the assignments.
Importantly, this table is recommended for usage in the `assignment-overview.xlsx` template.

##### Example
`python -m grading_tools.main gen-misc groups-info -m .\sandbox\raw\moodle-groups.csv -gfmts "Group A1 {:01}" "Group A2 {:02}" -o output.xlsx`

#### Generating Moodle/RWTHOnline Exports

Both moodle and RWTHOnline support .csv based upload of grades using a special exportable file containing the list of students and an empty column for grades. 
The `gen-grade-upload` and `gen-group-upload` generate a completed version of these files by joining the given list with a provided grading table or `exam-overview.xlsx`.  

##### Examples
```
python -m grading_tools.main gen-group-upload 
  -g grading-table.xlsx
  -m moodle-grading-table.csv
  -gfmt "Group A2 {:2}"
```

`python -m grading_tools.main gen-grade-upload both -h`

#### Generating Grade/Points Distribution Diagrams

There are some specialized rudimentary plots that can be generated from an exam-overview (grades, with and without assignment consideration) and grading tables (per-question point distribution). 

##### Example
`python -m grading_tools.main gen-diagrams all -h`

#### Saving Commands

Since commands can get long due to the many options and are unlikely to "change" much between members of a teaching team or over the course of a semester, there is support for .yaml file based configuration of commands.
Such a config can easily be shared to simplify "handover of work" between team members and ensure consistency.
There is a minimal example in the tests: [tests/merging/cfg.yaml](tests/merging/cfg.yaml).
A config file can contain arguments for multiple commands.
It is used via the `from-cfg` command as can be seen below.  
`python -m grading_tools.main from-cfg -cfg cfg.yaml -cmd merge [further arguments are passed through]`
The options specified in `cfg.yaml` under the key `merge` are then provided as additional arguments to the `merge` command.  

#### Ancillary: Handling the Moodle Assignment Submission .zip 

`python unwrap_presents -h`