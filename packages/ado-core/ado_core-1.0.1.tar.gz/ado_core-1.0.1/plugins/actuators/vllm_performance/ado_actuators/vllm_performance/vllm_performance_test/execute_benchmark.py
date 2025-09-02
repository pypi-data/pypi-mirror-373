# Copyright (c) IBM Corporation
# SPDX-License-Identifier: MIT

import os
import subprocess
import time
import typing
import uuid
from typing import Any

from ado_actuators.vllm_performance.vllm_performance_test.get_benchmark_results import (
    get_results,
)


def execute_benchmark(
    base_url: str,
    model: str,
    data_set: str,
    interpreter: str = "python",
    num_prompts: int = 500,
    request_rate: typing.Optional[int] = None,
    max_concurrency: typing.Optional[int] = None,
    hf_token: typing.Optional[str] = None,
    benchmark_retries: int = 3,
    retries_timeout: int = 5,
) -> dict[str, Any]:
    """
    Execute benchmark
    :param base_url: url for vllm endpoint
    :param model: model
    :param data_set: data set name ["sharegpt", "sonnet", "random", "hf"]
    :param interpreter - name of Python interpreter
    :param num_prompts: number of prompts
    :param request_rate: request rate
    :param max_concurrency: max concurrency
    :param hf_token: huggingface token
    :param benchmark_retries: number of benchmark execution retries
    :param retries_timeout: timeout between initial retry
    :return: results dictionary
    """
    print(f"executing benchmark, invoking service at {base_url} with the parameters: ")
    print(
        f"model {model}, data set {data_set}, python {interpreter}, num prompts {num_prompts}"
    )
    print(
        f"request_rate {request_rate}, max_concurrency {max_concurrency}, benchmark retries {benchmark_retries}"
    )

    # parameters
    code = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "benchmark_serving.py")
    )
    if hf_token is not None:
        request = f"export HF_TOKEN={hf_token} && "
    else:
        request = ""
    f_name = f"{uuid.uuid4().hex}.json"
    request += (
        f"{interpreter} {code} --backend openai --base-url {base_url} --dataset-name {data_set} "
        f"--model {model} --seed 12345 --num-prompts {num_prompts!s} --save-result --metric-percentiles "
        f'"25,75,99" --percentile-metrics "ttft,tpot,itl,e2el" --result-dir . --result-filename {f_name} '
    )
    if request_rate is not None:
        request += f"--request-rate {request_rate!s} "
    if max_concurrency is not None:
        request += f"--max-concurrency {max_concurrency!s}"
    timeout = retries_timeout
    for i in range(benchmark_retries):
        try:
            subprocess.check_call(request, shell=True)
            break
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            if i < benchmark_retries - 1:
                time.sleep(timeout)
                timeout *= 2
            else:
                print("Failed to execute benchmark")
                raise Exception(f"Failed to execute benchmark {e}")

    return get_results(f_name=f_name)


if __name__ == "__main__":
    results = execute_benchmark(
        interpreter="python3.10",
        base_url="https://inference-3scale-apicast-production.apps.rits.fmaas.res.ibm.com/",
        data_set="random",
        model="deepseek-ai/DeepSeek-V2.5",
        request_rate=None,
        max_concurrency=None,
        hf_token=os.getenv("HF_TOKEN"),
        num_prompts=100,
    )
    print(results)
