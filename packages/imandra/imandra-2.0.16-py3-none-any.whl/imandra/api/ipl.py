from . import ipl_common


def _mk_config(auth) -> ipl_common.Config:
    return {
        "host": auth.imandra_web_host,
        "headers": {"X-Auth": auth.token},
    }


def status(auth, job_id):
    config = _mk_config(auth)
    path = "api/ipl/jobs/{}/status"
    return ipl_common.status(config, path, job_id)


def wait(auth, job_id, interval=10):
    config = _mk_config(auth)
    path = "api/ipl/jobs/{}/status"
    return ipl_common.wait(config, path, job_id, interval)


def decompose(
    auth,
    file,
    model,
    testgen_lang,
    organization,
    callback,
    doc_gen,
    parent_job_id,
    lite,
):
    config = _mk_config(auth)
    path = "api/ipl/jobs"
    return ipl_common.decompose(
        config,
        path,
        file,
        model,
        testgen_lang,
        organization,
        callback,
        doc_gen,
        parent_job_id,
        lite,
    )


def data(auth, job_id, file=None):
    config = _mk_config(auth)
    path = "api/ipl/jobs/{}/data"
    return ipl_common.data(config, path, job_id, file)


def validate(auth, file):
    config = _mk_config(auth)
    path = "api/ipl/validate"
    return ipl_common.validate(config, path, file)


def simulator(auth, file):
    config = _mk_config(auth)
    path = "simulator/create"
    return ipl_common.simulator(config, auth.zone, path, file)


def list_jobs(auth, limit=10, job_type=None):
    config = _mk_config(auth)
    path = "api/ipl/jobs"
    return ipl_common.list_jobs(config, path, limit, job_type)


def unsat_analysis(auth, file, model, organization, callback):
    config = _mk_config(auth)
    path = "api/ipl-unsat-analysis/jobs"
    return ipl_common.unsat_analysis(config, path, file, model, organization, callback)


def log_analysis_builder(
    auth, file, organization=None, callback=None, decomp_job_id=None
):
    config = _mk_config(auth)
    path = "api/ipl-log-analysis-builder/jobs"
    return ipl_common.log_analysis_builder(
        config, path, file, organization, callback, decomp_job_id
    )


def cancel(auth, job_id):
    config = _mk_config(auth)
    path = "api/ipl/jobs/{}/cancel"
    return ipl_common.cancel(config, path, job_id)
