from src.config import Config
from src.RAID6 import RAID6
import os
from data import DATA_PATH
import time
import numpy as np

check=True
#------------------------ Store()
T_write_start = time.time()
cfg = Config()
dir=cfg.mkdisk('./','default')
test=RAID6(cfg,False)
filename='test_small.txt'
test.write_to_disk(os.path.join(DATA_PATH, filename), dir)

if check:
    print("original disks:")
    for i in range(8):
        print(test.read_data(dir+f'/disk_{i}'))
    print('\n')
T_write_end = time.time()
#------------------------ Update()

#------------------------ Fail()
test.fail_disk(dir, 4)
test.fail_disk(dir, 5)

#------------------------ Detect()
fail_ids = test.detect_failure(dir)

#------------------------ Rebuild()
T_rebuild_start = time.time()
test.rebuild(dir, fail_ids)
T_rebuild_end = time.time()

if check:
    print('\n')
    print("restored disks:")
    for i in range(8):
        tmp=test.read_data(f'./storage_rebuild/disk_{i}')
        print(tmp)
    print('\n')

#------------------------ Retrieve()
T_read_start = time.time()
restored_data = test.retrieve('./storage_rebuild')
T_read_end = time.time()
if check:
    print("restored data object:")
    print(restored_data)
    print('\n')

#---------------------------
read_time = T_read_end-T_read_start
write_time = T_write_end-T_write_start
rebuild_time = T_rebuild_end-T_rebuild_start

print(f"read time: {read_time} seconds")
print(f"write time: {write_time} seconds")
print(f"rebuild time: {rebuild_time} seconds")


