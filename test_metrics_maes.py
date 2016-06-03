from metrics import *
from itembased_recommender_system import *
import shelve
import matplotlib.pyplot as plt


genData('base','u2.base')
genData('test','u2.test')
print("data ready")

base = transform(shelve.open('base'))
test = transform(shelve.open('test'))
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
print("opened with size %d"%len(base))

tr = transform(base)
print("transformed")
ns = [30,100,200,300,500,0]
##ns = [1,2,3,4,5,6]
cls = ['b','g','r','c','m','y']
markers = ['.',',','o','v','^','<','>','p','*','+']
cls_n = 0
for n in ns:
    metrix = [JMSD,PCC,CPCC,SPCC,Jaccard,MSD,COS,ACOS]
    maes = {}
    for sim in metrix:
        if (n != 0):
            itMtr = itemMatrix(tr,n,sim)
        else:
            itMtr = itemMatrix(tr,n,sim,False)
        orig_recs = {}
        test_recs = {}
        for user in test:
            orig_recs[user] = {}
            test_recs[user] = {}
            for item in test[user]:
                rec = recommendOne(base,tr,itMtr,item,user)
                if (rec != 200):
                    orig_recs[user][item] = rec
                    test_recs[user][item] = test[user][item]
        mae = MAE(test_recs,orig_recs)
        print("Mae for %s is %f"%(sim.__name__,mae))
        maes[sim.__name__] = mae
    print(maes)
    labels = sorted(maes)
    x = [0,1,2,3,4,5,6,7]
    y = [maes[i] for i in labels]
    plt.plot(x,y,color = cls[cls_n],marker = markers[cls_n],linewidth=1.5,label = 'k = '+str(n))
##    plt.plot(x,y,'ko')
    cls_n += 1
plt.title('maes, user-based')
plt.axis([-1,8,0.7,1.1])
plt.ylabel('MAE')
plt.xlabel('metrics')
plt.xticks(x,labels,rotation='vertical')
plt.subplots_adjust(bottom=0.15)
plt.legend()
##for i,j in zip(x,y):
##    plt.annotate(str(round(j,4)),xy=(i-0.5,j+0.01))
plt.show()
##plt.savefig('E:/Diploma/results/maes-item-based_n'+str(n)+'.png')
