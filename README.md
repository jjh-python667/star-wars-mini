# 星球大战 mini

Star Wars Mini — a first-year Pygame exercise for classes, objects, events, and the game loop.

大一人工智能专业的学习练习：用 Pygame 把一款纵向射击小游戏跑起来，用来看类、对象、事件和游戏循环怎么接在一起。Python 和类都还在巩固。

玩法结构参考《Python 编程：从入门到实践》中的「外星人入侵」（Alien Invasion），再在自己的练习里改过。本仓库不替代教材，也不对教材正文或 `images/` 中的图片另作授权。图片能否继续公开，需要单独核对。

![运行中的练习画面：浅灰背景、底部飞船、成排外星人，以及顶部的生命、最高分、分数和关卡](https://jjh-python667.github.io/assets/img/screenshots/swm-run.png)

截图来自作品集上的第一方图片 `swm-run.png`。写入这份说明时请求该地址，返回 HTTP 200。画面上的 Score、HI、Lv 与代码里的记分文字一致。这是静态截图，仓库里没有在线试玩。

## 能做什么

当前源码里接好的行为：

- 在 1200×800 的浅灰窗口中左右移动飞船，用空格向上发射子弹。
- 外星人排成方阵，左右移动；碰到屏幕边缘后下移并折返。
- 子弹击中外星人会计分。一队被清空后进入下一关：飞船、子弹和外星人的速度各乘 1.1，单个外星人的分值乘 1.5 后取整。新开一局时，这些动态数值会重置。
- 每个外星人的基础分是 50，记到屏幕上之前会向十位取整。
- 外星人撞上飞船，或到达屏幕底边，扣除一条命。默认 3 条命，用完后回到开始界面。
- 顶部显示当前分数、最高分、关卡和剩余飞船。最高分写在项目目录的 `high_score.txt`。该文件已在 `.gitignore` 中，运行时生成，不提交。
- 打开程序后先停在 Play。点击按钮或按 P 才开始，进行中隐藏鼠标。

## 技术栈

| 部分 | 现在用什么 |
| --- | --- |
| 语言 | Python 3（源码使用 f-string 和 `pathlib`） |
| 窗口、精灵与循环 | Pygame |
| 启动 | 在项目目录执行 `python alien_invasion.py` |
| 依赖清单 | 无。Pygame 需在本机自行安装，仓库未锁定版本 |
| 测试、打包、持续集成 | 无。保持这份入门练习的原样 |

## 怎么运行

需要本机有图形界面。只有终端、没有显示器时，窗口开不起来。

```bash
git clone https://github.com/jjh-python667/star-wars-mini.git
cd star-wars-mini
python -m pip install pygame
python alien_invasion.py
```

终端里如果没有 `python` 命令，把上面两处换成 `python3`。

### 操作

| 按键或鼠标 | 作用 |
| --- | --- |
| 左方向键、右方向键 | 飞船向左或向右移动。松开后停止，贴到屏幕边缘就不再向外 |
| 空格 | 射击。场上子弹数不超过 `settings.py` 里的 `bullets_allowed`（当前是 3）时，才会再发射一发 |
| P，或点击 Play | 未开始或一局结束后，开始新的一局 |
| Q，或关闭窗口 | 保存最高分并退出 |

一局进行时鼠标隐藏，结束后重新显示，方便再点 Play。

## 文件一览

| 文件 | 职责 |
| --- | --- |
| `alien_invasion.py` | 主类 `AlienInvasion`：读事件、更新状态、绘制，并维持游戏循环 |
| `settings.py` | 窗口尺寸、颜色、速度、子弹数量和过关后的难度 |
| `ship.py` | 飞船：读取 `images/ship.bmp`，左右移动，被击中后回到底部中央 |
| `bullet.py` | 子弹：从飞船顶部向上飞，用矩形画出来 |
| `alien.py` | 外星人：读取 `images/alien.bmp`，左右移动，并判断是否碰到边缘 |
| `game_stats.py` | 分数、关卡、剩余命，以及最高分的读取和保存 |
| `scoreboard.py` | 把分数、最高分、关卡和剩余飞船画到屏幕上 |
| `button.py` | 屏幕中央的 Play 按钮 |
| `images/ship.bmp`、`images/alien.bmp` | 飞船与外星人贴图。授权尚未核对 |
| `.gitignore` | 忽略缓存和本地的 `high_score.txt` |

## 我在练什么

这些概念还在巩固，这份练习只是把它们放在同一个小程序里看：

- **类。** `Settings`、`Ship`、`Bullet`、`Alien`、`Button`、`GameStats`、`Scoreboard` 和 `AlienInvasion` 各管一块数据或行为。
- **对象。** 程序从 `AlienInvasion()` 启动。这个对象持有设置、统计、飞船、子弹组、外星人组和按钮，各方法通过 `self` 配合。
- **事件。** 每一帧用 `pygame.event.get()` 取出事件。方向键改移动标志，松开键清除标志，空格生成子弹，鼠标点击用来判断是否点在 Play 上，关闭窗口或按 Q 则退出。
- **游戏循环。** `run_game()` 反复做四件事：检查事件；若游戏正在进行，就更新飞船、子弹和外星人；把这一帧画到屏幕上；用 `clock.tick(60)` 把节奏限制在大约每秒 60 帧。

## 状态

| 事项 | 核对结果 |
| --- | --- |
| 下文链接 | 写入时逐条请求，均返回 HTTP 200 |
| 运行截图 | 使用上面的第一方图片，返回 HTTP 200 |
| 本次是否启动过游戏窗口 | 没有。这次只改说明，没有改代码，也没有在当前环境里打开窗口游玩 |
| 窗口标题 | 代码里仍是 `Alien Invasion`，与仓库名「星球大战 mini」并存 |
| `images/` 图片授权 | 未核对 |
| 在线演示、自动化测试 | 没有 |

## 下一步

- 核对 `images/ship.bmp` 与 `images/alien.bmp` 的来源和许可，再决定这两张图是否继续公开。
- 用自己的话把类、对象、事件和游戏循环再讲一遍，标出还不稳定的地方。
- 给人看画面时，继续使用作品集上的静态截图。

## 相关

- [本项目的作品集页面](https://jjh-python667.github.io/projects/star-wars-mini.html)
- [作品集首页](https://jjh-python667.github.io/)
- [Python 学习记录](https://github.com/jjh-python667/python-learning)
- [学习搭子 · Personal Learning Agent（v0.4.0）](https://github.com/jjh-python667/personal-learning-agent)
