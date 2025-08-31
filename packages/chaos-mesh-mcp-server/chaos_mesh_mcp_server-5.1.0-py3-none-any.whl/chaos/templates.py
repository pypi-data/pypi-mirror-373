# from aws_chaos import AWSChaosTemplate
from dns_chaos import DNSChaosTemplate
from io_chaos import IOChaosTemplate
from network_chaos import NetworkChaosTemplate
from pod_chaos import PodChaosTemplate
from stress_chaos import StressChaosTemplate
from time_chaos import TimeChaosTemplate

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
