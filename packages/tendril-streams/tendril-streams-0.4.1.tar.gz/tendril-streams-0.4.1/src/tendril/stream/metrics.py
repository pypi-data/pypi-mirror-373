

from copy import copy
from dataclasses import dataclass


@dataclass
class StreamProcessingMetrics:
    c_rx: int = 0
    c_tx: int = 0
    c_rs: int = 0
    c_rs_f: int = 0
    c_proc: int = 0
    l_rm: int = 0
    l_rsm: int = 0
    l_pm: int = 0


class StreamProcessingMetricsManager(object):
    def __init__(self, logger):
        self._logger = logger
        self._current: StreamProcessingMetrics = StreamProcessingMetrics()
        self._last: StreamProcessingMetrics = StreamProcessingMetrics()

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def current(self):
        return self._current

    def capture(self):
        self._logger.debug(
            "Received: {rx} ({rx_r}/s) | Reshaped: {rs} ({rs_r}/s) | "
            "Processed: {proc} ({proc_r}/s) | Sent: {tx} ({tx_r}/s) | "
            "Failures: {rs_f} ({rs_f_r}/s)",
            rx=self.current.c_rx, rx_r=self.current.c_rx - self._last.c_rx,
            rs=self.current.c_rs, rs_r=self.current.c_rs - self._last.c_rs,
            proc=self.current.c_proc, proc_r=self.current.c_proc - self._last.c_proc,
            tx=self.current.c_tx, tx_r=self.current.c_tx - self._last.c_tx,
            rs_f=self.current.c_rs_f, rs_f_r=self.current.c_rs_f - self._last.c_rs_f
        )

        self._logger.debug(
            "Received MQ Size: {received_mqs} ({received_mqr}/s)| "
            "Reshaped MQ Size: {reshaped_mqs} ({reshaped_mqr}/s)| "
            "Processed MQ Size: {processed_mqs} ({processed_mqr}/s)",
            received_mqs=self.current.l_rm,
            received_mqr=self.current.l_rm - self._last.l_rm,
            reshaped_mqs=self.current.l_rsm,
            reshaped_mqr=self.current.l_rsm - self._last.l_rsm,
            processed_mqs=self.current.l_pm,
            processed_mqr=self.current.l_pm - self._last.l_pm)

        self._last = copy(self._current)
