import html
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 1. ページ設定 & デザイントークン
# ---------------------------------------------------------
st.set_page_config(
    page_title="ストレス分析ヘルスケア",
    page_icon="🧘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

FONT = "'Zen Maru Gothic', 'Hiragino Maru Gothic ProN', 'Yu Gothic', sans-serif"
INK = "#4B3F5E"     # 本文（濃い梅色）
MUTED = "#7C718A"    # 補助テキスト
PLUM = "#8E6BE8"      # アクセント（ラベンダー）
MILK = "#FFF7F5"      # 背景（ミルクピンク）

# 状態ごとの色・表情・ひとこと
STATUS = {
    "green": dict(main="#5CC9A0", soft="#E4F7EE", face="😊", title="いい調子！",
                  msg="このペースを保てるといいね。"),
    "orange": dict(main="#FFA94D", soft="#FFF0DB", face="😟", title="ちょっとお疲れ気味",
                   msg="早めに休む時間をつくろうね。"),
    "red": dict(main="#FF7A9A", soft="#FFE3EA", face="😢", title="がんばりすぎかも",
                msg="今日は予定を軽くして、ゆっくり休もう。"),
}

FACTOR_EMOJI = {
    "就職活動": "💼",
    "学業・卒研": "📚",
    "人間関係": "👭",
    "体調・運動不足": "🛏️",
    "その他・日常": "☁️",
    "その他・特になし": "☁️",
}
PASTELS = ["#C9B6FF", "#FFC6D9", "#BFEBD7", "#FFE2A8", "#BFE0FF", "#FFD0B5"]

# 全てのCSSスタイルを1つのst.markdownにまとめ、中括弧をエスケープ
st.markdown(f"""
<style>
/* ---- ヘッダー ---- */
.app-head {{ display: flex; align-items: center; gap: 14px; margin-bottom: 18px; }}
.app-emoji {{ width: 52px; height: 52px; border-radius: 18px; background: #F0E6FF;
    display: grid; place-items: center; font-size: 1.7rem; }}
.app-title {{ font-size: 1.5rem; font-weight: 700; color: {INK}; line-height: 1.2; }}
.app-sub {{ font-size: .85rem; color: {MUTED}; margin-top: 2px; }}

/* ---- タブ（ピル型） ---- */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; background: #fff; padding: 5px; border-radius: 99px;
    border: 2px solid #FFE3EA; }}
.stTabs [data-baseweb="tab"] {{ flex: 1; height: 40px; border-radius: 99px; padding: 0 8px;
    color: {MUTED}; font-weight: 700; justify-content: center; }}
.stTabs [aria-selected="true"] {{ background: #F0E6FF; color: {INK}; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.2rem; }}

/* ---- ヒーローカード ---- */
.hero {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 22px;
    border-radius: 32px; padding: 24px 20px; margin-bottom: 14px; }}
.ring {{ width: 140px; height: 140px; border-radius: 50%; display: grid; place-items: center; flex: none; }}
.ring-inner {{ width: 106px; height: 106px; border-radius: 50%; background: #fff; display: grid;
    place-items: center; text-align: center; }}
.ring-num {{ font-size: 2.3rem; font-weight: 700; color: {INK}; line-height: 1; }}
.ring-sub {{ font-size: .75rem; color: {MUTED}; margin-top: 2px; }}
.hero-text {{ text-align: left; min-width: 180px; }}
.face {{ font-size: 2.4rem; line-height: 1; margin-bottom: 6px; }}
.hero-title {{ font-size: 1.3rem; font-weight: 700; color: {INK}; }}
.hero-msg {{ font-size: .95rem; color: {INK}; margin: 4px 0 10px; line-height: 1.6; }}
.pill {{ display: inline-block; padding: 4px 14px; border-radius: 99px; background: #fff;
    font-size: .85rem; font-weight: 700; color: {INK}; }}

/* ---- 歩数・睡眠カード ---- */
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; }}
.stat {{ background: #fff; border: 2px solid #FFE9EF; border-radius: 22px; padding: 16px; }}
.stat-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
.bubble {{ width: 34px; height: 34px; border-radius: 12px; display: grid; place-items: center; font-size: 1.1rem; }}
.stat-label {{ font-size: .9rem; font-weight: 700; color: {MUTED}; }}
.stat-value {{ font-size: 1.7rem; font-weight: 700; color: {INK}; line-height: 1.1; }}
.stat-value small {{ font-size: .85rem; font-weight: 500; color: {MUTED}; margin-left: 2px; }}
.bar {{ height: 10px; border-radius: 99px; background: #F5ECF8; margin: 12px 0 8px; overflow: hidden; }}
.bar > i {{ display: block; height: 100%; border-radius: 99px; }}
.stat-sub {{ font-size: .8rem; color: {MUTED}; }}

/* ---- メモカード & タグ ---- */
.memo {{ background: #fff; border: 2px dashed #E7D9F5; border-radius: 22px; padding: 16px 18px; margin-bottom: 14px; }}
.memo-label {{ font-size: .85rem; font-weight: 700; color: {MUTED}; margin-bottom: 6px; }}
.memo-text {{ font-size: 1rem; color: {INK}; line-height: 1.7; margin-bottom: 10px; }}
.chip {{ display: inline-block; padding: 4px 12px; border-radius: 99px; background: #F0E6FF;
    font-size: .82rem; font-weight: 700; color: {INK}; }}

/* ---- アラート ---- */
.alert {{ border-radius: 18px; padding: 14px 16px; margin-bottom: 10px; font-size: .95rem;
    line-height: 1.6; color: {INK}; }}
.alert-warn {{ background: #FFE3EA; }}
.alert-ok {{ background: #E4F7EE; }}

/* ---- 予測・結果カード ---- */
.result {{ border-radius: 26px; padding: 20px; margin: 6px 0 14px; }}
.result-label {{ font-size: .85rem; font-weight: 700; color: {MUTED}; margin-bottom: 4px; }}
.result-value {{ font-size: 2.2rem; font-weight: 700; color: {INK}; line-height: 1.1; }}
.result-value small {{ font-size: .9rem; font-weight: 500; color: {MUTED}; }}
.result-sub {{ margin-top: 10px; }}

/* ---- 凡例 ---- */
.legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 8px; }}
.legend span {{ padding: 3px 12px; border-radius: 99px; font-size: .78rem; font-weight: 700; color: {INK}; }}
.note {{ font-size: .78rem; color: {MUTED}; margin-top: 18px; text-align: center; }}

/* ---- ウィジェット ---- */
[data-testid="stSidebar"] {{ background: #FFEFF4; }}
.stButton > button[kind="primary"], button[data-testid="stBaseButton-primary"] {{
    background: {PLUM}; border: none; border-radius: 99px; color: #fff; font-weight: 700; padding: .6rem 1rem; }}
.stButton > button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {{
    background: #7B58D6; color: #fff; }}
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="base-input"] {{ border-radius: 16px !important; }}
[data-testid="stDataFrame"] {{ border-radius: 20px; overflow: hidden; border: 2px solid #FFE9EF; }}
</style>
""", unsafe_allow_html=True)


def render(markup: str):
    """インデントや空行でMarkdownに誤解されないようHTMLを整形して描画"""
    cleaned = "\n".join(line.strip() for line in markup.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def status_of(score: float) -> str:
    if score >= 70:
        return "red"
    if score >= 45:
        return "orange"
    return "green"


def fmt_date(d) -> str:
    return f"{d.month}/{d.day}"


# ---------------------------------------------------------
# 2. ロジック関数群
# ---------------------------------------------------------
def analyze_text_sentiment(text: str) -> float:
    if not text:
        return 0.0
    pos_words = ["嬉しい", "楽しい", "最高", "すっきり", "達成", "順調", "リフレッシュ", "感謝", "よい", "良い", "内定", "合格"]
    neg_words = ["疲れた", "つらい", "辛い", "しんどい", "忙しい", "眠い", "不安", "頭痛", "イライラ", "失敗", "落ち込む"]

    pos_count = sum(1 for word in pos_words if word in text)
    neg_count = sum(1 for word in neg_words if word in text)

    total = pos_count + neg_count
    if total == 0:
        return 0.0
    return (pos_count - neg_count) / total


def classify_stress_factor(text: str) -> str:
    if not text:
        return "その他・特になし"
    text = str(text)
    if any(w in text for w in ["就活", "面接", "選考", "エントリー", "ES", "企業", "説明会", "お祈り", "内定"]):
        return "就職活動"
    elif any(w in text for w in ["卒研", "卒業研究", "論文", "発表", "ゼミ", "教授", "課題", "テスト"]):
        return "学業・卒研"
    elif any(w in text for w in ["友達", "喧嘩", "人", "上司", "彼氏", "彼女", "親", "人間関係"]):
        return "人間関係"
    elif any(w in text for w in ["眠れなかった", "だるい", "頭痛", "熱", "体調", "動けない", "疲れた", "運動"]):
        return "体調・運動不足"
    else:
        return "その他・日常"


def calculate_health_scores(steps: int, sleep: float, stress_level: int, memo: str):
    steps_score = min(100.0, (steps / 8000.0) * 100.0)
    if sleep >= 7.5:
        sleep_score = max(0.0, 100.0 - (sleep - 7.5) * 10)
    else:
        sleep_score = max(0.0, (sleep / 7.5) * 100.0)

    sentiment = analyze_text_sentiment(memo)

    physical_deficit = ((100.0 - steps_score) * 0.2) + ((100.0 - sleep_score) * 0.3)
    subjective_stress = (stress_level / 5.0) * 40.0
    sentiment_stress = (-sentiment) * 10.0

    total_stress_index = min(100.0, max(0.0, physical_deficit + subjective_stress + sentiment_stress))

    if total_stress_index >= 70:
        risk_level = "高リスク"
        status_color = "red"
    elif total_stress_index >= 45:
        risk_level = "中リスク"
        status_color = "orange"
    else:
        risk_level = "良好"
        status_color = "green"

    factor = classify_stress_factor(memo)

    return {
        "steps_score": round(steps_score, 1),
        "sleep_score": round(sleep_score, 1),
        "sentiment": round(sentiment, 2),
        "stress_index": round(total_stress_index, 1),
        "risk_level": risk_level,
        "status_color": status_color,
        "factor": factor,
    }


def detect_early_warnings(df: pd.DataFrame) -> list:
    warnings = []
    if len(df) >= 2 and all(df.iloc[-2:]["ストレス指標"] >= 60):
        warnings.append("🚨 【連続高ストレス警告】2日以上高ストレス状態です。意識的な休息を取りましょう。")
    if len(df) >= 3:
        avg_sleep = df.iloc[-3:]["睡眠時間"].mean()
        if avg_sleep < 6.0:
            warnings.append(f"⚠️ 【睡眠負債】直近3日の平均睡眠時間は {avg_sleep:.1f} 時間です。")
        if df.iloc[-3:]["歩数"].mean() < 4000:
            warnings.append("🚶‍♂️ 【運動不足】軽いストレッチや散歩をおすすめします。")
    return warnings


def predict_tomorrow_stress(df: pd.DataFrame) -> dict:
    if len(df) < 3:
        return {"predicted_score": 50.0, "trend": "データ不足（横ばい推測）"}

    recent_df = df.tail(5)
    x = np.arange(len(recent_df))
    y = recent_df["ストレス指標"].values

    slope, intercept = np.polyfit(x, y, 1)
    predicted_val = round(max(0.0, min(100.0, float(slope * len(recent_df) + intercept))), 1)

    if slope > 3.0:
        trend = "上昇傾向 ↗️"
    elif slope < -3.0:
        trend = "改善傾向 ↘️"
    else:
        trend = "安定 ➡️"

    return {"predicted_score": predicted_val, "trend": trend}


# ---------------------------------------------------------
# 3. 認証 & ユーザー別データの初期化（ここに置き換え）
# ---------------------------------------------------------
# パスワード認証用のユーザーリスト
USER_CREDENTIALS = {
    "user_A": "password123",
    "user_B": "secret456",
    "test_user": "testpass"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""

# ユーザーごとのデータフレームを保持する辞書
if "user_databases" not in st.session_state:
    st.session_state.user_databases = {}


# =========================================================
# 4. 未ログイン時の画面（ログインフォーム）
# =========================================================
if not st.session_state.logged_in:
    st.title("🔐 ログイン認証")
    st.write("ストレス可視化セルフケア支援システムをご利用の際は、IDとパスワードを入力してください。")
    
    with st.form("login_form"):
        input_user = st.text_input("ユーザーID")
        input_pass = st.text_input("パスワード", type="password")
        submit_btn = st.form_submit_button("ログイン")
        
        if submit_btn:
            if input_user in USER_CREDENTIALS and USER_CREDENTIALS[input_user] == input_pass:
                st.session_state.logged_in = True
                st.session_state.current_user = input_user
                
                # ログインしたユーザーのデータがまだなければ初期データを作る
                if input_user not in st.session_state.user_databases:
                    today = datetime.now().date()
                    initial_entry = {
                        "日付": today, "歩数": 0, "睡眠時間": 0.0, "主観ストレス度": 3,
                        "メモ": "まだ記録がありません。サイドバーから今日の記録を入力してみましょう！",
                        "ストレス指標": 50.0, "リスク判定": "良好", "ストレス要因": "その他・特になし",
                    }
                    st.session_state.user_databases[input_user] = pd.DataFrame([initial_entry])
                
                st.success("ログインに成功しました！まもなく画面が切り替わります。")
                st.rerun()
            else:
                st.error("⚠️ ユーザーIDまたはパスワードが間違っています。")

# =========================================================
# 5. ログイン成功後のメインアプリ画面（元のUIやタブ、サイドバー）
# =========================================================
else:
    user = st.session_state.current_user
    
    # サイドバーにログイン中ユーザーとログアウトボタンを表示
    st.sidebar.success(f"👤 ログイン中: **{user}** さん")
    if st.sidebar.button("ログアウト"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    # 1. もしログイン中ユーザーのデータ箱がまだなければ、初期データを作成して用意する
    if user not in st.session_state.user_databases:
        today = datetime.now().date()
        initial_entry = {
            "日付": today,
            "歩数": 0,
            "睡眠時間": 0.0,
            "主観ストレス度": 3,
            "メモ": "まだ記録がありません。サイドバーから今日の記録を入力してみましょう！",
            "ストレス指標": 50.0,
            "リスク判定": "良好",
            "ストレス要因": "その他・特になし",
        }
        st.session_state.user_databases[user] = pd.DataFrame([initial_entry])

    # 2. ★ここがポイント！
    # ユーザーごとのデータを、元のUIがそのまま使える `st.session_state.df` に結びつける
    st.session_state.df = st.session_state.user_databases[user]
