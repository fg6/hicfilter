import argparse
import os.path
import sys
import utils
from utils import of,tf
from sklearn.externals import joblib
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def main():
    o_model_rf = 'randfor.sav'
    o_model_xgb = 'xgboost.sav'

    usage="\n %(prog)s -r full_path_to_file -m action -f model -o optimize [options]" 

    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-q", action="store_true", dest="quite", default=False,
                        help="don't print status messages to stdout")

    parser.add_argument("-r", dest="filename",
                        help="full path to read_map file") 
    parser.add_argument("-m", dest="action", 
                        help="train, looptrain, or predict?") 
    parser.add_argument("-f", dest="fitmodel", 
                        help="model to train or to load, (randfor, xgboost, both)") 
    parser.add_argument("-o", dest="optimize", 
                        help="optimize training paramters") 

    args = parser.parse_args()
    if not args.action or not args.filename or not args.fitmodel or not args.optimize:
        print("Some input is missing!")
        parser.print_help()
        sys.exit(1)
            
    if not os.path.exists(args.filename): 
        print("Sorry, file ", args.filename, "does not exists")
        sys.exit(1)

    # Train
    if args.action == 'train' or args.action == 'looptrain':
        if args.fitmodel != "randfor" and args.fitmodel != "xgboost" and args.fitmodel != "both":        
            print("\n Model ", args.fitmodel, 
                  " not recognized, please choose between \"randfor\" (Random Forest), \"xgboost\" (xgboost), or \"both\" " )
            sys.exit(1)

    # Predict
    elif args.action == 'predict':

        if args.fitmodel == "randfor" or args.fitmodel == "both":        
            if not os.path.exists(o_model_rf):
                print("Sorry, Random Forest model to load not found")
                sys.exit(1)
        if args.fitmodel == "xgboost" or args.fitmodel == "both":  
            if not os.path.exists(o_model_xgb):
                print("Sorry, XGBoost model to load not found")
                sys.exit(1)

        if args.fitmodel != "randfor" and args.fitmodel != "xgboost" and  args.fitmodel != "both":        
               if not os.path.exists(args.fitmodel):
                   print("Sorry, model to load not found", args.fitmodel)
                   sys.exit(1)

    # Wrong command
    else:
        print("I don't understand your command:", args.action, "\nPlease choose: train or predict")
        sys.exit(1)

        
    inputfile = args.filename
    action =  args.action
    fitmodel = args.fitmodel
    optimize = int(args.optimize)
        
    # minimum scaffold size
    min_size = 100000  

    ############################
    ########## Train ###########
    # loop over scaffold min_size
    if action == "looptrain":  
         print("Loop Training on scaffold length")

         sizes=[50000, 100000, 500000, 700000, 800000, 900000, 1000000, 1500000, 2000000]
         si=['50K', '100K', '500k', '700K', '800K', '900K', '1M', '1.5M', '2M']
       
         x = None; y =  None; X_train = None;  
         X_test = None; y_train = None; y_test = None
         
         filename = fitmodel + 'loop_train.txt'
         fp =  open(filename, 'w')
         for i, min_size in enumerate(sizes):
             del x, y, X_train, X_test, y_train, y_test 

             x, y = utils.read_data(inputfile, min_size, 1)
             
             ### Split sample in Train and Test to estimate Accuracy ###
             test_perc=0.2  # perc size of test sample
             X_train, X_test, y_train, y_test = utils.resize(x, y, test_perc)

             print(" Sample", si[i])
            
             if fitmodel == "randfor" or fitmodel == "both": 
            
                 n_est = 100 # same scores as 700 ??
                 maxf = 'log2'
                 crit = 'entropy'
                 min_s_leaf = 3 #10
 
                 if optimize == 1:
                     n_est, maxf, crit, min_s_leaf = utils.best_randforest_cl(x, y)
                
                 clf_rf = utils.randforest_cl(X_train, y_train, n_est, maxf, crit, min_s_leaf)
                 #joblib.dump(clf_rf,o_model_rf)  
             
             if fitmodel == "xgboost" or fitmodel == "both":
                 booster='gbtree'
                 eta=0.1
                 max_depth=30
                 subsample=0.5

                 if optimize == 1:
                     max_depth, subsample  = utils.best_xgboost_cl(x, y)

                 clf_xgb = utils.xgboost_cl(X_train, y_train, booster, eta, max_depth, subsample)
                 #joblib.dump(clf_xgb,o_model_xgb)  

             ######################################
             ### Test Predict with chosen Model ###

             print("\n Test sample: ")
             if fitmodel == "randfor":
                 y_pred = clf_rf.predict(X_test) 
                 score, pos_ok, false_neg, err_pos, neg_ok, false_pos, err_neg = utils.get_accuracy_cl(y_pred, y_test)
                 rf_scores = str(tf(score)) + " " + str(pos_ok) + " " + str(false_neg) + " " + str(of(err_pos)) + " " + str(neg_ok) + " " + str(false_pos) + " " + str(of(err_neg))
                 xgb_scores = ''
                 comb_score = ''

             elif fitmodel == "xgboost":
                 y_pred = clf_xgb.predict(X_test) 
                 score, pos_ok, false_neg, err_pos, neg_ok, false_pos, err_neg = utils.get_accuracy_cl(y_pred, y_test)
                 xgb_scores = str(tf(score)) + " " + str(pos_ok) + " " + str(false_neg) + " " + str(of(err_pos)) + " " + str(neg_ok) + " " + str(false_pos) + " " + str(of(err_neg)) 
                 rf_scores = ''
                 comb_score = ''

             elif fitmodel == "both":
                 y_pred_rf = clf_rf.predict(X_test) 
                 score, pos_ok, false_neg, err_pos, neg_ok, false_pos, err_neg = utils.get_accuracy_cl(y_pred_rf, y_test)
                 rf_scores = str(tf(score)) + " " + str(pos_ok) + " " + str(false_neg) + " " + str(of(err_pos) ) + " " + str(neg_ok) + " " + str(false_pos) + " " + str(of(err_neg)) 

                 y_pred_xgb = clf_xgb.predict(X_test) 
                 score, pos_ok, false_neg, err_pos, neg_ok, false_pos, err_neg = utils.get_accuracy_cl(y_pred_xgb, y_test)
                 xgb_scores = str(tf(score)) + " " + str(pos_ok) + " " + str(false_neg) + " " + str(of(err_pos))  + " " + str(neg_ok) + " " + str(false_pos) + " " + str(of(err_neg)) 
                
                 # Combine models
                 y_pred = np.array(y_pred_rf) | np.array(y_pred_xgb) 
                 
                 ### Estimate Accuracy and Confusion Matrix on Test sample 
                 score, pos_ok, false_neg, err_pos, neg_ok,  false_pos, err_neg = utils.get_accuracy_cl(y_pred, y_test)
                 comb_score = str(tf(score)) + " " + str(pos_ok) + " " + str(false_neg) + " " + str(of(err_pos) ) + " " + str(neg_ok) + " " + str(false_pos) + " " + str(of(err_neg)) 
                 #print("  Score :", (tf(tf(score))),"\n  Pos_ok:", pos_ok, "False Neg:", false_neg, " Pos error:", of(of(err_pos)) ,
                 #   "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos, " Neg error:", of(of(err_neg)) ,"%")
                
             line = si[i] + " " + rf_scores + " " + xgb_scores + " " + comb_score + "\n"
             print(line)
             fp.write(line) 
 
         fp.close()

         # Plot results for score and positive: how many we miss? how much contamination?
         col_names=['sample', 'score_rf', 'pos_rf', 'fneg_rf', 'epos_rf', 'neg_rf', 'fpos_rf', 'eneg_rf', 
                    'score_xgb','pos_xgb', 'fneg_xgb', 'epos_xgb', 'neg_xgb', 'fpos_xgb', 'eneg_xgb', 
                    'score','pos', 'fneg', 'epos', 'neg', 'fpos', 'eneg']
         df = pd.read_csv(filename, sep=" ", names =  col_names, header=None)
         
         fig, axes = plt.subplots(nrows=2, ncols=2)
         i=0
         j=0
         df.score_rf.plot(ax=axes[i,j], label='Random Forest', legend=True, title = "Accuracy Score on Test")
         df.score_xgb.plot(ax=axes[i,j], label='XGBoost', legend=True)
         df.score.plot(ax=axes[i,j], label='Combined', legend=True)
         j=1
         df.pos_rf.plot(ax=axes[i,j], label='Random Forest', legend=True, title = "Correct Positive")
         df.pos_xgb.plot(ax=axes[i,j], label='XGBoost', legend=True)
         df.pos.plot(ax=axes[i,j], label='Combined', legend=True)
         i=1
         j=0
         df.fneg_rf.plot(ax=axes[i,j], label='Random Forest', legend=True, title = "False Negative =  Missing")
         df.fneg_xgb.plot(ax=axes[i,j], label='XGBoost', legend=True)
         df.fneg.plot(ax=axes[i,j], label='Combined', legend=True)
         j=1
         df.fpos_rf.plot(ax=axes[i,j], label='Random Forest', legend=True, title = "False Positive = Contamination")
         df.fpos_xgb.plot(ax=axes[i,j], label='XGBoost', legend=True)
         df.fpos.plot(ax=axes[i,j], label='Combined', legend=True)

         
         #plt.show()
         fig.savefig(filename+'.png')  
         plt.close(fig)

    elif action == "train":
         print("Training with scaffold > ", min_size)

         x, y = utils.read_data(inputfile, min_size, 1)


         ### Split sample in Train and Test to estimate Accuracy ###
         test_perc=0.2  # perc size of test sample
         X_train, X_test, y_train, y_test = utils.resize(x, y, test_perc)


         ### Pick Model, Fit and Dump to file ###
         if fitmodel == "randfor" or fitmodel == "both": 
            
             n_est = 100 # same scores as 700 ??
             maxf = 'log2'
             crit = 'entropy'
             min_s_leaf = 3 #10
 
             if optimize == 1:
                 n_est, maxf, crit, min_s_leaf = utils.best_randforest_cl(x, y)
                 print(" Best xgboost")
                 #{'criterion': 'entropy', 'max_features': 'log2', 
                 #     'min_samples_leaf': 10, 'n_estimators': 700}
               #for min_size=100K: {'criterion': 'gini', 'max_features': 'log2', 'min_samples_leaf': 1, 'n_estimators': 1000}

             clf_rf = utils.randforest_cl(X_train, y_train, n_est, maxf, crit, min_s_leaf)
             joblib.dump(clf_rf,o_model_rf)  
             
         if fitmodel == "xgboost" or fitmodel == "both":
             booster='gbtree'
             eta=0.1
             max_depth=30
             subsample=0.5

             if optimize == 1:
                 print(" Best xgboost")
                 max_depth, subsample  = utils.best_xgboost_cl(x, y)
                 # {'max_depth': 30, 'subsample': 0.5} #booster, eta, not in version?
                 #for min_size=100K: 
             clf_xgb = utils.xgboost_cl(X_train, y_train, booster, eta, max_depth, subsample)
             joblib.dump(clf_xgb,o_model_xgb)  


         print("\n Train sample: ")
         ### Predict with chosen Model ###
         if fitmodel == "randfor":
             y_pred = clf_rf.predict(X_train) 
         elif fitmodel == "xgboost":
             y_pred = clf_xgb.predict(X_train) 
         elif fitmodel == "both":
             y_pred_rf = clf_rf.predict(X_train) 
             print("Random Forest Accuracy")
             score, pos_ok, false_neg, err_pos, neg_ok,  false_pos, err_neg = utils.get_accuracy_cl(y_pred_rf, y_train)
             print("  Score :", (tf(score)),"\n  Pos_ok:", pos_ok, "False Neg:", false_neg, " Pos error:", of(err_pos),
                   "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos, " Neg error:", of(err_neg),"%")
    
             y_pred_xgb = clf_xgb.predict(X_train) 
             print("Xgboost Accuracy")
             score, pos_ok, false_neg, err_pos, neg_ok,  false_pos, err_neg = utils.get_accuracy_cl(y_pred_xgb, y_train)
             print("  Score :", (tf(score)),"\n  Pos_ok:", pos_ok, "False Neg:", false_neg, " Pos error:", of(err_pos),
                   "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos, " Neg error:", of(err_neg),"%")

             #y_pred = y_pred_rf * y_pred_xgb
             y_pred = np.array(y_pred_rf) | np.array(y_pred_xgb) 
             print("Xgboost|RandForest Accuracy")
             #[x or y for (x, y) in zip(a, b)]   wo numpy

         ### Estimate Accuracy and Confusion Matrix on Training sample ###
         score, pos_ok, false_neg, err_pos, neg_ok,  false_pos, err_neg = utils.get_accuracy_cl(y_pred, y_train)
         ### Print Score and Confusion Matrix ### 
         print("  Score :", (tf(score)), " f1 score :", tf(f1score),
          "\n  Pos_ok:", pos_ok, 
          "False Neg:", false_neg, 
          " Pos error:", of(false_neg*100/(false_neg + pos_ok)),
          "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos,           
          " Neg error:", of(false_pos*100/(false_pos + neg_ok)),"%")
    
         print(len(y_pred), y_pred.sum())


         ######################################
         ### Test Predict with chosen Model ###


         print("\n Test sample: ")
         #print("  Tot Real Pos:", sum(y_test))
         if fitmodel == "randfor":
             y_pred = clf_rf.predict(X_test) 
         elif fitmodel == "xgboost":
             y_pred = clf_xgb.predict(X_test) 
         elif fitmodel == "both":
             y_pred_rf = clf_rf.predict(X_test) 
             print("Random Forest Accuracy")
             #print("  Predicted pos: ", y_pred_rf.sum(), " Predicted Neg: ", len(y_pred_rf)-y_pred_rf.sum() )
             score, pos_ok, false_neg, err_pos, neg_ok,  false_pos, err_neg = utils.get_accuracy_cl(y_pred_rf, y_test)
             print("  Score :", (tf(score)),"\n  Pos_ok:", pos_ok, "False Neg:", false_neg, " Pos error:", of(err_pos),
                   "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos, " Neg error:", of(err_neg),"%")
             y_pred_xgb = clf_xgb.predict(X_test) 
             print("Xgboost Accuracy")
             #print("  Predicted pos: ", y_pred_xgb.sum(), " Predicted Neg: ", len(y_pred_xgb)-y_pred_xgb.sum() )
             score, pos_ok, false_neg, err_pos, neg_ok,  false_pos, err_neg = utils.get_accuracy_cl(y_pred_xgb, y_test)
             print("  Score :", (tf(score)),"\n  Pos_ok:", pos_ok, "False Neg:", false_neg, " Pos error:", of(err_pos),
                   "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos, " Neg error:", of(err_neg),"%")

             # Combine models?
             #y_pred = y_pred_rf * y_pred_xgb
             y_pred = np.array(y_pred_rf) | np.array(y_pred_xgb) 
             print("Xgboost|RandForest Accuracy")

         ### Estimate Accuracy and Confusion Matrix on Test sample ###
         #print("  Predicted pos: ", y_pred.sum(), " Tot Neg: ", len(y_pred)-y_pred.sum() )
         score, pos_ok, false_neg, err_pos, neg_ok,  false_pos, err_neg = utils.get_accuracy_cl(y_pred, y_test)
         print("  Score :", (tf(score)),"\n  Pos_ok:", pos_ok, "False Neg:", false_neg, " Pos error:", of(err_pos),
               "%\n  Neg_ok:", neg_ok, "False_pos:", false_pos, " Neg error:", of(err_neg),"%")


    ############################
    ######## Predict ###########

    elif action == "predict":
        print("Predicting with scaffold > ", min_size)

        x, pairs = utils.read_data(inputfile, min_size, 0)
        # Important: x and pairs must keep the same indexes: no shuffling, sorting or similar

        ### Pick and Load Model ###
        if fitmodel == "randfor":
            clf = joblib.load('randfor.sav')
            y_pred = clf.predict(x) 
        elif fitmodel == "xgboost":
            clf = joblib.load('xgboost.sav')
            y_pred = clf.predict(x) 

        elif fitmodel == "both":
            clf_rf = joblib.load('randfor.sav')
            y_pred_rf = clf_rf.predict(x) 
       
            clf_xgb = joblib.load('xgboost.sav')
            y_pred_xgb = clf_xgb.predict(x) 
            
            y_pred = np.array(y_pred_rf) | np.array(y_pred_xgb) 

        else:
            clf = joblib.load(fitmodel)
            y_pred = clf.predict(x) 
            fitmodel = os.path.split(fitmodel)[1]


        ### Dump prediction to file ###
        o_pairs ='real_pairs_' + fitmodel + '.txt'
        fp =  open(o_pairs, 'w')
        for i,j in enumerate(y_pred):
            ### Dump to File if it's predicted to be a Real Connection ###
            if j == 1:                   
                fp.write(pairs[i,0]+" "+pairs[i,1]+"\n") 
                                
        fp.close()

if __name__ == "__main__":
    main()


