#!/usr/bin/python3
import re
import pandas
from immucellai2.myfunction5 import CLASS_FOR_TIME
import numpy as np
import random
from immucellai2.myclasses import CLASS_FOR_RUN, CLASS_FOR_RUNRESULT, CLASS_FOR_EMCEEPARAMETER
import scipy
import os
import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import chain
import joblib
import multiprocessing
from copy import deepcopy

class State:
    def __init__(self, coords, copy=False):
        self.coords = np.copy(coords) if copy else coords
class Move:
    def get_proposal(self, coords, random_state):
        raise NotImplementedError
    def propose(self, state, random_state):
        raise NotImplementedError
        
class GibbsMHMove(Move):
    def __init__(self, phi, alpha, sp):
        self.phi = phi
        self.alpha = alpha
        self.sp = sp
    def get_proposal(self, coords, random_state):
        return gibbs_proposal_function(coords, random_state, self.phi, self.alpha, self.sp)
    def propose(self, state, random_state):
        q, _ = self.get_proposal(state.coords, random_state)
        new_state = State(q)
        return new_state, np.ones(state.coords.shape[0], dtype=bool)
        
def gibbs_proposal_function(coords, random_state, phi, alpha, sp):
    min_threshold = 1e-6
    updated_coords = np.copy(coords) 
    column_sums = np.sum(phi, axis=0)
    normalized_matrix = phi / column_sums
    G, K = normalized_matrix.shape  # 使用 normalized_matrix 的形状
    for n in range(len(coords)):
        theta_n = updated_coords[n, :]
        prob_mat = np.multiply(normalized_matrix, theta_n)
        Z_n = []
        for g in range(G):
            row_sum = np.sum(prob_mat[g, :])  # 使用 NumPy 方法计算行和
            pvals = np.full(K, 1/K) if row_sum < min_threshold else prob_mat[g, :] / row_sum
            Z_n.append(random_state.multinomial(n=round(sp[g]), pvals=pvals))
        Z_nk = np.sum(Z_n, axis=0)
        alpha_param = Z_nk + alpha
        updated_coords[n, :] = random_state.dirichlet(alpha=alpha_param)
    return updated_coords, np.zeros(len(coords))
    
class EnsembleSampler:
    def __init__(self, nwalkers, ndim, phi_value, alpha_value, sp_value, iterations=1000, seed=42, checkpoint_step=1):
        self.nwalkers = nwalkers
        self.ndim = ndim
        self.iterations = iterations
        self.checkpoint_step = checkpoint_step
        self.phi_value = phi_value
        self.alpha_value = alpha_value
        self.sp_value = sp_value
        self.backend = Backend(nwalkers=nwalkers, ndim=ndim, iterations=iterations)
        self.random_state = np.random.RandomState(seed) 
    def sample(self, initial_state, iterations=1, progress=False, progress_kwargs=None):
        if progress_kwargs is None: 
            progress_kwargs = {} 
        state = State(initial_state, copy=True) 
        total = None if iterations is None else iterations
        with get_progress_bar(progress, total, **progress_kwargs) as pbar:
            i = 0 
            for _ in count() if iterations is None else range(iterations):
                gibbs_move = GibbsMHMove(self.phi_value, self.alpha_value, self.sp_value)
                state, accepted = gibbs_move.propose(state, self.random_state)
                self.backend.chain[i] = state.coords
                pbar.update(1) 
                i += 1
                yield state 
    def run_mcmc(self, initial_state, nsteps, **kwargs):
        for _ in self.sample(initial_state, iterations=nsteps, **kwargs):
            pass
        return self.backend.chain
    def get_chain(self, discard=0, flat=False, thin=1):
        chain = self.backend.chain[discard::thin] 
        if flat:
            return chain.reshape(-1, self.ndim) 
        return chain 
        
class Backend:
    def __init__(self, nwalkers, ndim, iterations):
        self.nwalkers = nwalkers
        self.ndim = ndim
        self.iteration = iterations
        self.chain = np.zeros((iterations, nwalkers, ndim))
        self.iteration = 0
    def save_step(self, state):
        self.chain[self.iteration, :, :] = state.coords
        self.iteration += 1
    def get_chain(self):
        return self.chain

class _NoOpPBar(object):
    def __init__(self):
        pass
    def __enter__(self, *args, **kwargs):
        return self
    def __exit__(self, *args, **kwargs):
        pass
    def update(self, count):
        pass

def get_progress_bar(display, total, **kwargs):
    if display:
        if tqdm is None:
            logger.warning(
                "You must install the tqdm library to use progress"
            )
            return _NoOpPBar()
        else:
            if display is True:
                return tqdm.tqdm(total=total, **kwargs)
            else:
                return getattr(tqdm, "tqdm_" + display)(total=total, **kwargs)
    return _NoOpPBar()

'''
def mcse_python(samples):
    n_iter, n_dim = samples.shape
    mcse_vec = np.empty(n_dim)
    for k in range(n_dim):
        x = samples[:, k]
        rho = np.correlate(x - x.mean(), x - x.mean(), mode='full')
        rho = rho[n_iter - 1:] / rho[n_iter - 1]
        lag = next((i for i, r in enumerate(rho[1:], 1) if r < 0.05), n_iter)
        ess = n_iter / (1 + 2 * rho[1:lag + 1].sum())
        mcse_vec[k] = np.std(x, ddof=1) / np.sqrt(ess)
    return mcse_vec '''

def mcse_python(segment):
    return np.std(segment, axis=0) / np.sqrt(len(segment))

def ThreadRunEachSamples( 
    EmceeParameters = None, 
    referenceMatrix = None, 
    SampleExpressionData = None, 
    SampleName=None, 
    seed=None, 
    MAPorMLE = ('MAP','MLE'), 
    *args): 
    samplename = SampleName
    phi_value = referenceMatrix 
    alpha_value = 1 
    sp_value = SampleExpressionData 
    K = EmceeParameters.ndims 
    rng = np.random.RandomState(seed)
    max_iter   = EmceeParameters.nsteps
    nwalkers = EmceeParameters.nwalkers
    tol_ratio  = 0.01
    eval_step  = 50
    theta = EmceeParameters.position
    if theta.ndim == 1:
        theta = theta.reshape(nwalkers, K)
    else:
        theta = theta[:nwalkers, :K] 
    full_chain = np.zeros((max_iter, nwalkers, K))
    converged = False
    converged_step = None
    for i in range(max_iter): 
        gibbs_move = GibbsMHMove(phi_value, alpha_value, sp_value)
        state, _ = gibbs_move.propose(State(theta), rng)
        theta = state.coords
        full_chain[i] = theta
        if (i + 1) % eval_step == 0 and i + 1 >= eval_step:
            segment = full_chain[(i + 1 - eval_step): (i + 1)].reshape(-1, K)
            mcse_vec = mcse_python(segment) 
            theta_hat = segment.mean(axis=0) 
            theta_hat_safe = np.where(theta_hat == 0, 1e-10, theta_hat) 
            ratio = mcse_vec / theta_hat_safe 
            if np.all(np.abs(ratio) <= tol_ratio):
                converged = True
                converged_step = i + 1 
                break 
    if converged and converged_step is not None:
        start_step = max(0, converged_step - 100)
        truncated_chain = full_chain[start_step:converged_step]
    else:
        start_step = max(0, max_iter - 100) 
        truncated_chain = full_chain[start_step:max_iter]
    flat_samples = truncated_chain.reshape(-1, K) 
    return full_chain, flat_samples     
    
class MultiprocessesResult(object): 
    def __init__(self, SampleName, SamplingResult, CellType): 
        self.SampleName = SampleName 
        self.CellTypeList = CellType 
        self.ResultObjectOne = CLASS_FOR_RUNRESULT( 
            SampleNameList = [ self.SampleName ] , 
            McmcSamplingResultList = np.array([ SamplingResult[0] ]) , 
            FlatSamplingResultList = np.array([ SamplingResult[1] ]) , 
            CellTypeList = CellType
        ) 
      
def MergeResultsForAllSample(ThreadList=list(), OtherParams=[], *args):
    print("Merge all results from deconvolution into one ResultObject...")
    if len(ThreadList) < 1: 
        return CLASS_FOR_RUNRESULT()  
    # Extracting all information from ThreadList
    SampleNames = [threadone.SampleName for threadone in ThreadList]
    FlatSamplings = [threadone.ResultObjectOne.FlatSamplingResult for threadone in ThreadList]
    McmcSamplings = [threadone.ResultObjectOne.McmcSamplingResult for threadone in ThreadList]
    CellTypeRatios = [threadone.ResultObjectOne.CellTypeRatioResult for threadone in ThreadList]
    CellTypeRatioFinals = [threadone.ResultObjectOne.CellTypeRatioResultFinal for threadone in ThreadList]
    # Corrected way to flatten a list of lists
    SampleNameWhole = list(chain.from_iterable(SampleNames)) 
    # Concatenate arrays and dataframes
    FlatSamplingWhole = np.concatenate(FlatSamplings, axis=0) 
    McmcSamplingWhole = np.concatenate(McmcSamplings, axis=0) 
    CellTypeRatioResultWhole = pandas.concat(CellTypeRatios) 
    CellTypeRatioResultFinalWhole = pandas.concat(CellTypeRatioFinals)
    # OtherParams handling
    CellTypeWhole = OtherParams[0]
    FileCellTypeCategory = OtherParams[1]
    # Creating the final merged result object
    MergeResultsObject = CLASS_FOR_RUNRESULT(
        SampleNameList=SampleNameWhole,
        CellTypeList=CellTypeWhole,
        FileCellTypeCategory=FileCellTypeCategory,
        McmcSamplingResultList=McmcSamplingWhole,
        FlatSamplingResultList=FlatSamplingWhole,
        CellTypeRatioResult=CellTypeRatioResultWhole,
        CellTypeRatioResultFinal=CellTypeRatioResultFinalWhole)
    return MergeResultsObject
    
def MainRun(RunObject, seed=42, MultithreadModule = 'joblib'): 
    np.random.seed(seed)
    random.seed(seed)
    EnvironmentRun = RunObject.EnvironmentRun 
    RecordTime = CLASS_FOR_TIME() 
    nsamples = len(RunObject.SampleList) 
    parameterlist = []
    #CelltypesReferenceMatrix = RunObject.CelltypesReferenceMatrix 
    for sample_index in range(nsamples):
        SampleName = RunObject.SampleList[sample_index]
        parameterlist.append((
            (RunObject.EmceeParameter).mycopy(),
            RunObject.CelltypesReferenceMatrix ,
            RunObject.SamplesBulkRNAseqExpression[sample_index],
            RunObject.SampleList[sample_index],
            seed + sample_index, 
            RunObject.MAPorMLE 
        )) 
    #EmceeParameterCopy = RunObject.EmceeParameter.mycopy() 
    MultiprocessingReturnValue = [] 
    if MultithreadModule == 'joblib':
        try: 
            results = joblib.Parallel(n_jobs=int(EnvironmentRun.ThreadNum), backend='loky',verbose=0)(joblib.delayed(ThreadRunEachSamples)(*arg) for arg in parameterlist) 
        except: 
            print('error occurs while paralleling') 
        finally: 
            del parameterlist 
            print('finished all!') 
    elif MultithreadModule == 'multiprocessing':
        with multiprocessing.Pool(processes=int(EnvironmentRun.ThreadNum)) as pool:
            results = pool.starmap(
                ThreadRunEachSamples, 
                [(EmceeParameterCopy, 
                  CelltypesReferenceMatrix, 
                  RunObject.SamplesBulkRNAseqExpression[sample_index], 
                  RunObject.SampleList[sample_index], 
                  seed + sample_index, 
                  RunObject.MAPorMLE
                  ) for sample_index in range(nsamples)]
            )   
    MergedResultObject = MergeResultsForAllSample(
        ThreadList=[MultiprocessesResult(
            RunObject.SampleList[i], 
            result, 
            deepcopy(RunObject.CellType)
        ) for i, result in enumerate(results)],
        OtherParams=[deepcopy(RunObject.CellType), RunObject.FileCellTypeCategory]
    ) 
    RecordTime.ShowCostTime()
    if os.path.exists("TempThread"): 
        os.system("rm -rf TempThread")
    print("###<----Main program Run finished...")
    return MergedResultObject 
