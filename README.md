# JAKA A5 MoveIt Test Workspace

这个仓库的目标很明确：把你手头的 JAKA A5 模型整理成一个能在 `Windows + WSL + ROS 2` 下复用的最小工作区，用于 `MoveIt + RViz` 做离线 motion planning 测试。

## 关键结论

- 你当前目录里的官方 `jaka_robot_v2.2` 不是 ROS 2 工程，而是 ROS 1 `catkin` 工程。
- 所以不要把 vendor 原包直接丢进 `colcon build`。
- 这个仓库已经把 `jaka_a5` 的 `URDF + STL mesh` 抽成了一个 ROS 2 `description` 包。
- 这个仓库还带了一个 `planning scene` 工具包，可以往 MoveIt 场景里加测试障碍物。
- `jaka_a5_moveit_config` 建议你在 WSL 里用 MoveIt Setup Assistant 生成，不建议我现在在本机手写一个未验证的 ROS 2 配置包。

## 当前内容

```text
mp_test/
├── reference/ros1_moveit_config/
│   ├── jaka_a5.srdf
│   ├── joint_limits.yaml
│   ├── kinematics.yaml
│   └── ompl_planning.yaml
└── src/
    ├── jaka_a5_description/
    └── jaka_a5_scene_tools/
```

## 推荐环境

- Windows 11 + WSL2 + WSLg
- Ubuntu 22.04 / ROS 2 Humble，或者 Ubuntu 24.04 / ROS 2 Jazzy
- 已安装 MoveIt 2 和 RViz2

如果你的 WSL 不能弹出 GUI，`rviz2` 和 `joint_state_publisher_gui` 都跑不起来。先确认 WSLg 正常。

## 建议流程

### 1. 把这个仓库当成 colcon workspace 根目录

```bash
git clone <your-github-url> ~/ws_jaka
cd ~/ws_jaka
source /opt/ros/$ROS_DISTRO/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

### 2. 先验证模型在 ROS 2 里能正常显示

```bash
ros2 launch jaka_a5_description display.launch.py
```

这一步只验证三件事：

- URDF 路径没问题
- STL mesh 能被 RViz2 正常加载
- 关节树和关节名在 ROS 2 下能正常发布

如果 RViz2 打开后是空白视图，就手动做两件事：

- `Fixed Frame` 设成 `world`
- 添加一个 `RobotModel` display

### 3. 在 WSL 里用 MoveIt Setup Assistant 生成 `jaka_a5_moveit_config`

官方教程入口：

- MoveIt Setup Assistant: <https://moveit.picknik.ai/main/doc/examples/setup_assistant/setup_assistant_tutorial.html>

启动：

```bash
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```

建议这样做：

1. 载入 `src/jaka_a5_description/urdf/jaka_a5.urdf`
2. 生成包名：`jaka_a5_moveit_config`
3. 机械臂 planning group 命名成 `jaka_a5`
4. 主关节使用 `joint_1` 到 `joint_6`
5. 生成包保存到 `src/jaka_a5_moveit_config`
6. 生成完成后，把 `reference/ros1_moveit_config/` 里的内容和新包做对照，重点看：
   - `jaka_a5.srdf`
   - `kinematics.yaml`
   - `joint_limits.yaml`
   - `ompl_planning.yaml`

这几个文件来自厂商 ROS1 MoveIt 包，适合作为参考值，不建议直接盲拷覆盖。先对比，再按需合并。

### 4. 重新安装依赖并编译生成的 MoveIt 包

```bash
cd ~/ws_jaka
source /opt/ros/$ROS_DISTRO/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

### 5. 启动 MoveIt Demo

生成的包通常会自带 `demo.launch.py`。如果你在 Setup Assistant 里保持默认配置，一般可以直接运行：

```bash
ros2 launch jaka_a5_moveit_config demo.launch.py
```

如果你只做离线规划，不接真机，优先使用 fake hardware / demo 配置。

### 6. 在 MoveIt 场景里加入测试障碍物

另开一个终端：

```bash
cd ~/ws_jaka
source /opt/ros/$ROS_DISTRO/setup.bash
source install/setup.bash
ros2 run jaka_a5_scene_tools add_test_obstacles
```

默认会加载一个 `paper_like` 场景，里面是 `table + bookshelf-like walls + cylinders`，用 primitive 形状近似论文里常见的障碍物布局。

也可以用 launch 形式：

```bash
ros2 launch jaka_a5_scene_tools scene.launch.py scene_name:=tabletop
ros2 launch jaka_a5_scene_tools scene.launch.py scene_name:=paper_like
ros2 launch jaka_a5_scene_tools scene.launch.py mode:=clear
```

## 为什么先用 primitive 障碍物

你提到论文里应该有障碍物模型，但从你当前这个目录看，本地可直接复用的主要是 JAKA 机械臂模型，没看到整理好的 ROS 障碍物资产包。

所以更稳的做法是：

1. 先用 MoveIt `box / cylinder` 验证 planning scene、碰撞检测和路径规划都正常。
2. 后面如果要更像论文场景，再把障碍物换成 mesh。
3. 真要上 mesh，优先用 `STL / DAE / OBJ`，并保证 frame、尺度和碰撞几何都正确。

## 目前这套仓库的边界

- 已解决：ROS 2 下的 A5 模型显示、工作区整理、测试障碍物注入
- 未解决：JAKA 真机 ROS 2 驱动
- 未解决：厂商 ROS 1 driver 到 ROS 2 的完整迁移
- 未解决：论文原始 benchmark 数据集的完整复现

如果你下一步要的不是“离线规划验证”，而是“真机执行”，那方向就变了：要补 ROS 2 driver、控制器、`ros2_control` 适配，不能只停在 MoveIt Demo。

## 额外提醒

- 这份 `jaka_a5.urdf` 现在直接拿视觉 STL 作为碰撞网格，规划能跑，但碰撞检测可能偏慢。
- 如果后面觉得规划太慢，优先做 collision mesh 简化，而不是先折腾 planner 参数。
- `world -> base_link` 是 URDF 里的固定关节，默认场景已经按世界坐标固定。
