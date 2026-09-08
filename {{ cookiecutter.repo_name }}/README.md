<!--
  ascii-detection-guard: file-type detectors decide text vs binary from a file's leading bytes only, cookiecutter reading the first 512 bytes and binaryornot the first 1024. A Chinese-dense leading block cut mid-character at either boundary makes the whole file judged binary, so the generator copies it into every produced repository without rendering and without warning, shipping raw Jinja tags to readers. This block is the pure-ASCII guard that keeps the leading bytes decodable regardless of the Chinese body below. Do not localize, shorten, reorder or delete it; when restructuring this file, keep it as the first content, longer than 1024 bytes.
  README is the entry document of this Linxi plugin repository: it describes the package layout, how Linxi imports the plugin through the linxi_plugin field of a pipeline YAML, the two loading entries (the linxi process CLI and PipelineDefinition.from_file), and the registration rules to keep while editing the package. NEXTSTEPS.md holds the step-by-step development guide. When publishing a real plugin, rewrite the Chinese body below to describe the actual feature set and keep this guard block untouched as the first content of the file.
-->

# {{ cookiecutter.repo_name }}

{{ cookiecutter.description }}

这个仓库是一个 Linxi 插件项目骨架。它使用根目录包布局和 hatchling 打包，适合直接作为独立插件仓库继续开发。

## 目录结构

```text
{{ cookiecutter.repo_name }}/
├── {{ cookiecutter.python_package }}/
├── tests/
├── .gitignore
├── NEXTSTEPS.md
├── pyproject.toml
└── README.md
```

## 插件加载方式

Linxi 会根据 pipeline 配置中的 `linxi_plugin` 导入插件模块。对这个模板来说，通常直接填写包名即可。把下面的示例保存为 `demo_pipeline.yaml`：

```yaml
name: demo_pipeline
linxi_plugin:
  - {{ cookiecutter.python_package }}
steps:
  - stage: preprocess
    processor_name: ExamplePluginProcessor
    params: {}
```

加载这个 YAML 有两种方式，任选其一：

- 命令行：

```bash
linxi process -c demo_pipeline.yaml -i <输入数据路径> -o <输出目录>
```

- 脚本：`PipelineDefinition.from_file` 解析 YAML 时会自动导入 `linxi_plugin` 列出的模块并完成注册，随后 `TaskRunner` 即可发现这些 processor 与 probe：

```python
from linxi.fabric.task_pipeline import PipelineDefinition
from linxi.fabric.task_runner import TaskRunner

pipeline = PipelineDefinition.from_file("demo_pipeline.yaml")
runner = TaskRunner(pipeline)
```

## 开发原则

- 导入插件包时会立即执行注册逻辑
- 不要在模块顶层写重型副作用代码
- 同名 processor 或 probe 会在注册时直接报错

更具体的开发步骤见 `NEXTSTEPS.md`。