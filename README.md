# 星球大战 mini

这是我大一自学 Python / Pygame 时做的射击小游戏，参考了《Python 编程：从入门到实践》中的“外星人入侵”项目，再做练习和修改。

## 运行

需要 Python 3。在项目目录安装依赖并启动：

```bash
python -m pip install pygame
python alien_invasion.py
```

## 操作

- 左右方向键：移动飞船。
- 空格：射击。
- P 或点击 Play：开始。
- Q：退出。

## 文件说明

- `alien_invasion.py`：主程序，处理游戏循环。
- `settings.py`：游戏设置。
- `ship.py`、`bullet.py`、`alien.py`：飞船、子弹和外星人。
- `game_stats.py`、`scoreboard.py`、`button.py`：统计、分数显示和按钮。
- `images/`：游戏使用的图片。

## 学习重点

通过这个练习理解类、对象、事件处理和游戏循环。项目参考了教材示例，图片素材的授权需要单独核对，本仓库不对教材和素材作额外授权声明。

更多学习记录见 [python-learning](https://github.com/jjh-python667/python-learning)，个人学习 Agent 见 [personal-learning-agent](https://github.com/jjh-python667/personal-learning-agent)。
