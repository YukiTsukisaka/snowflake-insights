import streamlit as st
from common.hello import say_hello
from common.snowflake_client import snowflake_connection, fetch_single_value

st.title(f"Snowflake Insights — {say_hello()}")

# Snowflake のシークレットは .streamlit/secrets.toml に置く
sf = st.secrets.get("snowflake", None)
if sf:
    try:
        # 簡単なクエリ実行例
        version = fetch_single_value(sf, "SELECT CURRENT_VERSION()")
        if version:
            st.write("Connected to Snowflake, version:", version)
        else:
            st.warning("Snowflake に接続したがバージョン情報が取得できませんでした。")
    except Exception as e:
        st.error(f"Snowflake 接続エラー: {e}")
else:
    st.info("Snowflake の資格情報が設定されていません（.streamlit/secrets.toml を確認してください）。")
