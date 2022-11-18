from src.config import Config
from src.RAID6 import RAID6
import os
from data import DATA_PATH
import time
import numpy as np

tt=0

#------------------------ Store()
cfg = Config()
dir=cfg.mkdisk('./','default')
test=RAID6(cfg,True)
filename='test_small.txt'
test.write_to_disk(os.path.join(DATA_PATH, filename), dir)
print('DISK0')
print(test.read_data(dir+f'/disk_{tt}'))
# for i in range(8):
#     test.read_data(dir+f'/disk_{i}')

#------------------------ Update()

# #------------------------ Fail()
# test.fail_disk(dir, 4)
# test.fail_disk(dir, 5)
# T_failure_start = time.time()

# #------------------------ Detect()
# fail_ids = test.detect_failure(dir)

# #------------------------ Rebuild()
# test.rebuild(dir, fail_ids)
# T_rebuild_finish = time.time()
# print(f"Rebuild Time: {T_rebuild_finish-T_failure_start} seconds.")

# # tmp=test.read_data(f'./storage_rebuild/disk_{tt}')
# # print(tmp, len(tmp))

#------------------------ Retrieve()

test.retrieve('./storage_default')

