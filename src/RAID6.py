import os
import numpy as np
from src.GaloisField import GaloisField
import math
from os.path import join, getsize

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
    def chunk_save(self, data, dir):
        for i in range(self.config.num_disk):
            if os.path.exists(os.path.join(dir, 'disk_{}'.format(i))):
                os.remove(os.path.join(dir, 'disk_{}'.format(i)))
        i = 0        
        data_list=[[] for i in range(self.config.num_disk)]
        while i < np.shape(data)[1]:
            for j in range(np.shape(data)[0]):
                disk_index=int((j+i/self.config.chunk_size+2)%self.config.num_disk)
                data_list[disk_index].append(data[j][i:i+self.config.chunk_size])
#                with open(os.path.join(dir, 'disk_{}'.format(disk_index)), 'wb+') as f:
#                    f.write(data[j][i:i+self.config.chunk_size])
            i=i+self.config.chunk_size
        for i in range(self.config.num_disk):
            with open(os.path.join(dir, 'disk_{}'.format(i)), 'wb+') as f:
                f.write(np.concatenate(data_list[i]))
            
    def write_to_disk(self, filename, dir):
        data = self.distribute_data(filename)
        parity_data = self.compute_parity(data)        
        self.chunk_save(parity_data, dir)
        print("write data and parity to disk successfully\n")

    def fail_disk(self, dir, disk_number):
        os.remove(os.path.join(dir,"disk_{}".format(disk_number)))
        print("disk {} failed".format(disk_number))
    
    def corrupt_disk(self, dir, disk_number):
        file_name = os.path.join(dir,"disk_{}".format(disk_number))
        with open(file_name, 'rb') as f:
            content = list(f.read())  
        content[0] = content[0]+1
        with open(file_name, 'wb+') as f:
            f.write(content)
        # print(len(content))
        # print(content[:10])

    def detect_failure(self, dir):
        for disk_number in range(self.config.num_disk):
            file_name = os.path.join(dir,"disk_{}".format(disk_number))
            if not os.path.exists(file_name):
                print("detected disk {} failture".format(disk_number))
                return

        file_list = []
        for i in range(self.config.num_disk):
            file_name = os.path.join(dir,"disk_{}".format(disk_number))
            with open(file_name, 'rb') as f:
                content = list(f.read()) 
                file_list.append(content)
        file_size = len(file_list[0])
        total_stripe_size =  math.ceil(file_size / self.config.chunk_size) 
        chunk_number = 0
        while chunk_number < total_stripe_size:
            current_stripe = []
            for j in range(self.config.num_disk):
                disk_index=int((j+i/self.config.chunk_size+2)%self.config.num_disk)
                current_stripe.append(file_list[disk_index][chunk_number*self.config.chunk_size: (chunk_number+1)*self.config.chunk_size])
            print(current_stripe)
            parity_chunks = self.gf.matmul(self.gf.vander, np.array(current_stripe[:self.config.num_data_disk, :]))
            for i in range(self.config.num_check_disk):
                if not (parity_chunks[i]==current_stripe[self.config.num_data_disk+i]).all:
                    number_of_failure += 1
                print("detected disk corrupted".format(disk_number))
                return
            chunk_number += 1

