# Fr1997 Python包

## 简介

Fr1997是一个功能丰富的Python私有包，集成了多种常用功能模块，包括网络爬虫、数据处理、文本分析、数据库操作等。本包需要正确配置参数才能使用，未配置参数的功能将无法正常运行。

## 主要功能

- 网络爬虫（小红书、抖音、知乎等平台）
- 数据库操作（MySQL、Redis、ElasticSearch）
- 文本处理（分词、拼音转换）
- 时间处理工具
- HTTP请求封装
- 云存储接口
- 微信自动化
- 飞书API集成
- Django集成工具

## 包结构说明

```
fr1997_pkg/
├── fr1997_mode/               # 核心模块目录
│   ├── __init__.py            # 导入入口
│   ├── mode_func/             # 功能类模块目录
│   │   ├── __init__.py        # 包初始化
│   │   ├── all_func.py        # 导入所有功能类并实例化
│   │   ├── base_mode_class.py # 基础模式类
│   │   ├── base_class.py      # 基础类
│   │   ├── gy_class.py        # 个人工具类
│   │   ├── mysql_class.py     # MySQL数据库操作类
│   │   ├── redis_class.py     # Redis数据库操作类
│   │   ├── es_class.py        # ElasticSearch操作类
│   │   ├── text_class.py      # 文本处理类
│   │   ├── time_class.py      # 时间处理类
│   │   ├── data_class.py      # 数据处理类
│   │   ├── http_class.py      # HTTP请求类
│   │   ├── spider_class.py    # 爬虫基础类
│   │   ├── xhs_class.py       # 小红书平台类
│   │   ├── douyin_class.py    # 抖音平台类
│   │   ├── zhihu_class.py     # 知乎平台类
│   │   ├── weixin_class.py    # 微信平台类
│   │   ├── feishu_class.py    # 飞书平台类
│   │   ├── django_class.py    # Django框架类
│   │   ├── cos_class.py       # 云存储类
│   │   ├── cache_class.py     # 缓存操作类
│   │   └── func_class.py      # 功能函数类
│   └── mode_static/           # 静态资源目录
├── setup.py                   # 打包配置文件
├── LICENSE                    # 许可证文件
└── README.md                  # 说明文档
```

### 使用方式

导入所有功能:

```python
from fr1997_mode import *

# 直接使用实例化好的功能对象
mode_text.some_function()  # 使用文本处理功能
mode_time.some_function()  # 使用时间处理功能
mode_xhs.some_function()  # 使用小红书相关功能
mode_mysql.some_function()  # 使用MySQL数据库功能
```

所有功能对象在`fr1997_mode/mode_func/all_func.py`中实例化，包括:

- `mode_text` - 文本处理
- `mode_time` - 时间处理
- `mode_myself` - 个人工具
- `mode_xhs` - 小红书平台
- `mode_data` - 数据分析
- `mode_pros` - 静态函数
- `mode_douyin` - 抖音平台
- `mode_spider` - 数据请求
- `mode_pro` - 模式功能
- `JFD` - 字段约束
- `mode_feishu` - 飞书API
- `mode_django` - Django配置
- `mode_mysql` - MySQL数据库
- `mode_cos` - 云存储
- `mode_fr_cos` - 个人云存储
- `mode_wx` - 微信自动化
- `http_class` - HTTP请求

## 安装指南

### 安装指定版本

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Fr1997v011==25.8.5.1
```

### 安装最新版本

```bash
pip install --upgrade Fr1997v011==25.8.5.1
```

### 清除pip缓存

```bash
pip cache purge
```

### 卸载

```bash
pip uninstall Fr1997v011
```

### 打包1.构建可执行文件

```bash
python setup.py build
```

### 打包2.源代码打包

```bash
python setup.py sdist
```

### 打包3.本地安装

```bash
pip install dist/Fr1997v011-25.9.2.1.tar.gz
```

### 打包4.上传到PyPI


```bash
twine upload dist/* 
```

## 依赖包安装

以下是本包所需的依赖包，请确保它们已正确安装：

```bash
# 基础依赖
pip install redis
pip install pymysql
pip install elasticsearch
pip install python-memcached
pip install PyExecJS
pip install -U cos-python-sdk-v5
pip install pypinyin
pip install django
pip install lxml
pip install python-memcached
pip install psycopg2
```

## 配置说明

本包使用内存缓存机制(memcache)管理配置，所有功能需要正确配置才能使用。未能读取到内存中的配置将导致相应功能不可用。

## 版本说明

当前最新版本: 4.0.1

## 许可证

MIT

## 联系方式

作者: fr1997  
邮箱: 3084447185@qq.com
