import requests
import streamlit as st

st.set_page_config(
    page_title="RiceOS Remote Keyboard",
    page_icon="⌨️",
    layout="centered",
)

st.title("RiceOS Remote Keyboard")
st.caption("透過 Wi-Fi 取代 CH9350 鍵盤輸入")

default_host = "http://192.168.0.108:8080"

esp_address = st.text_input(
    "ESP8266 位址",
    value=st.session_state.get("esp_address", default_host),
    placeholder="http://192.168.0.108:8080",
)

st.session_state["esp_address"] = esp_address.rstrip("/")

col1, col2 = st.columns(2)

with col1:
    if st.button("測試連線", use_container_width=True):
        try:
            response = requests.get(
                f"{st.session_state['esp_address']}/ping",
                timeout=5,
            )

            response.raise_for_status()

            st.success("ESP8266 Remote Server 已連線")
            st.code(response.text)

        except requests.RequestException as error:
            st.error(f"連線失敗：{error}")

with col2:
    if st.button("查看狀態", use_container_width=True):
        try:
            response = requests.get(
                f"{st.session_state['esp_address']}/status",
                timeout=5,
            )

            response.raise_for_status()

            st.json(response.json())

        except requests.RequestException as error:
            st.error(f"狀態讀取失敗：{error}")
        except ValueError:
            st.error("ESP8266 回傳的不是有效 JSON")

st.divider()

command = st.text_input(
    "輸入指令",
    placeholder="例如：help",
    key="command_input",
)

auto_enter = st.checkbox(
    "送出後自動按 Enter",
    value=True,
)

if st.button(
    "送出到 RiceOS",
    type="primary",
    use_container_width=True,
):
    if not command:
        st.warning("請先輸入內容")
    else:
        text_to_send = command

        if auto_enter and not text_to_send.endswith(("\n", "\r")):
            text_to_send += "\n"

        try:
            response = requests.post(
                f"{st.session_state['esp_address']}/keyboard",
                data={"text": text_to_send},
                timeout=5,
            )

            response.raise_for_status()

            result = response.json()

            if result.get("ok"):
                st.success(
                    f"已送出 {result.get('accepted', len(text_to_send))} 個字元"
                )
            else:
                st.error(result.get("error", "ESP8266 拒絕輸入"))

        except requests.RequestException as error:
            st.error(f"送出失敗：{error}")
        except ValueError:
            st.error("ESP8266 回傳格式錯誤")

st.divider()

st.subheader("特殊按鍵")

key_columns = st.columns(4)

special_keys = [
    ("Enter", "ENTER"),
    ("Backspace", "BACKSPACE"),
    ("Esc", "ESC"),
    ("Tab", "TAB"),
]

for column, (label, key_name) in zip(key_columns, special_keys):
    with column:
        if st.button(label, use_container_width=True):
            try:
                response = requests.post(
                    f"{st.session_state['esp_address']}/key",
                    data={"key": key_name},
                    timeout=5,
                )

                response.raise_for_status()

                result = response.json()

                if result.get("ok"):
                    st.success(f"{label} 已送出")
                else:
                    st.error(result.get("error", "按鍵送出失敗"))

            except requests.RequestException as error:
                st.error(f"送出失敗：{error}")
            except ValueError:
                st.error("ESP8266 回傳格式錯誤")

st.info(
    "目前版本是整行送出模式。輸入 help 並勾選自動 Enter，OLED 應立即顯示並執行 help。"
)
