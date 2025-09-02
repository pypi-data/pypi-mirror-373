

import json
from datetime import datetime
from datetime import UTC
from twisted.application.service import Service
from twisted.internet.task import LoopingCall


from tendril.core.mq.spec import MQConnectionSpec
from tendril.tx.utils.logger import TwistedLoggerMixin
from tendril.config import SYS_PING


class TwistedEngineBase(Service, TwistedLoggerMixin):
    name = "TwistedEngineBase"

    def __init__(self, *args, ping_connection_spec=None, **kwargs):
        self._running = False
        self._ping_task = None
        self._ping_connection_spec = ping_connection_spec
        if self._ping_connection_spec is None:
            self._ping_connection_spec = MQConnectionSpec(
                routing = 'ping.{}',
                exchange_name = 'system.topic',
                service_name = 'amqp091:system'
            )
        self._system_amqp = None
        super(TwistedEngineBase, self).__init__(*args, **kwargs)
        self.log_init()

    def _start(self):
        if self.ping_task is not None:
            self.ping_task.start(1)

    def _ping(self):
        if self._system_amqp:
            self._system_amqp.send_message(
                exchange=self._ping_connection_spec.exchange_name,
                routing_key=self._ping_connection_spec.routing.format(self.name),
                message=json.dumps({
                    'messageType': 'ping',
                    'componentName': self.name,
                    'timestamp': datetime.now(UTC).isoformat(),
                })
            )

    @property
    def ping_task(self):
        if SYS_PING and self._ping_task is None:
            _system_amqp_service = self.parent.getServiceNamed(self._ping_connection_spec.service_name)
            self._system_amqp = _system_amqp_service.getFactory()
            self.log.info(f"Creating ping task for {self.name}")
            self._ping_task = LoopingCall(self._ping)
        return self._ping_task

    def _stop(self):
        if self.ping_task is not None:
            self.ping_task.stop()

    def start(self):
        if not self._running:
            self._start()
            self._running = True

    def stop(self):
        if self._running:
            self._stop()
            self._running = False

    def startService(self):
        super().startService()
        self.start()

    def stopService(self):
        self.stop()
        super().stopService()
