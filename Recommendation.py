import networkx
from operator import itemgetter
import matplotlib.pyplot as plt

# Read the data from the amazon-books.txt;
# populate amazonProducts nested dicitonary;
# key = ASIN; value = MetaData associated with ASIN
fhr = open('./amazon-books.txt', 'r', encoding='utf-8', errors='ignore')
amazonBooks = {}
fhr.readline()
for line in fhr:
    cell = line.split('\t')
    MetaData = {}
    MetaData['Id'] = cell[0].strip() 
    ASIN = cell[1].strip()
    MetaData['Title'] = cell[2].strip()
    MetaData['Categories'] = cell[3].strip()
    MetaData['Group'] = cell[4].strip()
    MetaData['SalesRank'] = int(cell[5].strip())
    MetaData['TotalReviews'] = int(cell[6].strip())
    MetaData['AvgRating'] = float(cell[7].strip())
    MetaData['DegreeCentrality'] = int(cell[8].strip())
    MetaData['ClusteringCoeff'] = float(cell[9].strip())
    amazonBooks[ASIN] = MetaData
fhr.close()

# Read the data from amazon-books-copurchase.adjlist;
# assign it to copurchaseGraph weighted Graph;
# node = ASIN, edge= copurchase, edge weight = category similarity
fhr=open("amazon-books-copurchase.edgelist", 'rb')
copurchaseGraph=networkx.read_weighted_edgelist(fhr)
fhr.close()

# Now let's assume a person is considering buying the following book;
# what else can we recommend to them based on copurchase behavior 
# we've seen from other users?
print ("Looking for Recommendations for Customer Purchasing this Book:")
print ("--------------------------------------------------------------")
purchasedAsin = '0805047905'

# Let's first get some metadata associated with this book
print ("ASIN = ", purchasedAsin) 
print ("Title = ", amazonBooks[purchasedAsin]['Title'])
print ("SalesRank = ", amazonBooks[purchasedAsin]['SalesRank'])
print ("TotalReviews = ", amazonBooks[purchasedAsin]['TotalReviews'])
print ("AvgRating = ", amazonBooks[purchasedAsin]['AvgRating'])
print ("DegreeCentrality = ", amazonBooks[purchasedAsin]['DegreeCentrality'])
print ("ClusteringCoeff = ", amazonBooks[purchasedAsin]['ClusteringCoeff'])

# (1) 
#     Get the depth-1 ego network of purchasedAsin from copurchaseGraph,
#     and assign the resulting graph to purchasedAsinEgoGraph.
purchasedAsinEgoGraph = networkx.ego_graph(copurchaseGraph,purchasedAsin,radius=1)

# (2)
#     Use the island method on purchasedAsinEgoGraph to only retain edges with 
#     threshold >= 0.5, and assign resulting graph to purchasedAsinEgoTrimGraph

threshold = 0.5
purchasedAsinEgoTrimGraph = networkx.Graph()

# get the weight
weightNodeDict={}

for fnode, tnode, edge in purchasedAsinEgoGraph.edges(data=True):
    if edge['weight'] >= threshold:
        purchasedAsinEgoTrimGraph.add_edge(fnode,tnode,edge=edge['weight'])
        if (fnode==purchasedAsin):
            weightNodeDict[tnode]=edge['weight']


# (3) Y
#     Find the list of neighbors of the purchasedAsin in the 
#     purchasedAsinEgoTrimGraph, and assign it to purchasedAsinNeighbors


purchasedAsinNeighbors = [asin for asin in purchasedAsinEgoTrimGraph.neighbors(purchasedAsin)]


import numpy as np
import pandas as pd

# (4) 
# ----------------------------------------------


SalesRank=[]
TotalReviews=[]
AvgRating=[]
DegreeCentrality=[]
ClusteringCoeff=[]

for asin in purchasedAsinNeighbors:
    SalesRank.append(amazonBooks[asin]['SalesRank'])
    TotalReviews.append(amazonBooks[asin]['TotalReviews'])
    AvgRating.append(amazonBooks[asin]['AvgRating'])
    DegreeCentrality.append(amazonBooks[asin]['DegreeCentrality'])
    ClusteringCoeff.append(amazonBooks[asin]['ClusteringCoeff'])
 

columns=['SalesRank','TotalReviews','AvgRating','DegreeCentrality','ClusteringCoeff']
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import Normalizer
pd.set_option('display.max_columns',10)

df=pd.DataFrame(data={'Sales':SalesRank,'Reviews':TotalReviews,'Avg':AvgRating,'DC':DegreeCentrality,'CC':ClusteringCoeff},index=purchasedAsinNeighbors)
df['DcCC']=pow(df['DC'],df['CC'])

# log transformation with error check (if 0 exist in list)
def logtrans(n):
    if n ==0:
        return 0
    else:
        logn=np.log(n)
        return round(logn,2) 


df['log_Review']=df['Reviews'].apply(logtrans)
df['log_Avg']=df['Avg'].apply(logtrans)
df['log_Sales']=df['Sales'].apply(logtrans)


df['Rating&Review_Score']=df['log_Review']*df['log_Avg']
df['DC&ClusterCoef_Score']=pow(df['DC'],df['CC'])

# Minmax scale all the scores
minmax=MinMaxScaler()
dftrans=pd.DataFrame(minmax.fit_transform(df[['DC&ClusterCoef_Score','log_Sales','Rating&Review_Score']]), columns=['DcCC_Score','minmax_Sales','R&R_Score'], index=df.index)
dftrans=pd.concat([df,dftrans],axis=1)

dftrans['Sales_Score']=round(1-dftrans['minmax_Sales'],2)
dftrans=dftrans.drop(['DC&ClusterCoef_Score','minmax_Sales','Rating&Review_Score'],axis=1)
dftrans['composite_score']=dftrans['DcCC_Score']+dftrans['R&R_Score']+(dftrans['Sales_Score']*1/5)


print('--'*20)


## STEP (5) Final Recommendation Top Five


compositemeasure={}
for asin in dftrans.index:
    compositemeasure[asin]=round(dftrans['composite_score'].loc[asin],2)

compositemeasure_sorted=dict(sorted(compositemeasure.items(), key=itemgetter(1),reverse=True)[:5])


print("The top 5 recommendations are:")
items=['Title','SalesRank','TotalReviews','AvgRating','DegreeCentrality','ClusteringCoeff']
for asin in compositemeasure_sorted.keys():
    print("----------------------")
    print("recommandation:",asin)
    for i in items:
        print(i,":",amazonBooks[asin][i])
