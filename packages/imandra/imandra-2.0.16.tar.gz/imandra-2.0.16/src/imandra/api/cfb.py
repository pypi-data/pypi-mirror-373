import urllib
import urllib.request
import urllib.error
import urllib.parse
import json
import gzip
import io
import tarfile
import base64


def analyze(auth, job_file, path):
    with open(job_file, "r") as f:
        job_file_contents = f.read()

    bytes_io = io.BytesIO()
    tf = tarfile.open(mode="w", fileobj=bytes_io)
    tf.add(path, arcname="")

    b64_bytes = base64.b64encode(bytes_io.getvalue())
    b64_string = b64_bytes.decode("ascii")

    payload = {"job": job_file_contents, "pathTarArchiveBase64": b64_string}

    json_str = json.dumps(payload)
    json_bytes = json_str.encode("utf-8")

    content = gzip.compress(json_bytes)

    url = "{}/{}".format(auth.imandra_web_host, "api/imandra-cfb/analyze")

    clen = len(content)
    headers = {
        "X-Auth": auth.token,
        "Content-Length": clen,
        "Content-Encoding": "gzip",
        "Accept-Encoding": "gzip",
    }
    request = urllib.request.Request(url, content, headers=headers)

    try:
        with urllib.request.urlopen(request) as response:
            if response.headers["content-encoding"] == "gzip":
                return gzip.decompress(response.read()).decode("utf-8")
            else:
                return response.read().decode("utf-8")

    except urllib.error.HTTPError as e:
        raise ValueError(e.read().decode("utf-8"))
