#!/usr/bin/env python
# coding: utf-8

# A restful HTTP API for ansible by tornado
# Base on ansible-runner
# Github <https://github.com/lfbear/ansible-api>
# Author: lfbear

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from .websocket import Message
from .report import Reporter


class CallBack(object):
    """
    Callback functions for ansible-runner
    """

    def __init__(self):
        self._result = []
        self._drawer = []
        self._pepper = {}

    def event_pepper(self, event, data):
        self._pepper[event] = data

    def event_handler(self, data):
        rpt = Reporter(data)
        rpt.adorn(self._pepper)
        fmt = rpt.tidy()
        detail = rpt.detail()
        if fmt:
            Message.send(fmt)
        if detail:
            self._result.append(detail)

    def get_summary(self):
        result = {}
        for item in self._result:
            k = item.get('host', 'unknown')
            # print(k, item)
            if result.get(k, None) is None:
                result[k] = []
            result[k].append(item)

        return result

    def get_event(self):
        return self._result

    def status_drawer(self, data):
        self._drawer.append(data)

    def status_handler(self, data):
        status = data.get('status', '') if isinstance(data, dict) else data
        for item in self._drawer:
            if item.get('status', None) == status:
                raw = item.get('raw', lambda: {})()
                after = item.get('after', lambda: {})()
                # print('====>', raw, after)
                rpt = Reporter(raw)
                rpt.adorn({raw.get('event'): after})
                fmt = rpt.tidy()
                detail = rpt.detail()
                if fmt:
                    Message.send(fmt)
                if detail:
                    self._result.append(detail)
        # print(data, "status")
