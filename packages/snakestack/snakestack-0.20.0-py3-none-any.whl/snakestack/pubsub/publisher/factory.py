from typing import Self

try:
    from google.api_core.retry import Retry
    from google.cloud.pubsub_v1 import PublisherClient
    from google.cloud.pubsub_v1.types import (
        BatchSettings,
        LimitExceededBehavior,
        PublisherOptions,
        PublishFlowControl,
    )
except ImportError:
    raise RuntimeError("Pubsub extra is not installed. Run `pip install snakestack[pubsub]`.")

from snakestack import constants


class PubSubPublisherFactory:

    def __init__(self: Self, enable_open_telemetry: bool = False) -> None:
        self.enable_open_telemetry = enable_open_telemetry

    def create(
        self: Self,
        batch_settings: "BatchSettings",
        publisher_options: "PublisherOptions"
    ) -> PublisherClient:
        return PublisherClient(
            batch_settings=batch_settings,
            publisher_options=publisher_options,
        )

    def low_latency(self: Self) -> PublisherClient:
        """
        Cria um publisher otimizado para baixa latência.

        Ideal para eventos críticos que exigem envio quase imediato,
        como auditoria, billing ou notificações sensíveis ao tempo.

        Configurações:
        - Envia até 10 mensagens por batch com no máximo 10ms de espera.
        - Tamanho máximo do batch: 64KB.
        - Permite até 100 mensagens ou 1MB de mensagens pendentes no cliente.
        - Se exceder o fluxo, uma exceção será lançada (comportamento estrito).
        - Retry com timeout curto (5s) e backoff rápido.
        """
        batch_settings = BatchSettings(
            max_messages=10,
            max_latency=10 * constants.MILLISECONDS,
            max_bytes=64 * constants.KILOBYTE
        )

        publisher_options = PublisherOptions(
            flow_control=PublishFlowControl(
                message_limit=100,
                byte_limit=constants.MEGABYTE,
                limit_exceeded_behavior=LimitExceededBehavior.ERROR
            ),
            retry=Retry(
                initial=0.05,
                multiplier=1.2,
                maximum=5 * constants.SECONDS,
                timeout=5 * constants.SECONDS
            ),
            enable_open_telemetry_tracing=self.enable_open_telemetry
        )

        return self.create(
            batch_settings=batch_settings,
            publisher_options=publisher_options
        )

    def high_throughput(self: Self) -> PublisherClient:
        """
        Cria um publisher otimizado para throughput máximo.

        Ideal para processamento em lote, observabilidade ou
        sistemas com grandes volumes de mensagens e menor sensibilidade à latência.

        Configurações:
        - Até 1000 mensagens por batch, 10MB, ou 100ms de espera.
        - Buffer de até 5000 mensagens ou 50MB.
        - Bloqueia publicações quando limites são excedidos.
        - Retry com deadline longo (90s) e backoff agressivo.
        """
        batch_settings = BatchSettings(
            max_messages=1000,
            max_latency=100 * constants.MILLISECONDS,
            max_bytes=10 * constants.MEGABYTE
        )

        publisher_options = PublisherOptions(
            flow_control=PublishFlowControl(
                message_limit=5000,
                byte_limit=50 * constants.MEGABYTE,
                limit_exceeded_behavior=LimitExceededBehavior.BLOCK
            ),
            retry=Retry(
                initial=0.2,
                multiplier=1.5,
                maximum=60 * constants.SECONDS,
                timeout=90 * constants.SECONDS
            ),
            enable_open_telemetry_tracing=self.enable_open_telemetry
        )

        return self.create(
            batch_settings=batch_settings,
            publisher_options=publisher_options
        )

    def balanced(self: Self) -> PublisherClient:
        """
        Cria um publisher balanceado entre latência e throughput.

        Ideal para cenários padrão de produção com volume moderado
        e necessidade de desempenho confiável.

        Configurações:
        - Até 500 mensagens por batch, 1MB, ou 50ms de espera.
        - Até 1000 mensagens ou 10MB no buffer do cliente.
        - Bloqueia quando excede o limite de fluxo (comportamento seguro).
        - Retry configurado com deadline de 60 segundos e backoff exponencial.
        """
        batch_settings = BatchSettings(
            max_messages=500,
            max_latency=50 * constants.MILLISECONDS,
            max_bytes=constants.MEGABYTE
        )

        publisher_options = PublisherOptions(
            flow_control=PublishFlowControl(
                message_limit=1000,
                byte_limit=10 * constants.MEGABYTE,
                limit_exceeded_behavior=LimitExceededBehavior.BLOCK
            ),
            retry=Retry(
                initial=0.1,
                multiplier=1.3,
                maximum=30 * constants.SECONDS,
                timeout=60 * constants.SECONDS
            ),
            enable_open_telemetry_tracing=self.enable_open_telemetry
        )

        return self.create(
            batch_settings=batch_settings,
            publisher_options=publisher_options
        )

    def aggressive(self: Self) -> PublisherClient:
        """
        Cria um publisher agressivo, ideal para testes de carga e ambientes controlados.

        Usa limites extremamente altos e não bloqueia nem lança exceções ao ultrapassar
        o fluxo, favorecendo performance e volume.

        Configurações:
        - Até 2000 mensagens por batch, 10MB, ou 500ms de espera.
        - Buffer com até 10000 mensagens ou 100MB.
        - Ignora excessos de fluxo (comportamento arriscado).
        - Retry rápido com timeout moderado (20s).
        """
        batch_settings = BatchSettings(
            max_messages=2000,
            max_latency=500 * constants.MILLISECONDS,
            max_bytes=10 * constants.MEGABYTE
        )

        publisher_options = PublisherOptions(
            flow_control=PublishFlowControl(
                message_limit=10000,
                byte_limit=100 * constants.MEGABYTE,
                limit_exceeded_behavior=LimitExceededBehavior.IGNORE
            ),
            retry=Retry(
                initial=0.1,
                multiplier=2.0,
                maximum=10 * constants.SECONDS,
                timeout=20 * constants.SECONDS
            ),
            enable_open_telemetry_tracing=self.enable_open_telemetry
        )

        return self.create(
            batch_settings=batch_settings,
            publisher_options=publisher_options
        )
