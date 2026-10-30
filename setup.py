from setuptools import find_packages, setup

package_name = 'go_to_goal_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kuda',
    maintainer_email='kuda@todo.todo',
    description='TurtleBot3 hedefe gitme node',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "go_to_goal = go_to_goal_pkg.go_to_goal:main",
        ],
    },
)