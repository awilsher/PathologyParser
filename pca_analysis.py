import gc
import pandas as pd
import random
import numpy as np
import Parse1 as parser
from sklearn.decomposition import PCA
from sklearn import preprocessing
import matplotlib.pyplot as plt
import pylab

# conduct PCA on the matrix of reports (rows) vs word vectors (columns where 1 column represents a word, and entry in each column represents a count)
# this is intended to give a *very* rough estimate of the number of report formats by looking at the variation explained by the presence/absence of each word 
# however, this isn't overly useful as reports in the same format will share multiple words in common
# better off trying to compare word/token sequences (e.g. \PAR\R should only occur in one report format)
parser.move('syp.stripped.csv.small','syp.stripped.csv.small.moved',0,-1)    
f = parser.loadFile('syp.stripped.csv.small.moved')

dict = {}
rowCount = {}
i = 0 
for row in f.rows:
	for word in row.wordCounts:	
		if word not in dict and word not in ['NOT','AND','IN','THIS','TO',':','THE','OF']:
			dict[word] = i
			i += 1
			rowCount[word] = 0
		if word not in ['NOT','AND','IN','THIS','TO',':','THE','OF']:
			rowCount[word] += 1
dict = None
gc.collect()
print(str(i) + " unique words " )

top_1000 = {}
i= 0
for s in sorted(rowCount.items(), key=lambda e: (e[1], e[0])):
	if i >= len(rowCount) - 1000:
		top_1000[s[0]] = len(rowCount) - i - 1
	i += 1

matrix = np.zeros((len(f.rows),len(top_1000)))

i = 0
for row in f.rows:
	hasEntry = False;
	for word in row.wordCounts:
		if word in top_1000:
			matrix[i][top_1000[word]] += 1
			hasEntry = True;
	if not hasEntry:
		matrix[i][random.randint(0,999)] = 1
	i += 1
			
X = matrix

normalized = preprocessing.normalize(X, norm='l2', axis=1, copy=True, return_norm=False)

print(normalized)

covariances = []

for i in range(1,100):
	print("######################## N_COMPONENTS: " + str(i))
	pca = PCA(copy=True, iterated_power='auto', n_components=i, random_state=None,
	   svd_solver='auto', tol=0.0, whiten=False)
	pca.fit(normalized)
	print("#### EXPLAINED VARIANCE")
	print(pca.explained_variance_ratio_)
	print("#### COVARIANCE")
	print(pca.get_covariance())
	covariances.append([pca.get_covariance()[0][0]])

df = pd.DataFrame(covariances, columns=["covar"])

df['components'] = pd.Series(list(range(len(df))))	
print(df)
df.plot(x='components', y='covar')
pylab.show()
# take the first 10 singular values
#S = S[0:10,0:10]

# reconstruct the matrix
#reconstructed = np.dot(U, np.dot(S, Vt))




# sorted = reconstructed.sort_values(list(range(10)), ascending=False)




