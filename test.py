from src.config import Config
from src.RAID6 import RAID6
import os
from data import DATA_PATH
import time
import numpy as np

T1 = time.time()
cfg = Config()
dir=cfg.mkdisk('./','default')

test=RAID6(cfg,True)
filename='test_small.txt'

test.write_to_disk(os.path.join(DATA_PATH, filename), dir)
test.read_data(dir+'/disk_0')

# T2 = time.time()
# print('程序运行时间:%s毫秒' % ((T2 - T1)*1000))
# # test.fail_disk(dir, 0)
# test.corrupt_disk(dir, 1)
# test.corrupt_disk(dir, 2)
# test.detect_failure(dir)
