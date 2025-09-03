# Copyright 2025 Snowflake Inc.
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from threading import Lock


class ThreadSafeSingleton(type):

    """Thread-safe implementation of Singleton metaclass.

    This metaclass ensures that only one instance of any class using it exists,
    with thread-safe initialization to prevent race conditions in multi-threaded
    environments.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """Create or return the singleton instance for the class.

        Possible changes to the value of the `__init__` argument do not affect
        the returned instance after first initialization.

        Args:
            *args: Arguments to pass to class constructor
            **kwargs: Keyword arguments to pass to class constructor

        Returns:
            The singleton instance of the class

        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
