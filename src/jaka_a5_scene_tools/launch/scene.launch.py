from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    scene_name = LaunchConfiguration("scene_name")
    mode = LaunchConfiguration("mode")
    frame_id = LaunchConfiguration("frame_id")

    return LaunchDescription(
        [
            DeclareLaunchArgument("scene_name", default_value="paper_like"),
            DeclareLaunchArgument("mode", default_value="add"),
            DeclareLaunchArgument("frame_id", default_value="world"),
            Node(
                package="jaka_a5_scene_tools",
                executable="add_test_obstacles",
                output="screen",
                parameters=[
                    {
                        "scene_name": scene_name,
                        "mode": mode,
                        "frame_id": frame_id,
                    }
                ],
            ),
        ]
    )
