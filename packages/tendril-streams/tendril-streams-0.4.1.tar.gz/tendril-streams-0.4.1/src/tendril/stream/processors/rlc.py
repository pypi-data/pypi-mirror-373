# encoding: utf-8

# Copyright (C) 2021 Neel Aundhia, IIT Kanpur
#               2021 Chintalagiri Shashank, IIT Kanpur
#
# This file is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from .base import MessageProcessorBase


class RunLengthProcessor(MessageProcessorBase):
    def __init__(self):
        super(RunLengthProcessor, self).__init__()
        self._last_value = None
        self._run_length = 0

    def process(self, message):
        if not self._last_value or message != self._last_value:
            self._last_value = message
            self._run_length = 1
            return message
        else:
            self._run_length += 1
