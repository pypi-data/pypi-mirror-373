from typing import TypedDict, cast

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.colors import ListedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from linq.schema import workflow_api

# Automata's categorical color palette from here https://www.notion.so/automatatech/Colour-6a469fc971d542359cd900a42ad9b9ba?pvs=4
AUTOMATA_COLORS = [
    "#F581EE",
    "#89E0CB",
    "#A9D9FE",
    "#8CBCAC",
    "#FCCAF8",
    "#99B7CD",
    "#D8FFFC",
    "#D89EC6",
    "#CBD8D5",
    "#8197AC",
    "#CAB4C8",
    "#FE81C7",
    "#032F58",
    "#97B1AB",
    "#14C197",
    "#197959",
    "#B0FFF9",
    "#326F9C",
    "#54B2FC",
    "#F996F1",
    "#B03D8D",
    "#956891",
    "#EB04DC",
    "#FD048F",
]

# Create a global colormap from the colors
cmap = ListedColormap(AUTOMATA_COLORS)


class TaskRow(TypedDict):
    task_id: str
    start: int
    end: int
    instrument_id: str
    labware_id: str


def get_instruments_by_id(result: workflow_api.WorkflowPlanResult) -> dict[str, str]:
    return {detail.instrument.id: detail.instrument.name or detail.instrument.id for detail in result.plan.values()}


def get_labware_by_id(result: workflow_api.WorkflowPlanResult) -> dict[str, str]:
    return {
        labware.id: labware.description or labware.id
        for detail in result.plan.values()
        for labware in [*detail.labware_in, *detail.labware_out]
    }


def create_dataframe(result: workflow_api.WorkflowPlanResult) -> pd.DataFrame:
    data = []
    for task_id, details in result.plan.items():
        for source in details.labware_in:
            row: TaskRow = {
                "task_id": task_id,
                "start": details.start,
                "end": details.end,
                "instrument_id": details.instrument.id,
                "labware_id": source.id,
            }
            data.append(row)
    return pd.DataFrame(data)


def create_plot(
    title: str,
    start: list[int],
    end: list[int],
    y_values: list[str],
    color_values: list[str],
    y_labels: dict[str, str],
    color_labels: dict[str, str],
) -> tuple[Figure, Axes]:
    """Creates a Gantt chart with a The x-axis is time, the y-axis can be labware or instruments with a third dimension of color, which can represent instruments or labware."""

    if len(start) != len(end) or len(start) != len(y_values) or len(start) != len(color_values):
        raise ValueError("The length of the start, end, y_values, and color_values must be the same")

    missing_keys = [value for value in set(y_values) if value not in y_labels]
    if missing_keys:
        raise ValueError(f"Missing keys in y_labels: {', '.join(missing_keys)}")

    missing_keys = [value for value in set(color_values) if value not in color_labels]
    if missing_keys:
        raise ValueError(f"Missing keys in color_labels: {', '.join(missing_keys)}")

    fig = plt.figure(figsize=(8, 5))
    ax = plt.gca()

    # Create a dictionary to map instruments to y-values
    y_lookup: dict[str, int] = {y: i for i, y in enumerate(set(y_values))}

    # Create a color map for the labware ids
    color_lookup: dict[str, tuple[float, float, float, float]] = {
        c: cmap(i % len(AUTOMATA_COLORS)) for i, c in enumerate(set(color_values))
    }

    for i in range(len(start)):
        ax.broken_barh(
            [(start[i], end[i] - start[i])],
            (y_lookup[y_values[i]] - 0.4, 0.8),
            facecolor=color_lookup[color_values[i]],
        )

    # Set the y-ticks to be the instruments
    ax.set_yticks(list(y_lookup.values()))
    ax.set_yticklabels([y_labels[i] for i in y_lookup])

    # Create a legend with the labware
    handles = [Rectangle((0, 0), 1, 1, color=color_lookup[c]) for c in set(color_values)]
    ax.legend(handles, [color_labels[l] for l in set(color_values)])

    ax.set_xlabel("Time (s)")
    ax.set_title(title, loc="left")
    # Adjust layout to ensure y-axis labels are fully visible
    plt.tight_layout()
    plt.autoscale(enable=True, axis="both")

    return (fig, ax)


def show_labware_plot(result: workflow_api.WorkflowPlanResult) -> None:
    df = create_dataframe(result)
    labware_by_id = get_labware_by_id(result)
    instrument_by_id = get_instruments_by_id(result)

    _fig, _ax = create_plot(
        "Labware View",
        cast(list[int], df["start"].tolist()),
        cast(list[int], df["end"].tolist()),
        cast(list[str], df["labware_id"].tolist()),
        cast(list[str], df["instrument_id"].tolist()),
        cast(dict[str, str], labware_by_id),
        instrument_by_id,
    )
    plt.show()


def show_instrument_plot(result: workflow_api.WorkflowPlanResult) -> None:
    df = create_dataframe(result)
    labware_by_id = get_labware_by_id(result)
    instrument_by_id = get_instruments_by_id(result)

    _fig, _ax = create_plot(
        "Instrument View",
        cast(list[int], df["start"].tolist()),
        cast(list[int], df["end"].tolist()),
        cast(list[str], df["instrument_id"].tolist()),
        cast(list[str], df["labware_id"].tolist()),
        cast(dict[str, str], instrument_by_id),
        labware_by_id,
    )
    plt.show()
