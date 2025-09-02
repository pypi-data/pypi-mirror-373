import logging
import os
from collections import defaultdict
from datetime import datetime

import psutil
import pytz
from twisted.internet.task import LoopingCall
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger

logger = logging.getLogger(__name__)


class PeekPsUtil:
    # For the CPU load, we should be polling regularly to get an accurate result
    __LOOPING_CALL_PERIOD = 1.0
    __STATS_LOGGING_PERIOD = 60.0

    # Singleton
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(PeekPsUtil, cls).__new__(cls)
            # Lazy load the instance
            cls._instance.__singleton_init__()

        return cls._instance

    def __singleton_init__(self):
        self.__lastStatsLogDateTime = datetime.now(pytz.utc)
        self.__process = psutil.Process(os.getpid())
        self.__cpuPercent = 0.0
        self.__lastNicStats = None

        self.__loopingCall = LoopingCall(
            peekCatchErrbackWithLogger(logger)(self.__loopingCallTask)
        )

        d = self.__loopingCall.start(self.__LOOPING_CALL_PERIOD)
        d.addErrback(vortexLogFailure, logger)

    @deferToThreadWrapWithLogger(logger)
    def __loopingCallTask(self):
        self.__cpuPercent = self.__process.cpu_percent()
        self.__logProcessStats()

    def __logProcessStats(self):
        diff = (
            datetime.now(pytz.utc) - self.__lastStatsLogDateTime
        ).total_seconds()
        if diff < self.__STATS_LOGGING_PERIOD:
            return

        self.__lastStatsLogDateTime = datetime.now(pytz.utc)

        memInfo = self.__process.memory_info()
        logger.info(
            "CPU %s, Physical Memory %s, Virtual Memory %s",
            self.__cpuPercent,
            "{:,}MB".format(round(memInfo.rss / (1024 * 1024), 1)),
            "{:,}MB".format(round(memInfo.vms / (1024 * 1024), 1)),
        )

        self.__logNetConnections()

        try:
            self.__logNicStats(diffSeconds=diff)
        except Exception as e:
            logger.exception(e)

    def __logNetConnections(self):
        """
        connection(
            fd=115,
            family=2,
            type=1,
            local_address=("10.0.0.1", 48776),
            remote_address=("93.186.135.91", 80),
            status="ESTABLISHED",
        ),

        """
        conns = [
            c
            for c in self.__process.connections()
            if c.status == "ESTABLISHED" and c.raddr.port > 30000
        ]
        connCount = defaultdict(lambda: 0)
        for c in conns:
            connCount[c.raddr.ip] += 1
        duplicates = ", ".join(
            ["%s * %s" % (v, k) for k, v in connCount.items() if v != 1]
        )

        logger.info(
            f"We have {len(conns)} netstat connections,"
            f" {VortexFactory.getInboundConnectionCount()} vortex connections,"
            + (
                " with netstat duplicates: %s" % duplicates
                if duplicates
                else " with no duplicates"
            )
        )

    def __logNicStats(self, diffSeconds: float):
        """
        >> > psutil.net_io_counters(pernic=True)
        {
            'lo': snetio(bytes_sent=547971, bytes_recv=547971,
                packets_sent=5075, packets_recv=5075, errin=0, errout=0,
                dropin=0, dropout=0),
            'wlan0': snetio(bytes_sent=13921765, bytes_recv=62162574,
                packets_sent=79097, packets_recv=89648, errin=0, errout=0,
                dropin=0, dropout=0)
        }
        """

        statsByNic = {}
        statsByNic.update(psutil.net_io_counters(pernic=True, nowrap=True))
        statsByNic.pop("lo", None)

        oldStats = self.__lastNicStats
        self.__lastNicStats = statsByNic

        if not oldStats:
            return

        for nic in statsByNic:
            lastSentRate = (
                statsByNic[nic].bytes_sent - oldStats[nic].bytes_sent
            ) / diffSeconds

            lastRecvRate = (
                statsByNic[nic].bytes_recv - oldStats[nic].bytes_recv
            ) / diffSeconds

            logger.info(
                "NIC %s Throughput, %s sent, %s received, averaged over %s "
                "seconds",
                nic,
                "{:,}MB/s".format(round(lastSentRate / (1024 * 1024), 1)),
                "{:,}MB/s".format(round(lastRecvRate / (1024 * 1024), 1)),
                int(diffSeconds),
            )

    @property
    def cpuPercent(self):
        return self.__cpuPercent

    @property
    def memoryInfo(self):
        return self.__process.memory_info()
