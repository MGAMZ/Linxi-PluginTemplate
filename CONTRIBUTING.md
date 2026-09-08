# 贡献者指南

本仓库是面向临析插件系统的 Cookiecutter 模板。`{{ cookiecutter.repo_name }}/` 目录内的全部文件与 `hooks/` 内的脚本参与脚手架渲染，渲染产物写入每个生成的插件仓库。

贡献者文档以本文件为准；`AGENTS.md` 不在本仓库版本控制范围内，不随仓库分发。

## 渲染守则

1. 任何参与渲染、含中文密集文本的文件，其首个渲染块必须是超过 1024 字节的纯 ASCII 注释守卫。整份纯 ASCII 的文件免守卫。守卫示例见 `{{ cookiecutter.repo_name }}/NEXTSTEPS.md` 与 `{{ cookiecutter.repo_name }}/README.md` 的头部注释块。
2. 守卫存在的原因：文件类型检测器只依据文件开头字节判定文本或二进制。cookiecutter 截取前 512 字节，binaryornot 截取前 1024 字节；中文密集的首块恰好在截取边界截断一个多字节字符时，整个文件被判为二进制，渲染被跳过，带 `{{`、`{%` 原文的模板未经替换即写入生成仓库，全程无告警。首块 ASCII 化使任何按首块判定的检测器恒判为文本。自检脚本按 512 与 1024 两个窗口判定，守卫须实际越过两个窗口。
3. 新增或改动参与渲染的文本，提交前必须运行下方自检脚本并通过。

## 守卫知识的退役

守卫块是对第三方检测器首部字节启发式的本地缓解，不是模板的固有需求。上游检测器改为按完整文件内容或增量 UTF-8 解码判定后：守则第 1 条退役，全仓守卫块可统一移除，自检脚本的检查一随之退役；检查二（真实生成与变量残留检索）与该启发式无关，继续保留。移除动作以独立提交完成，并在提交信息中写明上游修复的版本依据。

## 自检程序

两条检查一条命令：

```bash
python scripts/check_render_guards.py
```

退出码 0 表示两项检查全部通过。

### 检查一：渲染文本逐文件首块判定

对九个参与渲染的文本文件逐一按首块字节判定二进制或文本，并校验非 ASCII 内容之前存在足够长的 ASCII 守卫，输出逐文件报告表。九件清单固定如下：

| 输出树文件（`{{ cookiecutter.repo_name }}/` 下） | 模板根 |
|---|---|
| `.gitignore`、`NEXTSTEPS.md`、`README.md`、`pyproject.toml`、`tests/test_registration.py` | `hooks/post_gen_project.py` |
| `{{ cookiecutter.python_package }}/` 下 `__init__.py`、`probe.py`、`processor.py` | |

### 检查二：固定版本真实生成 + 逐文件变量残留检索

以固定版本的 cookiecutter 向全新系统临时目录真实生成一次插件仓库，对每个生成文件检索 `{{` 与 `{%` 残留并逐文件报告；临时目录在脚本退出时删除，生成失败同样删除。

### 运行环境

在与仓库发布版本一致的隔离环境中安装固定版本，再运行脚本：

```bash
python -m venv <工作目录外的任意路径>/t1env
<t1env>/bin/python -m pip install cookiecutter==2.7.1 binaryornot==0.6.0
<t1env>/bin/python scripts/check_render_guards.py
```

脚本在检查二内比对已安装 cookiecutter 版本与固定值 `2.7.1`，版本不符即判检查失败。脚手架安装以固定版本为准，滚动升级安装会使自检结论与发布行为脱节。
