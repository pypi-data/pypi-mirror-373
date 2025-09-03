import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Literal, Union

import fused._global_api
from fused._optional_deps import HAS_PANDAS
from fused.api import FusedAPI
from fused.models.udf.udf import Udf


def invoke_lite(api: FusedAPI, function_name, payload, seq):
    t0 = time.perf_counter()

    try:
        response = api._run_lite(function_name, payload)
        dur = time.perf_counter() - t0
        return response, dur, seq
    except Exception as exc:
        dur = time.perf_counter() - t0
        return [f"ERR: {str(exc)}"] * len(payload), dur, seq


def lite_batch(
    url_or_udf: Union[str, Path, Udf],
    batch_size: int,
    arg_list: list[dict],
    processor: Literal["duckdb", "pandas"] = "pandas",
):
    """Main function to run the batch invocation.

    Args:
        url_or_udf: A UDF identifier, name, token, url or UDF object. If not a UDF object use `fused.load` to fetch it.
        batch_size: Payload size sent to each invocation
        arg_list: A list of input parameters for the UDF specified as a list of dictionaries.
        processor: Main executor to run the UDF

    Example:
        >>> import fused
        >>> from fused._lite import lite_batch
        >>> @fused.udf
        >>> def udf(x):
        >>>     import time
        >>>     time.sleep(0.5)
        >>>     return x
        >>> lite_batch(code, 20, [{"x": i} for i in range(200)])


    """
    invocations = math.ceil(len(arg_list) / batch_size)
    max_workers = invocations
    item_count = len(arg_list)
    processor_name = f"fused-lite-poc-{processor}"

    try:
        if isinstance(url_or_udf, Udf):
            udf = url_or_udf
        else:
            udf = fused.load(url_or_udf)

        lines = udf.code.split("\n")
        # TODO: Possibly install fused on the processor
        filtered_lines = [
            line for line in lines if not line.lstrip().startswith("@fused.udf")
        ]

        code = "\n".join(filtered_lines)

        payload_list = []
        # Add python code to be sent to processor
        # TODO: Update request format
        for i, d in enumerate(arg_list):
            if not isinstance(d, dict):
                raise TypeError(
                    f"Error: Payload item {i + 1} must be a dict, got {type(d).__name__}"
                )
            d["python_code"] = code

            # Create nested structure for each payload
            # TODO: udf_name is currently unused in nested structure
            nested_payload = {"udf_name": "", "udf_kwargs": d}
            payload_list.append(nested_payload)

        batch_start = 0
        batch_payloads = []
        for batch_num in range(1, invocations + 1):
            batch_payload = payload_list[batch_start : batch_start + batch_size]

            # udf_name in outer structure is used to indicate processor
            # TODO: Update request format
            payload_data = {
                "udf_name": processor_name,
                "udf_kwargs": {"payloads": batch_payload},
            }
            batch_payloads.append(payload_data)
            batch_start += batch_size

    except json.JSONDecodeError as e:
        raise ValueError(f"Error: Invalid JSON in payload: {e}")
    except Exception as e:
        raise ValueError(f"Error processing payloads: {e}")

    # Execute all invocations concurrently
    results = []
    api = fused._global_api.get_api()
    with ThreadPoolExecutor(max_workers=max_workers) as exe:
        start = time.perf_counter()

        fut_to_seq = {
            exe.submit(
                invoke_lite, api, "fused-lite-poc-async", batch_payloads[seq - 1], seq
            ): seq
            for seq in range(1, max_workers + 1)
        }

        for fut in as_completed(fut_to_seq):
            results.append(fut.result())

    total_time = time.perf_counter() - start

    successful = 0
    parsed_results = []
    notified_error = False
    for batch_result_list, dur, seq in results:
        for r in batch_result_list:
            if isinstance(r, dict) and r["success"]:
                parsed_result = r["response_payload"]
                successful += 1
            elif isinstance(r, str):
                parsed_result = {"success": False, "body": r}
            else:
                parsed_result = {"success": False, "body": r["error"]}

            parsed_result["batch"] = seq
            parsed_result["duration"] = dur
            parsed_result["function_name"] = processor_name

            parsed_results.append(parsed_result)

            if not notified_error and not parsed_result["success"]:
                print("An error occurred in one or more results", file=sys.stderr)
                notified_error = True

    parsed_results.sort(key=lambda r: (r["success"], r["batch"]))
    failed = len(payload_list) - successful
    throughput = item_count / total_time

    print(f"{successful}/{item_count} succeeded, {failed} failed")
    print(f"Batch size: {batch_size} per worker")
    print(f"Workers: {max_workers}")
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {throughput:.1f} invocations/second")

    return create_results_dataframe(parsed_results)


def create_results_dataframe(results):
    """Create a pandas DataFrame from results."""
    # TODO: Provide alternatives if pandas not available
    if not HAS_PANDAS:
        raise ImportError("pandas is required to use this method")

    import pandas as pd

    if not results:
        return pd.DataFrame()

    df_data = []
    for result in results:
        df_data.append(
            {
                "batch_num": result["batch"],
                "duration_seconds": result["duration"],
                "response": result["body"],
                "success": result["success"],
                "function_name": result["function_name"],
            }
        )

    results_df = pd.DataFrame(df_data)

    # Add some derived columns
    if len(results_df) > 0:
        results_df["duration_ms"] = results_df["duration_seconds"] * 1000
        results_df["rank_by_duration"] = results_df["duration_seconds"].rank(
            ascending=False
        )

    return results_df
