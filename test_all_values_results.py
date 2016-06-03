from metrics import *
from itembased_recommender_system import *
import shelve


genData('base','u2.base')
print('base data ready')
genData('test','u2.test')
print('test data ready')

base = shelve.open('base')
test = shelve.open('test')

print('data opened %d'%len(base))

tr = transform(base)
print('transformed')

##SupMatrix = multipleSupportMatrix(tr,[PCC,CPCC,SPCC,Jaccard,MSD,JMSD,COS,ACOS],'result')
##print('support matrix calculated!!!')

SM = shelve.open('result')
SupMatrix = {}
for i in SM:
    SupMatrix[i] = SM[i]

print('SM opened with size%d'%len(SupMatrix))

sims = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
disims = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0,
         0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
res = {}
n = 300
for sim in sims:
    res[sim] = {}
    for disim in disims:
        originalRes = {}
        testRes = {}
        itMS = itemMatrixSup(tr,n,SupMatrix,7,sim,disim)
        for user in test:
            testRes[user] = {}
            originalRes[user] = {}
            for item in test[user]:
                rec = recommendOne(base,tr,itMS,item,user)
                if (rec != 200):
                    testRes[user][item] = rec
                    originalRes[user][item] = test[user][item]
        res[sim][disim] = MAE(originalRes,testRes)
        print('MAE for %f sim and %f disim is %f'%(sim,disim,res[sim][disim]))
