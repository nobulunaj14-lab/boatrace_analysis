import streamlit as st
import pandas as pd

st.set_page_config(layout="centered")

st.title("🚤 競艇予想ツール【スマホ対応】")

# ===== 競艇場 =====
stadium_data = {
    "桐生": {"in":1.2}, "戸田": {"in":0.9}, "江戸川": {"in":0.8},
    "平和島": {"in":0.9}, "多摩川": {"in":1.1}, "浜名湖": {"in":1.1},
    "蒲郡": {"in":1.2}, "常滑": {"in":1.2}, "津": {"in":1.2},
    "三国": {"in":1.1}, "びわこ": {"in":1.0}, "住之江": {"in":1.2},
    "尼崎": {"in":1.2}, "鳴門": {"in":1.1}, "丸亀": {"in":1.1},
    "児島": {"in":1.0}, "宮島": {"in":0.9}, "徳山": {"in":1.2},
    "下関": {"in":1.1}, "若松": {"in":1.1}, "芦屋": {"in":1.2},
    "福岡": {"in":1.1}, "唐津": {"in":1.2}, "大村": {"in":1.3},
}

stadium = st.selectbox("競艇場", list(stadium_data.keys()))

st.subheader("出走データ（平均STは「-」可）")

boats = []

# ===== 入力（スマホ用：縦並び） =====
for i in range(6):
    st.markdown(f"### {i+1}号艇")

    course = st.text_input(f"コース{i+1}", str(i+1))
    st_time = st.text_input(f"ST{i+1}", "0.15")
    avg_st = st.text_input(f"平均ST{i+1}", "0.15")
    ex = st.text_input(f"展示タイム{i+1}", "6.80")
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
        s += 1

    s += motor * 0.3
    s += boat * 0.2

    return s

# ===== 色分け =====
def highlight(row, max_score):
    if row["スコア"] == max_score:
        return ['background-color: #ff4d4d'] * len(row)  # 赤（本命）
    elif row["スコア"] >= max_score * 0.9:
        return ['background-color: #ffcc00'] * len(row)  # 黄（対抗）
    else:
        return [''] * len(row)

# ===== 実行 =====
if st.button("🚀 予想実行"):
    df = pd.DataFrame(boats)
    df["スコア"] = df.apply(score, axis=1)

    df_sorted = df.sort_values(by="スコア", ascending=False)

    max_score = df_sorted["スコア"].max()

    # 表示用（艇番削除＋インデックス削除）
    display_df = df_sorted.drop(columns=["艇番"]).reset_index(drop=True)

    st.subheader("📊 スコア（色分け）")

    styled = display_df.style.apply(
        lambda row: highlight(row, max_score), axis=1
    )

    st.dataframe(styled, use_container_width=True)
