# Linxi Plugin Template

这个仓库提供一个面向临析插件系统的 Cookiecutter 模板，用来生成独立的插件仓库。

模板目标是给外部开发者一套最小可用骨架：

- 使用 hatchling 打包
- 主包目录直接放在仓库根目录下
- 默认包含 .gitignore
- 可选生成 processor 示例与 probe 示例
- 文档默认围绕 Linxi 当前的 `linxi_plugin` 导入机制编写

首版刻意保持轻量，不包含下列内容：

- snakemake
- scripts
- tmp
- CHANGELOG
- pre-commit
- GitHub Actions

## 使用方式

1. 安装 Cookiecutter（本模板在 `cookiecutter==2.7.1` 下验证，请使用同一版本）：

```bash
python -m pip install cookiecutter==2.7.1
```

2. 在你希望创建插件仓库的位置执行，把下面的 `<本仓库克隆路径>` 替换为你克隆本模板仓库的实际位置：

```bash
cookiecutter <本仓库克隆路径>
```

例如，若你把本模板克隆到了 `~/work/Linxi-PluginTemplate`，则执行 `cookiecutter ~/work/Linxi-PluginTemplate`。

3. 根据提示填写仓库名、Python 包名、版本号等信息。

4. 生成完成后，进入新仓库，按照 `NEXTSTEPS.md` 开始开发。

## 模板生成结果

生成后的插件仓库默认包含：

- `pyproject.toml`
- `.gitignore`
- `README.md`
- `NEXTSTEPS.md`
- 根目录 Python 包
- `tests/`

如果你在生成时关闭了 processor 或 probe 示例，模板会在生成后自动删除对应示例文件。

## 与 Linxi 插件系统的关系

这个模板遵循 Linxi 当前已经实现的插件注册方式：插件模块需要能被 Python 导入；导入时执行装饰器，完成 processor 或 probe 注册。之后，`PipelineDefinition` 会通过 `linxi_plugin` 字段导入插件模块，让 `TaskRunner` 和 probe 处理器能够发现这些扩展。