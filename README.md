# README

---

### python依赖
```shell
    flask
    pymysql
    faker
```
### vscode插件
>[[REST Client]](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)网络请求发送
>[[Python]](https://marketplace.visualstudio.com/items?itemName=ms-python.python)python运行插件
>[[CSV]](https://marketplace.visualstudio.com/items?itemName=ReprEng.csv)csv查看器

---

### 开发守则
1.严禁在/tests内添加非测试用途的代码,是模块就丢对应文件里。

---

#### 1. 进入虚拟环境
```shell
    .venv\Scripts\activate
```
#### 2. 退出虚拟环境
```shell
    deactivate.bat
```

#### 提交main分支
```shell
    git remote add origin git@github.com:Kartery0804/test_DB_1.0.0.git
    git branch -M main
    git push -u origin main
```

#### 创建虚拟环境
```shell
    python -m venv .venv
    python -m pip install --upgrade pip
```
---
