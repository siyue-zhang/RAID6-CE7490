import time
import os

class Config(object):
    '''
    setup configuration of RAID6 controller
    :param num_disk: total disk count
    :param num_data_disk:  disk for data storage
    :param num_check_disk: disk for parity storage
    '''
    def __init__(self):
        self.num_disk = 8
        self.num_data_disk = 6
        self.num_check_disk = 2

        assert self.num_disk == self.num_data_disk + self.num_check_disk

        self.block_size = 4
        self.chunk_size = 16
        self.stripe_size = self.num_data_disk * self.chunk_size #每个stripe写多少
        
        assert self.chunk_size % self.block_size == 0

        print("\nNum of Disk: %d" % self.num_disk)
        print("Num of Data Disk: %d" % self.num_data_disk)
        print("Num of Checksum: %d" % self.num_check_disk)
        print("\nRAID-6 configuration initialized\n")
        # input("Press Enter to continue ...\n")
    
    def mkdisk(self, root):
        '''
        Make test directory for disk
        :return: dir
        '''
        test_dir = os.path.join(root, 'test '+time.strftime('%Y-%m-%d %H:%M:%S'))
        os.mkdir(test_dir)
        return test_dir
    