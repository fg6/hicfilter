#import numpy as np	

class of(float):
    def __str__(self):
        return "%0.1f" % self.real
class tf(float):
    def __str__(self):
        return "%0.3f" % self.real

def read_data(file, min_size, train):
    import pandas as pd
    # columns:
    if train:
        t=0         # target column is first
    else:         
        t=-1        # no target column

    nlinks = t + 5
    scaf1_len = t + 3
    scaf2_len = scaf1_len + 1
    hits = nlinks + 1

    # read file
    tdf = pd.read_csv(file, sep=" ", header=None)
      
    # keep only scaffold >= min_size
    tdf = tdf[ (tdf[scaf1_len] > min_size) & (tdf[scaf2_len] > min_size) ]

    # normalize hits by total number of links in this scaffold pair
    tdf.loc[:, hits:]  = tdf.loc[:, hits:].divide(tdf.values[:,nlinks], axis='index')  

    data = tdf.as_matrix()
    #np.random.shuffle(data) ## this sould not interefere with anything
    
    # X: get data except scaffold names
    x = data[:, scaf1_len:]    # keeping scaffold lengths, accuracy a bit better
    #x = data[:, nlinks:]
    

    if train:
        y = list(data[:, t])
        return x, y
    else:
        # save pairs of scaffolds:
        pairs = data[:, t+1:t+3] 
        # Important: x and pairs must keep the same indexes: no shuffling, sorting or similar

        return x, pairs
  

def resize(X, target, test_perc):
    from sklearn.model_selection import train_test_split
    
    X_train, X_test, y_train, y_test = train_test_split(X, target, random_state=1, test_size = test_perc)   

    return X_train, X_test, y_train, y_test



def randforest_cl(x, y, n_est, maxf, crit, min_s_leaf):
    from sklearn.ensemble import RandomForestClassifier
    print("\n Fitting with Random Forest")
    clf =  RandomForestClassifier(n_jobs=-1, max_features= maxf, n_estimators=n_est, class_weight='balanced',
                                  criterion = crit, min_samples_leaf = min_s_leaf, oob_score = True) 
    clf.fit(x, y)
    return(clf)

def best_randforest_cl(x, y):
    from sklearn.model_selection  import GridSearchCV
    from sklearn.ensemble import RandomForestClassifier
    print(" Optimizing parameters for Random Forest")
    clf =  RandomForestClassifier(n_jobs=-1, max_features= 'sqrt', n_estimators=200, class_weight='balanced',
                                  criterion = 'gini', min_samples_leaf = 1, oob_score = True) 

    param_grid = {        
        'n_estimators': [100, 200, 700, 1000],
        'max_features': ['auto', 'sqrt', 'log2'],
        'criterion': ['gini', 'entropy'],
        'min_samples_leaf': [1, 3, 5, 10]
        }
    
    ### Create a classifier with the parameter candidates ###
    CV = GridSearchCV(estimator=clf, param_grid=param_grid, cv= 5, scoring='accuracy', verbose=10)

    ### Train the classifier ### 
    CV.fit(x, y)

    ### Get the best parameters ###
    matrix = CV.cv_results_
    print('\n',CV.best_params_)   
    
    return CV.best_estimator_.n_estimators, CV.best_estimator_.max_features, CV.best_estimator_.criterion, CV.best_estimator_.min_samples_leaf


def best_xgboost_cl(x, y):
    from sklearn.model_selection  import GridSearchCV
    from xgboost import XGBClassifier
    print(" Optimizing parameters for Xgboost")

    #clf = XGBClassifier(nthread=15, booster='gbtree', eta=0.1, max_depth=6, subsample=1)
    clf = XGBClassifier(nthread=15, max_depth=6, subsample=1)

    param_grid = {  
        #'booster': ['gbtree', 'gblinear', 'dart'],
        #'eta': [0.1, 0.5, 0.8],
        'max_depth': [5, 10, 30],
        'subsample': [0.5, 1],
        }
    
    ### Create a classifier with the parameter candidates ###
    CV = GridSearchCV(estimator=clf, param_grid=param_grid, cv= 5, scoring='accuracy', verbose=10)

    ### Train the classifier ### 
    CV.fit(x, y)

    ### Get the best parameters ###
    print('\n',CV.best_params_)   
    return CV.best_estimator_.max_depth,CV.best_estimator_.subsample
#CV.best_estimator_.booster, CV.best_estimator_.eta, CV.best_estimator_.max_depth,CV.best_estimator_.subsample



def xgboost_cl(x, y, booster, eta, max_depth, subsample):
    from xgboost import XGBClassifier
    print(" Fitting with XGBoost")
    
    # issue: the xgboost version I have does not support booster and eta
    #clf = XGBClassifier(booster = booster, eta = eta,  max_depth = max_depth, subsample = subsample)
    clf = XGBClassifier(  max_depth = max_depth, subsample = subsample)
    clf.fit(x, y)
    return(clf)


def get_accuracy_cl(y_pred, y):
    from sklearn import metrics
    print(" Getting Scores..")
             
    ### Estimate Accuracy ###
    score = metrics.accuracy_score(y, y_pred)     
    
    # testing score
    f1score = metrics.f1_score(y, y_pred) 
    # for binary clf check this: sklearn.metrics.roc_curve

    ### Confusion Matrix ###
    conmat = metrics.confusion_matrix(y, y_pred)
    pos_ok = conmat[1][1]
    neg_ok = conmat[0][0]
    false_pos = conmat[0][1]
    false_neg = conmat[1][0]

    ### Print Score and Confusion Matrix ### 
    print("  Score :", (tf(score)), " f1 score :", tf(f1score),
          "\n  Pos_ok:", pos_ok, "False Neg:", false_neg, 
          " Pos error:", of(false_pos*100/(false_neg + pos_ok)),
          "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos,           
          " Neg error:", of(false_neg*100/(false_pos + neg_ok)),"%")
    
