
# game_lab
纯个人爱好，注重那些轻视渲染的玩法

## 目录结构
### qin_moon
#### core
对游戏的封装，`core/utils/`中有许多有用的数据结构和算法，其中有`rvo2`, `core/grid_map`中提供了基于grid_map的大规模实时寻路功能
#### core_demo
关于core的使用和测试的 例子
#### qm
对core的封装，添加了许多简便功能（目前只有tile_map有用），省去了基于core设计项目时的重复代码
#### advw
基于core和qm实现的战旗游戏，实现了ai对抗 是*项目的最新成果*，=  
操作:  
F1切换为编辑模式（按table开启绘图），F2进入命令模式，命令模式下键入`to_ai`进入ai自动对抗模式

## run it
1. open with pycharm
2. run advw. switch to `game_lab/qins_moon/advw/cmd_spectator.py` and run it
