import os
import numpy as np
from src.GaloisField import GaloisField
import math
def offset(lst, offset):
    lst=list(lst)
    return np.asarray(lst[offset:] + lst[:offset])

class RAID6(object):
    '''
    A class for RAID6 controller
    '''
    def __init__(self, config):
        self.config = config
        self.gf = GaloisField(num_data_disk = self.config.num_data_disk, num_check_disk= self.config.num_check_disk)
        self.data_disk_list  = list(range(self.config.num_data_disk))
        self.check_disk_list = list(range(self.config.num_data_disk,self.config.num_data_disk+self.config.num_check_disk))
        print("RAID6 test begin, ready to store data\n")    
    def read_data(self, filename, mode = 'rb'):
        '''
        read data according to row
        '''
        with open(filename, mode) as f:
            return list(f.read())    
    def distribute_data(self, filename):
        '''
        split data to different disk
        :param filename:
        :return: data array
        '''
        content = self.read_data(filename) #读取file并且获得长度

        file_size = len(content) #大小

        total_stripe_number = math.ceil(file_size / self.config.stripe_size) 

        extra_stripe_size = total_stripe_number * self.config.stripe_size - file_size
        
        content = content + [0] * extra_stripe_size
        
        content = np.array(content)
        #stripe_size=chunk_size*num_data_disk
        content = content.reshape(self.config.num_data_disk, self.config.chunk_size * total_stripe_number)

        return content
    
    def compute_parity(self, content):
        return np.concatenate([content,self.gf.matmul(self.gf.vander, content)],axis=0)
    def switch(self):
        pass
    def transform_disk(self, data):
        input_data=data
        for i in range(np.shape(input_data)[0]):
            input_data[i]=offset(input_data[i],i)
        return input_data
    
    def write_to_disk(self, filename, dir):
        data = self.distribute_data(filename)
        parity_data = self.compute_parity(data)        
        input_data = self.transform_disk(parity_data)
        for i in range(self.config.num_disk):
            with open(os.path.join(dir, 'disk_{}'.format(i)), 'wb') as f:
                f.write(input_data[i])
        print("write data and parity to disk successfully\n")

    def fail_disk(self, dir, disk_number):
        os.remove(os.path.join(dir,"disk_{}".format(disk_number)))
        print("disk {} failed".format(disk_number))
    
    def corrupt_disk(self, dir, disk_number):
        file_name = os.path.join(dir,"disk_{}".format(disk_number))
        with open(file_name, 'rb') as f:
            content = list(f.read())  
        print(len(content))
        print(content[:10])

    def detect_failure(self, dir):
        number_of_failure = 0
        for disk_number in range(self.config.num_disk):
            file_name = os.path.join(dir,"disk_{}".format(disk_number))
            if not os.path.exists(file_name):
                number_of_failure += 1
                print("detected disk {} failture".format(disk_number))
                return
        for disk_number in range(self.config.num_disk):
            with open(file_name, 'rb') as f:
                content = list(f.read())  
            print(len(content))
            print(content[:10])

