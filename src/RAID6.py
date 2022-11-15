import os
import numpy as np
from src.GaloisField import GaloisField
import math

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
        input_data=[]
        data=data.T
        length=int(data.shape[0]/self.config.num_disk)
        for i in range(self.config.num_disk):
            input_data.append(np.concatenate(data[i*length:(i+1)*length,:]))
        return input_data
    def write_to_disk(self, filename, dir):
        data = self.distribute_data(filename)
        parity_data = self.compute_parity(data)        
        input_data = self.transform_disk(parity_data)
        for i in range(self.config.num_disk):
            with open(os.path.join(dir, 'disk_{}'.format(i)), 'wb') as f:
                f.write(input_data[i])
        print("write data and parity to disk successfully\n")
    