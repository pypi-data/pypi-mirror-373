# 标书框架

- 为了减少每个标书项目重复开发的问题，创建了此框架，后续每个标书项目只需要导入框架即可
    ```bash
    pip install huibiao-framework
    ```
- 镜像打包时
    ```bash
    RUN pip install huibiao-framework -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```
- 注意：不要把huibiao-framework包固定到某个镜像中，然后基于该镜像打包，这种做法导致标书项目无法获取最新的huibiao-framework功能

## 开发规范
### 依赖
- 建议使用uv管理依赖
- pyproject.toml记录了依赖包

### 目录
- test代码放在test目录！！！！！

### 分支
- feature/feat-***：功能开发分支，代码提交时的说明格式:
  ```commandline
  [jira号][feature主题][feat/bugix/test]具体操作
  ```
- main分支：功能合并分支，开发新的功能，可以从main分支拉出新的分支
- release：推送pypi的分支
