from metrics import *
from itembased_recommender_system import *
import shelve
import matplotlib.pyplot as plt

genData('base','u2.base')
print('base data ready')
genData('test','u2.test')
print('test data ready')

base = transform(shelve.open('base'))
test = transform(shelve.open('test'))

#transform both base and test for user-based
##base = transform(base)
##test = transform(test)

print('data opened %d'%len(base))

##base = {'max':{'odin doma':3,'labirint straha':5,'detektiv':2,'komnata':4},
##            'dima':{'odin doma':5,'labirint straha':1,'detektiv':5},
##            'alex':{'odin doma':5,'pila':2,'komnata':3,'grabim bank':3,'labirint straha':1,'detektiv':4,'dom s privideniamy':3},
##            'den':{'odin doma':2,'grabim bank':3,'labirint straha':5,'dom s privideniamy':5},
##            'kirill':{'grabim bank':3,'labirint straha':4,'detektiv':1,'dom s privideniamy':5},
##            'olga':{'odin doma':3,'pila':4,'detektiv':4,'komnata':1,'dom s privideniamy':3},
##            'lera':{'odin doma':4,'pila':3,'grabim bank':4,'labirint straha':1},
##            'anna':{'pila':4,'grabim bank':2,'labirint straha':5,'komnata':4,'detektiv':4,'dom s privideniamy':4}}
##
##test = {'max':{'pila':4,'dom s privideniamy':3},
##            'dima':{'pila':2,'dom s privideniamy':1},
##            'kirill':{'odin doma':3,'pila':4},
##            'olga':{'grabim bank':4,'labirint straha':1}}
tr = transform(base)
            
        
print('transformed')
SupMatrix = multipleSupportMatrix(tr,[PCC,CPCC,SPCC,Jaccard,MSD,JMSD,COS,ACOS],'result')
print('support matrix calculated!!!')

SM = shelve.open('result')
SupMatrix = {}
for i in SM:
    SupMatrix[i] = SM[i]

print('SM opened with size%d'%len(SupMatrix))
n = 300
maes = {}
#start loop
for v in range(9):    
    originalRes = {}
    testRes = {}
    if (n == 0):
        itMS = itemMatrixSup(tr,n,SupMatrix,v,1,0)
    else:
        itMS = itemMatrixSup(tr,n,SupMatrix,v,1,0)
    print('item support matrix for %d value calculated'%v)
    print('calculating test recommendations..')
    for user in test:
        testRes[user] = {}
        originalRes[user] = {}
        for item in test[user]:
            rec = recommendOne(base,tr,itMS,item,user)
            if (rec != 200):
                testRes[user][item] = rec
                originalRes[user][item] = test[user][item]
    maes[v] = MAE(originalRes,testRes)
    print('MAE for %d value is %f'%(v,maes[v]))
#end loop
print (maes)
labels = sorted(maes)
x = [0,1,2,3,4,5,6,7,8]
y = [maes[i] for i in labels]
plt.plot(x,y,'ko-')
##plt.title('MAE for different support values')
plt.ylabel('MAE')
plt.xlabel('support threshold')
plt.axis([-1,9,0.72,0.78])
plt.xticks(x)
for i,j in zip(x,y):
    plt.annotate(str(round(j,4)),xy=(i-0.5,j+0.005))
##plt.savefig('E:/Diploma/results/maes-support_n'+str(n)+'.png')
plt.show()
