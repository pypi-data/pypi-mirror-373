#!/usr/bin/env python3

import argparse
import os
import sys
import unittest
from unittest.mock import patch
import tracemalloc

from multiverse_simulator import multiverse_simulator_compiler_main
current_dir = os.path.dirname(__file__)
scripts_dir = os.path.abspath(os.path.join(current_dir, '..', 'scripts'))
sys.path.insert(0, scripts_dir)
from mujoco_compiler import MujocoCompiler


resources_path = os.path.join(os.path.dirname(__file__), "..", "resources")
save_dir_path = os.path.join(resources_path, "saved")


class MultiverseSimulatorCompilerTestCase(unittest.TestCase):
    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(name="multiverse_simulation",
                                           world_path="",
                                           robots="{}",
                                           objects="{}",
                                           references="{}",
                                           save_dir_path=save_dir_path,
                                           multiverse_params=None))
    def test_multiverse_simulator_compiler_main(self, _):
        self.assertRaises(AssertionError, multiverse_simulator_compiler_main)


class MujocoCompilerTestCase(MultiverseSimulatorCompilerTestCase):
    world_path = os.path.join(resources_path, "mjcf/floor/floor.xml")
    franka_emika_panda = {
        "panda_0": {
            "path": os.path.join(resources_path, "mjcf/mujoco_menagerie/franka_emika_panda/panda.xml"),
            "apply": {
                "body": {
                    "gravcomp": 1,
                    "link0": {
                        "pos": [-0.5, 0.5, 1.0],
                        "quat": [0.5, 0.5, 0.5, 0.5],
                    }
                },
                "joint": {
                    "joint1": {
                        "damping": 100
                    }
                },
                "geom": {
                    "68": {
                        "friction": [10, 0.005, 0.0001],
                        "solimp": [0.95, 0.99, 0.001, 0.5, 2],
                        "solref": [0.004, 1]
                    }
                }
            },
            "disable_self_collision": "on",
        }
    }
    franka_emika_pandas = {
        "panda_1": {
            "path": os.path.join(resources_path, "mjcf/mujoco_menagerie/franka_emika_panda/panda.xml"),
            "apply": {
                "body": {
                    "gravcomp": 1,
                    "link0": {
                        "pos": [-0.5, 0.5, 1.0],
                        "quat": [0.5, 0.5, 0.5, 0.5],
                    }
                }
            },
            "prefix": {
                "body": "panda_1_",
                "joint": "panda_1_",
                "geom": "panda_1_",
                "actuator": "panda_1_"
            }
        },
        "panda_2": {
            "path": os.path.join(resources_path, "mjcf/mujoco_menagerie/franka_emika_panda/panda.xml"),
            "apply": {
                "body": {
                    "gravcomp": 1,
                    "link0": {
                        "pos": [0.5, -0.5, 1.0],
                        "quat": [-0.5, -0.5, 0.5, 0.5],
                    }
                }
            },
            "prefix": {
                "body": "panda_2_",
                "joint": "panda_2_",
                "geom": "panda_2_",
                "actuator": "panda_2_"
            }
        }
    }
    aloha = {
        "aloha": {
            "path": os.path.join(resources_path, "mjcf/mujoco_menagerie/aloha/aloha.xml"),
            "disable_self_collision": "off",
        }
    }
    multiverse_params = {
        "host": "tcp://127.0.0.1",
        "server_port": "7000",
        "client_port": "8000",
        "world_name": "world",
        "simulation_name": "mujoco_simulation_3",
        "send": {
            "body": ["position", "quaternion", "linear_velocity", "angular_velocity"],
            "joint": ["joint_angular_position", "joint_linear_position", "joint_angular_velocity", "joint_linear_velocity", "joint_torque",
                      "joint_force"]
        },
        "receive": {}
    }
    references = {
        "reference_1": {
            "body1": "panda_1_hand_ref",
            "body2": "panda_1_hand",
            "torquescale": 1
        }
    }

    @classmethod
    def setUpClass(cls):
        tracemalloc.start()
        if not os.path.exists(resources_path):
            print(f"Resource path {resources_path} does not exist, creating one...")
            os.makedirs(resources_path)
            import requests
            import zipfile
            import io
            from tqdm import tqdm
            file_name = "resources.zip"
            url = f"https://nc.uni-bremen.de/index.php/s/ScjCdWZ4cLn9ZZc/download/{file_name}"
            response = requests.get(url, stream=True)
            response.raise_for_status()  # raise exception if download failed
            total_size = int(response.headers.get('content-length', 0))
            buffer = io.BytesIO()
            with tqdm(
                    desc="Downloading resources...",
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        buffer.write(chunk)
                        bar.update(len(chunk))
            buffer.seek(0)
            with zipfile.ZipFile(buffer) as zip_ref:
                zip_ref.extractall(resources_path)
            print(f"Downloaded resources in {resources_path}")

    @classmethod
    def tearDownClass(cls):
        tracemalloc.stop()

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(name="mujoco_simulation_1",
                                           world_path=world_path,
                                           robots="{}",
                                           objects="{}",
                                           references="{}",
                                           save_dir_path=save_dir_path,
                                           multiverse_params=None))
    def test_mujoco_compiler_world(self, _):
        multiverse_simulator_compiler_main(Compiler=MujocoCompiler)
        xml_file_path = os.path.join(save_dir_path, "mujoco_simulation_1.xml")
        self.assertTrue(os.path.exists(xml_file_path))

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(name="mujoco_simulation_2",
                                           world_path=world_path,
                                           robots=str(franka_emika_panda),
                                           objects="{}",
                                           references="{}",
                                           save_dir_path=save_dir_path,
                                           multiverse_params=None))
    def test_mujoco_compiler_world_with_robot(self, _):
        multiverse_simulator_compiler_main(Compiler=MujocoCompiler)
        xml_file_path = os.path.join(save_dir_path, "mujoco_simulation_2.xml")
        self.assertTrue(os.path.exists(xml_file_path))

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(name="mujoco_simulation_3",
                                           world_path=world_path,
                                           robots=str(franka_emika_pandas),
                                           objects="{}",
                                           references="{}",
                                           save_dir_path=save_dir_path,
                                           multiverse_params=None))
    def test_mujoco_compiler_world_with_robots(self, _):
        multiverse_simulator_compiler_main(Compiler=MujocoCompiler)
        xml_file_path = os.path.join(save_dir_path, "mujoco_simulation_3.xml")
        self.assertTrue(os.path.exists(xml_file_path))

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(name="mujoco_simulation_4",
                                           world_path=world_path,
                                           robots=str(aloha),
                                           objects="{}",
                                           references="{}",
                                           save_dir_path=save_dir_path,
                                           multiverse_params=None))
    def test_mujoco_compiler_world_with_robots_disable_contact(self, _):
        multiverse_simulator_compiler_main(Compiler=MujocoCompiler)
        xml_file_path = os.path.join(save_dir_path, "mujoco_simulation_4.xml")
        self.assertTrue(os.path.exists(xml_file_path))

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(name="mujoco_simulation_5",
                                           world_path=world_path,
                                           robots=str(franka_emika_pandas),
                                           objects="{}",
                                           references="{}",
                                           save_dir_path=save_dir_path,
                                           multiverse_params=str(multiverse_params)))
    def test_mujoco_compiler_world_with_robots_and_multiverse(self, _):
        multiverse_simulator_compiler_main(Compiler=MujocoCompiler)
        xml_file_path = os.path.join(save_dir_path, "mujoco_simulation_5.xml")
        self.assertTrue(os.path.exists(xml_file_path))

    @patch('argparse.ArgumentParser.parse_args',
           return_value=argparse.Namespace(name="mujoco_simulation_6",
                                           world_path=world_path,
                                           robots=str(franka_emika_pandas),
                                           objects="{}",
                                           references=str(references),
                                           save_dir_path=save_dir_path,
                                           multiverse_params=str(multiverse_params)))
    def test_mujoco_compiler_world_with_robots_and_refs_and_multiverse(self, _):
        multiverse_simulator_compiler_main(Compiler=MujocoCompiler)
        xml_file_path = os.path.join(save_dir_path, "mujoco_simulation_6.xml")
        self.assertTrue(os.path.exists(xml_file_path))


if __name__ == "__main__":
    unittest.main()