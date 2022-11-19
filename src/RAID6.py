import os
import numpy as np
from src.GaloisField import GaloisField
import math
from os.path import join, getsize
from collections import defaultdict

def offset(lst, offset):
    lst=list(lst)
    return np.asarray(lst[offset:] + lst[:offset])

class RAID6(object):
    '''
    A class for RAID6 controller
    '''
    def __init__(self, config, debug=True):
        self.debug = debug
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
            data = list(f.read())
            if self.debug:
                print(f"read {filename}")
                print(data)
                print('\n')
            return data

    def distribute_data(self, filename):
        '''
        split data to different disk
        :param filename:
        :return: data array
        '''                
        content = self.read_data(filename) #读取file并且获得长度
        file_size = len(content) #大小
        padding_content=[[] for _ in range(self.config.num_data_disk)]
        
        for i in range(math.ceil(file_size/self.config.chunk_size)):
            padding_content[i%self.config.num_data_disk] = padding_content[i%self.config.num_data_disk] + list(content[i*self.config.chunk_size:min((i+1)*self.config.chunk_size,len(content))])
        
        total_stripe_number = math.ceil(file_size / self.config.stripe_size)
        
        for i in range(len(padding_content)):
            if len(padding_content[i])<self.config.chunk_size *total_stripe_number:
                padding_content[i] = list(padding_content[i]) + (self.config.chunk_size * total_stripe_number - len(padding_content[i])) * [0]
        
        padding_content = [np.array(tmp) for tmp in padding_content]
        
        content = np.concatenate(padding_content, axis=0)
        
        content = content.reshape(self.config.num_data_disk, self.config.chunk_size * total_stripe_number)
        if self.debug:
            print('file_size: ', file_size)
            print(f'distribute data into {self.config.num_data_disk} disks {len(content)} x {len(content[0])}:')
            print(content)
            print('\n')
        print('ssss')
        for x in content:
            print(x)
        return content
    
    def compute_parity(self, content):
        data = np.concatenate([content,self.gf.matmul(self.gf.vander, content)],axis=0)
        if self.debug:
            print("with parity: ")
            print(data)
        return data

    def chunk_save(self, data, dir):
        for i in range(self.config.num_disk):
            if os.path.exists(os.path.join(dir, 'disk_{}'.format(i))):
                os.remove(os.path.join(dir, 'disk_{}'.format(i)))
        i = 0        

        data_list=[[] for _ in range(self.config.num_disk)]
        while i < np.shape(data)[1]:
            for j in range(np.shape(data)[0]):
                if j < i/self.config.chunk_size:
                    disk_index = j                     
                elif self.config.num_data_disk > j >= i/self.config.chunk_size:
                    disk_index = j + 2                    
                elif j>=self.config.num_data_disk:
                    disk_index = int(i/self.config.chunk_size+j-self.config.num_data_disk)                               
                data_list[disk_index].append(data[j][i:i+self.config.chunk_size])                        
            i=i+self.config.chunk_size        
        for i in range(self.config.num_disk):
            print(data_list[i])
            with open(os.path.join(dir, 'disk_{}'.format(i)), 'wb+') as f:
                f.write(bytearray(list(np.concatenate(data_list[i]))))
            
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
            f.write(bytearray(content))

    def detect_failure(self, dir):
        fail_ids = []
        for disk_number in range(self.config.num_disk):
            file_name = os.path.join(dir,"disk_{}".format(disk_number))
            if not os.path.exists(file_name):
                print("detected disk {} failture".format(disk_number))
                fail_ids.append(disk_number)
        return fail_ids

        # file_list = []
        # for i in range(self.config.num_disk):
        #     file_name = os.path.join(dir,"disk_{}".format(i))
        #     with open(file_name, 'rb') as f:
        #         content = list(f.read()) 
        #         file_list.append(content)
        # file_size = len(file_list[0])
        # total_stripe_size =  math.ceil(file_size / self.config.chunk_size) 
        # chunk_number = 0
        # while chunk_number < total_stripe_size:
        #     current_stripe = []
        #     for j in range(self.config.num_disk):
        #         disk_index=int((j+i/self.config.chunk_size+2)%self.config.num_disk)
        #         current_stripe.append(file_list[disk_index][chunk_number*self.config.chunk_size: (chunk_number+1)*self.config.chunk_size])
        #     parity_chunks = self.gf.matmul(self.gf.vander, np.array(current_stripe[:self.config.num_data_disk]))
        #     for i in range(self.config.num_check_disk):
        #         if not (parity_chunks[i]==current_stripe[self.config.num_data_disk+i]).all:
        #             number_of_failure += 1
        #         print("detected disk corrupted".format(disk_number))
        #         return
        #     chunk_number += 1

    def rebuild(self, dir, fail_ids):
        n = len(fail_ids)
        if n > self.config.num_check_disk:
            print("\n","ERROR: too many failed disks.", "\n")
            return -1

        chunks_restore = []
        all_disks = defaultdict(lambda: None)
        for d in os.listdir(dir):
            all_disks[int(d.split("_")[-1])]=self.read_data(dir+'/'+d)
        print('all')
        print(all_disks[0])
        assert(len(all_disks[list(all_disks.keys())[0]])%self.config.chunk_size==0)
        n_chunks = int(len(all_disks[0])/self.config.chunk_size)

        parity_start_disk=0
        for i in range(n_chunks):
            parity_disks=np.arange(parity_start_disk, parity_start_disk+self.config.num_check_disk)
            parity_disks=[p%self.config.num_disk for p in parity_disks]

            print('aaa',parity_disks)
            F = self.gf.vander
            I = np.identity(self.config.num_data_disk)
            A = np.concatenate((I,F))

            E_remove = []
            for j in range(self.config.num_disk):
                if j not in fail_ids:
                    if j not in parity_disks:
                        E_remove.append(all_disks[j][i*self.config.chunk_size:(i+1)*self.config.chunk_size])

            for z in parity_disks:
                if z not in fail_ids:
                    E_remove.append(all_disks[z][i*self.config.chunk_size:(i+1)*self.config.chunk_size])
            
            remian_rows = []
            id = 0
            for m in range(self.config.num_disk):
                if m not in fail_ids and m not in parity_disks:
                    remian_rows.append(id)
                if m not in parity_disks:
                    id+=1

            parity_row=self.config.num_data_disk
            for x in parity_disks:
                if x not in fail_ids:
                    remian_rows.append(parity_row)
                parity_row+=1

            print("E",'\n',E_remove)
            A_remove = A[remian_rows,:]
            print("inv")
            print(A_remove)
            A_r_inv = self.gf.gf_inverse(np.array(A_remove,dtype=int))
            D = self.gf.matmul(A_r_inv,np.array(E_remove,dtype=int))
            chunks_restore.append(D.tolist())

            parity_start_disk += 1

        data_restore = [[] for _ in range (self.config.num_data_disk)]
        for c in range(n_chunks):
            for l in range(self.config.num_data_disk):
                data_restore[l].extend(chunks_restore[c][l])

        for x in data_restore:
            print(x)

        parity_data_restore = self.compute_parity(np.array(data_restore))
        dir_rebuild=self.config.mkdisk('./','rebuild')      
        self.chunk_save(parity_data_restore, dir_rebuild)

        return

    def retrieve(self, dir):
        
        fail_ids = self.detect_failure(dir)
        if len(fail_ids)>0:
            raise Exception("Sorry, storage disks are damaged.")

        chunks_restore = []
        all_disks = defaultdict(lambda: None)
        for d in os.listdir(dir):
            all_disks[int(d.split("_")[-1])]=self.read_data(dir+'/'+d)

        print("show disk 0 data: \n",all_disks[0])
        n_chunks = int(len(all_disks[0])/self.config.chunk_size)

        parity_start_disk=0
        remove_parity = []
        for i in range(n_chunks):
            parity_disks=np.arange(parity_start_disk, parity_start_disk+self.config.num_check_disk)
            parity_disks=[p%self.config.num_disk for p in parity_disks]

            remove_parity_chunk = []
            for j in range(self.config.num_disk):
                if j not in parity_disks:
                   remove_parity_chunk.append(all_disks[j][i*self.config.chunk_size:(i+1)*self.config.chunk_size]) 
            remove_parity.append(remove_parity_chunk)
            parity_start_disk += 1

        data_retrieve = []
        for h in range(n_chunks):
            for v in range(self.config.num_data_disk):
                data_retrieve.extend(remove_parity[h][v])
        data_retrieve = [ x for x in data_retrieve if x!=0]
        # print(data_retrieve)

        np.savetxt('data_retrieved.txt', data_retrieve)

        return data_retrieve

