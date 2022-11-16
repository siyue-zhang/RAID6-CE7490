from src.config import Config
from src.RAID6 import RAID6
import os
#from data import DATA_PATH
DATA_PATH="./data/"
cfg = Config()
dir=cfg.mkdisk('./')
test=RAID6(cfg)
filename='txt_test.txt'
test.write_to_disk(os.path.join(DATA_PATH, filename), dir)
test.fail_disk(dir, 0)