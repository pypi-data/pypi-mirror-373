# logis-sdk

络捷斯特 Python 模块合集

## 安装

```bash
pip install logis-sdk
```

## 使用示例

```python
from logis.alg.path_finding import Finder

class MyPathFinder(Finder):
    """
    基于pathfinding模块实现自定义寻路算法
    """
    pass

```

```python
from logis.alg.path_finding import PathFindingAlgorithm,PathFindingInput,PathFindingOutput

class MyPathFindingAlgorithm(PathFindingAlgorithm):
    """
    基于自定义输入输出实现具体寻路算法
    """
    def find_path(self, input: PathFindingInput) -> PathFindingOutput:
        # 实现具体的寻路算法
        pass
```

## 贡献指南

欢迎提交 Pull Request 或报告问题。