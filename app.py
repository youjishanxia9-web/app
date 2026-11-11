import html
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from supabase import create_client, Client

# ---------------------------------------------------------
# 1. ページ設定 & Supabase接続の初期化
# ---------------------------------------------------------
st.set_page_config(
    page_title="ストレス分析ヘルスケア",
    page_icon="🧘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# StreamlitのSecrets（またはRender等の環境変数）からSupabase接続情報を取得
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

FONT = "'Zen Maru Gothic', 'Hiragino Maru Gothic ProN', 'Yu Gothic', sans-serif"
INK = "#4B3F5E"    # 本文（濃い梅色）
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

# CSSスタイル
st.markdown(f"""
<style>
.app-head {{ display: flex; align-items: center; gap: 14px; margin-bottom: 18px; }}
.app-emoji {{ width: 52px; height: 52px; border-radius: 18px; background: #F0E6FF;
    display: grid; place-items: center; font-size: 1.7rem; }}
.app-title {{ font-size: 1.5rem; font-weight: 700; color: {INK}; line-height: 1.2; }}
.app-sub {{ font-size: .85rem; color: {MUTED}; margin-top: 2px; }}

.stTabs [data-baseweb="tab-list"] {{ gap: 4px; background: #fff; padding: 5px; border-radius: 99px;
    border: 2px solid #FFE3EA; }}
.stTabs [data-baseweb="tab"] {{ flex: 1; height: 40px; border-radius: 99px; padding: 0 8px;
    color: {MUTED}; font-weight: 700; justify-content: center; }}
.stTabs [aria-selected="true"] {{ background: #F0E6FF; color: {INK}; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 1.2rem; }}

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

.memo {{ background: #fff; border: 2px dashed #E7D9F5; border-radius: 22px; padding: 16px 18px; margin-bottom: 14px; }}
.memo-label {{ font-size: .85rem; font-weight: 700; color: {MUTED}; margin-bottom: 6px; }}
.memo-text {{ font-size: 1rem; color: {INK}; line-height: 1.7; margin-bottom: 10px; }}
.chip {{ display: inline-block; padding: 4px 12px; border-radius: 99px; background: #F0E6FF;
    font-size: .82rem; font-weight: 700; color: {INK}; }}

.alert {{ border-radius: 18px; padding: 14px 16px; margin-bottom: 10px; font-size: .95rem;
    line-height: 1.6; color: {INK}; }}
.alert-warn {{ background: #FFE3EA; }}
.alert-ok {{ background: #E4F7EE; }}

.result {{ border-radius: 26px; padding: 20px; margin: 6px 0 14px; }}
.result-label {{ font-size: .85rem; font-weight: 700; color: {MUTED}; margin-bottom: 4px; }}
.result-value {{ font-size: 2.2rem; font-weight: 700; color: {INK}; line-height: 1.1; }}
.result-value small {{ font-size: .9rem; font-weight: 500; color: {MUTED}; }}
.result-sub {{ margin-top: 10px; }}

.legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 8px; }}
.legend span {{ padding: 3px 12px; border-radius: 99px; font-size: .78rem; font-weight: 700; color: {INK}; }}
.note {{ font-size: .78rem; color: {MUTED}; margin-top: 18px; text-align: center; }}

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
# 3. 認証状態の初期化
# ---------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = ""


# =========================================================
# 4. 未ログイン時の画面（Supabaseのusersテーブルで認証）
# =========================================================
if not st.session_state.logged_in:
    st.title("🔐 ログイン認証")
    st.write("ストレス可視化セルフケア支援システムをご利用の際は、IDとパスワードを入力してください。")
    
    with st.form("login_form"):
        input_user = st.text_input("ユーザーID")
        input_pass = st.text_input("パスワード", type="password")
        submit_btn = st.form_submit_button("ログイン")
        
        if submit_btn:
            # Supabaseの users テーブルから該当ユーザーを検索
            response = supabase.table("users").select("*").eq("username", input_user).execute()
            user_rows = response.data
            
            if user_rows and user_rows[0]["password"] == input_pass:
                st.session_state.logged_in = True
                st.session_state.current_user = input_user
                st.success("ログインに成功しました！まもなく画面が切り替わります。")
                st.rerun()
            else:
                st.error("⚠️ ユーザーIDまたはパスワードが間違っています。")

# =========================================================
# 5. ログイン成功後のメインアプリ画面
# =========================================================
else:
    user = st.session_state.current_user
    
    # サイドバーにログイン中ユーザーとログアウトボタンを表示
    st.sidebar.success(f"👤 ログイン中: **{user}** さん")
    if st.sidebar.button("ログアウト"):
        st.session_state.logged_in = False
        st.session_state.current_user = ""
        st.rerun()

    # --- Supabaseからこのユーザーのデータを取得 ---
    db_res = supabase.table("stress_records").select("*").eq("username", user).execute()
    
    if db_res.data:
        user_df = pd.DataFrame(db_res.data)
        # カラム名のマッピング・調整
        if "date" in user_df.columns:
            user_df["日付"] = pd.to_datetime(user_df["date"]).dt.date
        if "steps" in user_df.columns:
            user_df["歩数"] = user_df["steps"]
        if "sleep" in user_df.columns:
            user_df["睡眠時間"] = user_df["sleep"]
        if "stress_level" in user_df.columns:
            user_df["主観ストレス度"] = user_df["stress_level"]
        if "memo" in user_df.columns:
            user_df["メモ"] = user_df["memo"]
        if "stress_index" in user_df.columns:
            user_df["ストレス指標"] = user_df["stress_index"]
        if "risk_level" in user_df.columns:
            user_df["リスク判定"] = user_df["risk_level"]
        if "stress_factor" in user_df.columns:
            user_df["ストレス要因"] = user_df["stress_factor"]
    else:
        # まだ記録がなければ初期データを作成してSupabaseに保存
        today = datetime.now().date()
        initial_entry = {
            "username": user,
            "date": str(today),
            "steps": 0,
            "sleep": 0.0,
            "stress_level": 3,
            "memo": "まだ記録がありません。サイドバーから今日の記録を入力してみましょう！",
            "stress_index": 50.0,
            "risk_level": "良好",
            "stress_factor": "その他・特になし",
        }
        supabase.table("stress_records").insert(initial_entry).execute()
        user_df = pd.DataFrame([{
            "日付": today, "歩数": 0, "睡眠時間": 0.0, "主観ストレス度": 3,
            "メモ": "まだ記録がありません。サイドバーから今日の記録を入力してみましょう！",
            "ストレス指標": 50.0, "リスク判定": "良好", "ストレス要因": "その他・特になし"
        }])

    # 元のUIがそのまま動くように st.session_state.df に割り当て
    st.session_state.df = user_df.sort_values("日付").reset_index(drop=True)

    # ---------------------------------------------------------
    # 6. サイドバー：日次データ入力フォーム
    # ---------------------------------------------------------
    st.sidebar.header("📝 きょうの記録")
    input_date = st.sidebar.date_input("日付", datetime.now().date())
    input_steps = st.sidebar.number_input("歩数", min_value=0, max_value=50000, value=7000, step=500)
    input_sleep = st.sidebar.slider("睡眠時間 (時間)", min_value=0.0, max_value=12.0, value=7.0, step=0.5)
    input_stress = st.sidebar.select_slider("気分・ストレス感 (1:低 ～ 5:高)", options=[1, 2, 3, 4, 5], value=3)
    input_memo = st.sidebar.text_area("メモ / 日記", placeholder="例：面接が終わってホッとした。少し疲れた。")

    if st.sidebar.button("💾 保存する", type="primary", use_container_width=True):
        res = calculate_health_scores(input_steps, input_sleep, input_stress, input_memo)
        
        new_record = {
            "username": user,
            "date": str(input_date),
            "steps": int(input_steps),
            "sleep": float(input_sleep),
            "stress_level": int(input_stress),
            "memo": input_memo,
            "stress_index": float(res["stress_index"]),
            "risk_level": str(res["risk_level"]),
            "stress_factor": str(res["factor"]),
        }
        
        # すでに同じ日付のデータがSupabaseにあるか確認（UpsertまたはUpdate/Insert）
        existing = supabase.table("stress_records").select("id").eq("username", user).eq("date", str(input_date)).execute()
        if existing.data:
            rec_id = existing.data[0]["id"]
            supabase.table("stress_records").update(new_record).eq("id", rec_id).execute()
        else:
            supabase.table("stress_records").insert(new_record).execute()
            
        st.sidebar.success("クラウドに保存しました！画面を更新します。")
        st.rerun()

    # ---------------------------------------------------------
    # 7. メイン画面
    # ---------------------------------------------------------
    latest_row = st.session_state.df.iloc[-1]
    latest_calc = calculate_health_scores(
        latest_row["歩数"], latest_row["睡眠時間"], latest_row["主観ストレス度"], latest_row["メモ"]
    )

    render(f"""
    <div class="app-head">
    <div class="app-emoji">🧘</div>
    <div>
    <div class="app-title">ヘルスケア分析</div>
    <div class="app-sub">最終記録：{fmt_date(latest_row['日付'])}</div>
    </div>
    </div>
    """)

    tab1, tab2, tab3, tab4 = st.tabs(["🌷 TOP", "🔮 予測", "🍰 原因", "📒 履歴"])

    # ---------------------------------------------------------
    # Tab 1: きょうの要約
    # ---------------------------------------------------------
    with tab1:
        sc = STATUS[latest_calc["status_color"]]
        idx = latest_calc["stress_index"]

        render(f"""
        <div class="hero" style="background:{sc['soft']};">
        <div class="ring" style="background:conic-gradient({sc['main']} {idx}%, rgba(255,255,255,.75) 0);">
        <div class="ring-inner"><div>
        <div class="ring-num">{idx:.0f}</div>
        <div class="ring-sub">ストレス指標</div>
        </div></div>
        </div>
        <div class="hero-text">
        <div class="face">{sc['face']}</div>
        <div class="hero-title">{sc['title']}</div>
        <div class="hero-msg">{sc['msg']}</div>
        <span class="pill">状態：{latest_calc['risk_level']}</span>
        </div>
        </div>
        """)

        steps_pct = min(100.0, latest_calc["steps_score"])
        sleep_pct = min(100.0, latest_calc["sleep_score"])
        render(f"""
        <div class="grid2">
        <div class="stat">
        <div class="stat-head"><span class="bubble" style="background:#FFE9D6;">👟</span><span class="stat-label">歩数</span></div>
        <div class="stat-value">{latest_row['歩数']:,}<small>歩</small></div>
        <div class="bar"><i style="width:{steps_pct}%; background:#FFB48A;"></i></div>
        <div class="stat-sub">目標8,000歩の {latest_calc['steps_score']:.0f}%</div>
        </div>
        <div class="stat">
        <div class="stat-head"><span class="bubble" style="background:#E3EEFF;">🌙</span><span class="stat-label">睡眠時間</span></div>
        <div class="stat-value">{latest_row['睡眠時間']}<small>時間</small></div>
        <div class="bar"><i style="width:{sleep_pct}%; background:#9DB8FF;"></i></div>
        <div class="stat-sub">充足度 {latest_calc['sleep_score']:.0f}%</div>
        </div>
        </div>
        """)

        memo_text = html.escape(str(latest_row["メモ"])) if latest_row["メモ"] else "メモはまだありません"
        factor = latest_calc["factor"]
        render(f"""
        <div class="memo">
        <div class="memo-label">💭 きょうのメモ</div>
        <div class="memo-text">{memo_text}</div>
        <span class="chip">{FACTOR_EMOJI.get(factor, '☁️')} {factor}</span>
        </div>
        """)

        st.subheader("🔔 お知らせ・今日のアドバイス")

        df_today = st.session_state.df.sort_values("日付")
        latest_row = df_today.iloc[-1]
        warnings = detect_early_warnings(df_today)

        if warnings:
            for w in warnings:
                render(
                    f'<div class="alert alert-warn">'
                    f'{html.escape(w)}</div>'
                )
        else:
            render(
                '<div class="alert alert-ok">'
                '✅ 大きな注意サインは検出されていません。'
                '</div>'
            )

        advice = []
        if latest_row["ストレス指標"] >= 70:
            advice.append(
                "🌿 ストレス指標が高めです。"
                "予定を詰め込みすぎず、ゆっくり休む時間を作りましょう。"
            )
        elif latest_row["ストレス指標"] >= 45:
            advice.append(
                "☕ 少し疲れがたまっているかもしれません。"
                "短い休憩や深呼吸で気分を切り替えてみましょう。"
            )
        else:
            advice.append(
                "🌷 今の状態を保てるように、"
                "無理のない生活リズムを続けてみましょう。"
            )

        if latest_row["睡眠時間"] < 6 and latest_row["睡眠時間"] > 0:
            advice.append(
                "🌙 睡眠時間が短めです。"
                "今夜は早めに休めるようにしてみましょう。"
            )

        if latest_row["歩数"] < 4000 and latest_row["歩数"] > 0:
            advice.append(
                "🚶 歩数が少なめです。体調に合わせて、"
                "軽いストレッチや短い散歩を取り入れてみましょう。"
            )

        render(
            '<div class="alert alert-ok">'
            '<strong>💡 今日できるセルフケア</strong><br>'
            + "<br>".join(html.escape(a) for a in advice)
            + "</div>"
        )

        render('<div class="note">※ 表示は記録に基づく一般的なセルフケアの目安です。医療的な診断ではありません。</div>')


    # ---------------------------------------------------------
    # Tab 2: ストレス予測 & シミュレーター
    # ---------------------------------------------------------
    with tab2:
        st.subheader("🔮 明日のストレス予測")
        pred = predict_tomorrow_stress(st.session_state.df)
        pc = STATUS[status_of(pred["predicted_score"])]

        render(f"""
        <div class="result" style="background:{pc['soft']};">
        <div class="result-label">明日の予想スコア</div>
        <div class="result-value">{pred['predicted_score']}<small> / 100</small></div>
        <div class="result-sub"><span class="pill">傾向：{pred['trend']}</span></div>
        </div>
        """)

        st.subheader("🧪 明日のおためしシミュレーション")
        st.caption("歩数・睡眠・負荷を動かすと、スコアがどう変わるか見られます。")

        sim_steps = st.number_input("予定歩数", min_value=0, max_value=30000, value=8000, step=1000)
        sim_sleep = st.slider("予定睡眠時間", min_value=0.0, max_value=12.0, value=7.5, step=0.5)
        sim_stress = st.select_slider("予想される負荷 (1:低 ～ 5:高)", options=[1, 2, 3, 4, 5], value=2)

        sim_res = calculate_health_scores(sim_steps, sim_sleep, sim_stress, "シミュレーション")
        diff = sim_res["stress_index"] - latest_calc["stress_index"]
        diff_text = f"今日より {abs(diff):.1f}pt {'改善' if diff < 0 else '悪化'}"
        simc = STATUS[status_of(sim_res["stress_index"])]

        render(f"""
        <div class="result" style="background:{simc['soft']};">
        <div class="result-label">シミュレーション結果 {simc['face']}</div>
        <div class="result-value">{sim_res['stress_index']}<small> / 100</small></div>
        <div class="result-sub"><span class="pill">{diff_text}</span></div>
        </div>
        """)


    # ---------------------------------------------------------
    # Tab 3: 原因の内訳 & 推移
    # ---------------------------------------------------------
    PLOT_CONFIG = {"displayModeBar": False}

    def base_layout(fig, height):
        fig.update_layout(
            font=dict(family=FONT, color=INK, size=13),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=10, r=10),
            height=height,
        )

    with tab3:
        df_chart = st.session_state.df.copy()

        st.subheader("🍰 ストレスの原因")
        factor_counts = df_chart["ストレス要因"].value_counts().reset_index()
        factor_counts.columns = ["ストレス要因", "件数"]
        labels = [f"{FACTOR_EMOJI.get(f, '☁️')} {f}" for f in factor_counts["ストレス要因"]]

        fig_pie = go.Figure(go.Pie(
            labels=labels,
            values=factor_counts["件数"],
            hole=0.6,
            sort=False,
            marker=dict(colors=PASTELS[: len(labels)], line=dict(color=MILK, width=4)),
            textinfo="percent",
            textfont=dict(size=14, color=INK),
            hovertemplate="%{label}<br>%{value}日<extra></extra>",
        ))
        base_layout(fig_pie, 380)
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.05, x=0.5, xanchor="center"),
            annotations=[dict(text=f"{len(df_chart)}日分", x=0.5, y=0.5, showarrow=False,
                              font=dict(size=18, color=INK))],
        )
        st.plotly_chart(fig_pie, use_container_width=True, config=PLOT_CONFIG)

        st.subheader("📈 ストレス指標の推移")
        fig_line = go.Figure()
        for y0, y1, col in [(0, 45, "rgba(92,201,160,.18)"), (45, 70, "rgba(255,169,77,.18)"), (70, 100, "rgba(255,122,154,.18)")]:
            fig_line.add_hrect(y0=y0, y1=y1, fillcolor=col, line_width=0, layer="below")
        fig_line.add_trace(go.Scatter(
            x=df_chart["日付"], y=df_chart["ストレス指標"],
            mode="lines+markers",
            line=dict(color=PLUM, width=4, shape="spline"),
            marker=dict(size=11, color="#fff", line=dict(color=PLUM, width=3)),
            hovertemplate="%{x|%m/%d}<br>ストレス指標 %{y}<extra></extra>",
        ))
        base_layout(fig_line, 320)
        fig_line.update_yaxes(range=[0, 100], tickvals=[0, 45, 70, 100], gridcolor="rgba(75,63,94,.08)",
                              zeroline=False, fixedrange=True)
        fig_line.update_xaxes(tickformat="%m/%d", showgrid=False, fixedrange=True)
        st.plotly_chart(fig_line, use_container_width=True, config=PLOT_CONFIG)

        render("""
        <div class="legend">
        <span style="background:#E4F7EE;">🟢 〜44 良好</span>
        <span style="background:#FFF0DB;">🟡 45〜69 中リスク</span>
        <span style="background:#FFE3EA;">🔴 70〜 高リスク</span>
        </div>
        """)

        st.subheader("📊 主観ストレスとアプリ評価の比較")

        df_compare = df_chart.sort_values("日付").copy()
        df_compare["主観評価換算"] = (
            (df_compare["主観ストレス度"] - 1) / 4 * 100
        )

        fig_compare = go.Figure()

        fig_compare.add_trace(go.Scatter(
            x=df_compare["日付"],
            y=df_compare["主観評価換算"],
            mode="lines+markers",
            name="主観ストレス（換算）",
            line=dict(color="#2563EB", width=3),
            marker=dict(size=8),
            customdata=df_compare["主観ストレス度"],
            hovertemplate=(
                "%{x|%m/%d}<br>"
                "主観評価：%{customdata} / 5<br>"
                "換算値：%{y:.1f} / 100"
                "<extra></extra>"
            ),
        ))

        fig_compare.add_trace(go.Scatter(
            x=df_compare["日付"],
            y=df_compare["ストレス指標"],
            mode="lines+markers",
            name="アプリ評価",
            line=dict(color="#EA580C", width=3),
            marker=dict(size=8),
            hovertemplate=(
                "%{x|%m/%d}<br>"
                "アプリ評価：%{y:.1f} / 100"
                "<extra></extra>"
            ),
        ))

        base_layout(fig_compare, 380)
        fig_compare.update_layout(
            title=dict(
                text="日ごとのストレス評価の比較",
                x=0,
                xanchor="left",
                y=0.98,
                yanchor="top",
            ),
            margin=dict(t=100, b=80),
            xaxis_title="日付",
            yaxis_title="ストレス評価",
            legend=dict(
                orientation="h",
                y=-0.2,
                x=0.5,
                xanchor="center",
            ),
            hovermode="x unified",
        )

        fig_compare.update_yaxes(
            range=[0, 100],
            tickvals=[0, 25, 50, 75, 100],
            gridcolor="rgba(75,63,94,.08)",
            zeroline=False,
        )
        fig_compare.update_xaxes(
            tickformat="%m/%d",
            showgrid=False,
        )

        st.plotly_chart(
            fig_compare,
            use_container_width=True,
            config=PLOT_CONFIG,
        )

        st.caption(
            "主観評価は1～5の値を0～100に換算しています。"
            "2本の線の推移を比較し、評価の違いを確認できます。"
        )


    # ---------------------------------------------------------
    # Tab 4: 履歴データ
    # ---------------------------------------------------------
    with tab4:
        st.subheader("📒 これまでの記録")
        df_view = st.session_state.df.sort_values("日付", ascending=False).copy()
        risk_icon = {"良好": "🟢 良好", "中リスク": "🟡 中リスク", "高リスク": "🔴 高リスク"}
        df_view["リスク判定"] = df_view["リスク判定"].map(risk_icon)
        df_view["ストレス要因"] = [f"{FACTOR_EMOJI.get(f, '☁️')} {f}" for f in df_view["ストレス要因"]]
        st.dataframe(
            df_view,
            column_config={
                "日付": st.column_config.DateColumn("日付", format="MM/DD"),
                "歩数": st.column_config.NumberColumn("歩数", format="%d 歩"),
                "睡眠時間": st.column_config.NumberColumn("睡眠", format="%.1f h"),
                "主観ストレス度": st.column_config.NumberColumn("気分(1-5)"),
                "ストレス指標": st.column_config.ProgressColumn("ストレス指標", min_value=0, max_value=100, format="%.1f"),
            },
            use_container_width=True,
            hide_index=True,
        )
