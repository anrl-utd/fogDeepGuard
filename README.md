# Resilient Deep Distributed Neural Networks (RDDNNs)
We present multiple methods to retain accuracy in the case of single or multiple layer failure during inference.

Guide to result reproduction:
## Methods
fixedGuard -- Weighted Residual connections using our hueristic  
activeGuard -- Networks of stochastic depth, with failure of layers probability reflecting failure during inference.  
activePatrol -- Networks of stochastic depth, but the addition of layers is weighted by a new variable, learned through gradient descent.
fixedActiveGuard -- Networks of stochastic depth, but the weighted addition of layers is done using the hueristic we developed.  

## Dataset preprocessing
Obtain the multiview camera dataset [here](https://cvlab.epfl.ch/data/multiclass). When unzipped, this data will be split into different folders, with images from each camera (c0, c1, c2, ..., c5), and a folder with bounding boxes for these cameras.

We recommend storing the data in the following hierarchy:
`
.  
+-- multiview  
|   +-- c0  
|   +-- c1  
|   +-- c2  
|   +-- c3  
|   +-- c4  
|   +-- c5  
`  
sss  
  
activeGuard:  
1-50: [0.9, 0.9, 0.8, 0.8, 0.7, 0.6, 0.7, 0.66]  
51-60: [0.99, 0.98, 0.94, 0.93, 0.9, 0.9, 0.87, 0.87]  
72-92: [0.8, 0.8, 0.75, 0.7, 0.65, 0.65, 0.6, 0.6]  
  
fixedGuard:  
1-20: [0.9, 0.9, 0.8, 0.8, 0.7, 0.6, 0.7, 0.66]  
21-40: [0.99, 0.98, 0.94, 0.93, 0.9, 0.9, 0.87, 0.87]  
41-60: [0.8, 0.8, 0.75, 0.7, 0.65, 0.65, 0.6, 0.6]  
  
baseline:  
1-10: [0.9, 0.9, 0.8, 0.8, 0.7, 0.6, 0.7, 0.66]  
11-20: [0.99, 0.98, 0.94, 0.93, 0.9, 0.9, 0.87, 0.87]  
21-30: [0.8, 0.8, 0.75, 0.7, 0.65, 0.65, 0.6, 0.6]  
  
best baseline models (best balanced accuracy):  
1-10: 0.7675381307656974, Model 7  
11-20: 0.9023973891307119, Model 16  
21-30: 0.8948180496772693, Model 21  
  
best activeGuard models (best balanced accuracy):  
1-50: 0.8695980515597302, Model 32  
51-60: 0.9485170604366707, Model 58  
72-92: 0.7933599743886389, Model 84