import argparse
import os.path
import sys
import utils
from sklearn.externals import joblib

def main():

    usage="\n %(prog)s -p full_path_to_file [options]" 

    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-q", action="store_true", dest="quite", default=False,
                        help="don't print status messages to stdout")
    parser.add_argument("-r", dest="filename",
                        help="full path to read_map file") 
    parser.add_argument("-m", dest="loadmodel", 
                        help="full path to saved model, or 'own' for model saved in same project (if exists)") 
    parser.add_argument("-f", dest="fitmodel", 
                        help="fit using this model and save to file, (randfor or xgboost)") 
    parser.add_argument("-o", dest="optimize", 
                        help="optimize training paramters") 


    args = parser.parse_args()
    if len(sys.argv) < 5:
        parser.print_help()
        sys.exit(1)
    
    if ( args.loadmodel == "own" or not args.loadmodel) and (not args.fitmodel):
        parser.print_help()
        print("\n  Please specify which model to use with the option -f \n")
        sys.exit(1)
    elif not args.loadmodel and args.fitmodel != "randfor" and args.fitmodel != "xgboost" and args.fitmodel != "both":        
        print("\n Model ", args.fitmodel, 
              " not recognized, please choose between \"randfor\" (Random Forest) or \"xgboost\" (xgboost)" )
        sys.exit(1)

        
    if not os.path.exists(args.filename): 
        print("Sorry, file ", args.filename, "does not exists")
        sys.exit(2)
    elif args.loadmodel and not os.path.exists(args.loadmodel): 
        print("Sorry, file for model ", args.loadmodel, "does not exists")
        sys.exit(2)
        
    inputfile = args.filename
    model =  args.loadmodel
    fitmodel = args.fitmodel
    optimize = int(args.optimize)


    train = 0
    if not args.loadmodel:
        train = 1
        

    # minimum scaffold size
    min_size = 1000000  

    # Read alignments
    if train:
        x, y = utils.read_data(inputfile, min_size, train)
    else:
        x, pairs = utils.read_data(inputfile, min_size, train)
        # Important: x and pairs must keep the same indexes: no shuffling, sorting or similar


    ############################
    ########## Train ###########

    if train:

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
               

             clf_rf = utils.randforest_cl(X_train, y_train, n_est, maxf, crit, min_s_leaf)
             o_model_rf = 'randfor.sav'
             joblib.dump(clf_rf,o_model_rf)  
             
         if fitmodel == "xgboost" or fitmodel == "both":
             booster='gbtree'
             eta=0.1
             max_depth=30
             subsample=0.5

             if optimize == 1:
                 print(" Best xgboost")
                 #max_depth, subsample  = utils.best_xgboost_cl(x, y)
                 # {'max_depth': 30, 'subsample': 0.5} #booster, eta, not in version?

             clf_xgb = utils.xgboost_cl(X_train, y_train, booster, eta, max_depth, subsample)
             o_model_xgb = 'xgboost.sav'
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
             utils.get_accuracy_cl(y_pred_rf, y_train)
             y_pred_xgb = clf_xgb.predict(X_train) 
             print("Xgboost Accuracy")
             utils.get_accuracy_cl(y_pred_xgb, y_train)
             
             import numpy as np
             #y_pred = y_pred_rf * y_pred_xgb
             y_pred = np.array(y_pred_rf) | np.array(y_pred_xgb) 
             print("Xgboost|RandForest Accuracy")
             #[x or y for (x, y) in zip(a, b)]   wo numpy

         ### Estimate Accuracy and Confusion Matrix on Training sample ###
         utils.get_accuracy_cl(y_pred, y_train)



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
             utils.get_accuracy_cl(y_pred_rf, y_test)
             y_pred_xgb = clf_xgb.predict(X_test) 
             print("Xgboost Accuracy")
             #print("  Predicted pos: ", y_pred_xgb.sum(), " Predicted Neg: ", len(y_pred_xgb)-y_pred_xgb.sum() )
             utils.get_accuracy_cl(y_pred_xgb, y_test)

             # Combine models?
             #y_pred = y_pred_rf * y_pred_xgb
             y_pred = np.array(y_pred_rf) | np.array(y_pred_xgb) 
             print("Xgboost|RandForest Accuracy")


         ### Estimate Accuracy and Confusion Matrix on Test sample ###
         #print("  Predicted pos: ", y_pred.sum(), " Tot Neg: ", len(y_pred)-y_pred.sum() )
         utils.get_accuracy_cl(y_pred, y_test)


    ############################
    ######## Predict ###########

    else:
        
        ### Pick and Load Model ###
        if model is "own":
            if fitmodel == "randfor":
                f_model =  'randfor.sav'
            elif fitmodel == "xgboost":
                f_model = 'xgboost.sav'
        else:
            f_model = model
        clf = joblib.load(f_model)

        ### Predict with chosen Model ###
        y_pred = clf.predict(x) 

        ### Dump prediction to file ###
        o_pairs ='real_pairs.txt'
        fp =  open(o_pairs, 'w')
        for i,j in enumerate(y_pred):
               
            ### Dump to File if it's predicted to be a Real Connection ###
            if j == 1:                   
                #print(pairs[i,0], pairs[i,1])
                pickle.dump(pairs[i,:], fp)
                 
                

if __name__ == "__main__":
    main()


