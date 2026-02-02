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

```mysql
CREATE DATABASE competition_db;
CREATE USER 'GitHubCodeSpaces'@'localhost' IDENTIFIED BY 'CodeSpaces';
GRANT ALL PRIVILEGES ON competition_db.* TO 'GitHubCodeSpaces'@'localhost';
FLUSH PRIVILEGES;
```
