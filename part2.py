#!/bin/python
from movielens import *
from numpy import *
import math

# Store data in arrays
user = []
item = []
rating = []
rating_test = []

# Load the movie lens dataset into arrays
d = Dataset()
d.load_users("./data/u.user", user)
d.load_items("./data/u.item", item)
d.load_ratings("./data/u.base", rating)
d.load_ratings("./data/u.test", rating_test)

n_users = len(user)
n_items = len(item)

# The utility matrix stores the rating for each user-item pair in the matrix form.
utility = zeros((n_users, n_items))
for r in rating:
    utility[r.user_id-1][r.item_id-1] = r.rating

# Finds the average rating for each user and stores it in the user's object
for i in range(0, n_users):
    user[i].avg_r = mean(utility[i])

# Finds the Pearson Correlation Similarity Measure between two users
def pcs(x, y):
    num = 0
    A = utility[x - 1]
    B = utility[y - 1]
    avg_rx = mean([a for a in A if a>0])
    avg_ry = mean([b for b in B if b>0])
    I = [ (rxi,ryi) for (rxi,ryi) in zip(A,B) if rxi>0 and ryi>0  ]
    if len(I)>0:
        cima = sum([ (rxi-avg_rx)*(ryi-avg_ry) for (rxi,ryi) in I])
        baixo1 = sum([ (rxi-avg_rx)**2 for (rxi,ryi) in I])
        baixo2 = sum([ (ryi-avg_ry)**2 for (rxi,ryi) in I])
        
        baixo1Sqrt = math.sqrt(baixo1)
        baixo2Sqrt = math.sqrt(baixo2)
        
        return cima/(baixo1Sqrt*baixo2Sqrt) if (baixo1Sqrt*baixo2Sqrt)!=0 else 0
    else:
        return 0
    

# Guesses the ratings that user with id, user_id, might give to item with id, i_id.
# We will consider the top_n similar users to do this.
def guess(user_id, i_id, top_n):
    similarity = []
    for i in range(0, n_users):
        if i+1 != user_id:
            similarity.append((pcs_matrix[user_id-1][i],i+1))
    
    similarity.sort(key=lambda x:x[0],reverse=True)
    similarity = similarity[:top_n]
    
    rating_topN_ri = [(i,utility[i-1][i_id-1]) for v,i in similarity if utility[i-1][i_id-1]>0 ]
    rating_topN_avg_diff_ri_u = [ri-user[u-1].avg_r for u,ri in rating_topN_ri ]
    
    avg_diff_ri_u = mean(rating_topN_avg_diff_ri_u) if len(rating_topN_avg_diff_ri_u)>0 else 0
    responseF = abs(user[user_id-1].avg_r + avg_diff_ri_u)

    return responseF


# Perform clustering on users and items
# Predit the ratings of the user-item pairs in rating_test
# Find mean-squared error
pcs_matrix = zeros((n_users, n_users))
for i in range(0, n_users):
    for j in range(0, n_users):
        pcs_matrix[i][j] = pcs(i + 1, j + 1)

print "\rGenerating Similarity Matrix [%d:%d] = %f" % (i+1, j+1, pcs_matrix[i][j])
# print pcs_matrix

n = 150
answer = open('./data/prediction_rating.txt', "wb")
for test in rating_test:
    answer.write("%s,%s,%s\n" % (test.user_id,test.item_id,guess(test.user_id,test.item_id,n)))
