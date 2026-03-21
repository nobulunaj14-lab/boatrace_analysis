import streamlit as st
import pandas as pd
import itertools

st.title("🚤 競艇予想ツール【風・波・展開・自動買い目】")

# ===== 全競艇場 =====
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

# ===== 入力 =====
stadium = st.selectbox("競艇場", list(stadium_data.keys()))
st_data = stadium_data[stadium]

st.subheader("🌊 気象条件")

colw1, colw2, colw3 = st.columns(3)

with colw1:
    wind_dir = st.selectbox("風向き", ["無風","向かい風","追い風","横風"])

with colw2:
    wind_speed = st.text_input("風速(m)", "3")

with colw3:
    wave = st.text_input("波の高さ(cm)", "5")

boats = []
st.subheader("出走データ")

# ===== 入力 =====
for i in range(6):
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        course = st.text_input(f"コース{i+1}", str(i+1))

    with col2:
        st_time = st.text_input(f"ST{i+1}", "0.15")

    with col3:
        avg_st = st.text_input(f"平均ST{i+1}", "0.15")

    with col4:
        ex_time = st.text_input(f"展示{i+1}", "6.80")

    with col5:
        motor = st.text_input(f"モーター{i+1}", "30")

    with col6:
        boat = st.text_input(f"ボート{i+1}", "30")

    boats.append({
        "艇番": i+1,
        "コース": course,
        "ST": st_time,
        "平均ST": avg_st,
        "展示タイム": ex_time,
        "モーター": motor,
        "ボート": boat
    })

# ===== 変換 =====
def to_float(x):
    try:
        return float(x)
    except:
        return 0

# ===== スコア =====
def score(row):
    st_val = to_float(row["ST"])
    avg_st = to_float(row["平均ST"])
    ex = to_float(row["展示タイム"])
    motor = to_float(row["モーター"])
    boat = to_float(row["ボート"])
    course = int(to_float(row["コース"]))

    s = (7.0 - ex) * 10

    if st_val <= 0.10:
        s += 10
    elif st_val <= 0.15:
        s += 8
    elif st_val <= 0.20:
        s += 5
    else:
        s -= 5

    if avg_st <= 0.13:
        s += 6
    elif avg_st <= 0.16:
        s += 3

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

# ===== 展開予測（風＋波込み） =====
def predict(df):
    st_dict = {row["コース"]: to_float(row["ST"]) for _, row in df.iterrows()}

    w = to_float(wind_speed)
    wa = to_float(wave)

    # 風影響
    if wind_dir == "向かい風":
        if w >= 5:
            return "荒れ（向かい風）"

    if wind_dir == "追い風":
        if st_dict.get(1,1) <= 0.15:
            return "逃げ"

    # 波
    if wa >= 10:
        return "荒れ（高波）"

    # 通常展開
    if st_dict.get(1,1) <= 0.15 and st_data["in"] >= 1.1:
        return "逃げ"

    if st_data["makuri"] >= 1.2:
        if st_dict.get(3,1) <= 0.12:
            return "まくり3"
        if st_dict.get(4,1) <= 0.12:
            return "まくり4"

    if st_data["sashi"] >= 1.1:
        if st_dict.get(2,1) <= 0.13:
            return "差し"

    return "荒れ"

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

# ===== 実行 =====
if st.button("🚀 予想実行"):
    df = pd.DataFrame(boats)

    df["スコア"] = df.apply(score, axis=1)

    st.subheader("📊 スコア")
    st.dataframe(df.sort_values(by="スコア", ascending=False))

    pattern = predict(df)

    st.subheader("🔥 展開")
    st.success(pattern)

    bets = generate(df, pattern)

    st.subheader("🎯 自動買い目")
    for b in bets:
        st.write(b)
