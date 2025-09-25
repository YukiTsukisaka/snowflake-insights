import streamlit as st
import pandas as pd
from common.hello import say_hello
from common.snowflake_client import snowflake_connection, fetch_single_value


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


# PEP8命名・構造改善: データ準備を関数化

def create_sample_dataframe() -> pd.DataFrame:
    """サンプル従業員データのDataFrameを返す。

    Returns:
        pd.DataFrame: id, 名前, 年齢, 所属, 選択 を列に持つデータ。
    """
    records = [
        {"id": 1, "名前": "田中", "年齢": 28, "所属": "営業"},
        {"id": 2, "名前": "鈴木", "年齢": 34, "所属": "開発"},
        {"id": 3, "名前": "佐藤", "年齢": 41, "所属": "人事"},
        {"id": 4, "名前": "高橋", "年齢": 25, "所属": "総務"},
    ]
    frame = pd.DataFrame(records)
    if "選択" not in frame.columns:
        frame["選択"] = False
    return frame


def render_selection_table(source_df: pd.DataFrame) -> pd.DataFrame:
    """選択用チェックボックス付きテーブルを表示し、編集後のDataFrameを返す。

    Args:
        source_df (pd.DataFrame): 元データ

    Returns:
        pd.DataFrame: data_editor後（選択列がユーザ操作で更新された）DataFrame
    """
    return st.data_editor(
        source_df,
        key="employee_table",
        use_container_width=True,
        hide_index=True,
        column_order=["選択", "id", "名前", "年齢", "所属"],
        column_config={
            "選択": st.column_config.CheckboxColumn(
                "選択", help="この行を選択"
            ),
        },
        disabled=["id", "名前", "年齢", "所属"],
        num_rows="fixed",
    )


def open_selection_dialog(selected_df: pd.DataFrame) -> None:
    """選択された行をフォーム付きダイアログで表示する。未選択なら警告。

    Args:
        selected_df (pd.DataFrame): 選択行のみを含むDataFrame（選択列=True）
    """
    display_df = selected_df.drop(columns=["選択"]).reset_index(drop=True)
    dialog_title = "選択した行の送信フォーム"

    if display_df.empty:
        st.warning("行が選択されていません。")
        return

    def render_form_contents() -> None:
        """ダイアログ内部のフォームUIを描画し、送信時は結果を表示。"""
        st.write(f"選択行数: {len(display_df)} 行")
        st.dataframe(display_df, use_container_width=True)
        st.divider()
        with st.form("submit_selected_rows"):
            st.text_area(
                "メモ (任意)",
                key="memo",
                placeholder="この送信に関するコメントを入力できます",
            )
            submitted = st.form_submit_button("送信", type="primary")
            if submitted:
                result_payload = {
                    "rows": display_df.to_dict(orient="records"),
                    "memo": st.session_state.get("memo", ""),
                    "count": len(display_df),
                }
                # セッションに保存して再実行（ダイアログを閉じる）
                st.session_state["last_submission"] = result_payload
                st.success("送信しました (ダミー処理)")
                # rerun により dialog が閉じる想定
                st.rerun()

    if hasattr(st, "dialog"):
        @st.dialog(dialog_title, width="large")
        def _dialog_wrapper():
            render_form_contents()
        _dialog_wrapper()
    else:
        st.info(
            "ダイアログ非対応バージョンのためページ内でフォーム表示しています。"
        )
        with st.expander(dialog_title, expanded=True):
            render_form_contents()


# ===== メイン処理部 =====

# ページ設定とタイトル
st.set_page_config(page_title="チェック付きデータフレームのサンプル", layout="centered")
st.title("チェック付きデータフレーム + ダイアログ表示")

# データ作成と表示
employee_df = create_sample_dataframe()
st.caption("行をチェックしてから下のボタンを押してください。")
updated_df = render_selection_table(employee_df)

# 選択行抽出
selected_rows_df = updated_df[updated_df["選択"]]

# ボタン & ダイアログ
open_button_clicked = st.button(
    "選択した行を確認",
    type="primary",
    disabled=selected_rows_df.empty,
    help="1行以上チェックすると押せます",
)
if open_button_clicked:
    open_selection_dialog(selected_rows_df)

# 送信結果があればトップに表示
if "last_submission" in st.session_state:
    st.success("前回の送信が完了しました")
    # st.json(st.session_state["last_submission"])  # デバッグ/確認用表示
