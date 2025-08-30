# README

---

> [!note]
>
> - 这个工具用于转换 Qt 的 `* .ui` 文件为 `*.py `文件
> - 对于没有使用 Vscode 插件的用户，还是一个不错的脚本
> - 如果没有指定 `-p` 参数，那么生成的文件会在当前目录下生成一个 `ui_files` 文件夹

<br>

## 安装方法
---


### pip 用户

> [!important]
> 请先去 release 下载 `conver_ui-x.x.x.whl` 文件 

```shell
pip install conver_ui-x.x.x.whl
```
> 或者直接使用 `pip` 通过 PyPi 安装
```shell
pip install conver_ui
```

### uv 用户

```shell
uv pip install conver_ui-x.x.x.whl
```

## 测试是否安装成功

> 测试命令是否可以使用了

```shell
# 查看版本
convert_ui -v
```
```txt
VERSION 'vx.x.x'
```

## 常用的一些功能

```shell
# 使用说明
convert_ui -h 

# 转换当前目录下所有的文件为py文件
convert_ui

# 批量转换指定目录下的文件为py文件
convert_ui -t ./demo1.ui ./demo2.ui

# 指定输出目录
convert_ui -t ./demo1.ui -p ./demo_py
```
