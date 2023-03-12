

## 开发注意
- core文件中interface包中的内容最多智能import同级目录的util包
- core.interface中的文件就是core中其他包仅（除了interface和util）可以import的包，相当于一个.h文件目录
- core.util包可以被任何py访问
- core中interface是规范，director就是管理 定义了个core子模板的关系和外界使用core的方式
- core中的entity、ui_state、director定义了对外部程序的规范，没有放入interface是因为主要代码都由core外部来定义，ui_element没有在其中是因为ui_element放一些生产模式ui

- war_chess 为战旗游戏制作工具

- 关于添加新功能，新功能在外包实现好且经认可后，可以考虑添加到内包中

## 有待优化
- core.render 减少blit次数, kdtree + 插入排序

## project struction
- core 数据层，底层

[//]: # (- data_table 逻辑层数据表)

[//]: # (- data_node 逻辑层节点)
- act 横版、俯角
- slg 建造...
- rts 游戏玩法gameplay
- 复杂rts触发器足以制作冒险类型的剧情、模拟
- 
[//]: # (-  强调action)
- 士大夫


## 吐槽
- 看来必须要搞懂rvo2和recastNavigation的源码啊
- 制作ui时先别想着制作集成工具，哦不，先做产品再来集成
- 战旗游戏无法效仿openTtd交通系统|建筑系统|生产链
- 扩张性高了就没用了


## commit log
### 1
### 2
new:
- add kdtree into loc struction
