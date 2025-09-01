# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
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

import importlib
import logging
import pkgutil
import time

import requests

logger = logging.getLogger(__name__)


def check_health(health_url: str, max_retries: int = 600, retry_interval: int = 2) -> bool:
    """
    Check the health of the PyTriton (via FAstAPI) and Ray server.
    """
    for _ in range(max_retries):
        try:
            response = requests.get(health_url)
            if response.status_code == 200:
                return True
            logger.info(f"Server replied with status code: {response.status_code}")
            time.sleep(retry_interval)
        except requests.exceptions.RequestException:
            logger.info("Server is not ready")
            time.sleep(retry_interval)
    return False


def check_endpoint(
    endpoint_url: str, endpoint_type: str, model_name: str, max_retries: int = 600, retry_interval: int = 2
) -> bool:
    """
    Check if the endpoint is responsive and ready to accept requests.
    """
    payload = {"model": model_name, "max_tokens": 1}
    if endpoint_type == "completions":
        payload["prompt"] = "hello"
    elif endpoint_type == "chat":
        payload["messages"] = [{"role": "user", "content": "hello"}]
    else:
        raise ValueError(f"Invalid endpoint type: {endpoint_type}")

    for _ in range(max_retries):
        try:
            response = requests.post(endpoint_url, json=payload)
            if response.status_code == 200:
                return True
            logger.info(f"Server replied with status code: {response.status_code}")
            time.sleep(retry_interval)
        except requests.exceptions.RequestException:
            logger.info("Server is not ready")
            time.sleep(retry_interval)
    return False


def wait_for_fastapi_server(
    base_url: str = "http://0.0.0.0:8080",
    model_name: str = "megatron_model",
    max_retries: int = 600,
    retry_interval: int = 10,
):
    """
    Wait for FastAPI server and model to be ready.

    Args:
        base_url (str): The URL to the FastAPI server (e.g., "http://0.0.0.0:8080").
        model_name (str): The name of the deployed model.
        max_retries (int): Maximum number of retries before giving up.
        retry_interval (int): Time in seconds to wait between retries.

    Returns:
        bool: True if both the server and model are ready within the retries, False otherwise.
    """

    completions_url = f"{base_url}/v1/completions/"
    health_url = f"{base_url}/v1/triton_health"

    logger.info("Checking server and model readiness...")
    if not check_health(health_url, max_retries, retry_interval):
        logger.info("Server is not ready.")
        return False
    if not check_endpoint(completions_url, "completions", model_name, max_retries, retry_interval):
        logger.info("Model is not ready.")
        return False
    logger.info("Server and model are ready.")
    return True


def _iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def list_available_evaluations() -> dict[str, list[str]]:
    """
    Finds all pre-defined evaluation configs across all installed evaluation frameworks.

    Returns:
        dict[str, list[str]]: Dictionary of available evaluations, where key is evaluation
            framework and value is list of available tasks.
    """
    # this import can be moved outside of this function when NeMoFWLMEval is
    # removed and we completed switch to NVIDIA Evals Factory
    try:
        import core_evals
    except ImportError:
        raise ImportError("Please ensure that core_evals is installed in your env as it is required to run evaluations")
    discovered_modules = {
        name: importlib.import_module(".input", package=name) for finder, name, ispkg in _iter_namespace(core_evals)
    }

    evals = {}
    for framework_name, input_module in discovered_modules.items():
        # sanity check - it shouldn't be possible to find framework that is not a submodule of core_evals
        if not framework_name.startswith("core_evals."):
            raise RuntimeError(f"Framework {framework_name} is not a submodule of core_evals")
        _, task_name_mapping, *_ = input_module.get_available_evaluations()
        evals[framework_name] = list(task_name_mapping.keys())
    return evals


def find_framework(eval_task: str) -> str:
    """
    Find framework for executing the evaluation eval_task.

    This function searches for framework (module) that defines a task with given name and returns the framework name.
    """
    evals = list_available_evaluations()
    frameworks = [f for f, tasks in evals.items() if eval_task in tasks]

    if len(frameworks) == 0:
        raise ValueError(f"Framework for task {eval_task} not found!")
    elif len(frameworks) > 1:
        frameworks_names = [f[len("core_evals.") :].replace("_", "-") for f in frameworks]
        raise ValueError(
            f"Multiple frameworks found for task {eval_task}: {frameworks_names}. "
            "Please indicate which version should be used by passing <framework>.<task>"
        )
    return frameworks[0]
