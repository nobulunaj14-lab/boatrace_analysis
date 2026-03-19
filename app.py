import streamlit as st
import pandas as pd
import itertools

st.title("🚤 競艇予想ツール【ボタンなし・完全手入力】")

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

st.subheader("出走データ入力（直接入力のみ）")

boats = []

# ===== 入力フォーム（すべてテキスト） =====
for i in range(6):
    st.markdown(f"### {i+1}号艇")

    col1, col2, col3 = st.columns(3)

    with col1:
        course = st.text_input(f"コース{i+1}", str(i+1))

    with col2:
        st_time = st.text_input(f"ST{i+1}", "0.15")

    with col3:
        ex_time = st.text_input(f"展示{i+1}", "6.80")

    boats.append({
        "艇番": i+1,
        "コース": course,
        "ST": st_time,
        "展示タイム": ex_time
    })

# ===== 数値変換（安全処理） =====
def to_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default

# ===== スコア関数 =====
def score(row):
    st_val = to_float(row["ST"])
    ex_val = to_float(row["展示タイム"])
    course = int(to_float(row["コース"], 1))

    s = (7.0 - ex_val) * 10

    # ST評価
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

    # コース補正
    s *= course_weight.get(course, 1.0)

    # 場補正
    if course == 1:
        s *= st_data["in"]
    elif course in [3,4]:
        s *= st_data["makuri"]
    elif course == 2:
        s *= st_data["sashi"]
    elif course in [5,6]:
        s *= st_data["wave"]

    return s

# ===== 実行 =====
if st.button("🚀 予想実行"):
    df = pd.DataFrame(boats)

    df["スコア"] = df.apply(score, axis=1)
    df["確率"] = df["スコア"] / df["スコア"].sum()

    st.subheader("📊 スコア結果")
    st.dataframe(df.sort_values(by="スコア", ascending=False))

    # ===== 買い目 =====
    st.subheader("💰 期待値")

    combos = list(itertools.permutations(df["艇番"], 3))[:20]
    bets = []

    for combo in combos:
        odds = st.text_input(f"{combo}", "20")

        odds_val = to_float(odds, 20)

        p = (
            df.loc[df["艇番"]==combo[0],"確率"].values[0] *
            df.loc[df["艇番"]==combo[1],"確率"].values[0] *
            df.loc[df["艇番"]==combo[2],"確率"].values[0]
        )

        ev = odds_val * p
        bets.append({"買い目": combo, "期待値": ev})

    bet_df = pd.DataFrame(bets)

    st.subheader("🔥 狙い目（期待値1.2以上）")
    st.dataframe(bet_df[bet_df["期待値"] > 1.2].sort_values(by="期待値", ascending=False))
