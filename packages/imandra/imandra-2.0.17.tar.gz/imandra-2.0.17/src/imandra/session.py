from .api import auth, instance
import imandra_http_api_client

from imandra_http_api_client.models import WithUnknownReasonBody, UpToBody
from imandra_http_api_client.models import InstanceResponse, InstanceResult
from imandra_http_api_client.models import VerifyResponse, VerifyResult


def instance_monkey_str(self):
    if self.type == InstanceResult.SAT:
        src = self.body.actual_instance.instance.model.src
        return "Instance found:\n{}".format(src.strip())
    elif self.type == InstanceResult.UNSAT:
        return "Unsatisfiable"
    elif self.type == InstanceResult.UNSAT_UPTO:
        steps = self.body.actual_instance.steps
        return "Unsatisfiable upto {}".format(steps)
    elif self.type == InstanceResult.UNKNOWN:
        instance = self.body.actual_instance
        if instance.__class__ == WithUnknownReasonBody:
            reason = instance.unknown_reason
            return "Unknown: {}".format(reason.strip())
        elif instance.__class__ == UpToBody:
            steps = instance.steps
            return "Unknown: Searched Up To {}".format(steps)
        return "Unknown"


def verify_monkey_str(self):
    if self.type == VerifyResult.REFUTED:
        src = self.body.actual_instance.instance.model.src
        return "Refuted, with counterexample:\n{}".format(src.strip())
    elif self.type == VerifyResult.PROVED:
        return "Proved"
    elif self.type == VerifyResult.PROVED_UPTO:
        steps = self.body.actual_instance.steps
        return "Proved upto {}".format(steps)
    elif self.type == VerifyResult.UNKNOWN:
        instance = self.body.actual_instance
        if instance.__class__ == WithUnknownReasonBody:
            reason = instance.unknown_reason
            return "Unknown: {}".format(reason.strip())
        elif instance.__class__ == UpToBody:
            steps = instance.steps
            return "Unknown: Verified Up To {}".format(steps)
        return "Unknown"


InstanceResponse.__str__ = instance_monkey_str  # type: ignore
VerifyResponse.__str__ = verify_monkey_str  # type: ignore


class HttpInstanceSession:
    def __init__(self):
        self.auth = auth.Auth()
        self.instance_ = instance.create(self.auth, None, "imandra-http-api")

        config = imandra_http_api_client.Configuration(
            host=self.instance_["new_pod"]["url"],
            access_token=self.instance_["new_pod"]["exchange_token"],
        )

        self.api_client = imandra_http_api_client.ApiClient(config)
        self.api_instance = imandra_http_api_client.DefaultApi(self.api_client)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        instance.delete(self.auth, self.instance_["new_pod"]["id"])

    def get_history(self):
        return self.api_instance.get_history()

    def reset(self):
        return self.api_instance.reset()

    def eval(self, src, **args):
        eval_request_src = imandra_http_api_client.EvalRequestSrc(src=src, **args)
        try:
            return self.api_instance.eval(eval_request_src)
        except Exception as err:
            return err

    def verify(self, src, **args):
        verify_request_src = imandra_http_api_client.VerifyRequestSrc(src=src, **args)
        return self.api_instance.verify_by_src(verify_request_src)

    def instance(self, src, **args):
        instance_request_src = imandra_http_api_client.InstanceRequestSrc(
            src=src, **args
        )
        return self.api_instance.instance_by_src(instance_request_src)

    def decompose(self, name, **args):
        decompose_request = imandra_http_api_client.DecomposeRequestSrc(
            name=name, **args
        )
        return self.api_instance.decompose(decompose_request)
