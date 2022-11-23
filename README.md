# RAID6-CE7490

Project 2: RAID-6 based distributed storage system

# Introduction

RAID 6, also known as double-parity RAID (redundant array of independent disks), is one of several RAID schemes that work by placing data on multiple disks and allowing input/output (I/O) operations to overlap in a balanced way, improving performance.

In this project, we developed the RAID-6 system based on the most popular Vandermonde-RS code using ```Python 3.7``` and the ```numpy``` library. Galois Field and matrix operations were employed in the development. Six major functions were programmed for distributing data storage, updating modified data, detecting disk failure, restoring corrupted data, and retrieving data objects respectively.

![](https://github.com/siyue-zhang/RAID6-CE7490/blob/master/images/system.png)

# Folder Structure

```
.
├── data                    # Data objects for experiment
│   ├── shakespeare.txt
│   └── img_test.png
├── src                     # RAID6 system source codes
│   ├── RAID6.py
│   ├── GaloisField.py 
│   └── config.py     
├── storage_default         # Folder to store data disks
│   ├── disk_0
│   ├── disk_1
│   └── ...      
├── storage_drebuild         # Folder to store rebuilt data disks after disk failure
│   ├── disk_0
│   ├── disk_1
│   └── ...  
├── images                   # Images for report
├── test.py                  # Test experiment code
├── data_retrieved.txt       # Retrieved data object from storage disks
└── README.md
```