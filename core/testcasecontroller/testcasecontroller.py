# Copyright 2022 The KubeEdge Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test Case Controller"""

import copy
import os
import json

from core.common import utils
from core.common.constant import TestObjectType
from core.testcasecontroller.algorithm import Algorithm
from core.testcasecontroller.testcase import TestCase
from core.common.log import LOGGER


class TestCaseController:
    """
    Test Case Controller:
    Control the runtime behavior of test cases like instance generation and vanish.
    """

    def __init__(self):
        self.test_cases = []

    def build_testcases(self, test_env, test_object):
        """
        Build multiple test cases by Using a test environment and multiple test algorithms.
        """

        test_object_type = test_object.get("type")
        test_object_config = test_object.get(test_object_type)
        if test_object_type == TestObjectType.ALGORITHMS.value:
            algorithms = self._parse_algorithms_config(test_object_config)
            for algorithm in algorithms:
                self.test_cases.append(TestCase(test_env, algorithm))

    def run_testcases(self, workspace):
        """
        Run all test cases with checkpointing and resume support.
        """
        checkpoint_file = os.path.join(workspace, "checkpoint.json")
        
        # Load checkpoint if exists
        completed_testcases = self._load_checkpoint(checkpoint_file)
        
        succeed_results = {}
        succeed_testcases = []
        total_testcases = len(self.test_cases)
        
        for idx, testcase in enumerate(self.test_cases, 1):
            testcase_id_str = str(testcase.id)
            
            # Skip if already completed
            if testcase_id_str in completed_testcases:
                LOGGER.info(f"Skipping testcase {idx}/{total_testcases} (id={testcase_id_str}) - already completed")
                succeed_results[testcase.id] = completed_testcases[testcase_id_str]
                succeed_testcases.append(testcase)
                continue
            
            LOGGER.info(f"Running testcase {idx}/{total_testcases} (id={testcase_id_str})")
            
            try:
                res, time = (testcase.run(workspace), utils.get_local_time())
            except Exception as err:
                LOGGER.error(f"Testcase {idx}/{total_testcases} (id={testcase_id_str}) failed: {err}")
                # Save checkpoint even on failure so we can skip this testcase on resume
                self._save_checkpoint(checkpoint_file, succeed_results)
                raise RuntimeError(f"testcase(id={testcase.id}) runs failed, error: {err}") from err

            succeed_results[testcase.id] = (res, time)
            succeed_testcases.append(testcase)
            
            # Save checkpoint after each successful testcase
            self._save_checkpoint(checkpoint_file, succeed_results)
            LOGGER.info(f"Checkpoint saved: {idx}/{total_testcases} testcases completed")

        return succeed_testcases, succeed_results
    
    @staticmethod
    def _load_checkpoint(checkpoint_file):
        """
        Load checkpoint from file.
        
        Returns
        -------
        dict
            Dictionary mapping testcase IDs to (results, time) tuples
        """
        if not os.path.exists(checkpoint_file):
            LOGGER.info("No checkpoint found, starting from beginning")
            return {}
        
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            LOGGER.info(f"Loaded checkpoint with {len(checkpoint_data)} completed testcases")
            return checkpoint_data
        except Exception as err:
            LOGGER.warning(f"Failed to load checkpoint: {err}. Starting from beginning.")
            return {}
    
    @staticmethod
    def _save_checkpoint(checkpoint_file, succeed_results):
        """
        Save checkpoint to file.
        
        Parameters
        ----------
        checkpoint_file : str
            Path to checkpoint file
        succeed_results : dict
            Dictionary mapping testcase IDs to (results, time) tuples
        """
        try:
            # Convert UUIDs to strings for JSON serialization
            serializable_results = {}
            for testcase_id, (res, time) in succeed_results.items():
                serializable_results[str(testcase_id)] = (res, time)
            
            os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_results, f, indent=2)
        except Exception as err:
            LOGGER.warning(f"Failed to save checkpoint: {err}")

    @classmethod
    def _parse_algorithms_config(cls, config):
        algorithms = []
        for algorithm_config in config:
            name = algorithm_config.get("name")
            config_file = algorithm_config.get("url")
            if not utils.is_local_file(config_file):
                raise RuntimeError(f"not found algorithm config file({config_file}) in local")

            try:
                config = utils.yaml2dict(config_file)
                algorithm = Algorithm(name, config)
                algorithms.append(algorithm)
            except Exception as err:
                raise RuntimeError(f"algorithm config file({config_file} is not supported, "
                                f"error: {err}") from err

        new_algorithms = []
        for algorithm in algorithms:
            for modules in algorithm.modules_list:
                new_algorithm = copy.deepcopy(algorithm)
                new_algorithm.modules = modules
                new_algorithms.append(new_algorithm)

        return new_algorithms
