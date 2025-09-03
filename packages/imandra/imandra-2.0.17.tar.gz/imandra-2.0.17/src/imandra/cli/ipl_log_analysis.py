import subprocess
import atexit
import signal
import os
import os.path
import urllib
import urllib.parse
import urllib.request
import urllib.error
import tarfile
from pathlib import Path
import sys
import time
import socket
import ipaddress
import shutil
import filecmp

from .. import api


# https://stackoverflow.com/a/47919356/4956000
def is_loopback(host):
    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            r = socket.getaddrinfo(host, None, family, socket.SOCK_STREAM)
        except socket.gaierror:
            return False
        for family, _, _, _, sockaddr in r:
            if not ipaddress.ip_address(sockaddr[0]).is_loopback:
                return False
    return True


def check_imandra_ready(port, timeout):
    request = urllib.request.Request(f"http://localhost:{port}/status")
    for x in range(timeout):
        time.sleep(1)
        try:
            response = urllib.request.urlopen(request)
            if response.read().decode("UTF-8") == "OK":
                return True
        except:
            pass
    return False


class IplLogAnalysis:
    def __init__(
        self,
        auth,
        ipl_file,
        traces,
        organization,
        callback,
        interactive,
        imandra_host,
        imandra_port,
        json_out,
        decomp_job_id,
        runner_image,
        sender_comp_id,
    ):
        self._auth = auth
        self._ipl_file = ipl_file
        self._traces_dir = Path(traces).absolute()
        self._organization = organization
        self._callback = callback
        self._interactive = interactive == "true"
        self._imandra_host = imandra_host
        self._imandra_port = imandra_port
        self._json_out = Path(json_out).absolute() if json_out is not None else None
        self._decomp_job_id = decomp_job_id
        self._runner_image = runner_image
        self._sender_comp_id = sender_comp_id

    def login(self):
        self._auth.login()

    def _start_imandra(self, timeout):
        self._imandra_host = "localhost"
        self._imandra_port = 3000
        args = [
            "imandra-http-api",
            "--skip-update",
            "--dir",
            self.job_model_path(),
        ]
        imandra_proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        imandra_pid = imandra_proc.pid

        def kill_imandra():
            os.kill(imandra_pid, signal.SIGTERM)

        atexit.register(kill_imandra)
        self._imandra_proc = imandra_proc
        self._imandra_pid = imandra_pid

        return check_imandra_ready(self._imandra_port, timeout)

    def start_imandra(self, timeout):
        if self._imandra_host is not None or self._imandra_port is not None:
            self._imandra_host = (
                self._imandra_host if self._imandra_host is not None else "localhost"
            )
            self._imandra_port = (
                self._imandra_port if self._imandra_port is not None else 3000
            )
            return True
        else:
            return self._start_imandra(timeout)

    def submit_job(self):
        job_id = api.ipl.log_analysis_builder(
            self._auth,
            self._ipl_file,
            self._organization,
            self._callback,
            self._decomp_job_id,
        )
        self._job_id = job_id
        return job_id

    def use_job(self, uuid):
        self._job_id = uuid

    def data_dir(self):
        return os.path.join(self._auth.folder_path, "data")

    def job_data_dir(self):
        return os.path.join(self.data_dir(), self._job_id)

    def find_local_job(self):
        if not self._ipl_file:
            return None

        data_dir = self.data_dir()

        def is_candidate(p):
            return os.path.isdir(
                os.path.join(data_dir, p, "lib", "ipl-log-analysis")
            ) and os.path.isfile(os.path.join(data_dir, p, "model.ipl"))

        job_dirs = list(
            filter(
                is_candidate,
                os.listdir(data_dir),
            )
        )

        for d in job_dirs:
            model_file = os.path.join(data_dir, d, "model.ipl")
            if filecmp.cmp(model_file, self._ipl_file):
                return d

        return None

    def job_archive_path(self):
        return os.path.join(self.data_dir(), "{}.{}".format(self._job_id, "tar.gz"))

    def job_model_path(self):
        return os.path.join(self.job_data_dir(), "ipl", "gen", "model")

    def prepare_job_data(self):
        data_dir = self.data_dir()

        if not os.path.exists(data_dir):
            print(f"Creating directory {data_dir}...")
            os.mkdir(data_dir)

        job_archive_path = self.job_archive_path()
        if not os.path.exists(job_archive_path):
            response = api.ipl.data(self._auth, self._job_id)
            with open(job_archive_path, "wb") as data_file:
                data_file.write(response["content"])

        job_data_dir = self.job_data_dir()
        if not os.path.exists(job_data_dir):
            print(f"Extracting job data in {job_data_dir}...")
            os.mkdir(job_data_dir)

            tar = tarfile.open(job_archive_path, "r:gz")
            tar.extractall(job_data_dir)
            tar.close()

            response = api.ipl.data(self._auth, self._job_id, file="version")
            with open(f"{job_data_dir}/version", "wb") as version_file:
                version_file.write(response["content"])

            ipl_file_copy = os.path.join(job_data_dir, "model.ipl")
            shutil.copyfile(src=self._ipl_file, dst=ipl_file_copy)

    def fetch_runner_binary(self, version):
        runner_dir = os.path.join(self.data_dir(), "log_analysis_runner")
        if not os.path.exists(runner_dir):
            os.mkdir(runner_dir)

        runner_filename = f"runner-static-bytecode-linux-{version}.tar.gz"
        runner_path = os.path.join(runner_dir, runner_filename)
        url = f"https://storage.googleapis.com/ipl-log-analysis-releases/{runner_filename}"

        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        content = response.read()

        with open(runner_path, "wb") as data_file:
            data_file.write(content)

        return runner_path

    def run_binary(self):
        job_data_dir = self.job_data_dir()

        with open(os.path.join(job_data_dir, "version"), "r") as version_file:
            job_runner_version = version_file.read().strip()

        try:
            runner_path = self.fetch_runner_binary(job_runner_version)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(
                    f"WARNING: runner binary version {job_runner_version} not found. Using latest version..."
                )
                runner_path = self.fetch_runner_binary("latest")
            else:
                raise ValueError(e.read().decode("utf-8"))

        print("Extracting runner binary...")
        runner_tar = tarfile.open(runner_path, "r:gz")
        runner_tar.extractall(job_data_dir)
        runner_tar.close()

        installed_runner_path = os.path.join(job_data_dir, "bin", "ipl_log_analysis")
        run_args = [
            f"--imandra-port={self._imandra_port}",
            "--fix-traces",
            self._traces_dir,
        ]

        if self._interactive:
            run_args.append("--interactive=true")

        if self._json_out:
            run_args.append(f"--json-out={self._json_out}")

        if self._sender_comp_id:
            run_args.append(f"--sender-comp-id={self._sender_comp_id}")

        run_args.append(f"--imandra-host={self._imandra_host}")

        run_cmd = [installed_runner_path] + run_args
        self.run_analysis_process(run_cmd)

    def runner_image(self):
        if self._runner_image:
            print(f"Using runner image {self._runner_image}...")
            return self._runner_image
        else:
            env = os.getenv("IMANDRA_ENV", "prod")
            if env == "dev":
                runner_image = "europe-west1-docker.pkg.dev/imandra-dev/imandra/ipl-log-analysis-runner"
            else:
                runner_image = "imandra/ipl-log-analysis-runner"

            with open(
                os.path.join(self.job_data_dir(), "version"), "r"
            ) as version_file:
                job_runner_version = version_file.read().strip()
            tagged_runner_image = f"{runner_image}:{job_runner_version}"
            pull_p = subprocess.run(
                ["docker", "pull", tagged_runner_image],
                stdout=sys.stdout,
                stderr=subprocess.STDOUT,
            )
            if pull_p.returncode != 0:
                print(
                    f"WARNING: runner image {runner_image} with tag {job_runner_version} not found. Using latest version..."
                )
                tagged_runner_image = f"{runner_image}:latest"
                pull_p = subprocess.run(
                    ["docker", "pull", tagged_runner_image],
                    stdout=sys.stdout,
                    stderr=subprocess.STDOUT,
                )
                if pull_p.returncode != 0:
                    print("Failed to pull runner image")
                    return None
            return tagged_runner_image

    def run_docker(self):
        try:
            subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL)
        except FileNotFoundError as e:
            print(e)
            return

        runner_image = self.runner_image()
        if runner_image is None:
            sys.exit(1)

        runner_args_list = [
            f"--imandra-port={self._imandra_port}",
            "--fix-traces ../traces",
        ]
        if self._interactive:
            runner_args_list.append("--interactive true")

        if self._json_out is not None:
            runner_args_list.append("--json-out=out.json")

        if self._sender_comp_id:
            runner_args_list.append(f"--sender-comp-id={self._sender_comp_id}")

        if not is_loopback(self._imandra_host):
            runner_args_list.append(f"--imandra-host={self._imandra_host}")
        else:
            runner_args_list.append("--imandra-host=host.docker.internal")

        runner_args = " ".join(runner_args_list)
        runner_script = f"cd ipl-log-analysis && sudo tar zxf plugin.tar.gz && ./bin/ipl_log_analysis {runner_args}"

        if self._json_out is not None:
            # --json-out needs output file to exist
            os.close(os.open(self._json_out, os.O_CREAT))
            runner_script = "touch ipl-log-analysis/out.json && " + runner_script

        mount_points = [
            "-v",
            f"{self.job_archive_path()}:/home/ocaml/ipl-log-analysis/plugin.tar.gz",
            "-v",
            f"{self._traces_dir}:/home/ocaml/traces",
        ]
        if self._json_out is not None:
            mount_points = mount_points + [
                "-v",
                f"{self._json_out}:/home/ocaml/ipl-log-analysis/out.json",
            ]

        docker_args = mount_points + [
            "--platform=linux/amd64",
            "--rm",
            runner_image,
            "sh",
            "-uexc",
            runner_script,
        ]

        if self._interactive:
            docker_cmd = ["docker", "run"] + ["-i"] + docker_args
        else:
            docker_cmd = ["docker", "run"] + docker_args

        self.run_analysis_process(docker_cmd)

    def run_analysis_process(self, cmd):
        input_buffer = sys.stdin
        output_buffer = sys.stdout
        proc = subprocess.Popen(
            cmd,
            encoding="utf-8",
            stdin=subprocess.PIPE,
            stdout=output_buffer,
            universal_newlines=True,
            stderr=subprocess.STDOUT,
        )

        if self._interactive:
            while True:
                try:
                    inpt = input_buffer.readline()
                    print(inpt, file=proc.stdin, flush=True)
                except BrokenPipeError:
                    return
        else:
            while proc.poll() is None:
                time.sleep(0.5)
