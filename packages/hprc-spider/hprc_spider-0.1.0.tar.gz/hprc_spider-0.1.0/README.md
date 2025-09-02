
# hprc_spider

一个用于hprc_spider的工具，可以读取hprc_spider的日志文件，并按照时间顺序执行hprc_spider请求。

## Features


## 安装

```bash
# 本地
pip install hprc_spider -i https://pypi.org/simple/
# 阿里云
pip install hprc_spider -i https://pypi.org/simple/
```

## 用法

```bash
python -m hprc_spider <log_file>
```


### 开发配置

```bash
# 克隆仓库
git clone git@github.com:atanx/hprc_spider.git
cd hprc_spider

# 安装开发依赖
pip install -e ".[dev]"

# 手动修改修改__init__.py中的__version__， 然后打包
make build

# 上传到xmov-pypi, 需要安装twine， 配置~/.pypirc
make upload
```

    