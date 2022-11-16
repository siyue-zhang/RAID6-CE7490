from src.config import Config
from src.RAID6 import RAID6
import os
#from data import DATA_PATH
DATA_PATH="./data/"
cfg = Config()
dir=cfg.mkdisk('./')
test=RAID6(cfg)
filename='test_small.txt'
test.write_to_disk(os.path.join(DATA_PATH, filename), dir)
# test.fail_disk(dir, 0)
# test.corrupt_disk(dir, 1)
test.detect_failure(dir)