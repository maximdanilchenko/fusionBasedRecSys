import shelve
import time
from metrics import *

# little data set for testing
testdata_users = {'max':{'odin doma':3,'labirint straha':5,'detektiv':2,'komnata':4},
            'dima':{'odin doma':5,'labirint straha':1,'detektiv':5},
            'alex':{'odin doma':5,'pila':2,'komnata':3,'grabim bank':3,'labirint straha':1,'detektiv':4,'dom s privideniamy':3},
            'den':{'odin doma':2,'grabim bank':3,'labirint straha':5,'dom s privideniamy':5},
            'kirill':{'grabim bank':3,'labirint straha':4,'detektiv':1,'dom s privideniamy':5},
            'olga':{'odin doma':3,'pila':4,'detektiv':4,'komnata':1,'dom s privideniamy':3},
            'lera':{'odin doma':4,'pila':3,'grabim bank':4,'labirint straha':1},
            'anna':{'pila':4,'grabim bank':2,'labirint straha':5,'komnata':4,'detektiv':4,'dom s privideniamy':4}}

testdata = {'grabim bank': {'den': 3, 'lera': 4, 'alex': 3, 'kirill': 3, 'anna': 2}, 
            'labirint straha': {'den': 5, 'lera': 1, 'max': 5, 'dima': 1, 'alex': 1, 'kirill': 4, 'anna': 5}, 
            'komnata': {'alex': 3, 'olga': 1, 'anna': 4, 'max': 4}, 
            'odin doma': {'den': 2, 'lera': 4, 'max': 3, 'dima': 5, 'alex': 5, 'olga': 3}, 
            'dom s privideniamy': {'den': 5, 'alex': 3, 'kirill': 5, 'anna': 4, 'olga': 3}, 
            'detektiv': {'max': 2, 'dima': 5, 'alex': 4, 'kirill': 1, 'anna': 4, 'olga': 4}, 
            'pila': {'lera': 3, 'alex': 2, 'anna': 4, 'olga': 4}}


# generating shelve DB based on movielens data
def genData(basename = 'prefsbase',datab = 'u.data',itemb = 'u.item'):
    movies = {}
    prefs = {}
    db = shelve.open(basename)
    for key in db:
        del key
    for i in open(itemb):
        info = i.split('|')
        movies[info[0]] = info[1]
    for i in open(datab):
        info = i.split()
        prefs.setdefault(info[0],{})
        prefs[info[0]][movies[info[1]]] = float(info[2])
    for i in prefs:
        db[i] = prefs[i]
    db.close()
    return ('success')

# generating shelve DB based on movielens data
def genDataNew(basename = 'prefsbase',datab = 'r1.train'):
    prefs = {}
    db = shelve.open(basename)
    for key in db:
        del key
    for i in open(datab):
        info = i.split('::')
        prefs.setdefault(info[0],{})
        prefs[info[0]][info[1]] = float(info[2])
    for i in prefs:
        db[i] = prefs[i]
    db.close()
    return ('success')

def genLitData(basename = 'prefsbase',datab = 'u.data',itemb = 'u.item'):
    movies = {}
    prefs = {}
    db = shelve.open(basename)
    for key in db:
        del key
    for i in open(itemb):
        info = i.split('|')
        if (int(info[0]) < 100):
            movies[info[0]] = info[1]
    for i in open(datab):
        info = i.split()
        prefs.setdefault(info[0],{})
        if (int(info[0]) < 100 and int(info[1]) < 100):
            prefs[info[0]][movies[info[1]]] = float(info[2])
    for i in prefs:
        db[i] = prefs[i]
    db.close()
    return ('success')

def singleSupportMatrix(pref_dict,similarity=PCC):
    Matrix = itemMatrix(pref_dict,0,similarity,False)
    print('itemMatrixReady')
    ratings = []
    for i in Matrix:
        for j in Matrix[i]:
            ratings.append(Matrix[i][j])
    print('ratings summed')
    ratings.sort()
    print('sorted')
    median = ratings[len(ratings)//2]
    print('median: %f'%median)
    SupportMatrix = {}
    c = 0
    for i in Matrix:
        SupportMatrix[i] = []
        for j in Matrix[i]:
            if (Matrix[i][j] > median):
                SupportMatrix[i].append((1,j))
            else:
                SupportMatrix[i].append((0,j))
        c += 1
        if (c%100 == 0):
            print('%d/%d'%(c,len(Matrix)))
    return SupportMatrix
    
def multipleSupportMatrix(pref_dict,similarities,DB):
    SupportMatrix = {}
    for i in pref_dict:
        SupportMatrix[i] = {}
        for j in pref_dict:
            if (j != i):
                SupportMatrix[i][j] = 0
    
    for sim in similarities:
        print('%s calculating'%sim.__name__)
        mat = singleSupportMatrix(pref_dict,sim)
        print('Sup value expanding')
        for name1 in mat:
            for (j,name2) in mat[name1]:
                SupportMatrix[name1][name2] += j
    ShvM = shelve.open(DB)
    for i in SupportMatrix:
        ShvM[i] = SupportMatrix[i]
    ShvM.close()
    print('Sup Matrix is ready')
    return SupportMatrix
                
# MAE - a and b - results for test data and original test data {{}{}{}}
def MAE(a,b):
    if (len(a) != len(b) or len(a) <= 0):
        return 100
    S = 0
    n = 0
    S = sum(abs(float(a[i][j]-b[i][j])) for i in a for j in a[i])
    M = sum(len(a[i]) for i in a)
    if (M == 0):
        return 100
    return S/M

def RMSE(a,b):
    if (len(a) != len(b) or len(a) <= 0):
        return 0
    S = sum((a[i][j]-b[i][j])**2 for i in a for j in a[i])
    M = sum(len(a[i]) for i in a)
    return sqrt(S)/M

# Get similarity value from Support Matrix (SM) with super similar value grater or equal then v for a and b
# sim for sup.similar, disim for sup.disimilar
def SUPSIM(pref,a,b,SM,v,sim,disim):
    if (SM[a][b] >= v):
        return sim * len(bothcalc(pref[a],pref[b]))/len(pref[b])
    else:
        return disim * len(bothcalc(pref[a],pref[b]))/len(pref[b])

def topSup(pref_dict,a,n,SupMatrix,v,sim,disim,best = True):
    top = []
    for i in pref_dict:
        if (i != a):
            top.append((SUPSIM(pref_dict,a,i,SupMatrix,v,sim,disim),i))
    if best:
        top.sort()
        top.reverse()
        return dict([(j,i) for (i,j) in top[0:n]])
    else:
        return dict([(j,i) for (i,j) in top])

def itemMatrixSup(pref_dict,n,SupMatrix,v,sim,disim,best = True):
    itM = {}
    for i in pref_dict:
        itM[i] = topSup(pref_dict,i,n,SupMatrix,v,sim,disim,best)
    return itM
    

def SUPSIM3(pref,a,b,SM,v,v1,sim,avr,disim):
    if (SM[a][b] >= v):
        if (SM[a][b] >= v1):            
            return sim * len(bothcalc(pref[a],pref[b]))/len(pref[b])
        return avr(pref[a],pref[b])
    else:
        return disim * len(bothcalc(pref[a],pref[b]))/len(pref[b])

def topSup3(pref_dict,a,n,SupMatrix,v,v1,sim,avr,disim,best = True):
    top = []
    for i in pref_dict:
        if (i != a):
            top.append((SUPSIM3(pref_dict,a,i,SupMatrix,v,v1,sim,avr,disim),i))
    if best:
        top.sort()
        top.reverse()
        return dict([(j,i) for (i,j) in top[0:n]])
    else:
        return dict([(j,i) for (i,j) in top])

def itemMatrixSup3(pref_dict,n,SupMatrix,v,v1,sim,avr,disim,best = True):
    itM = {}
    for i in pref_dict:
        itM[i] = topSup3(pref_dict,i,n,SupMatrix,v,v1,sim,avr,disim,best)
    return itM

# нахождение ближайших соседей
def top(pref_dict,a,n,similarity = PCC,best = True):
    top = []
    top.extend([(similarity(pref_dict[a],pref_dict[i]),i) for i in pref_dict if (i != a)])
    if best:
        top.sort()
        top.reverse()
        return dict([(j,i) for (i,j) in top[0:n]])
    else:
        return dict([(j,i) for (i,j) in top])

# трансформация словаря оценок
def transform(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person] = prefs[person][item]
    return result

# нахождение наилучших мер подобий для всех объектов из pref_dict
def itemMatrix(pref_dict,n,similarity,best = True):
    itM = {}
    print('calculating itemMatrix')
    c = 0
    lc = len(pref_dict)
    for i in pref_dict:
        itM[i] = top(pref_dict,i,n,similarity,best)
        c += 1
        if (c%50 == 0):
            print('%d/%d - %s'%(c,lc,similarity.__name__))
    return itM
#-------------------
# нахождение наилучших мер подобий для всех объектов из pref_dict
def itemMatrixAll(pref_dict,n,sims,best = True):
    itM = {}
    print('calculating itemMatrixAll')
    c = 0
    lc = len(pref_dict)
    for i in pref_dict:
        itM[i] = topAll(pref_dict,i,n,sims,best)
        c += 1
        if (c%50 == 0):
            print('%d/%d'%(c,lc))
    return itM
# нахождение ближайших соседей
def topAll(pref_dict,a,n,sims,best = True):
    top = []
    top.extend([(sum(sim(pref_dict[a],pref_dict[i]) for sim in sims)/len(sims),i) for i in pref_dict if (i != a)])
    if best:
        top.sort()
        top.reverse()
        return dict([(j,i) for (i,j) in top[0:n]])
    else:
        return dict([(j,i) for (i,j) in top])

#Main mathod for recommending!
#--------------------
# prefs: {u1:{i1,i2,i3},u2:{},{}}
# itemMatch: {i1:{i2,i3,i4},i2:{},i3:{}}
def recommendOne(prefs,prefsTr,itemMatch,item,user):
    if (user not in prefs):
        return 200
    if (item in prefs[user]):
        return 200
    if (item not in itemMatch):
        return 200
    itemRatings = prefs[user]
    userRatings = prefsTr[item]
    s = 0
    averageRat = sum(rating for (user,rating) in userRatings.items())/len(userRatings)
    up = sum((itemRatings[item2] - (sum(r for (u,r) in prefsTr[item2].items())/len(prefsTr[item2])))*
             itemMatch[item][item2] for item2 in  itemRatings if (item2 in itemMatch[item]))
    down = sum(abs(itemMatch[item][item2]) for item2 in  itemRatings if (item2 in itemMatch[item]))
    if (down == 0):
        return 200
    return (averageRat+up/down)

def recommendOneUser(prefs,prefsTr,itemMatch,item,user):
    if (item in prefs[user]):
        return 200
    if (user not in itemMatch):
        return 200
    if (item not in prefsTr):
        return 200
    itemRatings = prefs[user]
    userRatings = prefsTr[item]
    s = 0
    averageRat = sum(rating for (user,rating) in itemRatings.items())/len(itemRatings)
    
    up = sum((userRatings[user2] - averageRat)*itemMatch[user][user2] for user2 in  userRatings if (user2 in itemMatch[user]))
    down = sum(abs(itemMatch[user][user2]) for user2 in  userRatings if (user2 in itemMatch[user]))
    if (down == 0):
        return 200
    return (averageRat+up/down)

def recommendOne_two(prefs,prefsTr,itemMatch,item,user):
    if (item in prefs[user]):
        return 0
    if (item not in itemMatch):
        return 0
    itemRatings = prefs[user]
    userRatings = prefsTr[item]
    s = 0
    averageRat = sum(rating for (user,rating) in itemRatings.items())/len(itemRatings)
    
    up = sum((itemRatings[item2] - averageRat)*itemMatch[item][item2] for item2 in  itemRatings if (item2 in itemMatch[item]))
    down = sum(abs(itemMatch[item][item2]) for item2 in  itemRatings if (item2 in itemMatch[item]))
    if (down == 0):
        return 0
    return (averageRat+up/down)


# нахождение ближайших соседей
def topAld(pref_dict,a,n,sim):
    top = []
    for i in pref_dict:
        if (i != a):
            top.append((sim(pref_dict[i],pref_dict[a]),i))
    top.sort()
    top.reverse()
    return top[0:n]



# нахождение наилучших мер подобий для всех объектов из pref_dict
def itemMatrixAld(pref_dict,n,sim):
    start = time.time()
    itM = {}
    for i in pref_dict:
        itM[i] = topAld(pref_dict,i,n,sim)
    return itM

# выдача прогнозируемых оценок объектов в порядке убывания
def recommend(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    rs = 0
    #средняя оценка пользователя
    for (item,rating) in userRatings.items( ):
        rs += rating
    rs = rs/len(userRatings)
    #цикл по объектам максимально похожим на объекты данного пользователя
    for (item,rating) in userRatings.items( ):
        for (similarity,item2) in itemMatch[item]:
    #пропускаем, если пользователь уже оценивал данный объект
            if (item2 in userRatings):
                continue
            #взвешенная сумма отклоненных от среднего оценок, умноженных на коэффициент подобия
            scores.setdefault(item2,0)
            scores[item2]+=similarity*(rating-rs)
            # Сумма модулей всех коэффициентов подобия
            totalSim.setdefault(item2,0)
            totalSim[item2]+=abs(similarity)
    #считаем предполагаемые оценки и сортируем по убыванию
    rankings=[(rs + score/(totalSim[item]),item) for item,score in scores.items( )]
    rankings.sort( )
    rankings.reverse( )
    return rankings


