#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/1/18 13:32
# @Author  : 江斌
# @Software: PyCharm

import GPUtil

GPU_SUPPORT_LIST = '[GeForce GTX 10xx(Pascal), GeForce RTX 20xx(Turing)]'


class GPU(object):
    ARCH_TABLE = {
        'GeForce GTX 10': 'Pascal',
        'GeForce GTX 16': 'Turing',
        'GeForce RTX 20': 'Turing',
        # 'GeForce RTX 30': 'Ampere'
    }

    def __init__(self, name=None, driver=None):
        """
        字段说明：
            name：显卡型号
            driver：显卡驱动
            arch：显卡架构

        示例：
            >>> gpu = GPU()
            GPU(name="GeForce RTX 2080", driver="441.66", arch="Turing")
        """
        self.name = name
        self.driver = driver
        self.arch = self.get_arch(self.name)

    def get_arch(self, name):
        if isinstance(name, str):
            for k, v in self.ARCH_TABLE.items():
                if name.startswith(k):
                    return v
        return None

    def __str__(self):
        info = f'GPU(name="{self.name}", driver="{self.driver}", arch="{self.arch}")'
        return info

    __repr__ = __str__


class GPUs(object):
    def __init__(self):
        self.gpu_list = self.get_gpu_list()

    def get_gpu_list(self):
        gpu_list = GPUtil.getGPUs()
        return [GPU(name=each.name, driver=each.driver) for each in gpu_list]

    def __str__(self):
        return f'GPUs({str(self.gpu_list)})'


gpus = GPUs()
first_gpu = gpus.gpu_list[0] if len(gpus.gpu_list) > 0 else None

if __name__ == '__main__':
    print(gpus)
    print(first_gpu)
