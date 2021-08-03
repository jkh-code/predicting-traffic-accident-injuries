import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from typing import Tuple

def injury_vs_no_injury_plot(
        df: pd.DataFrame,
        feature_to_plot: str,
        figsize: Tuple[int, int]=(10, 7),
        title: str="TBD",
        xlabel: str="TBD",
        ylabel: str="TBD",
        percents: bool=False
        ) -> Tuple[Figure, Axes]:
    """Plot grouped bar chart with one group as 'No' injury crashes and the
    other group as 'Yes' injury crashes."""
    fig, ax = plt.subplots(figsize=figsize)
    if percents:
        perc = (
            (df.groupby(["has_injuries", feature_to_plot])["crash_record_id"]
                .count()) 
            / (df.groupby(["has_injuries"])["crash_record_id"].count()))
        (perc.reset_index()
            .set_index("has_injuries")
            .pivot(columns=feature_to_plot, values="crash_record_id")
            .fillna(0.0)).plot(kind="bar", ax=ax)
    else:
        (df.groupby(["has_injuries", feature_to_plot])["crash_record_id"]
            .count()
            .reset_index()
            .set_index("has_injuries")
            .pivot(columns=feature_to_plot, values="crash_record_id")
            .fillna(0.0)).plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels(["No", "Yes"])
    ax.legend(title=None)
    return fig, ax


if __name__ == "__main__":
    pass