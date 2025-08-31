# Copyright 2022 Webull
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class GRPCBaseRequest(object):

    def __init__(self, path, request=None, version='V1'):
        self._path = path
        self._request = request
        self._version = version

    def get_path(self):
        return self._path

    def serialize(self):
        if self._request:
            return self._request.SerializeToString()
        else:
            return None
