import json
import os
import shutil
import urllib.request
import tempfile
from sys import platform

from .. import api
from ..api.auth import Auth
from .ipl_log_analysis import IplLogAnalysis


def install_imandra_core(args):
    if os.name == "nt":
        print(
            "Imandra Core cannot be installed on native Windows.\n\nPlease install the Imandra CLI on Windows Subsystem for Linux (WSL), and re-run this command there."
        )
        exit(1)

    with urllib.request.urlopen(
        "https://storage.googleapis.com/imandra-installer/install.sh"
    ) as fi:
        (fd, path) = tempfile.mkstemp()
        with os.fdopen(fd, "w") as fo:
            fo.write(fi.read().decode("utf-8"))

    os.execvp("sh", ["sh"] + [path])


def run_repl(auth, args):
    if shutil.which(auth.imandra_repl):
        os.execvp(auth.imandra_repl, [auth.imandra_repl] + args)
    else:
        print(
            "imandra-repl is not installed. Run: 'imandra core install' to install it."
        )


def run_ipl_log_analysis(
    auth,
    file,
    traces,
    organization,
    callback,
    interactive,
    imandra_host,
    imandra_port,
    mode,
    uuid,
    json_out,
    decomp_job_id,
    runner_image,
    skip_cache,
    sender_comp_id,
):
    imandra_port = int(imandra_port) if imandra_port is not None else None

    analysis = IplLogAnalysis(
        auth,
        file,
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
    )

    if mode == "docker":
        docker_mode = True
    elif mode == "binary":
        if platform.startswith("linux"):
            docker_mode = False
        else:
            print("Binary mode is only available on Linux.")
            return
    else:
        print(f"Unknown mode '{mode}'.")
        return

    if file is not None and not os.path.isfile(file):
        print(f"not found: {file}")
        return
    if not os.path.isdir(traces):
        print(f"not found: {traces}")
        return

    analysis.login()

    local_uuid = analysis.find_local_job() if not skip_cache else None
    if local_uuid:
        print(f"Using existing job with UUID {local_uuid} for this IPL model.")
        print(
            "Run this command with --skip-cache to force the submission of a new job.\n"
        )
        analysis.use_job(local_uuid)

        if file is not None:
            print("WARNING: ignoring --file parameter\n")
        if decomp_job_id is not None:
            print("WARNING: ignoring --decomp_job_id parameter\n")
    elif uuid is not None:
        print(f"Using provided job with UUID {uuid}")
        analysis.use_job(uuid)

        if file is not None:
            print("WARNING: ignoring --file parameter")
        if decomp_job_id is not None:
            print("WARNING: ignoring --decomp_job_id parameter")
        analysis.prepare_job_data()
    else:
        job_id = analysis.submit_job()
        print("Processing new job with UUID {}...".format(job_id))

        job_res = api.ipl.wait(auth, job_id, interval=5)
        if job_res == "done":
            print("Job ready.")
        else:
            print("Job failed.")
            return
        analysis.prepare_job_data()

    print("Starting Imandra HTTP API...")
    imandra_ready = analysis.start_imandra(10)
    if not imandra_ready:
        print("Failed to start Imandra HTTP API (timed out after 10 seconds).")
        return

    if docker_mode:
        analysis.run_docker()
    else:
        analysis.run_binary()


def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(prog="imandra", description="Imandra CLI")

    parser.set_defaults(run=lambda _: parser.print_help())
    subparsers = parser.add_subparsers()

    auth = Auth()

    parser_auth = subparsers.add_parser("auth")
    parser_auth.set_defaults(run=lambda _: parser_auth.print_help())
    parser_auth_subparsers = parser_auth.add_subparsers()

    def auth_login(_):
        auth.login()
        print("Logged in")

    parser_login = parser_auth_subparsers.add_parser("login")
    parser_login.set_defaults(run=auth_login)

    def auth_logout(_):
        auth.logout()
        print("Logged out")

    parser_logout = parser_auth_subparsers.add_parser("logout")
    parser_logout.set_defaults(run=auth_logout)

    def auth_export(_):
        print(json.dumps(auth.export()))

    parser_export = parser_auth_subparsers.add_parser("export")
    parser_export.set_defaults(run=auth_export)

    def auth_import(_):
        lines = []
        for line in sys.stdin:
            lines.append(line)

        details = json.loads("\n".join(lines))
        auth.import_(details)

    parser_import = parser_auth_subparsers.add_parser("import")
    parser_import.set_defaults(run=auth_import)

    parser_ipl = subparsers.add_parser("ipl")
    parser_ipl.set_defaults(run=lambda _: parser_ipl.print_help())
    parser_ipl_subparsers = parser_ipl.add_subparsers()

    def ipl_decompose(args):
        if args.file is not None and args.parent_job_id is not None:
            print(
                "error: --file and --parent-job-id are mutually exclusive operations. "
                "You must pick one or the other"
            )
            sys.exit(1)
        if args.file is None and args.parent_job_id is None:
            print("error: --file must be provided")

        if args.lite is not None and args.lite != "true" and args.lite != "false":
            print('error: --lite, if set, must be either "true" or "false"  ')
        else:
            auth.login()
            job_id = api.ipl.decompose(
                auth,
                args.file,
                None,  # on CLI, always use a file
                args.testgen_lang,
                args.organization,
                args.callback,
                args.doc_gen,
                args.parent_job_id,
                args.lite,
            )
            print("{}/ipl/jobs/{}".format(auth.imandra_web_host, job_id))
            if args.wait:
                status = api.ipl.wait(auth, job_id)
                print(status)

    parser_ipl_decompose = parser_ipl_subparsers.add_parser("decompose")

    parser_ipl_decompose.add_argument("--file")
    parser_ipl_decompose.add_argument("--callback")
    parser_ipl_decompose.add_argument("--testgen-lang", help=argparse.SUPPRESS)
    parser_ipl_decompose.add_argument("--organization")
    parser_ipl_decompose.add_argument(
        "--doc-gen", choices=["true", "false"], default="true"
    )
    parser_ipl_decompose.add_argument(
        "--parent-job-id",
        help=(
            "The id of a previously completed job. Instead of running a "
            "full decomposition, re-run just the script generation phase of "
            "this parent-job. When using this option all other options will be "
            "ignore and the original values from the parent-job will be used."
        ),
    )
    parser_ipl_decompose.add_argument(
        "--wait",
        action="store_true",
        help=("Block until the decomp job has finished running"),
    )
    parser_ipl_decompose.add_argument(
        "--lite",
        choices=["true", "false"],
        default="false",
        help=("Action-only, non-FIX decomposition"),
    )

    parser_ipl_decompose.set_defaults(run=ipl_decompose)

    def ipl_unsat_analysis(args):
        if args.file is None:
            print("error: --file must be provided")
        else:
            auth.login()
            job_id = api.ipl.unsat_analysis(
                auth,
                args.file,
                None,  # You must pass in as file instead of string
                args.organization,
                args.callback,
            )
            print("{}".format(job_id))

            if args.wait:
                status = api.ipl.wait(auth, job_id)
                print(status)

    parser_ipl_unsat_analysis = parser_ipl_subparsers.add_parser("unsat-analysis")

    parser_ipl_unsat_analysis.add_argument("--file")
    parser_ipl_unsat_analysis.add_argument("--callback")
    parser_ipl_unsat_analysis.add_argument("--organization")
    parser_ipl_unsat_analysis.add_argument(
        "--wait",
        action="store_true",
        help=("Block until the unsat analysis job has finished running"),
    )
    parser_ipl_unsat_analysis.set_defaults(run=ipl_unsat_analysis)

    def ipl_log_analysis(args):
        if args.file is None and args.uuid is None:
            print("error: either --file or --uuid must be provided")
        elif args.traces is None:
            print("error: --traces must be provided")
        else:
            run_ipl_log_analysis(
                auth,
                args.file,
                args.traces,
                args.organization,
                args.callback,
                args.interactive,
                args.imandra_host,
                args.imandra_port,
                args.mode,
                args.uuid,
                args.json_out,
                args.decomp_job_id,
                args.runner_image,
                args.skip_cache,
                args.sender_comp_id,
            )

    parser_ipl_log_analysis = parser_ipl_subparsers.add_parser("log-analysis")
    parser_ipl_log_analysis.add_argument("--file")
    parser_ipl_log_analysis.add_argument("--traces")
    parser_ipl_log_analysis.add_argument("--callback")
    parser_ipl_log_analysis.add_argument("--organization")
    parser_ipl_log_analysis.add_argument("--imandra_host")
    parser_ipl_log_analysis.add_argument("--imandra_port")
    parser_ipl_log_analysis.add_argument("--uuid")
    parser_ipl_log_analysis.add_argument("--json-out")
    parser_ipl_log_analysis.add_argument("--decomp-job-id")
    parser_ipl_log_analysis.add_argument("--runner-image")
    parser_ipl_log_analysis.add_argument("--sender-comp-id")
    parser_ipl_log_analysis.add_argument(
        "--interactive", choices=["true", "false"], default="false"
    )
    parser_ipl_log_analysis.add_argument(
        "--mode", choices=["docker", "binary"], default="docker"
    )
    parser_ipl_log_analysis.add_argument("--skip-cache", action="store_true")
    parser_ipl_log_analysis.set_defaults(run=ipl_log_analysis)

    def ipl_simulator(args):
        if args.file is None:
            print("error: --file must be provided")
        else:
            auth.login()
            resp = api.ipl.simulator(auth, args.file)
            urls = dict(resp["new_pod"]["urls"])
            print("Simulator available at: {}/".format(urls["http"]))

    parser_ipl_simulator = parser_ipl_subparsers.add_parser("simulator")
    parser_ipl_simulator.add_argument("--file")
    parser_ipl_simulator.set_defaults(run=ipl_simulator)

    def ipl_status(args):
        if args.uuid is None:
            print("error: --uuid must be provided")
        else:
            auth.login()
            status = api.ipl.status(auth, args.uuid)
            print(status)

    parser_ipl_status = parser_ipl_subparsers.add_parser("status")
    parser_ipl_status.add_argument("--uuid")
    parser_ipl_status.set_defaults(run=ipl_status)

    def ipl_data(args):
        if args.uuid is None:
            print("error: --uuid must be provided")
        else:
            auth.login()
            response = api.ipl.data(auth, args.uuid, args.stdout)
            data = response["content"]
            if args.stdout:
                print(data.decode("utf-8"))
            else:
                filename = args.uuid + (
                    "" if response["content_type"] == "text/plain" else ".tar.gz"
                )

                with open(filename, "wb") as data_file:
                    data_file.write(data)
                print(filename)

    parser_ipl_data = parser_ipl_subparsers.add_parser("data")
    parser_ipl_data.add_argument("--uuid")
    parser_ipl_data.add_argument("--stdout", action="store_true")
    parser_ipl_data.set_defaults(run=ipl_data)

    def ipl_validate(args):
        if args.file is None:
            print("error: --file must be provided")
            return
        auth.login()
        response = api.ipl.validate(auth, args.file)
        print(json.dumps(response, indent=4))

    parser_ipl_validate = parser_ipl_subparsers.add_parser("validate")
    parser_ipl_validate.add_argument("--file")
    parser_ipl_validate.set_defaults(run=ipl_validate)

    def ipl_list_jobs(args):
        auth.login()
        job_type = args.job_type
        resp = api.ipl.list_jobs(auth, limit=10, job_type=job_type)

        if len(resp["jobs"]) == 0:
            print("No jobs submitted yet.")
        else:
            colsfmt = "{:<36} {:<16} {:<20} {:<30} {:<30} {:<30}"
            print(
                colsfmt.format(
                    "ID", "Status", "Filename", "Submitted", "Started", "Ended"
                )
            )
            for job in resp["jobs"]:
                endTime = "-"
                if job["status"] == "cancelled":
                    endTime = job["cancelledAt"]
                elif job["status"] == "done":
                    endTime = job["completedAt"]
                elif job["status"] == "error":
                    endTime = job["failedAt"]

                filename = job["iplFile"]["filename"]
                if len(filename) > 20:
                    filename = filename[:17] + "..."

                print(
                    colsfmt.format(
                        job["id"],
                        job["status"],
                        filename,
                        job["queuedAt"],
                        job["startedAt"],
                        endTime,
                    )
                )

    parser_ipl_jobs = parser_ipl_subparsers.add_parser("list-jobs")
    parser_ipl_jobs.add_argument(
        "--job-type",
        choices=["ipl-worker", "ipl-unsat-analysis", "ipl-log-analysis-builder"],
    )
    parser_ipl_jobs.set_defaults(run=ipl_list_jobs)

    def ipl_cancel(args):
        if args.uuid is None:
            print("error: --uuid must be provided")
        else:
            auth.login()
            api.ipl.cancel(auth, args.uuid)
            print("Cancel requested for job: {}".format(args.uuid))

    parser_ipl_cancel = parser_ipl_subparsers.add_parser("cancel")
    parser_ipl_cancel.add_argument("--uuid")
    parser_ipl_cancel.set_defaults(run=ipl_cancel)

    def ipl_wait(args):
        if args.uuid is None:
            print("error: --uuid must be provided")
        else:
            auth.login()
            status = api.ipl.wait(auth, args.uuid)
            print(status)

    parser_ipl_wait = parser_ipl_subparsers.add_parser("wait")
    parser_ipl_wait.add_argument("--uuid")
    parser_ipl_wait.set_defaults(run=ipl_wait)

    parser_core = subparsers.add_parser("core")
    parser_core.set_defaults(run=lambda _: parser_core.print_help())
    parser_core_subparsers = parser_core.add_subparsers()

    parser_instances = parser_core_subparsers.add_parser("instances")
    parser_instances.set_defaults(run=lambda _: parser_instances.print_help())
    parser_instances_subparsers = parser_instances.add_subparsers()

    def instance_list(_):
        auth.login()
        instances = api.instance.list(auth)
        print("Instances: \n")
        for i in instances:
            print(" [{}] [{}] {}".format(i["assigned_at"], i["pod_type"], i["pod_id"]))

    parser_instances_list = parser_instances_subparsers.add_parser("list")
    parser_instances_list.set_defaults(run=instance_list)

    def instance_create(args):
        if args.instance_type is None:
            print("error: --instance-type must be provided")
        else:
            auth.login()
            auth.ensure_zone()
            response = api.instance.create(auth, args.version, args.instance_type)
            print("Instance created:")
            print("- url: {}".format(response["new_pod"]["url"]))
            print("- token: {}".format(response["new_pod"]["exchange_token"]))

    parser_instances_create = parser_instances_subparsers.add_parser("create")
    parser_instances_create.add_argument("--instance-type")
    parser_instances_create.add_argument("--version")
    parser_instances_create.set_defaults(run=instance_create)

    def instance_kill(args):
        if args.id is None:
            print("error: --id must be provided")
        else:
            auth.login()
            api.instance.delete(auth, args.id)
            print("Instance killed")

    parser_instances_kill = parser_instances_subparsers.add_parser("kill")
    parser_instances_kill.add_argument("--id")
    parser_instances_kill.set_defaults(run=instance_kill)

    def rule_synth(args):
        if args.file is None:
            print("error: --file must be provided")
        else:
            auth.login()
            response = api.rule_synth.synth(auth, args.file)
            print(response)

    parser_rule_synth = subparsers.add_parser("rule-synth")
    parser_rule_synth.set_defaults(run=lambda _: parser_rule_synth.print_help())
    parser_rule_synth_subparsers = parser_rule_synth.add_subparsers()

    parser_synth = parser_rule_synth_subparsers.add_parser("synth")
    parser_synth.add_argument("--file")
    parser_synth.set_defaults(run=rule_synth)

    def cfb_analyze(args):
        if args.job is None:
            print("error: --job must be provided")
        elif args.path is None:
            print("error: --path must be provided")
        else:
            auth.login()
            response = api.cfb.analyze(auth, args.job, args.path)
            print(response)

    parser_cfb = subparsers.add_parser("cfb")
    parser_cfb.set_defaults(run=lambda _: parser_cfb.print_help())
    parser_cfb_subparsers = parser_cfb.add_subparsers()

    parser_cfb_analyze = parser_cfb_subparsers.add_parser("analyze")
    parser_cfb_analyze.add_argument("--job")
    parser_cfb_analyze.add_argument("--path")
    parser_cfb_analyze.set_defaults(run=cfb_analyze)

    def repl(args):
        run_repl(auth, args.args)

    parser_repl = parser_core_subparsers.add_parser("repl")
    parser_repl.add_argument("args", nargs=argparse.REMAINDER)
    parser_repl.set_defaults(run=repl)

    parser_install = parser_core_subparsers.add_parser("install")
    parser_install.set_defaults(run=install_imandra_core)

    if len(sys.argv) > 2 and sys.argv[1] == "core" and sys.argv[2] == "repl":
        # Run this directly so we can pass --help directly to the repl command to see its own help text
        run_repl(auth, sys.argv[3:])
    else:
        args = parser.parse_args()
        args.run(args)
