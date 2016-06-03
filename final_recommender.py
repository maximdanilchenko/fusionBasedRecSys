from metrics import *
from itembased_recommender_system import *
import shelve
import matplotlib.pyplot as plt
import time

genData('base','u2.base')
print('base data ready')
genData('test','u2.test')
print('test data ready')

base = shelve.open('base')
test = shelve.open('test')

print('data opened %d'%len(base))

tr = transform(base)

        
print('transformed')
t1 = time.clock()
SupMatrix = multipleSupportMatrix(tr,[PCC,CPCC,SPCC,Jaccard,MSD,JMSD,COS,ACOS],'result')
print('time for supmatrix is %f'%(time.clock()-t1))
print('support matrix calculated!!!')

SM = shelve.open('result')
SupMatrix = {}
for i in SM:
    SupMatrix[i] = SM[i]
print('SM opened with size%d'%len(SupMatrix))

##minmae = 1
metrix = [JMSD,PCC,CPCC,SPCC,Jaccard,MSD,COS,ACOS]
maes = []
n = 300

# testing all avr sim values (metrics) for all sim and disim values
##for metric in metrix:
##    for i in reversed(range(10)):
##        for j in range(i+1):
##            originalRes = {}
##            testRes = {}
##            itMS = itemMatrixSup3(tr,n,SupMatrix,j,i,1,metric,0)
##            #print('calculating test recommendations..')
##            for user in test:
##                testRes[user] = {}
##                originalRes[user] = {}
##                for item in test[user]:
##                    rec = recommendOne(base,tr,itMS,item,user)
##                    if (rec != 200):
##                        testRes[user][item] = rec
##                        originalRes[user][item] = test[user][item]
##            mae = MAE(originalRes,testRes)
##            maes.append((mae,j,i,metric.__name__))
##            if (mae < minmae):
##                print('min MAE is %f for borders (%d,%d) and metric %s'%(mae,j,i,metric.__name__))
##                minmae = mae
##        

#testing best result        
originalRes = {}
testRes = {}
t1 = time.clock()
itMS = itemMatrixSup3(tr,n,SupMatrix,7,9,1,COS,0)
print('time for itemMatrix is %f'%(time.clock()-t1))
print('calculating test recommendations..')
t1 = time.clock()
for user in test:
    testRes[user] = {}
    originalRes[user] = {}
    for item in test[user]:
        rec = recommendOne(base,tr,itMS,item,user)
        if (rec != 200):
            testRes[user][item] = rec
            originalRes[user][item] = test[user][item]
print('time is %f for %d recommendations'%((time.clock()-t1),sum(len(test[i]) for i in test)))
mae = MAE(originalRes,testRes)
print('MAE is %f'%mae)
