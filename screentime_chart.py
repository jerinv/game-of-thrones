# -*- coding: utf-8 -*-
"""
Created on Sun May 12 12:33:40 2019

@author: jerin
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# =============================================================================
# Number of characters to plot
# =============================================================================
topNum = 15
# =============================================================================


def read_data():
    df = pd.read_json(r"data/episodes.json", orient="values")
    return df


def create_dataset(df):
    seasonNums = []
    episodeNums = []
    sceneStarts = []
    sceneEnds = []
    characterNames = []
    for row in df.itertuples():
        seasonNum = row.episodes["seasonNum"]
        episodeNum = row.episodes["episodeNum"]
        for scene in row.episodes["scenes"]:
            sceneStart = scene["sceneStart"]
            sceneEnd = scene["sceneEnd"]
            for character in scene["characters"]:
                characterName = character["name"]

                seasonNums.append(seasonNum)
                episodeNums.append(episodeNum)
                sceneStarts.append(sceneStart)
                sceneEnds.append(sceneEnd)
                characterNames.append(characterName)

    screenTime = pd.DataFrame(
        {
            "Season": seasonNums,
            "Episode": episodeNums,
            "SceneStart": sceneStarts,
            "SceneEnd": sceneEnds,
            "Name": characterNames,
        }
    )
    return screenTime


df = read_data()
screenTime = create_dataset(df)

screenTime["SceneStart"] = pd.to_timedelta(screenTime.SceneStart)
screenTime["SceneEnd"] = pd.to_timedelta(screenTime.SceneEnd)
screenTime["Duration"] = screenTime.SceneEnd - screenTime.SceneStart

total_screenTime_bySeason = (
    screenTime.groupby(["Season", "Name"])["Duration"].sum().reset_index()
)
total_screenTime = screenTime.groupby(["Name"])["Duration"].sum().reset_index()

topChars = total_screenTime.sort_values("Duration", ascending=False).head(topNum)
topChars["Duration_Hours"] = topChars.Duration.apply(lambda x: x.total_seconds() / 60)
topNames = topChars.Name.tolist()
topDurations = topChars.Duration_Hours.tolist()

df_plot = total_screenTime_bySeason[
    total_screenTime_bySeason.Name.isin(topNames)
].copy()
df_plot["Duration_Hours"] = df_plot.Duration.apply(lambda x: x.total_seconds() / 60)
df_plot = df_plot.pivot_table(
    index="Name",
    columns="Season",
    values="Duration_Hours",
    fill_value=0,
    aggfunc=np.sum,
    margins=True,
)
df_plot = df_plot.sort_values(by="All").drop(columns="All").head(topNum)

# add rows
add_rows = df_plot.iloc[1,].to_frame()
add_rows.columns = [""]
add_rows[""] = 0
for _ in range(0, 6):
    df_plot = df_plot.append(add_rows.T)
df_plot.columns = ["Season " + str(i) for i in df_plot.columns]

# =============================================================================
# Start Visualization
# =============================================================================
main_color = "whitesmoke"
fig, ax = plt.subplots(1, figsize=(20, 12))
fig.patch.set_facecolor(main_color)
ax.patch.set_facecolor(main_color)
# get colormap and plot
cm = plt.get_cmap("RdGy")
df_plot.plot(kind="barh", stacked=True, ax=ax, colormap=cm)
ax.set_ylabel("")
ax.set_xlabel("Minutes", size=20, labelpad=10.5)

# Turn on x-axis ticks
ax.tick_params(axis="x", which="major", length=7)

# begone the right, left, top and bottom spines
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines["left"].set_visible(False)

# removing the tick marks
ax.tick_params(left=False)

# Add image
# img = plt.imread(r'images/got_title.png', format='png')
# imagebox = OffsetImage(img, zoom=1)
# imagebox.image.axes = ax
# ab = AnnotationBbox(imagebox, (325,topNum+4),
#                xybox=(0, 1),
#                xycoords='data',
#                boxcoords="offset points",
#                pad=0, bboxprops=dict(ec='w')
#                )
# ax.add_artist(ab)

# Add image
# img = plt.imread(r'images/got_houses.png', format='png')
# imagebox = OffsetImage(img, zoom=0.5)
# imagebox.image.axes = ax
# ab = AnnotationBbox(imagebox, (500,5),
#                xybox=(0, 1),
#                xycoords='data',
#                boxcoords="offset points",
#                pad=0, bboxprops=dict(ec='w')
#                )
# ax.add_artist(ab)

# Set legend location and color
ax.legend(
    loc=(0.000, 0.01 * topNum + 0.57),
    prop={"size": 16},
    ncol=8,
    edgecolor=main_color,
    facecolor=main_color,
)

# Increase size of tick labels
ax.tick_params(axis="y", labelsize=18)
ax.tick_params(axis="x", labelsize=18)

string = f"Top {topNum} Characters by Screen Time"
ax.text(
    510,
    topNum + 1.85,
    string,
    fontweight=550,
    fontsize=30,
    horizontalalignment="right",
    verticalalignment="top",
)

string = "By Jerin Varghese\nData: github.com/jeffreylancaster/game-of-thrones"
fig.text(0.005, 0.05, string, fontdict={"color": "gray", "size": 12, "va": "center"})

for i, duration in enumerate(topDurations):
    ax.text(
        duration + 5, -i + (topNum - 1) - 0.15, int(round(duration, 0)), fontsize=16
    )

# Remove extra white space
plt.subplots_adjust(top=0.985, right=0.99)

# fig.savefig(
#     r"images/got_screentime.png", facecolor=fig.get_facecolor(), bbox_inches="tight"
# )

# Add GoT Title Image
screentime_img = Image.open(r"images/got_screentime.png", "r")
got_title_img = Image.open(r"images/got_title.png", "r")
dragon_img = Image.open(r"images/dragon_silo.png", "r")
screentime_img.paste(got_title_img, (415, 0), mask=got_title_img)
screentime_img.paste(dragon_img, (30, -10), mask=dragon_img)
# screentime_img.save(r"charts/game_of_thrones_screentime.png", format="png")
