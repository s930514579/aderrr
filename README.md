# aderrr

基础 Python 项目，使用 Python 3.12 或更新版本。

## 安装

在仓库根目录运行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install setuptools==80.9.0
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

## 运行与测试

```bash
.venv/bin/aderrr
.venv/bin/python -m aderrr --version
.venv/bin/python -m unittest discover -s tests -v
```

应用代码位于 `src/aderrr/`，测试位于 `tests/`。当前命令行程序是可扩展的初始入口，尚未实现业务功能。

## 可视化编辑环境

运行 `./.venv/bin/python tools/editor_server.py`，然后打开 `http://127.0.0.1:8765`。页面左侧显示项目文件，右侧可以查看和保存文本文件。部署时设置 `ADERRR_EDITOR_HOST=0.0.0.0` 和平台提供的 `PORT`。也可以使用仓库中的 Dockerfile。

Render 免费部署配置见 `render.yaml`。将仓库连接到 Render 后选择该配置即可创建公网服务；免费实例空闲后会休眠。
