"""
@author: Federica Colombo
         Psychiatry and Clinical Psychobiology Unit, Division of Neuroscience, 
         IRCCS San Raffaele Scientific Institute, Milan, Italy
"""

from sklearn.model_selection import RepeatedKFold, RepeatedStratifiedKFold
from neureval.relative_validation_confounds import RelativeValidationConfounds
from collections import namedtuple
from scipy import stats
import numpy as np
import math
import logging
import multiprocessing as mp
import itertools
import pandas as pd
import statistics

logging.basicConfig(format='%(asctime)s, %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


class FindBestClustCVConfounds(RelativeValidationConfounds):
    """
    Child class of :class:`reval.relative_validation.RelativeValidationConfounds`.
    It performs (repeated) k-fold cross validation on the training set to
    select the best number of clusters, i.e., the number that minimizes the
    normalized stability (i.e., average misclassification
    error/asymptotic misclassification rate).

    :param nfold: number of CV folds.
    :type nfold: int
    :param nclust_range: list with clusters to look for, default None.
    :type nclust_range: list of int
    :param s: classification object inherited
        from :class:`neureval.relative_validation.RelativeValidationConfounds`.
    :type s: class
    :param c: clustering object inherited
        from :class:`neureval.relative_validation.RelativeValidationConfounds`.
    :type c: class
    :param preprocessing: preprocessing method inherited
        from :class:`neureval.relative_validation.RelativeValidationConfounds`.
    :type preprocessing: class
    :param nrand: number of random labeling iterations
        to compute asymptotic misclassification rate, inherited from
        :class:`neureval.relative_validation.RelativeValidation` class.
    :type nrand: int
    :param n_jobs: number of processes to be run in parallel, default 1.
    :type n_jobs: int

    :attribute: cv_results_ dataframe with cross validation results. Columns are
        ncl = number of clusters; ms_tr = misclassification training;
        ms_val = misclassification validation.
    """

    def __init__(self, c, s, preprocessing, nrand, nfold=2, n_jobs=1, nclust_range=None):
        """
        Construct method.
        """
        super().__init__(c, s, preprocessing, nrand)
        self.nfold = nfold
        if abs(n_jobs) > mp.cpu_count():
            self.n_jobs = mp.cpu_count()
        else:
            self.n_jobs = abs(n_jobs)
        self.nclust_range = nclust_range

    def best_nclust_confounds(self, data, modalities, covariates, iter_cv=1, strat_vect=None):
        """
        This method takes as input the training dataset and the
        stratification vector (if available) and performs a
        (repeated) CV procedure to select the best number of clusters that minimizes
        normalized stability.

        :param data: training dataset.
        :type data: ndarray, (n_samples, n_features)
        :param modalities: dictionary specifying the datasets for each type of input features
        :type modalities: dictionary
        :param covariates: dictionary specifying the covariates for each type of input features
        :type covatìriates: dictionary
        :param iter_cv: number of iteration for repeated CV, default 1.
        :type iter_cv: integer
        :param strat_vect: vector for stratification, defaults to None.
        :type strat_vect: ndarray, (n_samples,)
        :return: CV metrics for training and validation sets, best number of clusters,
            misclassification errors at each CV iteration.
        :rtype: dictionary, int, (list) if n_clusters parameter is not available
        """
        
        reval = RelativeValidationConfounds(self.clust_method, self.class_method, self.preproc_method, self.nrand)

        if strat_vect is not None:
            kfold = RepeatedStratifiedKFold(n_splits=self.nfold, n_repeats=iter_cv, random_state=42)
        else:
            kfold = RepeatedKFold(n_splits=self.nfold, n_repeats=iter_cv, random_state=42)
        fold_gen = kfold.split(data, strat_vect)
        if self.nclust_range is not None and 'n_clusters' in self.clust_method.get_params().keys():
            params = list(itertools.product([(modalities, reval, covariates)],
                                            fold_gen, self.nclust_range))
        elif self.nclust_range is not None and 'n_components' in self.clust_method.get_params().keys():
            params = list(itertools.product([(modalities, reval, covariates)],
                                            fold_gen, self.nclust_range))
        else:
            params = list(itertools.product([(modalities, reval, covariates)],fold_gen))
        
        if self.n_jobs > 1:
            p = mp.Pool(processes=self.n_jobs)
            miscl = list(zip(*p.starmap(self._fit_confounds, params)))
            p.close()
            p.join()
            out = list(zip(*miscl))
        else:
            miscl = []
            for p in params:
                if len(p) > 2:
                    miscl.append(self._fit_confounds(data_obj=p[0],
                                                     idxs=p[1],
                                                     ncl=p[2]))
                else:
                    miscl.append(self._fit_confounds(data_obj=p[0],
                                                     idxs=p[1]))
            out = miscl

        # return dataframe attribute (cv_results_) with cv scores
        # If no point are labeled (e.g., all points assigned to -1 class by HDBSCAN)
        # the method returns
        cv_results_ = pd.DataFrame(out,
                                   columns=['ncl', 'ms_tr', 'ms_val', 'tr_labels', 'val_labels'])
        ctrl_rows = cv_results_.shape[0]
        cv_results_.dropna(axis=0, inplace=True)
        if 0 < ctrl_rows - cv_results_.shape[0] < ctrl_rows:
            logging.info("Dropped results where clustering algorithm failed to identify clusters.")
            FindBestClustCVConfounds.cv_results_ = cv_results_
        elif ctrl_rows - cv_results_.shape[0] == 0:
            FindBestClustCVConfounds.cv_results_ = cv_results_
        else:
            logging.info(f"{self.clust_method} was not able to identify any cluster. Failed run with "
                         f"{self.class_method}.")
            return None

        
        metrics = {'train': {}, 'val': {}}
        for ncl in cv_results_.ncl.unique():
            norm_stab_tr = cv_results_.loc[cv_results_.ncl == ncl]['ms_tr']
            norm_stab_val = cv_results_.loc[cv_results_.ncl == ncl]['ms_val']
            metrics['train'][ncl] = (np.mean(norm_stab_tr), _confint(norm_stab_tr))
            metrics['val'][ncl] = (np.mean(norm_stab_val), _confint(norm_stab_val))

        val_score = np.array([val[0] for val in metrics['val'].values()])
        bestscore = min(val_score)
        # select the cluster with the minimum misclassification error
        # and the maximum number of clusters
        if self.nclust_range is not None and 'n_clusters' in self.clust_method.get_params().keys():
            bestncl = self.nclust_range[np.flatnonzero(val_score == bestscore)[-1]]
            # To comment
            best_idx = cv_results_.loc[cv_results_.ncl == bestncl].ms_val.idxmin()
            idx_vect = np.concatenate((params[best_idx][1][-2], params[best_idx][1][-1]))
            label_vect = np.concatenate((out[best_idx][-2], out[best_idx][-1]))
            tr_lab = [lab for _, lab in sorted(zip(idx_vect, label_vect))]
            return metrics, bestncl, tr_lab
        elif self.nclust_range is not None and 'n_components' in self.clust_method.get_params().keys():
            bestncl = self.nclust_range[np.flatnonzero(val_score == bestscore)[-1]]
            # To comment
            best_idx = cv_results_.loc[cv_results_.ncl == bestncl].ms_val.idxmin()
            idx_vect = np.concatenate((params[best_idx][1][-2], params[best_idx][1][-1]))
            label_vect = np.concatenate((out[best_idx][-2], out[best_idx][-1]))
            tr_lab = [lab for _, lab in sorted(zip(idx_vect, label_vect))]
            return metrics, bestncl, tr_lab
        else:
            bestncl = list(metrics['val'].keys())[np.flatnonzero(val_score == bestscore)[-1]]
            best_idx = cv_results_.loc[cv_results_.ncl == bestncl].ms_val.idxmin()
            idx_vect = np.concatenate((params[best_idx][1][-2], params[best_idx][1][-1]))
            label_vect = np.concatenate((out[best_idx][-2], out[best_idx][-1]))
            tr_lab = [lab for _, lab in sorted(zip(idx_vect, label_vect))]
            return metrics, bestncl, tr_lab
    
    def evaluate_confounds(self, data, modalities, covariates, tr_idx, val_idx, nclust=None, tr_lab=None):
        """
        Method that applies the selected clustering algorithm with the best number of clusters
        to the test set. It returns clustering labels.
    
        :param data: dataset.
        :type data: ndarray, (n_samples, n_features)
        :param modalities: dictionary specifying the datasets for each type of input feature
        :type modalities: dictionary
        :param covariates: dictionary specifying the covariates for each type of input feature
        :type covariates: dictionary
        :param tr_idx: index specifying the training dataset
        :type tr_idx: array-like
        :param val_idx: index specifying the validation dataset
        :type val_idx: array-like
        :param nclust: best number of clusters, default None.
        :type nclust: int
        :param tr_lab: clustering labels for the training set. If not None
            the clustering algorithm is not performed and the classifier is fitted.
            Available for clustering methods without `n_clusters` parameter. Default None.
        :type tr_lab: array-like
        :return: labels and accuracy for both training and test sets.
        :rtype: namedtuple, (train_cllab: array, train_acc:float, test_cllab:array, test_acc:float)
        """
      
        if isinstance(tr_lab, list):
            tr_lab = np.array(tr_lab)
        try:
            if 'n_clusters' in self.clust_method.get_params().keys():
                self.clust_method.n_clusters = nclust
                train_cor_dic, test_cor_dic = super().GLMcorrection_confounds(modalities,covariates, tr_idx, val_idx)
                tr_misc, modelfit, labels_tr, X_train_cor = super().train(train_cor_dic, tr_lab)
            elif 'n_components' in self.clust_method.get_params().keys():
                self.clust_method.n_components = nclust
                train_cor_dic, test_cor_dic = super().GLMcorrection_confounds(modalities,covariates, tr_idx, val_idx)
                tr_misc, modelfit, labels_tr, X_train_cor = super().train(train_cor_dic, tr_lab)
            else:
                train_cor_dic, test_cor_dic = super().GLMcorrection_confounds(modalities, covariates, tr_idx, val_idx)
                tr_misc, modelfit, labels_tr, X_train_cor = super().train(train_cor_dic, tr_lab)
            
            if self.preproc_method is not None:
                ts_misc, labels_ts, X_test_cor = super().test(test_cor_dic, modelfit, fit_preproc=self.preproc_method)
            else:
                ts_misc, labels_ts, X_test_cor = super().test(test_cor_dic, modelfit)
        except TypeError:
            logging.info(f"Not possible to perform evaluation on the test set. "
                         f"No clusters were identified with "
                         f"{self.clust_method}")
            return None

        Eval = namedtuple('Eval',
                      ['train_cllab', 'train_acc', 'test_cllab', 'test_acc'])
        out = Eval(labels_tr, 1 - tr_misc,  labels_ts, 1 - ts_misc)
        return out



    @staticmethod
    def _fit_confounds(data_obj, idxs, ncl=None):
        """
        Function that calls training, test, covariates, and random labeling.
    
        :param data_obj: dataset and `reval.RelativeValidationConfounds` class.
        :type data_obj: tuple
        :param cov_obj: covariates and diagnosis labels.
        :type cov_obj: tuple
        :param idxs: lists of training and validation indices.
        :type idxs: tuple
        :param ncl: number of clusters, default None
        :type ncl: int
        :return: number of clusters and misclassification errors for training and validation.
        :rtype: tuple (int, float, float)
        """
    
        modalities, reval, covariates = data_obj
        tr_idx, val_idx = idxs
        if 'n_clusters' in reval.clust_method.get_params().keys():
           reval.clust_method.n_clusters = ncl
        elif 'n_components' in reval.clust_method.get_params().keys():
           reval.clust_method.n_components = ncl
   
        
        # Case in which the number of clusters identified is not sufficient or points are not classified
        # (it happens particularly for SpectralClustering and HDBSCAN)
        try:
            train_cor_dic, test_cor_dic = reval.GLMcorrection_confounds(modalities, covariates, tr_idx, val_idx)
            miscl_tr, modelfit, tr_labels, X_train_cor = reval.train(train_cor_dic)
            if reval.preproc_method is not None:
                miscl_val, val_labels, X_test_cor = reval.test(test_cor_dic, modelfit, fit_preproc=reval.preproc_method)
                rndmisc_mean_val = reval.rndlabels_traineval(X_train_cor, X_test_cor, tr_labels, val_labels)
            else:
                miscl_val, val_labels, X_test_cor = reval.test(test_cor_dic, modelfit)
                rndmisc_mean_val = reval.rndlabels_traineval(X_train_cor, X_test_cor, tr_labels, val_labels)
               
            # If random labeling gives perfect prediction, substitute
            # misclassification for validation loop with 1.0
            if rndmisc_mean_val > 0.0:
                ms_val = miscl_val / rndmisc_mean_val
            else:
                ms_val = 1.0
            return len([n for n in np.unique(val_labels) if n >= 0]), miscl_tr, ms_val, tr_labels, val_labels
        except TypeError:
            return None, None, None, None, None

        
def _confint(vect):
    """
    Private function to compute confidence interval.

    :param vect: performance scores.
    :type vect: array-like
    :return: mean and error.
    :rtype: tuple
    """
    mean = np.mean(vect)
    # interval = 1.96 * math.sqrt((mean * (1 - mean)) / len(vect))
    interval = stats.t.ppf(1 - (0.05 / 2), len(vect) - 1) * (np.std(vect) / math.sqrt(len(vect)))
    return mean, interval
