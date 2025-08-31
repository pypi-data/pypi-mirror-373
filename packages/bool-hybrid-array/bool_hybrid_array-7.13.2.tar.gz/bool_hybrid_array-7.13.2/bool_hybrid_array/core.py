from __future__ import annotations
import builtins
import array,bisect,numpy as np
from collections.abc import MutableSequence,Iterable,Generator,Iterator
import itertools,copy,sys
class BoolHybridArray(MutableSequence):
    class _CompactBoolArray:
        def __init__(self, size: int):
            self.size = size
            self.n_per_uint8 = 8
            self.n_uint8 = (size + self.n_per_uint8 - 1) // self.n_per_uint8
            self.data = np.zeros(self.n_uint8, dtype=np.uint8)
        def resize(self, new_size: int) -> None:
            if new_size <= self.size:
                return
            new_n_uint8 = (new_size + self.n_per_uint8 - 1) // self.n_per_uint8
            if new_n_uint8 > self.n_uint8:
                self.data = np.pad(self.data, (0, new_n_uint8 - self.n_uint8), constant_values=0)
            self.n_uint8 = new_n_uint8
            self.size = new_size
        def __getitem__(self, index: int | slice) -> bool | list[bool]:
            if isinstance(index, slice):
                start, stop, step = index.indices(self.size)
                result = []
                for i in range(start, stop, step):
                    uint8_pos = i // self.n_per_uint8
                    bit_offset = i % self.n_per_uint8
                    result.append(bool((self.data[uint8_pos] >> bit_offset) & 1))
                return result
            if not (0 <= index < self.size):
                raise IndexError(f"密集区索引 {index} 超出范围 [0, {self.size})")
            uint8_pos = index // self.n_per_uint8
            bit_offset = index % self.n_per_uint8
            return bool((self.data[uint8_pos] >> bit_offset) & 1)
        def __setitem__(self, index: int | slice, value):
            if isinstance(index, slice):
                start, stop, step = index.indices(self.size)
                indices = list(range(start, stop, step))
                if isinstance(value, (list, tuple)):
                    if len(value) != len(indices):
                        raise ValueError("值的数量与切片长度不匹配")
                    for i, val in zip(indices, value):
                        self._set_single(i, bool(val))
                else:
                    val_bool = bool(value)
                    for i in indices:
                        self._set_single(i, val_bool)
                return
            if not (0 <= index < self.size):
                raise IndexError(f"密集区索引 {index} 超出范围 [0, {self.size})")
            self._set_single(index, bool(value))
        def _set_single(self, index: int, value: bool) -> None:
            uint8_pos = index // self.n_per_uint8
            bit_offset = index % self.n_per_uint8
            self.data[uint8_pos] &= ~(1 << bit_offset) & 0xFF
            if value:
                self.data[uint8_pos] |= (1 << bit_offset)
        def set_all(self, value: bool):
            self.data[:] = 0xFF if value else 0x00
        def count_true(self) -> int:
            return sum(bin(byte).count('1') for byte in self.data)
        def __iter__(self):
            return (self[i] for i in range(self.size))
        def __len__(self):
            return self.size
    def __init__(self, split_index: int, size=None, is_sparse=False) -> None:
        self.split_index = int(split_index) if split_index < 1.5e+9 else int(1.45e+9)
        self.size = size or 0
        self.is_sparse = is_sparse
        self.small = self._CompactBoolArray(self.split_index + 1)
        self.small.set_all(not is_sparse)
        self.large = array.array('I')
        self.next_index = 0
    def accessor(self, i: int, value: bool|None = None) -> bool|None:
        def _get_sparse_info(index: int) -> tuple[int, bool]:
            pos = bisect.bisect_left(self.large, index)
            exists = pos < len(self.large) and self.large[pos] == index
            return pos, exists
        if value is None:
            if i <= self.split_index:
                return self.small[i]
            else:
                _, exists = _get_sparse_info(i)
                return exists if self.is_sparse else not exists
        else:
            if i <= self.split_index:
                self.small[i] = value
                return None
            else:
                pos, exists = _get_sparse_info(i)
                condition = not value or exists
                if self.is_sparse != condition:
                    self.large.insert(pos, i)
                else:
                    if pos < len(self.large):
                        del self.large[pos]
                return None
    def __getitem__(self, key:int|slice) -> BoolHybridArray:
        if isinstance(key, slice):
            start, stop, step = key.indices(self.size)
            return BoolHybridArr(self[i] for i in range(start, stop, step))
        key = key if key >=0 else key + self.size
        if 0 <= key < self.size:
            return self.accessor(key)
        raise IndexError("索引超出范围")
    def __setitem__(self, key: int | slice, value) -> None:
        if isinstance(key, int):
            adjusted_key = key if key >= 0 else key + self.size
            if not (0 <= adjusted_key < self.size):
                raise IndexError("索引超出范围")
            self.accessor(adjusted_key, bool(value))
            return
        if isinstance(key, slice):
            original_size = self.size
            start, stop, step = key.indices(original_size)
            value_list = list(value)
            new_len = len(value_list)
            if step != 1:
                slice_indices = list(range(start, stop, step))
                if new_len != len(slice_indices):
                    raise ValueError(f"值长度与切片长度不匹配：{new_len} vs {len(slice_indices)}")
                for i, val in zip(slice_indices, value_list):
                    self[i] = val
                return
            for i in range(stop - 1, start - 1, -1):
                if i <= self.split_index:
                    if i >= len(self.small):
                        self.small = np.pad(
                            self.small, 
                            (0, i - len(self.small) + 1),
                            constant_values=not self.is_sparse
                        )
                del self[i]
            for idx, val in enumerate(value_list):
                self.insert(start + idx, bool(val))
            return
        raise TypeError("索引必须是整数或切片")
    def __repr__(self) -> str:
        return(f"BoolHybridArray(split_index={self.split_index}, size={self.size}, "
        +f"is_sparse={self.is_sparse}, small_len={len(self.small)}, large_len={len(self.large)})")
    def __delitem__(self, key: int) -> None:
        key = key if key >= 0 else key + self.size
        if not (0 <= key < self.size):
            raise IndexError(f"索引 {key} 超出范围 [0, {self.size})")
        if key <= self.split_index:
            if key >= len(self.small):
                raise IndexError(f"小索引 {key} 超出small数组范围（长度{len(self.small)}）")
            self.small = np.delete(self.small, key)
            self.small = np.append(self.small, not self.is_sparse)
            self.split_index = min(self.split_index, len(self.small) - 1)
        else:
            pos = bisect.bisect_left(self.large, key)
            if pos < len(self.large) and self.large[pos] == key:
                del self.large[pos]
            adjust_pos = bisect.bisect_right(self.large, key)
            for i in range(adjust_pos, len(self.large)):
                self.large[i] -= 1
        self.size -= 1
    def __str__(self) -> str:
        return f"BoolHybridArr([{','.join(map(str,self))}])"
    def insert(self, key: int, value: bool) -> None:
        value = bool(value)
        key = key if key >= 0 else key + self.size
        key = max(0, min(key, self.size))
        if key <= self.split_index:
            if key > len(self.small):
                self.small = np.pad(
                    self.small, 
                    (0, key - len(self.small) + 1),
                    constant_values=not self.is_sparse
                )
            self.small = np.insert(self.small, key, value)
            self.split_index = min(self.split_index + 1, len(self.small) - 1)
        else:
            pos = bisect.bisect_left(self.large, key)
            for i in range(pos, len(self.large)):
                self.large[i] += 1
            if (self.is_sparse and value) or (not self.is_sparse and not value):
                self.large.insert(pos, key)
        self.size += 1
    def __len__(self) -> int:
        return self.size
    def __iter__(self):
        return(self[i] for i in range(self.size))
    def __next__(self):
        self.next_index += 1
        self.next_index %= len(self)
        return self[self.next_index-1]
    def __contains__(self, value) -> bool:
        return isinstance(value, bool) and any(v == value for v in self)
    def __bool__(self) -> bool:
        return self.size > 0
    def __any__(self):
        return self.count(True)>0
    def __all__(self):
        return self.count(True)==len(self)
    def __eq__(self, other) -> bool:
        if not isinstance(other, (BoolHybridArray, list, tuple, np.ndarray, array.array)):
            return False
        if len(self) != len(other):
            return False
        return all(a == b for a, b in zip(self, other))
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    def __and__(self, other) -> BoolHybridArray:
        if type(other) == int:
            other = bin(other)[2:]
        if len(self) != len(other):
            raise ValueError(f"与运算要求数组长度相同（{len(self)} vs {len(other)}）")
        return BoolHybridArr(a & b for a, b in zip(self, other))
    def __int__(self):
        return int(''.join(map(str,map(int,self))),base=2)
    def __or__(self, other) -> BoolHybridArray:
        if type(other) == int:
            other = bin(other)[2:]
        if len(self) != len(other):
            raise ValueError(f"或运算要求数组长度相同（{len(self)} vs {len(other)}）")
        return BoolHybridArr(a | b for a, b in zip(self, other))
    def __ror__(self, other) -> BoolHybridArray:
        if type(other) == int:
            other = bin(other)[2:]
        return self | other
    def __rshift__(self, other) -> BoolHybridArray:
        arr = BoolHybridArr(self)
        arr >>= other
        return arr
    def __irshift__(self, other) -> BoolHybridArray:
        if int(other) < 0:
            self <<= -other
            return self
        if other >= len(self):
            return FalsesArray(1)
        for i in range(int(other)):
            self.pop(-1)
        return self
    def __ilshift__(self ,other) -> BoolHybridArray:
        if int(other) < 0:
            self >>= -other
            return self
        if not is_sparse:
            self += FalsesArray(int(other))
            self.optimize()
        else:
            self.size += int(other)
        return self
    def __lshift__(self ,other) -> BoolHybridArray:
        if int(other) < 0:
            return self >> -other
        return self+FalsesArray(int(other))
    def __add__(self, other) -> BoolHybridArray:
        arr = BoolHybridArr(self)
        arr += other
        arr.optimize()
        return arr
    def __invert__(self) -> BoolHybridArray:
        return BoolHybridArr(not val for val in self)
    def __rand__(self, other) -> BoolHybridArray:
        if type(other) == int:
            other = bin(other)[2:]
        return self & other
    def __xor__(self, other) -> BoolHybridArray:
        if len(self) != len(other):
            raise ValueError(f"异或运算要求数组长度相同（{len(self)} vs {len(other)}）")
        return BoolHybridArr(a ^ b for a, b in zip(self, other))
    def __rxor__(self, other) -> BoolHybridArray:
        return self^other
    def __invert__(self) -> BoolHybridArray:
        return BoolHybridArr(not a for a in self)
    def copy(self) -> BoolHybridArray:
        return BoolHybridArr(self)
    def __copy__(self) -> BoolHybridArray:
        return self.copy()
    def find(self,value):
        return [i for i in range(len(self)) if self[i]==value]
    def extend(self, iterable:Iterable) -> None:
        if isinstance(iterable, (Iterator, Generator, map)):
            iterable,copy = itertools.tee(iterable, 2)
            len_ = sum(1 for _ in copy)
        else:
            len_ = len(iterable)
        self.size += len_
        self[-len_:] = iterable
    def index(self, value) -> int:
        value = bool(value)
        x = 'not find'
        for i in range(self.size):
            if self[i] == value:
                return i
            elif self[-i] == value:
                x = len(self)-i
            if len(self)-i == i:
                break
        if x != 'not find':
            return x
        raise ValueError(f"{value} not in BoolHybridArray")
    def count(self, value) -> int:
        value = bool(value)
        return sum(1 for v in self if v is value)
    def optimize(self) -> None:
        self.__dict__ = BoolHybridArr(self).__dict__
    def memory_usage(self, detail=False) -> dict | int:
        small_mem = len(self.small)//8
        large_mem = len(self.large)*4
        equivalent_list_mem = 40 + 8 * len(self)
        equivalent_numpy_mem = 96+len(self)
        total = small_mem+large_mem
        if not detail:
            return total
        need_optimize = False
        optimize_reason = ""
        sparse_ratio = len(self.large) / max(len(self), 1)
        if sparse_ratio > 0.4 and len(self) > 500:  # 阈值可根据测试调整
            need_optimize = True
            optimize_reason = "稀疏区索引密度过高，优化后可转为密集存储提升速度"
        elif len(self) < 32 and total > len(self):
            need_optimize = True
            optimize_reason = "小尺寸数组存储冗余，优化后将用int位存储进一步省内存"
        elif np.count_nonzero(np.array(self.small)) / max(len(self.small), 1) < 0.05 and len(self) > 1000:
            need_optimize = True
            optimize_reason = "密集区有效值占比过低，优化后可转为稀疏存储节省内存"
        return {
            "总占用(字节)": total,
            "密集区占用": small_mem,
            "稀疏区占用": large_mem,
            "对比原生list节省": f"{(1 - total/equivalent_list_mem)*100:.1f}%",
            "对比numpy节省": f"{(1 - total/equivalent_numpy_mem)*100:.1f}%" if equivalent_numpy_mem > 0 else "N/A",
            "是否需要优化": "是" if need_optimize else "否",
            "优化理由/说明": optimize_reason if need_optimize else "当前存储模式已适配数据特征，无需优化"
        }
def BoolHybridArr(lst: Iterable, is_sparse=None) -> BoolHybridArray:
    a = isinstance(lst, (Iterator, Generator, map))
    if a:
        lst, copy1, copy2 = itertools.tee(lst, 3)
        size = sum(1 for _ in copy1)
        true_count = sum(bool(val) for val in copy2)
    else:
        size = len(lst)
        true_count = sum(bool(val) for val in lst)
    if size == 0:
        return BoolHybridArray(0, 0, is_sparse=False if is_sparse is None else is_sparse)
    if is_sparse is None:
        is_sparse = true_count <= (size - true_count)
    split_index = int(min(size * 0.8, np.sqrt(size) * 100))
    split_index = np.sqrt(size) if true_count>size/3*2 or true_count<size/3 else max(split_index, 1)
    arr = BoolHybridArray(split_index, size, is_sparse)
    small_max_idx = min(split_index, size - 1)
    if a:
        small_data = []
        large_indices = []
        for i, val in enumerate(lst):
            val_bool = bool(val)
            if i <= small_max_idx:
                small_data.append(val_bool)
            else:
                if (is_sparse and val_bool) or (not is_sparse and not val_bool):
                    large_indices.append(i)
        if small_data:
            arr.small[:len(small_data)] = small_data
        if large_indices:
            arr.large.extend(large_indices)
    else:
        if small_max_idx >= 0:
            arr.small[:small_max_idx + 1] = [bool(val) for val in lst[:small_max_idx + 1]]
        large_indices = [
            i for i in range(split_index + 1, size)
            if (is_sparse and bool(lst[i])) or (not is_sparse and not bool(lst[i]))
        ]
        arr.large.extend(large_indices)
    arr.large = sorted(arr.large)
    return arr
def TruesArray(size):
    split_index = int(min(size * 0.1, np.sqrt(float(size))))
    split_index = max(split_index, 1)
    return BoolHybridArray(split_index,size)
def FalsesArray(size):
    split_index = int(min(size * 0.1, np.sqrt(float(size))))
    split_index = max(split_index, 1)
    return BoolHybridArray(split_index,size,True)
builtins.FalsesArray = FalsesArray
builtins.TruesArray = TruesArray
builtins.BoolHybridArr = BoolHybridArr
builtins.BoolHybridArray = BoolHybridArray
builtins.builtins = builtins