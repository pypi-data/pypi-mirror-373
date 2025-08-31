# from .aws_chaos import AWSChaosTemplate
from chaos.dns_chaos import DNSChaosTemplate
from chaos.io_chaos import IOChaosTemplate
from chaos.network_chaos import NetworkChaosTemplate
from chaos.pod_chaos import PodChaosTemplate
from chaos.stress_chaos import StressChaosTemplate
from chaos.time_chaos import TimeChaosTemplate

TEMPLATES = {
    "pod_chaos": PodChaosTemplate(),
    "network_chaos": NetworkChaosTemplate(),
    "stress_chaos": StressChaosTemplate(),
    "io_chaos": IOChaosTemplate(),
    "dns_chaos": DNSChaosTemplate(),
    "time_chaos": TimeChaosTemplate(),
    # "aws_chaos": AWSChaosTemplate(),
}


def get_template(experiment_type: str):
    """Template retrieval"""
    return TEMPLATES.get(experiment_type)


def list_templates():
    """Eligible template list"""
    return list(TEMPLATES.keys())
