import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from typing import Tuple, Union

def injury_vs_no_injury_plot(
        df: pd.DataFrame,
        feature_to_plot: str,
        base_feature: str="has_injuries",
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
            (df.groupby([base_feature, feature_to_plot])["crash_record_id"]
                .count()) 
            / (df.groupby([base_feature])["crash_record_id"].count()))
        (perc.reset_index()
            .set_index(base_feature)
            .pivot(columns=feature_to_plot, values="crash_record_id")
            .fillna(0.0)).plot(kind="bar", ax=ax)
    else:
        (df.groupby([base_feature, feature_to_plot])["crash_record_id"]
            .count()
            .reset_index()
            .set_index(base_feature)
            .pivot(columns=feature_to_plot, values="crash_record_id")
            .fillna(0.0)).plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if base_feature == "has_injuries":
        ax.set_xticklabels(["No", "Yes"])
        ax.legend(title=None)
    elif base_feature == "injury_category":
        ax.legend(title=None, loc="upper left", bbox_to_anchor=(1, 1))
    return fig, ax

def rewrite_yaxis_labels(
        fig: Figure, ax: Axes, percent: bool=False, 
        start: Union[None, int, float]=None, 
        stop: Union[None, int, float]=None, 
        step: Union[None, int]=None, 
        num_points: Union[None, int]=None) -> Tuple[Figure, Axes]:
    """Rewrite y-axis labels for 1000's or percentages."""
    if percent:
        range_ = np.linspace(start, stop, num_points)
        ax.set_yticks(range_)
        ax.set_yticklabels([f"{num*100:.0f}%" for num in range_])
    else:
        range_ = range(start, stop+1, step)
        ax.set_yticks(range_)
        ax.set_yticklabels(
            [(f"{label/1000:.0f}k" if start >= 1_000 
                else f"{label}") for label in range_])
    
    fig.tight_layout()
    return fig, ax

def save_plot(plot_name: str, notebook: bool=True) -> None:
    """Save plot from a jupyter notebook or script."""
    if notebook:
        path = "./../images/" + plot_name + ".png"
    else:
        path = "./images/" + plot_name + ".png"
    
    plt.savefig(path, bbox_inches='tight')
    return None

# def limit_injury_category_plot() -> None:
    # fig, ax = plt.subplots(figsize=(10, 7))
    # perc = (
    #     (df_crashes.groupby(["injury_category", "first_crash_type"])["crash_record_id"]
    #         .count()) 
    #     / (df_crashes.groupby(["injury_category"])["crash_record_id"].count()))
    # perc = (perc.reset_index()
    #     .set_index("injury_category")
    #     .pivot(columns="first_crash_type", values="crash_record_id")
    #     .fillna(0.0))
    # perc.loc[:, (perc > 0.05).any().values].plot(kind="bar", ax=ax)
    # ax.set_title("Percent of Accidents by Top 8 First Crash Types")
    # ax.set_xlabel("Injury Category")
    # ax.set_ylabel("Percent of Group")
    # ax.legend(title=None, loc="upper left", bbox_to_anchor=(1, 1))
    # return None

if __name__ == "__main__":
    pass