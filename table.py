#building plot for all sim and disim values with data from file
#builded with test_all_values_resalts.py script

import matplotlib.pyplot as plt

f = open('result_maes.txt','r')
values = {}
for line in f:
    m = line.split()
    if (float(m[0]) not in values):
        values[float(m[0])] = {}
    values[float(m[0])][float(m[1])] = float(m[2])
f.close()
x = sorted([i for i in values[1.0]])
colors = ['b','g','r','c','m','y','k','#ff9900','#996633','#808080']
markers = ['.',',','o','v','^','<','>','p','*','+']
q = 0
for i in sorted(values):
    plt.plot(sorted(values[i]),[values[i][j] for j in sorted(values[i])],
             color=colors[q],linewidth=1.5,marker=markers[q],label='sim='+str(i))
    q += 1

plt.axis([-1,1,0.72,0.78])
plt.legend()
plt.ylabel('MAE')
plt.xlabel('Similarity value for super dissimilar users')
plt.xticks([x[i*2] for i in range(int(len(x)/2))])
plt.show()
