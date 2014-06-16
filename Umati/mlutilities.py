import pandas as pd
import numpy as np
from sklearn.cross_validation import StratifiedKFold
from sklearn import metrics


#report function for X,y
#do evaluation metrics
def eval_metrics(y_anot,y_pred):
    
    """
    Generates evaluation metrics
    returns multi valued function - see below
    """
    
    labels = np.unique(y_anot)
    
    report ={}
    report['accuracy'] = metrics.accuracy_score(y_anot,y_pred)
    report['auc'] = metrics.auc(y_anot,y_pred)
    report['f1'] = metrics.f1_score(y_anot,y_pred, average=None, labels=labels)
    report['precision'] = metrics.precision_score(y_anot,y_pred,average=None,labels=labels)
    report['recall'] = metrics.recall_score(y_anot,y_pred,average=None,labels=labels)
    
    
    
    return report

#Do average stratified k-fold report
def kfold_report(n_folds,clf,X,y,index=None):
    """
    Inputs:
    index - pandas index object for labels and predictions


    Returns;
    scores: average of eval metrics scores
    cms_ave: average of confusion matrixes, scaled up by number of folds, maybe some rounding
    labels_and_prediction: concatenated dataframe of label and predictions for each fold
    """
    skf = StratifiedKFold(y,n_folds=n_folds,indices=True)
    scores = None
    cms = []
    labels_and_prediction = pd.DataFrame(columns=['labels', 'prediction'])
    
    
    
    for train, test in skf:
    
        #Train model
        clf.fit(X[train,:],y[train])
        #predict on test
        y_pred = clf.predict(X[test,:])
        
        #do evaluation metrics
        score = eval_metrics(y[test],y_pred)
        
        
        if scores == None:
            scores = score
        else:
            
            for key in score.keys():
                scores[key]+=score[key]
                
        #Confusion matrix
        cm = metrics.confusion_matrix(y[test],y_pred)
        cms += [cm]
        
        #Lables and prediction
        this_labels_and_prediction = pd.DataFrame({'labels':y[test], 'prediction':y_pred})
        
        if index != None:
            this_labels_and_prediction.index = index[test]

        labels_and_prediction = pd.concat([labels_and_prediction,this_labels_and_prediction])
    
        
        
    for key in scores:
        scores[key] = scores[key]/n_folds
    
    cm_ave = sum(cms)/len(cms)*n_folds
    
   
    return scores, cm_ave, labels_and_prediction

#Create list of kfold classifiers
def kfold_train(n_folds,clf,X,y,index=None):
    """
    Inputs:
    index - pandas index object for labels and predictions


    Returns;
    list of tuples of trained classifiers, plus index of predicted set
    1st tuple = trained classifer
    if index equal pandas index
    2nd tuple = dict of pandas indexes for train and test
    if index = None
    2nd tuple = indices of train and test
    """
    from sklearn.base import clone
    
    skf = StratifiedKFold(y,n_folds=n_folds,indices=True)
    clfs = list()
    

    for train, test in skf:
    
        #Train model
        this_clf = clone(clf)
        this_clf.fit(X[train,:],y[train])

        if index!=None:
            this_index = {'train': index[train] , 'test': index[test]} 
        else:
            this_index = {'train': train , 'test': test} 

        clfs.append((this_clf,this_index))
    return clfs

###########Samplers:
from math import floor
import random

def sample_proportions(labels,
                        data,
                        sample_size, 
                        proportion_weighted, 
                        block_size = 10,
                        top_N = 10,
                        exclude_labels = True):
    #Function for doing proportional sampling
    #Very slow, must be able to optimise
    
    
    """
    Samples in proportion to pages already labelled - Need to be able to specify filter on label
    Inputs:
    
    labels - indexes of already labelled data and label
    data - data that needs to be labelled
    sample_size - size of final sample (approximate)
    proportion_weighted - proportion of sample to correspond to page proportion weighting scheme
    block_size - size of continuous comments blocks to label
    top_N - How many pages to use in the proportional weighing scheme
    exclude_labels - Exclude the rows in labels data from sampling

    Output:
    Index of samples as a subset of the original data index
    """
    
    
    #Construct df with pages and number of samples per page with respect to proportion
    freq_pages  = data.page_url.loc[labels.index].value_counts()
    #freq_pages  = data.loc[labels.index].page_url.value_counts()
    pc_pages = freq_pages/freq_pages.sum()
    buckets = (pc_pages.iloc[0:top_N]*sample_size*proportion_weighted).apply(floor)
    #Append the non-proportional number of samples to take
    buckets= buckets.append(pd.Series( sample_size - buckets.sum(), index=['restofsample']))
    print buckets
    if exclude_labels: 
        #Get index set of samples minus indexes of already labelled samples
        index_no_labels = data.index - labels.index
    else:
        index_no_labels = data.index
    
    #Get groups and index to make samples from and filter out already labelled
    df_groups = data[['page_url']].loc[index_no_labels]
    
    #Create empty of index of final samples
    sample_index = pd.Index([])
    
    
    #Do sampling
    for (group_lb, group_num_samples) in buckets.iteritems():
        
        if group_lb != 'restofsample':
            #get group index
            df_thisgroup = df_groups[df_groups['page_url'] == group_lb]
        
        elif group_lb == 'restofsample':
            #This will break unless rest_of_sample label is last
            rest_of_sample_index = index_no_labels - sample_index
            df_thisgroup = df_groups.loc[rest_of_sample_index]
            
        group_size = df_thisgroup.shape[0]
        print group_lb, group_size
        
        #We want to sample continuous blocks size N from group
        samples = set()
        sample_set = set([i for i in range(0,group_size-block_size)])
        
        while(len(samples) < group_num_samples):
            start_block = random.choice(list(sample_set))
            block = set(range(start_block,start_block+block_size))
            
            samples = samples.union(block) #Add lastest indexes sampled
            sample_set = sample_set.difference(block) #Remove indexes from set to be sampled
        
        #Get index labels
        samples = list(samples)
        samples.sort() #note that this working inplace
        this_index = [df_thisgroup.index[it] for it in samples] #Get index from full set rather than group
        this_index = pd.Index(this_index)
        
        sample_index += this_index
        
    return sample_index
        
def data_window(subdata,fulldata,lags = [1,0]):

    '''
    function selects a subset of a dataframe with a window around data
    Input
    subdata - subset of data, make sure data and fulldata have same index
    fulldata - full set of data to select from
    lags = list, first val is window size behind, second val is window size ahead
    ''' 

    subindex = pd.Index(subdata.index)
    fullindex = fulldata.index
    
    #Create df with index of fulldata and create trues for original data
    df_window = pd.DataFrame( {'window':len(fullindex)*[False], 'basedata' : len(fullindex)*[False]},  index = fullindex)
    df_window.loc[subindex] = True
    
    #Lags - create true for each element lag away from data
    num_behind, num_ahead = lags[0] , lags[1]
    lags= list(range(-num_behind,0)) + list(range(1,num_ahead+1))
    for lag in lags:
        
        lagged = df_window.shift(lag)
        index_lagged = lagged[lagged['basedata']==True].index
        df_window['window'].loc[index_lagged]= True
        
    
    return df_window
