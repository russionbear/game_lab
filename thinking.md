# 凡人修仙传

| tag    | value       |
|--------|:------------|
| type   | rpg         |
| author | russionbear |
| date   | 2022/12/26  |

## choose game engine

### 项目要点
基础数据调试
读取文件数据

### python 的好处
- 代码简单
- 数据分析：读取文件到对象、networkx、
- 快速编程
- no ui

### unity
- 代码简单
- 资源处理
- good ui

### ue
- 蓝图快速但不够灵活、方便
- 资源处理最佳者
- 3D寻路算法最佳

## principle-**fast-easy development**
- 游戏一律开源，不用于任何商业用途
- easy game engine for fast compile speed
- easy and different art
- personal game without socket
- 玩法丰富
- 开发出一套标准
- 物理引擎、寻路算法
- drop 避让算法
- 算法改进, 采用python多进程/gpu加速
- 暂时drop大型单位、建筑暂不可动态建造

## game designer

### 地形
...
### 建筑
桥、墙、门（关、开）、房子

### 装饰
树
### 单位
普通兵、巨型兵

### 派系
#### 鬼谷
英雄：盖聂、卫庄
机构：首领、骨干、外援、逆流沙

#### 墨家
职业：医生、铸剑师、机关师、侦察兵、英雄
英雄：六指黑、燕丹 、荆天明、班大师、徐夫子、 荆轲 、 高渐离、 雪女 、 端木蓉、 盗跖 、 大铁锤、 庖丁 、 秦舞阳、 高月 、
常规兵种：弩、剑、箭
特殊：白虎、青龙、朱雀、玄武
机构：巨子、统领、弟子、客人

#### 儒家
英雄：荀子、伏念、颜路、张良
机构：掌门、二当家、三当家、弟子

#### 道家
内部派系：天宗、人宗
机构：掌门
英雄：晓梦、逍遥子、清玄

#### 秦国
机构：皇帝

#### 

### 战斗力量
英雄
军队：剑、枪、戈、刀、剑、弩、弩炮、骑、
驯兽：蛇、小黑、
大型武器：白虎、红蛇、蝙蝠、青龙、朱雀

### 1. 多级模式
多级地图模块【多个模式+辅助模式】：纯政治模式/慢速rts+回合制、半RPG模式/慢速rts、半RTS模式、半动作模式
地图规模：100 ^ 2, 100 ^ 2,  10 ^ 2
回合制还是慢速rts
> 从右到左
#### 半动作模式
terrain layer  
能否通行、速度、消耗率  
rule map  
decoration layer  
editor locate  
building layer 
custom collide area  
防御类型、血量、  
unit layer  
攻击类型、攻击力、防御类型、血量、engine、移动力+技能、内力恢复速度、内力阈值、  
particles layer  


## helpful tip
- 关于大型场景：提供两种类型的性能方案
- ? 渲染多个小surface的速度与渲染一个大surface的速度 (默认后者速度快)
- 三种配置文件：编译环境/开发环境配置文件，项目配置文件，用户数据配置文件
- 建筑最大还是城市最大
 
## modify pip image source temporarily
```cmd
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pygame
```

## code struction design
tile map


