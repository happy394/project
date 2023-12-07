import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Volleyball analysing",
                   page_icon="🏐",
                   initial_sidebar_state="collapsed"
                   )

with st.sidebar:
    st.write("Some information about the project")
    st.link_button(
        "Dataset link",
        "https://www.kaggle.com/datasets/kacpergregorowicz/-mens-volleyball-plusliga-20082022/data"
    )

df = pd.read_csv("Mens-Volleyball-PlusLiga-2008-2023.csv")

df.drop(["T1_Srv_Sum", "T1_Srv_Err", "T1_Srv_Ace", "T1_Rec_Sum", "T1_Rec_Err", "T1_Rec_Perf", "T1_Att_Sum", "T1_Att_Err", "T1_Att_Kill",
         "T1_Att_Kill_Perc", "T1_Rec_Pos", "T1_Att_Blk", "T1_Sum", "T1_BP", "T1_Ratio",
         "T2_Srv_Sum", "T2_Srv_Err", "T2_Srv_Ace", "T2_Rec_Sum", "T2_Rec_Err", "T2_Rec_Perf", "T2_Att_Sum", "T2_Att_Err", "T2_Att_Kill",
         "T2_Att_Kill_Perc", "T2_Rec_Pos", "T2_Att_Blk", "T2_Sum", "T2_BP", "T2_Ratio"],
       axis=1, inplace=True)

col_with_perc = ['T1_Srv_Eff', 'T1_Att_Eff', 'T2_Srv_Eff', 'T2_Att_Eff']
for i in col_with_perc:
    df[i] = pd.to_numeric(df[i].str.replace('%', ''))

col_with_commas = ['T1_Blk_As', 'T2_Blk_As']
for i in col_with_commas:
    df[i] = pd.to_numeric(df[i].str.replace(',', '.'))

df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y, %H:%M')
df.sort_values("Date", inplace=True)


def time_change(val):
    for i in range(2008, 2023):
        if pd.Timestamp(i, 8, 30, 12) < val < pd.Timestamp(i + 1, 6, 1, 9):
            return i
    return False


def points_count(val_1, val_2):
    if val_1 == 3 and val_2 == 0:
        return "3-0"
    elif val_1 == 3 and val_2 == 1:
        return "3-1"
    elif val_1 == 3 and val_2 == 2:
        return "3-2"
    elif val_1 == 2 and val_2 == 3:
        return "2-3"
    elif val_1 == 1 and val_2 == 3:
        return "1-3"
    elif val_1 == 0 and val_2 == 3:
        return "0-3"


for date in df.Date:
    temp = time_change(date)
    ind = df[df["Date"] == date].index
    df.loc[ind, "Date"] = f"{temp}"
df.Date = df.Date.apply(lambda x: str(x)[:4])

teams_list = set(list(df["Team_1"])) | set(list(df["Team_2"]))
years_list = sorted(set(list(df["Date"])))

year_count = {}
for year in df.Date:
    year_count.update({year: 0})
for year in df.Date:
    year_count[year] += 1
buff_df = pd.DataFrame.from_dict(year_count.items())
buff_df = buff_df.rename(columns={0: "Year", 1: "Games"})

df_2 = df.loc[:, ["Date", "Team_1", "Team_2", "T1_Score", "T2_Score", "Winner"]]
df_2.reset_index(drop=True, inplace=True)
df_2.head()

points_dict = dict()
for year in years_list:
    points_dict.update({year: {}})
    for team in teams_list:
        points_dict[year].update({team: {}})
        points_dict[year][team].update({"sum": 0, "3-0": 0, "3-1": 0, "3-2": 0, "2-3": 0, "1-3": 0, "0-3": 0})
for ind in df_2.index:
    row = df_2.loc[ind]
    left = points_count(row.T1_Score, row.T2_Score)
    right = points_count(row.T2_Score, row.T1_Score)

    points_dict[row.Date][row.Team_1][left] += 1
    points_dict[row.Date][row.Team_2][right] += 1
for year in years_list:
    for team in teams_list:
        points_dict[year][team]["sum"] = (points_dict[year][team]["3-0"] + points_dict[year][team]["3-1"]) * 3 + \
                                         points_dict[year][team]["3-2"] * 2 + points_dict[year][team]["2-3"]

points_list = list()
for year in years_list:
    for team in teams_list:
        points_list.append([points_dict[year][team]["sum"], year, team, points_dict[year][team]["3-0"], points_dict[year][team]["3-1"],
                              points_dict[year][team]["3-2"], points_dict[year][team]["2-3"],
                              points_dict[year][team]["1-3"], points_dict[year][team]["0-3"]])

main_df = pd.DataFrame.from_dict(points_list)
main_df.columns = ["Points", "Year", "Team", "3-0", "3-1", "3-2", "2-3", "1-3", "0-3"]
for ind in main_df.index:
    if main_df.loc[ind]["Points"] == 0:
        main_df.drop(index=ind, inplace=True)


fig_2 = go.Figure()
count = 0
buff = []
for year in years_list:
    fig_2.add_trace(
        go.Bar(x=main_df.loc[main_df.Year == year].sort_values(by="Points", ascending=False)["Team"],
               y=main_df.loc[main_df.Year == year].sort_values(by="Points", ascending=False)["Points"],
               name=str(year)[:4],
               base=dict(color="#33CFA5"))
    )

    visibility = [False] * 23
    visibility[count] = True
    count += 1

    buff.append(
        dict(label=str(year)[:4],
             method="update",
             args=[{"visible": visibility}]
             )
    )
fig_2.update_layout(
    updatemenus=[
        dict(
            active=1,
            buttons=buff,
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0,
            xanchor="left",
            y=1.3,
            yanchor="top"
        ),

    ])

fig_3 = px.pie(buff_df, names="Year", values="Games", color_discrete_sequence=px.colors.sequential.RdBu)

st.title("Men's Volleyball - PlusLiga - 2008-2023")
st.subheader("Library statistics")
col1, col2, col3 = st.columns(3)
with col1:
    _value = len(df.index)
    st.metric(label="Matches", value=_value)
with col2:
    _value = len(teams_list)
    st.metric(label="Teams", value=_value)
with col3:
    _value = 14
    st.metric(label="Years", value=_value)

st.subheader("Number of matches each year")
st.plotly_chart(fig_3)

st.subheader("Result table for each year")
st.plotly_chart(fig_2)

st.subheader("Tournament table by every year")
year_option = st.selectbox("Choose the year", years_list)
target_columns = ['Points', 'Team', '3-0', '3-1', '3-2', '2-3', '1-3', '0-3']
_main_df = main_df[main_df.Year == year_option][target_columns].sort_values(by="Points", ascending=False)
best_team = _main_df["Team"].iloc[0]
_main_df = _main_df.style.background_gradient(subset=["Points"])
st.dataframe(
    _main_df,
    hide_index=True
)

st.write(f"Winner: {best_team}", )

_col1, _col2, _col3 = st.columns(3)
if best_team == "ZAKSA Kędzierzyn-Koźle":
    with _col1:
        st.write(' ')
    with _col2:
        st.image("https://upload.wikimedia.org/wikipedia/en/7/7b/ZAKSAKKLogo.png", width=200)
    with _col3:
        st.write(' ')
if best_team == "Asseco Resovia":
    with _col1:
        st.write(' ')
    with _col2:
        st.image("https://i.pinimg.com/originals/9e/d3/2d/9ed32d9cfd182141618d6c92a428b5b2.jpg", width=170)
    with _col3:
        st.write(' ')
if best_team == "PGE Skra Bełchatów":
    with _col1:
        st.write(' ')
    with _col2:
        st.image("https://play-lh.googleusercontent.com/R1rtUtkN4bYrQDwtVZmxUEKNVQ8BbtJl907av4QCffj_UMVpWD_ztaf4OyzGand0nU0", width=200)
    with _col3:
        st.write(' ')
