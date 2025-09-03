import json
import os
import os.path
from typing import Any, Dict, TypedDict
import urllib
import urllib.parse
import urllib.request
import urllib.error
import time


class Config(TypedDict):
    host: str
    headers: Dict[str, Any]


def status(config: Config, path: str, job_id):
    path = path.format(job_id)
    url = "{}/{}".format(config["host"], path)

    request = urllib.request.Request(url, headers=config["headers"])

    try:
        response = urllib.request.urlopen(request)
        resp = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))

    return json.loads(resp)["status"]


def wait(config: Config, path: str, job_id, interval):
    time.sleep(interval)
    s = status(config, path, job_id)
    if s in ["queued", "processing"]:
        return wait(config, path, job_id, interval)
    else:
        return s


def decompose(
    config: Config,
    path: str,
    file,
    model,
    testgen_lang,
    organization,
    callback,
    doc_gen,
    parent_job_id,
    lite,
):
    params_dict = {"lang": "ipl"}
    if parent_job_id is not None:
        params_dict["parent-job-id"] = parent_job_id

    if file:
        if model:
            raise ValueError(
                "Only one of `file` and `model` arguments should be provided"
            )
        with open(file, "r") as ipl_file:
            contents = ipl_file.read()
            params_dict["filename"] = os.path.basename(file)
    elif model:
        contents = model
    else:
        raise ValueError(
            "At least one of `file` and `model` arguments must be provided"
        )
    data = contents.encode("utf-8")
    if testgen_lang is not None:
        params_dict["testgen-lang"] = testgen_lang

    if doc_gen is not None:
        params_dict["doc-gen"] = doc_gen

    if organization is not None:
        params_dict["organization-id"] = organization

    if callback is not None:
        params_dict["callback"] = callback

    params_dict["lite"] = lite

    params = urllib.parse.urlencode(params_dict)
    url = "{}/{}?{}".format(config["host"], path, params)
    request = urllib.request.Request(url, data, headers=config["headers"])

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))

    job_id = response.read().decode("utf-8")
    return job_id


def data(config: Config, path: str, job_id, file=None):
    params = f"file={file}" if file is not None else ""
    path = path.format(job_id)
    path = "{}?{}".format(path, params)
    url = "{}/{}".format(config["host"], path)

    request = urllib.request.Request(url, headers=config["headers"])

    try:
        response = urllib.request.urlopen(request)
        content = response.read()
        content_type = response.headers.get("Content-Type")
        return {
            "content_type": content_type,
            "content": content,
        }
    except urllib.error.HTTPError as e:
        if e.code == 302:
            content = e.read()
            content_type = e.headers.get("Content-Type")
            return {
                "content_type": content_type,
                "content": content,
            }
        else:
            raise ValueError(e.read().decode("utf-8"))


def simulator(config: Config, zone: str, path: str, file):
    with open(file, "r") as ipl_file:
        content = ipl_file.read()
    url = "{}/{}".format(config["host"], path)

    req = {"payload": content, "cluster": zone, "version": "latest"}

    data = json.dumps(req)
    clen = len(data)
    data = data.encode("utf-8")
    headers = config["headers"].copy()
    headers["Content-Type"] = "application/json"
    headers["Content-Length"] = clen

    request = urllib.request.Request(url, data, headers=headers)

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))

    resp = json.loads(response.read())
    return resp


def list_jobs(config: Config, path: str, limit=10, job_type=None):
    path = f"{path}?limit={limit}"
    if job_type:
        path = f"{path}&job-type={job_type}"
    url = "{}/{}".format(config["host"], path)

    request = urllib.request.Request(url, headers=config["headers"])

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))

    resp = json.loads(response.read())
    return resp


def unsat_analysis(config: Config, path: str, file, model, organization, callback):
    params_dict = {"lang": "ipl"}

    if file:
        if model:
            raise ValueError(
                "Only one of `file` and `model` arguments should be provided"
            )
        with open(file, "r") as ipl_file:
            contents = ipl_file.read()
            params_dict["filename"] = os.path.basename(file)
    elif model:
        contents = model
    else:
        raise ValueError(
            "At least one of `file` and `model` arguments must be provided"
        )
    data = contents.encode("utf-8")

    if organization is not None:
        params_dict["organization-id"] = organization

    if callback is not None:
        params_dict["callback"] = callback

    params = urllib.parse.urlencode(params_dict)
    url = "{}/{}?{}".format(config["host"], path, params)
    request = urllib.request.Request(url, data, headers=config["headers"])

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))

    job_id = response.read().decode("utf-8")
    return job_id


def log_analysis_builder(
    config: Config,
    path: str,
    file,
    organization=None,
    callback=None,
    decomp_job_id=None,
):

    filename = os.path.basename(file)
    params_dict = {"filename": filename}
    with open(file, "r") as ipl_file:
        content = ipl_file.read()
        file_contents = content.encode("utf-8")

    if organization is not None:
        params_dict["organization-id"] = organization

    if callback is not None:
        params_dict["callback"] = callback

    if decomp_job_id is not None:
        params_dict["decomp-job-id"] = decomp_job_id

    params = urllib.parse.urlencode(params_dict)
    url = "{}/{}?{}".format(config["host"], path, params)
    request = urllib.request.Request(url, file_contents, headers=config["headers"])

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))

    job_id = response.read().decode("utf-8")
    return job_id


def cancel(config: Config, path: str, job_id):
    path = path.format(job_id)
    url = "{}/{}".format(config["host"], path)

    request = urllib.request.Request(
        url, headers=config["headers"], method="POST", data=None
    )

    try:
        response = urllib.request.urlopen(request)
        response.read()
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))


def validate(
    config: Config,
    path: str,
    file: str | None = None,
    model: str | None = None,
    organization: str | None = None,
):
    if file:
        if model:
            raise ValueError(
                "Only one of `file` and `model` arguments should be provided"
            )

        with open(file, "r") as ipl_file:
            contents = ipl_file.read()

    elif model:
        contents = model
    else:
        raise ValueError(
            "At least one of `file` and `model` arguments must be provided"
        )

    payload = contents.encode("utf-8")

    params_dict = {}
    if organization is not None:
        params_dict["organization-id"] = organization

    params = urllib.parse.urlencode(params_dict)
    url = "{}/{}?{}".format(config["host"], path, params)
    request = urllib.request.Request(url, payload, headers=config["headers"])

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))

    resp = json.loads(response.read())
    return resp
