import streamlit as st
from common.hello import say_hello
from common.snowflake_client import snowflake_connection, fetch_single_value
import pandas as pd

st.title(f"Snowflake Insights — {say_hello()}")

# # Snowflake のシークレットは .streamlit/secrets.toml に置く
# sf = st.secrets.get("snowflake", None)
# if sf:
#     try:
#         # 簡単なクエリ実行例
#         version = fetch_single_value(sf, "SELECT CURRENT_VERSION()")
#         if version:
#             st.write("Connected to Snowflake, version:", version)
#         else:
#             st.warning("Snowflake に接続したがバージョン情報が取得できませんでした。")
#     except Exception as e:
#         st.error(f"Snowflake 接続エラー: {e}")
# else:
#     st.info("Snowflake の資格情報が設定されていません（.streamlit/secrets.toml を確認してください）。")

# streamlit_app.py
# streamlit_app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="チェック付きデータフレームのサンプル", layout="centered")
st.title("チェック付きデータフレーム + ダイアログ表示")

# --- サンプルデータ ---
data = [
    {"id": 1, "名前": "田中", "年齢": 28, "所属": "営業"},
    {"id": 2, "名前": "鈴木", "年齢": 34, "所属": "開発"},
    {"id": 3, "名前": "佐藤", "年齢": 41, "所属": "人事"},
    {"id": 4, "名前": "高橋", "年齢": 25, "所属": "総務"},
]
df = pd.DataFrame(data)

# 選択列を追加（なければ）
if "選択" not in df.columns:
    df["選択"] = False

st.caption("行をチェックしてから下のボタンを押してください。")

# --- チェックボックスを一番左に配置して表示 ---
edited_df = st.data_editor(
    df,
    key="table",
    use_container_width=True,
    hide_index=True,
    column_order=["選択", "id", "名前", "年齢", "所属"],  # 先頭に「選択」
    column_config={
        "選択": st.column_config.CheckboxColumn("選択", help="この行を選択"),
    },
    disabled=["id", "名前", "年齢", "所属"],  # チェック以外は編集不可
    num_rows="fixed",
)

# --- 選択行の抽出 ---
selected_rows = edited_df[edited_df["選択"]]
selected_count = len(selected_rows)

# --- ダイアログ表示の互換関数（st.dialog / experimental_dialog / 代替） ---
def show_selected_dialog(sel_df: pd.DataFrame) -> None:
    disp_df = sel_df.drop(columns=["選択"]).reset_index(drop=True)
    title = "選択した行の情報"

    if hasattr(st, "dialog"):  # 新API
        @st.dialog(title, width="large")
        def _dlg():
            st.write(f"選択行数: {len(disp_df)} 行")
            st.dataframe(disp_df, use_container_width=True)
        _dlg()

    elif hasattr(st, "experimental_dialog"):  # 旧API
        @st.experimental_dialog(title)
        def _dlg():
            st.write(f"選択行数: {len(disp_df)} 行")
            st.dataframe(disp_df, use_container_width=True)
        _dlg()

    else:
        # ダイアログAPIが無い場合の簡易フォールバック
        st.warning("このStreamlitバージョンではダイアログAPIが見つかりません。ページ内に展開して表示します。")
        with st.expander(title, expanded=True):
            st.write(f"選択行数: {len(disp_df)} 行")
            st.dataframe(disp_df, use_container_width=True)

# --- ボタン（未選択なら無効） ---
btn = st.button(
    "選択した行を確認",
    type="primary",
    disabled=(selected_count == 0),
    help="1行以上チェックすると押せます",
)

# --- ボタン押下時にダイアログを開く ---
if btn:
    show_selected_dialog(selected_rows)
