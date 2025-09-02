# encoding: utf-8

# Copyright (C) 2021 Neel Aundhia, IIT Kanpur
#               2021 Chintalagiri Shashank, IIT Kanpur
#
# This file is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import inspect
from .processors.base import MessageProcessorBase


class ProcessingChannel(object):
    def __init__(self, channel_id, processors=None):
        self._ident = channel_id
        self._processors = processors or []

    @property
    def ident(self):
        return self._ident

    @property
    def processors(self):
        return self._processors

    def install_processor(self, processor):
        if inspect.isclass(processor) and \
                issubclass(processor, MessageProcessorBase):
            self._processors.append(processor())
        else:
            self._processors.append(processor)

    def process(self, message):
        for processor in self._processors:
            if not message:
                return
            if isinstance(processor, MessageProcessorBase):
                message = processor.process(message)
            else:
                message = processor(message)
        return message
