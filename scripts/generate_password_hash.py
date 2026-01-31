import hashlib
import getpass

# ユーザーにパスワードの入力を促す
password = getpass.getpass("設定したい合言葉を入力してください: ")

# パスワードをSHA256でハッシュ化
hashed_password = hashlib.sha256(password.encode()).hexdigest()

# 結果を表示
print("\n---")
print("生成されたSHA256ハッシュ値:")
print(hashed_password)
print(
    "\n上記のハッシュ値をコピーして、.streamlit/secrets.toml ファイルの 'APP_PASSWORD_HASH' に設定してください。"
)
