from src.config import Config
from src.RAID6 import RAID6
import os
from data import DATA_PATH
import time

T1 = time.time()
cfg = Config()
dir=cfg.mkdisk('./')
test=RAID6(cfg)
filename='txt_test.txt'
test.write_to_disk(os.path.join(DATA_PATH, filename), dir)
T2 = time.time()
print('程序运行时间:%s毫秒' % ((T2 - T1)*1000))
