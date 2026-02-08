# GitHub Codespaces でテスト

## MySQL

### インストール

```bash
sudo apt update
```

```bash
sudo apt install mysql-server
```

### 起動

```bash
sudo service mysql start
```

### 起動確認

```bash
sudo service mysql status
```

### 初期設定

```bash
sudo mysql
```

```sql
CREATE DATABASE app_db;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'app_pass';
GRANT ALL PRIVILEGES ON app_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

## PostgreSQL

### インストール

```bash
sudo apt update
```

```bash
sudo apt install -y postgresql postgresql-contrib
```

### バージョン確認

```bash
psql --version
```

### 起動

```bash
sudo service postgresql start
```

### 起動確認

```bash
sudo service postgresql status
```

### 初期設定

```bash
sudo -u postgres psql
```

パスワード聞かれる

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

認証方式を trust に変更

```diff
-local all postgres peer
+local all postgres trust
```

保存して閉じる `Ctrl + O` → `Enter`（保存）、`Ctrl + X`（閉じる）

```bash
sudo service postgresql restart
```

```bash
psql -U postgres
```

```sql
ALTER USER postgres
WITH PASSWORD 'postgrespass';
```

```sql
CREATE DATABASE app_db;
CREATE USER app_user WITH PASSWORD 'app_pass';
GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;
```

```sql
\c app_db
GRANT ALL ON SCHEMA public TO app_user;
```
