# /// script
# dependencies = ["toml"]
# ///
import hashlib
import getpass
import os
import toml


def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()


if __name__ == "__main__":
    # ユーザーにパスワードの入力を促す
    password = getpass.getpass("設定したい合言葉を入力してください: ")

    # パスワードをSHA256でハッシュ化
    hashed_password = generate_password_hash(password)

    # 結果を表示
    print("\n---")
    print("生成されたSHA256ハッシュ値:")
    print(hashed_password)

    streamlit_secrets_path = ".streamlit/secrets.toml"

    # secrets.tomlを読み込む、存在しない場合は空のdictを生成
    if os.path.exists(streamlit_secrets_path):
        with open(streamlit_secrets_path, "r", encoding="utf-8") as f:
            secrets = toml.load(f)
    else:
        secrets = {}

    # APP_PASSWORD_HASHを更新または追加
    secrets["APP_PASSWORD_HASH"] = hashed_password

    # secrets.tomlに書き込む
    with open(streamlit_secrets_path, "w", encoding="utf-8") as f:
        toml.dump(secrets, f)

    print(
        f"\n生成されたパスワードハッシュを {streamlit_secrets_path} に書き込みました。"
    )
