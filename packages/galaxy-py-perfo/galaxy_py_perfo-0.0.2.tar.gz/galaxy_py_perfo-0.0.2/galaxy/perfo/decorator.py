#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from functools import wraps
from time import perf_counter

from galaxy.utils.base import Component


def timed(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = f(*args, **kwargs)
        elapsed = perf_counter() - start
        if isinstance(args[0], Component) and hasattr(args[0], "log") and args[0].log is not None:
            args[0].log.logger.debug("The method '{}' of component {} took {:0.6f} seconds to complete".format(f.__name__,
                                                                                                               str(args[0]),
                                                                                                               elapsed))
        else:
            print("The method {} took {:0.6f} seconds to complete".format(f.__name__, elapsed))
        return result
    return wrapper


def async_timed(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        start = perf_counter()
        result = await f(*args, **kwargs)
        elapsed = perf_counter() - start
        if isinstance(args[0], Component) and hasattr(args[0], "log") and args[0].log is not None:
            args[0].log.logger.debug("The method '{}' of component {} took {:0.6f} seconds to complete".format(f.__name__,
                                                                                                               str(args[0]),
                                                                                                               elapsed))
        else:
            print("The method '{}' took {:0.6f} seconds to complete".format(f.__name__, elapsed))
        return result
    return wrapper
