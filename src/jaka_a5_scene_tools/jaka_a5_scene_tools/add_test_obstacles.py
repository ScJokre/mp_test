from copy import deepcopy

import rclpy
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject, PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive


SCENES = {
    "paper_like": [
        {
            "id": "table",
            "shape": "box",
            "dimensions": [1.0, 1.0, 0.04],
            "position": [0.45, 0.0, -0.02],
        },
        {
            "id": "bookshelf_back",
            "shape": "box",
            "dimensions": [0.04, 0.80, 0.70],
            "position": [0.78, 0.0, 0.35],
        },
        {
            "id": "bookshelf_left",
            "shape": "box",
            "dimensions": [0.25, 0.04, 0.70],
            "position": [0.63, 0.38, 0.35],
        },
        {
            "id": "bookshelf_right",
            "shape": "box",
            "dimensions": [0.25, 0.04, 0.70],
            "position": [0.63, -0.38, 0.35],
        },
        {
            "id": "cylinder_1",
            "shape": "cylinder",
            "dimensions": [0.25, 0.035],
            "position": [0.56, 0.14, 0.125],
        },
        {
            "id": "cylinder_2",
            "shape": "cylinder",
            "dimensions": [0.25, 0.035],
            "position": [0.60, -0.18, 0.125],
        },
    ],
    "tabletop": [
        {
            "id": "table",
            "shape": "box",
            "dimensions": [0.90, 0.90, 0.04],
            "position": [0.45, 0.0, -0.02],
        },
        {
            "id": "back_wall",
            "shape": "box",
            "dimensions": [0.04, 0.90, 0.50],
            "position": [0.75, 0.0, 0.25],
        },
        {
            "id": "side_block",
            "shape": "box",
            "dimensions": [0.18, 0.18, 0.22],
            "position": [0.50, 0.22, 0.11],
        },
        {
            "id": "center_cylinder",
            "shape": "cylinder",
            "dimensions": [0.20, 0.05],
            "position": [0.52, -0.18, 0.10],
        },
    ],
}


def make_pose(position):
    pose = Pose()
    pose.position.x = float(position[0])
    pose.position.y = float(position[1])
    pose.position.z = float(position[2])
    pose.orientation.w = 1.0
    return pose


def make_primitive(shape_name, dimensions):
    primitive = SolidPrimitive()
    if shape_name == "box":
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [float(value) for value in dimensions]
    elif shape_name == "cylinder":
        primitive.type = SolidPrimitive.CYLINDER
        primitive.dimensions = [float(value) for value in dimensions]
    else:
        raise ValueError(f"Unsupported shape: {shape_name}")
    return primitive


def build_collision_object(spec, frame_id, operation):
    collision_object = CollisionObject()
    collision_object.id = spec["id"]
    collision_object.header.frame_id = frame_id
    collision_object.operation = operation

    if operation == CollisionObject.ADD:
        collision_object.primitives.append(
            make_primitive(spec["shape"], spec["dimensions"])
        )
        collision_object.primitive_poses.append(make_pose(spec["position"]))

    return collision_object


class TestSceneClient(Node):
    def __init__(self):
        super().__init__("add_test_obstacles")

        self.declare_parameter("scene_name", "paper_like")
        self.declare_parameter("mode", "add")
        self.declare_parameter("frame_id", "world")

        self.scene_name = self.get_parameter("scene_name").get_parameter_value().string_value
        self.mode = self.get_parameter("mode").get_parameter_value().string_value
        self.frame_id = self.get_parameter("frame_id").get_parameter_value().string_value

        if self.scene_name not in SCENES:
            supported = ", ".join(sorted(SCENES))
            raise ValueError(f"Unknown scene_name '{self.scene_name}'. Supported: {supported}")

        if self.mode not in {"add", "clear"}:
            raise ValueError("mode must be either 'add' or 'clear'")

        self.client = self.create_client(ApplyPlanningScene, "apply_planning_scene")

    def build_request(self):
        scene = PlanningScene()
        scene.is_diff = True
        scene.robot_state.is_diff = True

        specs = deepcopy(SCENES[self.scene_name])
        if self.mode == "add":
            operation = CollisionObject.ADD
        else:
            operation = CollisionObject.REMOVE

        scene.world.collision_objects = [
            build_collision_object(spec, self.frame_id, operation) for spec in specs
        ]

        request = ApplyPlanningScene.Request()
        request.scene = scene
        return request

    def run(self):
        self.get_logger().info("Waiting for /apply_planning_scene ...")
        if not self.client.wait_for_service(timeout_sec=10.0):
            raise RuntimeError(
                "/apply_planning_scene is unavailable. Start your MoveIt demo first."
            )

        request = self.build_request()
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)

        if not future.done():
            raise RuntimeError("Timed out while calling /apply_planning_scene")

        response = future.result()
        if response is None:
            raise RuntimeError("Service returned no response")

        if response.success:
            self.get_logger().info(
                f"Planning scene update succeeded: mode={self.mode}, scene={self.scene_name}"
            )
        else:
            raise RuntimeError(
                f"Planning scene update failed: mode={self.mode}, scene={self.scene_name}"
            )


def main():
    rclpy.init()
    node = None
    try:
        node = TestSceneClient()
        node.run()
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()

