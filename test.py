from src.config import Config
from src.RAID6 import RAID6
import os
from data import DATA_PATH
import time
import numpy as np

# Print the intermediate result to check the process
check=True

# Experiment start
#------------------------ Store()
# write data object to disks with parities
T_write_start = time.time()
cfg = Config()
dir=cfg.mkdisk('./','default')
test=RAID6(cfg,False)

## 3 sizes of files for testing
# filename = 'test_small.txt' # 104 bytes
# filename = 'shakespeare_small.txt' # 1145 bytes
filename = 'shakespeare.txt' # 5,458,199 bytes

test.write_to_disk(os.path.join(DATA_PATH, filename), dir)

if check:
    print("original disks:")
    original_disks = []
    for i in range(8):
        original_disks.append(test.read_data(dir+f'/disk_{i}'))
        # print(original_disks[i])
    print('\n')
T_write_end = time.time()

#------------------------ Fail()
# introduce disk failure

test.fail_disk(dir, 4)
test.fail_disk(dir, 5)

#------------------------ Detect()
# detect which disks are corrupted

fail_ids = test.detect_failure(dir)

#------------------------ Rebuild()
# restore the data and parity disks

T_rebuild_start = time.time()
test.rebuild(dir, fail_ids)
T_rebuild_end = time.time()

if check:
    print('\n')
    print("restored disks:")
    for i in range(8):
        tmp=test.read_data(f'./storage_rebuild/disk_{i}')
        if tmp==original_disks[i]:
            print(f"disk_{i} is correct.")
        else:
            print(f"! disk_{i} is ERROR. original len: {len(original_disks[i])} restore len: {len(tmp)}")
            print("original:")
            print(original_disks[i])
            print("restore:")
            print(tmp)
    print('\n')

#------------------------ Retrieve()
# re-ensamble data object

T_read_start = time.time()
restored_data = test.retrieve('./storage_rebuild')
T_read_end = time.time()
# if check:
#     print("restored data object:")
#     print(restored_data)
#     print('\n')

#---------------------------
read_time = T_read_end-T_read_start
write_time = T_write_end-T_write_start
rebuild_time = T_rebuild_end-T_rebuild_start

print(f"read time: {read_time} seconds")
print(f"write time: {write_time} seconds")
print(f"rebuild time: {rebuild_time} seconds")


