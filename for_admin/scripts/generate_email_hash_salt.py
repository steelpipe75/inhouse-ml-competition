# /// script
# dependencies = ["toml"]
# ///
import os
import base64
import toml


def generate_salt():
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


if __name__ == "__main__":
    salt = generate_salt()
    print(salt)

    streamlit_secrets_path = ".streamlit/secrets.toml"

    # secrets.tomlを読み込む、存在しない場合は空のdictを生成
    if os.path.exists(streamlit_secrets_path):
        with open(streamlit_secrets_path, "r", encoding="utf-8") as f:
            secrets = toml.load(f)
    else:
        secrets = {}

    # EMAIL_HASH_SALTを更新または追加
    secrets["EMAIL_HASH_SALT"] = salt

    # secrets.tomlに書き込む
    with open(streamlit_secrets_path, "w", encoding="utf-8") as f:
        toml.dump(secrets, f)

    print(f"Generated EMAIL_HASH_SALT and wrote it to {streamlit_secrets_path}")
