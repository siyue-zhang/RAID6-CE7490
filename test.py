from src.config import Config
from src.RAID6 import RAID6
import os
from data import DATA_PATH
import time
import numpy as np

T1 = time.time()
cfg = Config()
dir=cfg.mkdisk('./')
test=RAID6(cfg)
filename='test_small.txt'
test.write_to_disk(os.path.join(DATA_PATH, filename), dir)
T2 = time.time()
#print('程序运行时间:%s毫秒' % ((T2 - T1)*1000))
# test.fail_disk(dir, 0)
A1=test.gf.gf_inverse(np.array([[1,2],[3,3]]))
print(A1)
print(test.gf.matmul(A1,np.array([[1,2],[3,3]])))
#test.corrupt_disk(dir, 1)
#test.corrupt_disk(dir, 2)
#test.detect_failure(dir)
