import streamlit as st
import pandas as pd
import itertools

st.set_page_config(layout="centered")

st.title("🚤 競艇予想ツール【プロ仕様フル版】")

# ===== 全24場 =====
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

# ===== 競艇場 =====
stadium = st.selectbox("競艇場", list(stadium_data.keys()))
st_data = stadium_data[stadium]

# ===== 気象 =====
st.subheader("🌊 気象条件")
wind_dir = st.selectbox("風向き", ["無風","向かい風","追い風","横風"])
wind_speed = float(st.text_input("風速", "3"))
wave = float(st.text_input("波の高さ", "5"))

# ===== 入力 =====
boats = []
st.subheader("出走データ（平均STは「-」可）")

for i in range(6):
    st.markdown(f"### {i+1}号艇")

    course = st.text_input(f"コース{i+1}", str(i+1))
    st_time = st.text_input(f"ST{i+1}", "0.15")
    avg_st = st.text_input(f"平均ST{i+1}", "0.15")
    ex = st.text_input(f"展示{i+1}", "6.80")
    motor = st.text_input(f"モーター{i+1}", "30")
    boat = st.text_input(f"ボート{i+1}", "30")

    boats.append({
        "艇番": i+1,
        "コース": course,
        "ST": st_time,
        "平均ST": avg_st,
        "展示タイム": ex,
        "モーター": motor,
        "ボート": boat
    })

# ===== 変換 =====
def to_float_or_none(x):
    try:
        if str(x).strip() == "-":
            return None
        return float(x)
    except:
        return None

# ===== スコア =====
def score(row):
    st_val = to_float_or_none(row["ST"])
    avg_st = to_float_or_none(row["平均ST"])
    ex = to_float_or_none(row["展示タイム"]) or 7.0
    motor = to_float_or_none(row["モーター"]) or 0
    boat = to_float_or_none(row["ボート"]) or 0
    course = int(to_float_or_none(row["コース"]) or 1)

    s = (7.0 - ex) * 10

    if st_val is not None:
        if st_val <= 0.10: s += 10
        elif st_val <= 0.15: s += 8
        elif st_val <= 0.20: s += 5
        else: s -= 5

    if avg_st is not None:
        if avg_st <= 0.13: s += 6
        elif avg_st <= 0.16: s += 3
    else:
        s += 1  # データなし＝少し荒れ要素

    s += motor * 0.3
    s += boat * 0.2

    s *= course_weight.get(course,1)

    if course == 1:
        s *= st_data["in"]
    elif course in [3,4]:
        s *= st_data["makuri"]
    elif course == 2:
        s *= st_data["sashi"]
    elif course in [5,6]:
        s *= st_data["wave"]

    return s

# ===== 展開予測 =====
def predict(df):
    st_vals = [to_float_or_none(v) or 0.2 for v in df["ST"]]

    if wave >= 10:
        return "荒れ（高波）"

    if wind_dir == "向かい風" and wind_speed >= 5:
        return "荒れ（向かい風）"

    if st_vals[0] <= 0.15 and st_data["in"] >= 1.1:
        return "逃げ"

    if st_data["makuri"] >= 1.2:
        if st_vals[2] <= 0.12:
            return "まくり3"
        if st_vals[3] <= 0.12:
            return "まくり4"

    if st_data["sashi"] >= 1.1 and st_vals[1] <= 0.13:
        return "差し"

    return "混戦"

# ===== 買い目 =====
def generate(df, pattern):
    top = list(df.sort_values(by="スコア", ascending=False)["艇番"])

    if pattern == "逃げ":
        return [(1, top[1], top[2])]

    if pattern == "まくり3":
        return [(3,1,top[2]), (3,top[2],1)]

    if pattern == "まくり4":
        return [(4,1,top[2]), (4,top[2],1)]

    if pattern == "差し":
        return [(2,1,top[2])]

    return list(itertools.permutations(top[:4],3))[:6]

# ===== 色分け =====
def highlight(row, max_score):
    if row["スコア"] == max_score:
        return ['background-color: red'] * len(row)
    elif row["スコア"] >= max_score * 0.9:
        return ['background-color: yellow'] * len(row)
    return [''] * len(row)

# ===== 実行 =====
if st.button("🚀 予想実行"):
    df = pd.DataFrame(boats)
    df["スコア"] = df.apply(score, axis=1)

    df_sorted = df.sort_values(by="スコア", ascending=False)
    max_score = df_sorted["スコア"].max()

    display_df = df_sorted.drop(columns=["艇番"]).reset_index(drop=True)

    st.subheader("📊 スコア")
    styled = display_df.style.apply(lambda r: highlight(r, max_score), axis=1)
    st.dataframe(styled, use_container_width=True)

    pattern = predict(df)
    st.subheader("🔥 展開")
    st.success(pattern)

    bets = generate(df, pattern)
    st.subheader("🎯 買い目")
    for b in bets:
        st.write(b)
