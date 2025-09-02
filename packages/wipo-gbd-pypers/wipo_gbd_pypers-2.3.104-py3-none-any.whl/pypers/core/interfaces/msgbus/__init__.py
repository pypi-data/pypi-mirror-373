from .sqs import SQS

_sqs = None
_publishing = None

def get_msg_bus():
    global _sqs
    if _sqs is None:
        _sqs = SQS()
    return _sqs
