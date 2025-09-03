import urllib
import urllib.parse
import urllib.request
import urllib.error
import gzip


def synth(auth, file_path):
    with open(file_path, "rb") as f:
        file_contents = f.read()
        content = gzip.compress(file_contents)

    url = "{}/{}".format(auth.imandra_web_host, "api/imandra-rule-synth/synth")
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
