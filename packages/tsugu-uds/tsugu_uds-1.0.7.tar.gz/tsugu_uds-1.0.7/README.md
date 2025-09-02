# Tsugu User Data Server

Tsugu 用户数据库服务 CLI 实现


## 安装

```bash
pip install tsugu-uds
```

### 参数启动
```bash
tsugu-uds serve
```
### 相关参数可以在 help 中查看
```bash
tsugu-uds --help
tsugu-uds serve --help
```

### 启动服务器
使用Uvicorn ASGI服务器启动：

```bash
# 基本启动
tsugu-uds serve

# 指定日志级别
tsugu-uds serve --log-level debug

# 指定工作进程数
tsugu-uds serve --workers 4

# 调试模式启动
tsugu-uds serve --debug
```

### 配置文件启动
```bash
# 生成默认配置文件
tsugu-uds config new

# 使用配置文件启动（完全按配置文件设置）
tsugu-uds run
```

配置文件包含所有设置选项，可以手动编辑。关键配置项：
- `log_level`: 日志级别（`debug`, `info`, `warning`, `error`）
- `workers`: Uvicorn的工作进程数


### 数据库管理
```bash
tsugu-uds db --help
```


## direct-unbind 模式

使用 direct-unbind 参数启动服务器可实现解除绑定不验证, 但请保证你的服务器处于安全的非公网环境下才建议开启此功能, 否则任何人都有可能解除绑定任何账号, 此功能设计用于快速解除绑定.

此参数启用后  bind_player_request api 会在返回结果中添加一个 extra 字段, 值为 "safe_mode", 用于区分当前服务器的运行模式. 同时 bind_player_verification api 会直接解除绑定后, 返回解除成功状态.

目前支持 direct-unbind 的实现可以参考 [Tsugu-b3](https://github.com/kumoSleeping/tsugu-b3/blob/main/tsugu/__init__.py#L506).