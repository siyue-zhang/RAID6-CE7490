# RAID6-CE7490

<p align="center">
    <img src='https://linustechtips.com/main/uploads/monthly_09_2015/post-239070-0-22015900-1441472733.gif' width="400" height="250">
</p>

[Previous Student's Project](https://github.com/MengShen0709/CE7490-RAID6)

[Our Overleaf Report](https://www.overleaf.com/7292873883sjhhnnhyysmm)

[A Tutorial on Reed-Solomon Coding for Fault-Tolerance in RAID-like Systems](http://web.eecs.utk.edu/~jplank/plank/papers/CS-96-332.pdf)

# Folder Structure

```
.
├── data                    # Data objects for experiment
│   ├── shakespeare.txt
│   └── img_test.png
├── src                     # RAID6 system codes
│   ├── RAID6.py
│   ├── GaloisFielf.py 
│   └── config.py     
├── storage_default         # Folder to store data disks
│   ├── disk_0
│   ├── disk_1
│   └── ...      
├── storage_drebuild         # Folder to store rebuilt data disks after disk failure
│   ├── disk_0
│   ├── disk_1
│   └── ...  
├── test.py                  # Test experiment code
├── data_retrieved.txt       # Retrieved data object from storage disks
└── README.md
```