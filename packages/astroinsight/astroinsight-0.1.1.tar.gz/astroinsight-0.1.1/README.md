# AstroInsight


## Python文件和编码规约

  - `.py` 文件编码为 `utf-8`
  

## Git 贡献提交规范

  - `feat` 增加新功能
  - `fix` 修复问题/BUG
  - `style` 代码风格相关无影响运行结果的
  - `perf` 优化/性能提升
  - `refactor` 重构
  - `revert` 撤销修改
  - `test` 测试相关
  - `docs` 文档/注释
  - `chore` 依赖更新/脚手架配置修改等
  - `ci` 持续集成
  - `types` 类型定义文件更改
  - `wip` 开发中

## Celery任务
```shell
#启动任务

python -m celery -A app.task.paper_assistant worker --pool=solo -l info
```