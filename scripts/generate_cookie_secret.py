# /// script
# dependencies = ["toml"]
# ///
import os
import base64
import toml

def generate_cookie_secret():
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

if __name__ == "__main__":
    secret = generate_cookie_secret()
    print(secret)

    streamlit_secrets_path = ".streamlit/secrets.toml"

    # secrets.tomlを読み込む、存在しない場合は空のdictを生成
    if os.path.exists(streamlit_secrets_path):
        with open(streamlit_secrets_path, "r", encoding="utf-8") as f:
            secrets = toml.load(f)
    else:
        secrets = {}

    # [streamlit]セクションが存在しない場合は作成
    if "auth" not in secrets:
        secrets["auth"] = {}

    # cookie_secretを更新または追加
    secrets["auth"]["cookie_secret"] = secret

    # secrets.tomlに書き込む
    with open(streamlit_secrets_path, "w", encoding="utf-8") as f:
        toml.dump(secrets, f)

    print(f"Generated cookie secret and wrote it to {streamlit_secrets_path}")
