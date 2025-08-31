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

from pythonic_fp.gadgets.box import Box


class TestGadgetBox:
    """Functionality testing"""

    def test_box_unchanged(self) -> None:
        box_init_empty: Box[int] = Box()
        box_init_full = Box(42)

        if box_init_empty or not box_init_full:
            assert False

        for ii in box_init_empty:
            assert False

        for ii in box_init_full:
            assert ii == 42

        for ii in box_init_empty:
            if ii == 42:
                break
        else:
            assert True

        for ii in box_init_full:
            if ii == 42:
                break
        else:
            assert False

        for ii in box_init_full:
            if ii == -1:
                break
        else:
            assert True

        assert repr(box_init_empty) == 'Box()'
        assert repr(box_init_full) == 'Box(42)'

        assert len(box_init_empty) == 0
        assert len(box_init_full) == 1

        assert box_init_empty == box_init_empty
        assert box_init_full == box_init_full
        assert box_init_empty != box_init_full

        assert box_init_empty.get(-1) == -1
        assert box_init_full.get(-1) == 42

        try:
            assert box_init_full.get() == 42
        except ValueError:
            assert False
        else:
            assert True
        finally:
            assert True

        try:
            assert box_init_empty.get() == 42
        except ValueError:
            assert True
        else:
            assert False
        finally:
            assert True

        assert box_init_full.map(lambda x: x // 2) == Box(21)
        assert box_init_empty.map(lambda x: x // 2) == Box()
        assert box_init_full == Box(42)
        assert box_init_empty == Box()
        assert box_init_full.map(lambda x: str(x)) == Box('42')
        assert box_init_empty.map(lambda x: str(x)) == Box()
        
        def f(x: int) -> Box['str']:
            return Box(str(2*x))

        assert box_init_full.bind(f) == Box('84')
        assert box_init_empty.bind(f) == Box[str]()
