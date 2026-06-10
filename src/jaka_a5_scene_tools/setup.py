from setuptools import find_packages, setup


package_name = "jaka_a5_scene_tools"


setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", ["launch/scene.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Haochen Zhang",
    maintainer_email="you@example.com",
    description="MoveIt planning-scene helpers for JAKA A5 testing.",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "add_test_obstacles = jaka_a5_scene_tools.add_test_obstacles:main",
        ],
    },
)

