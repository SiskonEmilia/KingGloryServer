# KingGloryServer

KingGloryServer 是一个王者荣耀数据服务器端程序。它会定期的从王者荣耀官网拉取英雄数据，并且存入 static 文件夹中的 Heroes.xml 中，您可以在客户端通过网址直接访问。

## 使用方法

```bash
go get github.com/siskonemilia/KingGloryServer
cd $GOPATH/src/github.com/siskonemilia/KingGloryServer
# On CentOS7 with Python 3.6
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
chmod +x static/crawler.py
nohup static/crawler.py > /dev/null 2>&1 &
go run main.go
```