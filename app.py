import streamlit as st
import pandas as pd
import itertools

st.title("🚤 競艇予想ツール【プロ仕様】")

# ===== 競艇場データ =====
stadium_data = {
    "桐生": {"in":1.2,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "戸田": {"in":0.9,"makuri":1.2,"sashi":1.1,"wave":1.3},
    "江戸川": {"in":0.8,"makuri":1.3,"sashi":1.2,"wave":1.5},
    "平和島": {"in":0.9,"makuri":1.2,"sashi":1.1,"wave":1.3},
    "多摩川": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "浜名湖": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "蒲郡": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "常滑": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "津": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "三国": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "びわこ": {"in":1.0,"makuri":1.1,"sashi":1.0,"wave":1.1},
    "住之江": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "尼崎": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "鳴門": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "丸亀": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "児島": {"in":1.0,"makuri":1.1,"sashi":1.0,"wave":1.1},
    "宮島": {"in":0.9,"makuri":1.2,"sashi":1.1,"wave":1.3},
    "徳山": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "下関": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "若松": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "芦屋": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "福岡": {"in":1.1,"makuri":1.0,"sashi":1.0,"wave":1.0},
    "唐津": {"in":1.2,"makuri":0.9,"sashi":1.0,"wave":0.9},
    "大村": {"in":1.3,"makuri":0.8,"sashi":1.0,"wave":0.8},
}

course_weight = {1:1.5,2:1.2,3:1.0,4:0.9,5:0.8,6:0.7}

# ===== 競艇場選択 =====
stadium = st.selectbox("競艇場", list(stadium_data.keys()))
st_data = stadium_data[stadium]

st.subheader("出走データ入力（すべて手入力）")

boats = []

# ===== 入力フォーム =====
for i in range(6):
    st.markdown(f"### {i+1}号艇")

    col1, col2, col3 = st.columns(3)

    with col1:
        course = st.number_input(f"コース{i+1}", 1, 6, i+1)

    with col2:
        # フライング対応（-0.15〜0.40、0.01刻み）
        st_time = st.number_input(
            f"ST{i+1}",
            min_value=-0.15,
            max_value=0.40,
            value=0.15,
            step=0.01,
            format="%.2f"
        )

    with col3:
        ex_time = st.number_input(
            f"展示{i+1}",
            min_value=6.50,
            max_value=7.20,
            value=6.80,
            step=0.01,
            format="%.2f"
        )

    boats.append({
        "艇番": i+1,
        "コース": course,
        "ST": st_time,
        "展示タイム": ex_time
    })

# ===== スコア関数 =====
def score(row):
    s = (7.0 - row["展示タイム"]) * 10

    st_val = row["ST"]

    # ===== ST評価 =====
    if st_val < 0:
        st_score = 5 + (st_val * 20)
    elif st_val <= 0.10:
        st_score = 10
    elif st_val <= 0.15:
        st_score = 8
    elif st_val <= 0.20:
        st_score = 6
    elif st_val <= 0.25:
        st_score = 3
    elif st_val <= 0.30:
        st_score = 0
    else:
        st_score = -6

    s += st_score

    # ===== コース補正 =====
    s *= course_weight[row["コース"]]

    # ===== 場補正 =====
    if row["コース"] == 1:
        s *= st_data["in"]
    if row["コース"] in [3,4]:
        s *= st_data["makuri"]
    if row["コース"] == 2:
        s *= st_data["sashi"]
    if row["コース"] in [5,6]:
        s *= st_data["wave"]

    return s

# ===== 実行 =====
if st.button("🚀 予想実行"):
    df = pd.DataFrame(boats)

    df["スコア"] = df.apply(score, axis=1)
    df["確率"] = df["スコア"] / df["スコア"].sum()

    st.subheader("📊 スコア結果")
    st.dataframe(df.sort_values(by="スコア", ascending=False))

    # ===== 買い目生成 =====
    st.subheader("💰 期待値")

    combos = list(itertools.permutations(df["艇番"], 3))[:20]
    bets = []

    for combo in combos:
        odds = st.number_input(f"{combo}", 1.0, 500.0, 20.0)

        p = (
            df.loc[df["艇番"]==combo[0],"確率"].values[0] *
            df.loc[df["艇番"]==combo[1],"確率"].values[0] *
            df.loc[df["艇番"]==combo[2],"確率"].values[0]
        )

        ev = odds * p
        bets.append({"買い目": combo, "オッズ": odds, "期待値": ev})

    bet_df = pd.DataFrame(bets)

    st.subheader("🔥 狙い目（期待値1.2以上）")
    st.dataframe(bet_df[bet_df["期待値"] > 1.2].sort_values(by="期待値", ascending=False))
