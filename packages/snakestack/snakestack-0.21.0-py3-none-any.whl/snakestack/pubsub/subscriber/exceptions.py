class BaseMessageError(Exception):
    """Erro genérico de processamento de mensagem."""


class AckableError(BaseMessageError):
    """Erro em que a mensagem deve ser ACKed mesmo com falha."""


class RetryableError(BaseMessageError):
    """Erro em que a mensagem deve ser NACKed para retry."""


class BlockRuleError(RetryableError):
    """Mensagem bloqueada por regra de negócio (deve ser NACKed)."""
