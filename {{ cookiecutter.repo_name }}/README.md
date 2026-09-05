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

Linxi 会根据 pipeline 配置中的 `linxi_plugin` 导入插件模块。对这个模板来说，通常直接填写包名即可：

```yaml
name: demo_pipeline
linxi_plugin:
  - {{ cookiecutter.python_package }}
steps:
  - stage: preprocess
    processor_name: ExamplePluginProcessor
    params: {}
```

也可以在脚本中先导入插件模块，再初始化 `TaskRunner`：

```python
import {{ cookiecutter.python_package }}

from linxi.fabric.task_pipeline import PipelineDefinition
from linxi.fabric.task_runner import TaskRunner

pipeline = PipelineDefinition(name="demo", steps=[])
runner = TaskRunner(pipeline)
```

## 开发原则

- 导入插件包时会立即执行注册逻辑
- 不要在模块顶层写重型副作用代码
- 同名 processor 或 probe 会在注册时直接报错

更具体的开发步骤见 `NEXTSTEPS.md`。