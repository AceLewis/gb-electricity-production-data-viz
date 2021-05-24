import os
from datetime import datetime

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd


def read_data_from_csv():
    """
    Read CSV file from disk and return a pandas DataFrame
    """
    df = pd.read_csv("gridwatch.csv")
    df.set_index(["id"], inplace=True)
    return df


def filter_data(df):
    """
    Data needs to be filtered, this removes some spikes.
    """
    # Quantile were hand picked by looking at the data.
    q_low = df[" demand"].quantile(0.00013)
    q_hi = df[" demand"].quantile(0.999933)
    return df[(df[" demand"] < q_hi) & (df[" demand"] > q_low)]


def rolling_mean(series):
    """
    Do a rolling mean because we don't want to plot hourly changes else it would be too chaotic.
    """
    return series.rolling(50000, min_periods=1).mean()


if __name__ == "__main__":
    df_filtered = filter_data(read_data_from_csv())

    timestamp = pd.to_datetime(df_filtered[" timestamp"])
    coal = df_filtered[" coal"]
    nuclear = df_filtered[" nuclear"]
    ccgt = df_filtered[" ccgt"]
    wind = df_filtered[" wind"]
    hydro = df_filtered[" hydro"]
    biomass = df_filtered[" biomass"]
    oil = df_filtered[" oil"]
    solar = df_filtered[" solar"]
    ocgt = df_filtered[" ocgt"]
    other = df_filtered[" other"]

    # Seperate into energy types as we don't want to plot all individually (it will be messy)
    green_energy = wind + hydro + biomass + solar
    # Other is mostly short term operating reserve generation by diesel
    fossil_fuels = ccgt + oil + ocgt + other

    # Do the rolling mean
    green_energy = rolling_mean(green_energy)
    # Nuclear is not renewable (but is sustainable)
    nuclear = rolling_mean(nuclear)
    fossil_fuels = rolling_mean(fossil_fuels)
    # Coal is dirty and being phased out so it is nice to include
    coal = rolling_mean(coal)

    # Needed to calculate the percentage
    total = green_energy + fossil_fuels + coal + nuclear

    # Calculate percentage for each
    green_percent = 100 * green_energy / total
    nuclear_percent = 100 * nuclear / total
    fossil_fuels_percent = 100 * fossil_fuels / total
    coal_percent = 100 * coal / total

    fig, ax = plt.subplots(figsize=(8, 8))

    # Dictionary of what to stackplot
    energy_production_types = {
        "Renewable (Wind, Hydro, Solar and Biomass)": green_percent,
        "Nuclear": nuclear_percent,
        "Other Fossil Fuels (Gas, Oil, and Diesel STOR)": fossil_fuels_percent,
        "Coal": coal_percent,
    }
    ax.stackplot(
        timestamp,
        energy_production_types.values(),
        labels=energy_production_types.keys(),
        colors=["tab:green", "tab:blue", "tab:gray", "k"],
    )
    ax.set(facecolor="tab:green")  # Fixes visual glitch

    # Plot is made, now title, label and make it look better
    fontdict = {"fontsize": 21, "fontweight": "bold", "color": "gray"}
    plt.title("Great British Electricity Production by Source", fontdict=fontdict)

    fontdict = {"fontsize": 20, "fontweight": "bold", "color": "gray"}
    plt.ylabel("Percentage", fontdict=fontdict)

    # Change label axis weight and colour
    ax.xaxis.label.set_color("grey")
    ax.xaxis.label.set_weight("bold")
    ax.yaxis.label.set_color("grey")
    ax.yaxis.label.set_weight("bold")

    # Change splines, splines are the lines on the graph
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_color("grey")
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["bottom"].set_linewidth(1.5)

    # Increase tick font size and colour
    ax.yaxis.set_tick_params(labelsize=20, colors="grey")
    ax.xaxis.set_tick_params(labelsize=15, colors="grey")

    plt.grid(b=True, which="both", linestyle="--", linewidth=0.25)

    # Set limits on x and y
    ax.set_ylim([0, 1])
    ax.set_xlim([datetime(2012, 1, 1), timestamp.iloc[-1]])

    # Put legend outside of the plot because you can't see the key of one item if it is inside
    handles, labels = ax.get_legend_handles_labels()
    legend = fig.legend(
        reversed(handles), reversed(labels), loc="upper left", bbox_to_anchor=(0.08, 0.13)
    )
    plt.setp(legend.get_texts(), color="grey", fontweight="bold")

    # Need to offset the x labels so the first year does not overlap with 0 percent.
    offset = matplotlib.transforms.ScaledTranslation(0, -0.1, fig.dpi_scale_trans)
    for label in ax.xaxis.get_majorticklabels():
        label.set_transform(label.get_transform() + offset)

    plt.autoscale(enable=True, axis="y", tight=True)
    plt.tight_layout(rect=[0, 0.103, 0.97, 1])
    plt.rcParams["axes.axisbelow"] = False

    # Put some text in the bottom left.
    fontdict = {"fontsize": 10, "fontweight": "bold", "color": "gray"}
    fig.text(
        0.01,
        0.005,
        "Source: https://gridwatch.templar.co.uk/ - AceLewis.com",
        fontdict=fontdict,
        horizontalalignment="left",
    )

    # Save and show figure.
    os.makedirs("./images/", exist_ok=True)
    fig.savefig(f"./images/gb_electricity_production.png", dpi=300)
    fig.savefig(f"./images/gb_electricity_production.svg", dpi=300)

    plt.show()
