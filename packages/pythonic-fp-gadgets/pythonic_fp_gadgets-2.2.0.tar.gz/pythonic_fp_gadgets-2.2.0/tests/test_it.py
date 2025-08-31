# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pythonic_fp.circulararray.auto import ca, CA
from pythonic_fp.gadgets.it import it

class TestGadgetIt:
    """Functionality testing"""

    def test_it(self) -> None:
        ref0: list[int] = []
        trg0: list[int] = list(it())
        assert ref0 == trg0

        ref1 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2046, 4092]
        trg1 = list(it(1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2046, 4092))
        assert ref1 == trg1

        ref2 = [1, 2, 3]
        trg2 = [*it(1,2,3)]
        assert ref2 == trg2

        ca_iter = CA((1, 2))
        ca_args = ca(1, 2)
        assert ca_iter == ca_args

        ca0_ref: CA[int] = ca()
        ca0_trg: CA[int] = CA[int](it())
        assert ca0_ref == ca0_trg

        ca1_ref: CA[int] = CA((42, 7, 11, 100))
        ca1_trg = CA(it(42, 7, 11, 100))
        ca1_splat1 = ca(*it(42, 7, 11, 100))
        ca1_splat2 = ca(*it(42, 7), *it(11, 100))
        assert ca1_ref == ca1_trg == ca1_splat1 == ca1_splat2
