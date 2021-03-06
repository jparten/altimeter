#!/usr/bin/env python3
"""Run a query against the latest graph for a given name and optional version.
Run as a lambda this calls Neptune.
Run from the command line this finds the runquery lambda, sends a query to it and
reads the results from S3.
"""
import hashlib
import json
import sys
import time

import boto3

from altimeter.core.awslambda import get_required_lambda_env_var, get_required_lambda_event_var
from altimeter.core.neptune.client import AltimeterNeptuneClient, NeptuneEndpoint


def lambda_handler(event, context):
    graph_names_list = get_required_lambda_event_var(event, "graph_names")
    if not isinstance(graph_names_list, list):
        raise ValueError(f"Value for graph_names should be a list. Is {type(graph_names_list)}")
    graph_names = set(graph_names_list)
    query = get_required_lambda_event_var(event, "query")
    if not isinstance(query, str):
        raise ValueError(f"Value for query should be a str. Is {type(query)}")
    max_age_min = get_required_lambda_event_var(event, "max_age_min")
    if not isinstance(max_age_min, int):
        raise ValueError(f"Value for max_age_min should be an int. Is {type(max_age_min)}")

    host = get_required_lambda_env_var("NEPTUNE_HOST")
    port = get_required_lambda_env_var("NEPTUNE_PORT")
    region = get_required_lambda_env_var("NEPTUNE_REGION")
    results_bucket = get_required_lambda_env_var("RESULTS_BUCKET")

    endpoint = NeptuneEndpoint(host=host, port=port, region=region)
    client = AltimeterNeptuneClient(max_age_min=max_age_min, neptune_endpoint=endpoint)
    query_result = client.run_query(graph_names=graph_names, query=query)

    csv_results = query_result.to_csv()

    query_hash = hashlib.sha256(query.encode()).hexdigest()
    now_str = str(int(time.time()))
    results_key = "/".join(("-".join(graph_names), query_hash, f"{now_str}.csv"))
    s3_client = boto3.Session().client("s3")
    s3_client.put_object(Bucket=results_bucket, Key=results_key, Body=csv_results)

    return {
        "results_bucket": results_bucket,
        "results_key": results_key,
        "num_results": query_result.get_length(),
    }


def get_runquery_lambda_name():
    runquery_lambda_name_prefix = "ITCloudGraph-RunQuery-"
    lambda_client = boto3.client("lambda")
    paginator = lambda_client.get_paginator("list_functions")
    for resp in paginator.paginate():
        for func in resp["Functions"]:
            if func["FunctionName"].startswith(runquery_lambda_name_prefix):
                return func["FunctionName"]
    raise ValueError(
        (
            f"Unable to find a runquery lambda with name starting with "
            f"{runquery_lambda_name_prefix}"
        )
    )


def main(argv=None):
    import argparse

    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("query_file", type=str)
    parser.add_argument("--graph_names", type=str, default=["alti"], nargs="+")
    parser.add_argument("--max_age_min", type=int, default=1440)
    args_ns = parser.parse_args(argv)

    with open(args_ns.query_file, "r") as query_fp:
        query = query_fp.read()

    runquery_lambda_name = get_runquery_lambda_name()

    payload = {
        "graph_names": args_ns.graph_names,
        "max_age_min": args_ns.max_age_min,
        "query": query,
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    lambda_client = boto3.client("lambda")
    invoke_lambda_resp = lambda_client.invoke(
        FunctionName=runquery_lambda_name, Payload=payload_bytes
    )
    lambda_resp_bytes = invoke_lambda_resp["Payload"].read()
    lambda_resp_str = lambda_resp_bytes.decode("utf-8")
    lambda_resp = json.loads(lambda_resp_str)
    if "errorMessage" in lambda_resp:
        print("Error running query:")
        print(lambda_resp["errorMessage"])
        sys.exit(1)
    results_bucket = lambda_resp["results_bucket"]
    results_key = lambda_resp["results_key"]
    s3_client = boto3.client("s3")
    s3_resp = s3_client.get_object(Bucket=results_bucket, Key=results_key)
    results_bytes = s3_resp["Body"].read()
    results_str = results_bytes.decode("utf-8")
    print(results_str)


if __name__ == "__main__":
    sys.exit(main())
