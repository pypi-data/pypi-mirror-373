# -*- coding: utf-8 -*-




import numpy as np
import pandas as pd
import time
from datetime import datetime
import os

from multiprocessing import Pool
from tqdm import tqdm
from contextlib import nullcontext
import tempfile
import functools

import emcee

from .config import (
    MAGMODELPATH,
    INTERPMAGMODELPATH,
    STDMODELPATH,
    INTERPSTDMODELPATH,
    PARSECMODELPATH
    )
from .photometry import MeasuredPhotometry, SyntheticPhotometry
from .simulation import Probability, MCMC
from .target import Target
from .metadata import InitialConditions, Parallax, Moves, PhotometryMetadata, MetaDataFrame
from .utils import app_mag, app_mag_error, mag_to_flux, load_isochrone, WaitingAnimation, sigma


pd.options.display.float_format = '{:.6g}'.format




__all__ = ['Estimate']




def cleanup_cache_on_exception(method):
    """Decorator to cleanup resources if an exception occurs."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            self._cleanup()  # Call the cleanup method
            raise  # Optionally re-raise the exception
    return wrapper




class Estimate(object):
    
    """
    Automates the data gathering and mcmc simulation to estimate the fit parameters.
    
    Parameters
    ----------
    target : str or `Target` object
        The target whose parameters are estimated via MCMC simulation.
    isochrone : str, optional
        If 'mag', uses the isochrone that incorporates the effects of magnetic fields
        (better for young stars). If 'std', uses the standard, non-magnetic isochrone.
        The default is 'mag'.
    interp_method : str, optional
        If 'true', uses the standard interpolation method of DFInterpolator.
        If 'nearest' uses nearest-neighbor interpolation. If 'hybrid' uses
        nearest-neighbor interpolation for age and DFInterpolator for mass.
        The default is 'true'.
    include_params : list, optional
        Which parameters (stellar and/or free parameters) to include in the final output. 
        Fewer parameters may decrease runtime. if `zero_extinction=True`, extinction will
        not be included even if it is listed here. If `None`, all parameters will be included. 
        The default is `None`.
    use_synphot : bool, optional
        Use the built-in synphot methods to calculate extinction or calculate 
        extinction with `numpy` arrays which is faster. The default is `False`.
    zero_extinction : bool, optional
        If `True`, set extinction to zero (Av=0). The default is `False`.
    walker_init_tol : int, optional
        How many attempts should be made to initialize the walker positions
        before the simulation starts? The deault is 1000.
    meas_phot_kwargs : dict, optional
        Keyword arguments to pass to `:class: stelpar.MeasuredPhotometry`.
        The default is `None`.
    pool : `multiprocessing.Pool()` object or similar, optional. 
        This only allows passing a user-controlled pool. 
        Stelpar will try to parallelize regardless. The default is `None`.
    """
    
    def __init__(
            self, 
            target, 
            isochrone='mag', 
            interp_method='true', 
            include_params=None, 
            use_synphot=False,
            zero_extinction=False, 
            walker_init_tol=1000, 
            meas_phot_kwargs=None,
            pool=None,
            ):
        
        ## setup target-specific metadata
        
        # check if target is `Target` object or just string
        if isinstance(target, Target):
            self.target = target.name
            self.coords = target.coords
            
            self._ic = target.initial_conditions.loc[self.target].copy()
            self._user_plx = target.plx
            self._moves = target.moves
            self._phot_meta = target.photometry_meta.copy()
            
        else:
            self.target = target
            self.coords = None
            
            self._ic = InitialConditions().initial_conditions.copy()
            self._user_plx = Parallax().value
            self._moves = Moves().moves
            self._phot_meta = PhotometryMetadata().photometry.copy()
            
            
        ## select the appropriate isochrone model
        
        self._isochrone = isochrone
        self._interp_method = interp_method

        # self._cachedir = CACHEDIR
        self._cachedir = tempfile.TemporaryDirectory()

        
        if self._isochrone.lower() == 'mag':

            gridcachefile = '.grid_cache_mag'
            
            if self._interp_method.lower() == 'true':
                gridpath = MAGMODELPATH
                
            if self._interp_method.lower() == 'nearest' or self._interp_method.lower() == 'hybrid':
                gridpath = INTERPMAGMODELPATH
        
        elif self._isochrone.lower() == 'std':

            gridcachefile = '.grid_cache_std'
            
            if self._interp_method.lower() == 'true':
                gridpath = STDMODELPATH
                
            if self._interp_method.lower() == 'nearest' or self._interp_method.lower() == 'hybrid':
                gridpath = INTERPSTDMODELPATH
        
        elif self._isochrone.lower() == 'parsec':

            gridcachefile = '.grid_cache_par'
            
            if self._interp_method.lower() == 'true':
                raise ValueError(
                    "invalid interpolation method: 'true' interpolation is too slow on the PARSEC grid. "
                    "Choose a different interpolation method or use a different isochrone grid."
                    )
                
            if self._interp_method.lower() == 'nearest' or self._interp_method.lower() == 'hybrid':
                gridpath = PARSECMODELPATH
            
        else:
            raise ValueError(
                "invalid isochrone: can only be 'mag', 'std', or 'parsec'"
                )
        
        
        if self._interp_method.lower() == 'true':
            self._model_grid = load_isochrone(gridpath)
            
            if self._isochrone.lower() == 'parsec':
                isochrone_cols = self._model_grid.columns.values
            else:
                isochrone_cols = None
            
            self._agelist = None
            self._masslist = None
        
        elif self._interp_method.lower() == 'nearest' or self._interp_method.lower() == 'hybrid':
            with WaitingAnimation("loading isochrone model grid", delay=0.5):
                grid = load_isochrone(gridpath)
                print('')
                
            self._agelist = grid.index.get_level_values('age').drop_duplicates()
            
            if self._isochrone.lower() == 'parsec':
                isochrone_cols = grid.columns.values
                self._masslist = None
            else:
                isochrone_cols = None
                self._masslist = grid.index.get_level_values('mass').drop_duplicates()

            gridcache = os.path.join(self._cachedir.name, gridcachefile)
            
            grid.to_pickle(gridcache)
            
            del grid
            
            self._model_grid = gridcache
            

        ## if an error occurs in any of this, clear the cache    
        try:
            ## check if synphot is going to be used for the extinction calculation
        
            self._use_synphot = use_synphot
            
            
            ## check if extinction is going to be set to zero
            
            self._zero_extinction = zero_extinction


            ## which parameters will be included in the final output

            self._default_params = ['age', 'mass', 'Av', 'f', 'Teff', 'logg', 'logL', 'radius', 'density']
            if include_params is not None:

                if not set(include_params).issubset(set(self._default_params)):
                    raise KeyError(
                        "Invalid parameter(s) in `include_params`. "
                        f"Possible parameters include {self._default_params}."
                        )
                
                self._params = include_params
            
            else:
                self._params = self._default_params

            if self._zero_extinction:
                self._params = [p for p in self._params if p!='Av']
            
            
            ## check the walker positions initialization tolerance
            
            self._walker_init_tol = walker_init_tol
            
            
            ## handle any kwargs for MeasuredPhotometry
            
            if meas_phot_kwargs is None:
                self._meas_phot_kwargs = dict()
            else:
                self._meas_phot_kwargs = meas_phot_kwargs
                
            
            ## collect data, initialize classes, and setup functions
            
            self._mp = MeasuredPhotometry(
                self.target,
                self.coords,
                photometry_meta=self._phot_meta,
                user_plx=self._user_plx,
                isochrone_cols=isochrone_cols,
                **self._meas_phot_kwargs
            )
            
            self.photometry, self._termination_message = self._mp.get_data()
            
            if self.photometry is False:
                self._sp, self._prob, self.log_prob_fn = False, False, False
                
            else:
                self._sp = SyntheticPhotometry(
                    self.photometry, 
                    model_grid=self._model_grid, 
                    interp_method=self._interp_method,
                    extinction_kwargs={'use_synphot':self._use_synphot}, 
                    interp_kwargs={'agelist':self._agelist, 'masslist':self._masslist}
                    )
                
                self._prob = Probability(self.photometry, self._sp.photometry_model, self._ic, zero_extinction=self._zero_extinction)
                
                self.log_prob_fn = self._prob.log_probability
            
            if pool is None:
                self._pool = Pool()
            else:
                self._pool = pool
            
            
            ## metadata parameters for output
            
            self._run_date = None
            self._sim_runtime = None
            self._posterior_extract_time = None
            
            
            ## EstimateResults object to store results
            
            self.results = EstimateResults(
                target=target,
                options={
                    'isochrone' : self._isochrone,
                    'interp_method' : self._interp_method,
                    'use_synphot' : self._use_synphot,
                    'zero_extinction' : self._zero_extinction,
                    'walker_init_tol' : self._walker_init_tol,
                    'meas_phot_kwargs' : self._meas_phot_kwargs,
                    }
                )
        
        except:
            self._cleanup()
            raise
        
        
        
    
    @cleanup_cache_on_exception
    def run(self, nwalkers, nsteps, progress=True, verbose=True, backend=None):
        """
        Wrapper for `stelpar.MCMC.run` which runs MCMC simulation using `emcee`.

        Parameters
        ----------
        nwalkers : int
            The number of independent walkers in the simulation chain.
        nsteps : int
            The number of iterations of the simulation.
        progress : bool, optional
            If `True`, provides a progress bar during the sumulation.  The default is `True`.
        verbose : bool, optional
            If `True`, outputs the current status of the simulation.
            The defauls is `True`.
        backend : emcee.backends.HDFBackend, optional
            Backend to save progress of MCMC. 
            See https://emcee.readthedocs.io/en/stable/tutorials/monitor/ for more information.
            The default is `None`.

        Returns
        -------
        sampler : EnsembleSampler
            `emcee.EnsembleSampler` object containing all estimated values and metadata from the simulation.

        """
        
        self._run_date = datetime.today().strftime('%Y%m%d')
        start = time.time()
        
        
        if self.photometry is False:
            print(self._termination_message)
            
            return False
        
        if verbose:
            print(f"\nrunning MCMC for {self.target:s} ({self._isochrone:s}):")
            walker_context = WaitingAnimation("initializing walker positions", delay=0.5)
        else:
            walker_context = nullcontext()
            
        time.sleep(1)
        
        mcmc = MCMC(
            nwalkers, 
            nsteps, 
            self.log_prob_fn, 
            self._ic, 
            self._moves, 
            pool=self._pool, 
            zero_extinction=self._zero_extinction, 
            walker_init_tol=self._walker_init_tol, 
            walker_init_context=walker_context,
            backend=backend
        )
        
        mcmc.run(progress=progress)
        
        time.sleep(1)
        
        sampler = mcmc.sampler
        
        
        stop = time.time()
        delta = stop-start
        self._sim_runtime = time.strftime('%H:%M:%S', time.gmtime(delta))
        
        
        options = self.results.options
        options.update(nwalkers=nwalkers, nsteps=nsteps)
        
        self.results.add_kwarg(
            options=options,
            sampler=sampler,
            stats={
                'mean_acceptance_frac' : float(f'{np.mean(sampler.acceptance_fraction):.3f}'),
                'median_autocorr_time' : float(f'{np.median(sampler.get_autocorr_time(tol=0)):.3f}'),
                'date' : self._run_date,
                'sim_runtime' : self._sim_runtime
                }
            )
        
        
        
        return sampler
        
        
        
    
    @cleanup_cache_on_exception
    def posterior(self, sampler, thin=1, discard=0, max_prob=False, force_true_interp=False, verbose=True):
        """
        Calculates full posterior distributions for the fit parameters and others, including radius, Teff, and density. 
        Interpolates estimated magnitudes from age and mass obtained from fit.
        See https://emcee.readthedocs.io/en/stable/tutorials/line/ for more general information.

        Parameters
        ----------
        sampler : EnsembleSampler
            `emcee.EnsembleSampler` object containing all estimated values and metadata from the simulation.
        thin : int, optional
            Use every `thin` values of the posterior. The defualt is 1.
        discard : int, optional
            Remove (burnin) the first `discard` elements from the posterior.
            The defult is 0.
        max_prob : bool, optional
            Whether to calculate maximum-probability parameters. This can be computationally expensive.
            The default is `False`.
        force_true_interp : bool, optional
            If `True`, the non-fit chains are interpolated using the 'true' interpolation
            method. If `False` (default), uses the same interpolation method as the
            MCMC simulation.
        verbose : bool, optional
            If `True`, uses print statements to indicate the current status of the simulation.
            The defauls is `True`.

        Returns
        -------
        posterior : stelpar.metadata.MetaDataFrame
            The estimated fit parameters and other stellar parameters, including uncertainties.
        photometry : stelpar.metadata.MetaDataFrame
            The measured and estimated magnitudes and other photometric data.
        posterior_chains : stelpar.metadata.MetaDataFrame
            The flattened lists of estimated or interpolated values of each parameter (including non-fit parameters) 
            at every step of the simulation (i.e., the posterior distributions).

        """
        
        start = time.time()
        
        
        if sampler is False:
            return False, False, False
        
        if verbose:
            print(f"\nextracting posterior for {self.target:s} ({self._isochrone:s}):")
        
        samples = sampler.get_chain
            
            
        try:
            flat_samples = samples(discard=discard, thin=thin, flat=True)
        except ValueError:
            flat_samples = samples(flat=True)
        
        
        if max_prob:
            if verbose:
                print("\ncalculating max log probability:")
            
            log_prob, max_prob_index = self._max_log_probability(flat_samples)
        
        
        if self._zero_extinction:
            posterior_chains = pd.DataFrame(flat_samples, columns=['age', 'mass', 'f'])
            
        else:
            posterior_chains = pd.DataFrame(flat_samples, columns=['age', 'mass', 'Av', 'f'])
        
        
        if verbose:
            print("\ngetting other parameter chains:")
            
            
            
        if force_true_interp:
            if self._interp_method == 'true':
                sp = self._sp
            
            else:
                if self._isochrone.lower() == 'mag':
                    grid = load_isochrone(MAGMODELPATH)
                    
                elif self._isochrone.lower() == 'std':
                    grid = load_isochrone(STDMODELPATH)
                    
                sp = SyntheticPhotometry(
                    self.photometry,
                    model_grid=grid,
                    interp_method='true'
                    )
                
        else:
            sp = self._sp
        
        
        ## get the posterior chains of the non-fit parameters

        other_params = [p for p in self._params if p not in ['age', 'mass', 'Av', 'f', 'density']]

        if len(other_params) > 0:
            
            # try to use pool to parallelize this if possible
            if self._pool is None:
                
                posterior_chains[other_params] = pd.concat(
                    [sp.interpolate_isochrone((posterior_chains['age'][i], posterior_chains['mass'][i])).loc[(posterior_chains['age'][i], posterior_chains['mass'][i]), other_params]
                    for i in tqdm(range(len(flat_samples)))],
                    ignore_index=True)
            else:
                
                map_func = self._pool.imap
            
                time.sleep(1)
                
                posterior_chains[other_params] = pd.concat(
                    list(
                        res.loc[:, other_params] for res in tqdm(
                            map_func(
                                sp.interpolate_isochrone, 
                                ((posterior_chains['age'][i], posterior_chains['mass'][i]) for i in range(len(posterior_chains)))
                                ), total=len(posterior_chains)
                            )
                        ), 
                    ignore_index=True
                    )
        
                time.sleep(1)
        

        if 'density' in self._params:
            posterior_chains['density'] = posterior_chains['mass'] / (posterior_chains['radius']**3)
        
        posterior = pd.DataFrame(index=self._params)
        
        # calculate the median value (50th percentile), and upper and lower confidence 
        # (84th and 16th percentiles) for each parameter
        for p in self._params:
            mc = np.nanpercentile(posterior_chains[p], [16, 50, 84])
            q = np.diff(mc)
            
            posterior.loc[p, 'median'] = mc[1]

            if max_prob:
                posterior.loc[p, 'max_probability'] = posterior_chains.loc[max_prob_index, p]
            
            posterior.loc[p, 'uncertainty'] = np.mean([q[0], q[1]])
            posterior.loc[p, '+'] = q[1]
            posterior.loc[p, '-'] = q[0]
            
        posterior.index.names = ['parameter']
            
            
        if self._zero_extinction:
            # value of Av here doesn't matter as long as `zero_extinction=True`
            median_photometry_model, teff_lp = self._sp.photometry_model(posterior.loc['age', 'median'], posterior.loc['mass', 'median'], 0, zero_extinction=self._zero_extinction)
            if max_prob:
                max_prob_photometry_model, teff_lp = self._sp.photometry_model(posterior.loc['age', 'max_probability'], posterior.loc['mass', 'max_probability'], 0, zero_extinction=self._zero_extinction)
            
        else:
            median_photometry_model, teff_lp = self._sp.photometry_model(posterior.loc['age', 'median'], posterior.loc['mass', 'median'], posterior.loc['Av', 'median'])
            if max_prob:
                max_prob_photometry_model, teff_lp = self._sp.photometry_model(posterior.loc['age', 'max_probability'], posterior.loc['mass', 'max_probability'], posterior.loc['Av', 'max_probability'])
        
        
        photometry = self.photometry
        
        med_f_abs = posterior.loc['f', 'median']
        if max_prob:
            max_f_abs = posterior.loc['f', 'max_probability']
        
        
        if median_photometry_model is not False:
            
            photometry = photometry.assign(
                MEDIAN_ABSOLUTE_MAGNITUDE=median_photometry_model['CORRECTED_MAGNITUDE'],
                MEDIAN_ABSOLUTE_MAGNITUDE_ERROR=lambda x: x['ABSOLUTE_MAGNITUDE_ERROR'].apply(sigma, args=([med_f_abs])),
                median_apparent_magnitude=lambda x: x['MEDIAN_ABSOLUTE_MAGNITUDE'].apply(app_mag, args=([x['parallax'].values[0]])),
                median_apparent_magnitude_error=lambda x: x['MEDIAN_ABSOLUTE_MAGNITUDE_ERROR'].apply(app_mag_error, args=([x['parallax'].values[0], x['parallax_error'].values[0]]))
            )

            
            for band in photometry.index:
                photometry.loc[(band, ['median_flux', 'median_flux_error'])] = mag_to_flux(*photometry.loc[(band, ['median_apparent_magnitude', 'zeropoint_flux', 'median_apparent_magnitude_error'])])

            photometry['median_percent_error'] = 100 * np.abs((photometry['flux'] - photometry['median_flux']) / photometry['flux'])
        
        
        if max_prob and max_prob_photometry_model is not False:

            photometry = photometry.assign(
                MAX_PROBABILITY_ABSOLUTE_MAGNITUDE=median_photometry_model['CORRECTED_MAGNITUDE'],
                MAX_PROBABILITY_ABSOLUTE_MAGNITUDE_ERROR=lambda x: x['ABSOLUTE_MAGNITUDE_ERROR'].apply(sigma, args=([max_f_abs])),
                max_probability_apparent_magnitude=lambda x: x['MAX_PROBABILITY_ABSOLUTE_MAGNITUDE'].apply(app_mag, args=([x['parallax'].values[0]])),
                max_probability_apparent_magnitude_error=lambda x: x['MAX_PROBABILITY_ABSOLUTE_MAGNITUDE_ERROR'].apply(app_mag_error, args=([x['parallax'].values[0], x['parallax_error'].values[0]]))
            )
        
            for band in photometry.index:
                photometry.loc[(band, ['max_probability_flux', 'max_probability_flux_error'])] = mag_to_flux(*photometry.loc[(band, ['max_probability_apparent_magnitude', 'zeropoint_flux', 'max_probability_apparent_magnitude_error'])])
        
            photometry['max_probability_percent_error'] = 100 * np.abs((photometry['flux'] - photometry['max_probability_flux']) / photometry['flux'])
        
            
        # percent errors should be the same between apparent and ABSOLUTE
        
        photometry.index.names = ['band']
        
        
        ## apply metadata
        
        stop = time.time()
        delta = stop-start
        self._posterior_extract_time = time.strftime('%H:%M:%S', time.gmtime(delta))
        
        
        metadata = {
            'target' : self.target,
            'coordinates' : self.coords,
            'isochrone' : self._isochrone,
            'interp_method' : self._interp_method,
            'use_synphot' : self._use_synphot,
            'zero_extinction' : self._zero_extinction,
            'force_posterior_true_interp' : force_true_interp,
            'nwalkers' : sampler.nwalkers,
            'nsteps' : len(samples()),
            'discard' : discard,
            'thin' : thin,
            'mean_acceptance_frac' : float(f'{np.mean(sampler.acceptance_fraction):.3f}'),
            'median_autocorr_time' : float(f'{np.median(sampler.get_autocorr_time(tol=0)):.3f}'),
            'date' : self._run_date,
            'sim_runtime' : self._sim_runtime,
            'posterior_extract_time' : self._posterior_extract_time
            }
        
        posterior = MetaDataFrame(posterior.copy(), meta_base_type='posterior', metadata=metadata)
        photometry = MetaDataFrame(photometry.copy(), meta_base_type='photometry', metadata=metadata)
        posterior_chains = MetaDataFrame(posterior_chains.copy(), meta_base_type='chains', metadata=metadata)
        
        
        options = self.results.options
        options.update(discard=discard, thin=thin, force_posterior_true_interp=force_true_interp)
        stats = self.results.stats
        stats.update(posterior_extract_time=self._posterior_extract_time)
        
        self.results.add_kwarg(
            posterior=posterior,
            photometry=photometry,
            chains=posterior_chains,
            options=options,
            stats=stats
            )
        
        
        return posterior, photometry, posterior_chains
        
        
        
    
    def _max_log_probability(self, coords, progress=True):
        """
        Returns the maximum of the caluclated log probabilities and its index. 
        Simplified version of :func: `emcee.EnsembleSampler.compute_log_prob`
        for this use case (no need for blobs).
        
        Parameters
        ----------
        coords : numpy.ndarray
            The position matrix in parameter space for each fit parameter.
        progress : bool, optional
            If `True`, provides a progress bar during the calculation. The default is True.
            
        Returns
        -------
        log_prob : array
            The list of calculated log-probability for each coordinate.
        max_log_prob_index : int
            The index where `log_prob` is maximized.
        
        """
        
        p = coords
        
        
        if progress and self._pool is not None:
            map_func = self._pool.imap
            # imap gives tqdm an iterable
        elif not progress and self._pool is not None:
            map_func = self._pool.map
        else:
            map_func = map
            
            
        if progress:
            time.sleep(1)
            
            results = list(res for res in tqdm(map_func(self.log_prob_fn, [r for r in p]), total=len(p)))
            
            time.sleep(1)
        else:
            results = list(map_func(self.log_prob_fn, (p[i] for i in range(len(p)))))
            
            
        log_prob = np.array([float(l) for l in results])
        
        if np.any(np.isnan(log_prob)):
            raise ValueError("Probability function returned NaN")
            
           
        
        max_log_prob_index = np.argmax(log_prob)
        
        
        return log_prob, max_log_prob_index
    
    
    
    
    def _get_log_likelihoods(self, coords, progress=True):
        """
        Returns a distribution of log-likelihood values from a given simulation.
        Calculates the likelihoods in an analogous way to `self._max_log_probability`.
        
        Parameters
        ----------
        coords : numpy.ndarray
            The position matrix in parameter space for each fit parameter.
        progress : bool, optional
            If `True`, provides a progress bar during the calculation. The default is True.
            
        Returns
        -------
        log_likelihood : array
            The list of calculated log-likelihood for each coordinate.
        
        """
        
        p = coords
        
        
        if progress and self._pool is not None:
            map_func = self._pool.imap
            # imap gives tqdm an iterable
        elif not progress and self._pool is not None:
            map_func = self._pool.map
        else:
            map_func = map
            
            
        if progress:
            time.sleep(1)
            
            results = list(res for res in tqdm(map_func(self._prob.log_likelihood, [r for r in p]), total=len(p)))
            
            time.sleep(1)
        else:
            results = list(map_func(self._prob.log_likelihood, (p[i] for i in range(len(p)))))
            
        log_likelihood = np.array([float(l) for l in results])
        
        if np.any(np.isnan(log_likelihood)):
            raise ValueError("Likelihood function returned NaN")
            
           
        
        return log_likelihood
    

    def __del__(self):

        self._cleanup()
    

    def _cleanup(self):

        self._cachedir.cleanup()
    
    
    
    
class EstimateResults(object):
    
    
    
    def __init__(
            self, 
            target=None, 
            sampler=None, 
            posterior=None, 
            photometry=None, 
            chains=None, 
            options=None, 
            stats=None
            ):
        
        self._input = dict()
        self._output = dict()
        
        self._input['target'] = target
        self._input['options'] = options
        
        self._output['sampler'] = sampler
        self._output['posterior'] = posterior
        self._output['photometry'] = photometry
        self._output['chains'] = chains
        self._output['stats'] = stats
        
        
        
        
    def __repr__(self):
        
        target = self.target
        if isinstance(target, str):
            target_repr = f"{target!r}"
        elif isinstance(target, Target):
            target_repr = f"<{target.__class__.__module__}.{target.__repr__()}>"
        elif target is None:
            target_repr = repr(target)
            
        sampler = self.sampler
        if isinstance(sampler, emcee.EnsembleSampler):
            sampler_repr = f"<{sampler.__class__.__module__}.{sampler.__class__.__name__}>"
        elif sampler is None:
            sampler_repr = f"{sampler!r}"
            
        posterior = self.posterior
        if isinstance(posterior, pd.DataFrame):
            posterior_repr = (f"<{posterior.__class__.__module__}.{posterior.__class__.__name__} "
                              f"[{posterior.shape[0]} rows x {posterior.shape[1]} columns]>"
                              )
        elif posterior is None:
            posterior_repr = f"{posterior!r}"
            
        photometry = self.photometry
        if isinstance(photometry, pd.DataFrame):
            photometry_repr = (f"<{photometry.__class__.__module__}.{photometry.__class__.__name__} "
                              f"[{photometry.shape[0]} rows x {photometry.shape[1]} columns]>"
                              )
        elif photometry is None:
            photometry_repr = f"{photometry!r}"
            
        chains = self.chains
        if isinstance(chains, pd.DataFrame):
            chains_repr = (f"<{chains.__class__.__module__}.{chains.__class__.__name__} "
                              f"[{chains.shape[0]} rows x {chains.shape[1]} columns]>"
                              )
        elif chains is None:
            chains_repr = f"{chains!r}"
        
        return (
            f"{self.__class__.__name__}"
            "("
            f"target={target_repr}, "
            f"sampler={sampler_repr}, "
            f"posterior={posterior_repr}, "
            f"photometry={photometry_repr}, "
            f"chains={chains_repr}"
            ")"
            )
    
    
    
    
    def __str__(self):
        
        units = {
            'age' : 'Myr',
            'mass' : 'M_Sun',
            'Av' : 'mag',
            'f' : 'mag',
            'Teff' : 'K',
            'radius' : 'R_Sun',
            'logg' : 'log(cm/s^2)',
            'logL' : 'log(L_Sun)',
            'density' : 'M_Sun/R_Sun^3'
            }
        
        
        target = self.target
        if isinstance(target, str):
            target_info = f"{target!r}"
            prior_info = ''
            bounds_info = ''
        elif isinstance(target, Target):
            if target.coords is None:
                target_info = f"{target.name!r}"
            else:
                target_info = f"{target.name!r} at [{target.coords.to_string(style='hmsdms')}]"
            
            prior_info = '\n - priors:'
            priors = target.initial_conditions.prior.loc[target.name]
            useful_priors = [(param, *priors.loc[param], units[param]) for param in priors.index if np.nan not in priors.loc[param]]
            for tup in useful_priors:
                prior_info = prior_info + f"\n   - {tup[0]}: {tup[1]} +/- {tup[2]} {tup[3]}"
            
            bounds_info = '\n - bounds:'
            bounds = target.initial_conditions.loc[target.name, 'bounds']
            useful_bounds = [(param, *bounds.loc[param], units[param]) for param in bounds.index]
            for tup in useful_bounds:
                bounds_info = bounds_info + f"\n   - {tup[0]}: ({tup[1]}, {tup[2]}) {tup[3]}"
            
        elif target is None:
            return "\nNo results"
        
        options = self.options
        if options is None:
            options_info = ''
        else:
            options_info = ''
            for key in options:
                if type(options[key]) is not dict:
                    options_info = options_info + f"\n - {key}: {options[key]!r}"
                else:
                    options_info = options_info + f"\n - {key}:"
                    for subkey in options[key]:
                        options_info  = options_info + f"\n   - {subkey}: {options[key][subkey]!r}"
                        
        stats = self.stats
        if stats is None:
            stats_info = ''
        else:
            stats_info = '\n - stats:'
            for key in stats:
                stats_info = stats_info + f"\n   - {key}: {stats[key]!r}"
                
        photometry = self.photometry
        if photometry is None or photometry is False:
            bands_info = ''
        else:
            bands_info = f'\n - bands ({len(photometry.index)}):'
            for band in photometry.index:
                bands_info = bands_info + f"\n   - {band!r}"
        
        posterior = self.posterior
        if posterior is None or posterior is False:
            params_info = ''
        else:
            params_info = '\n - stellar parameters:'
            for param in posterior.index:
                params_info = params_info + (
                    f"\n   - {param}: {posterior.loc[param, 'median']:.3g} "
                    f"+/- {posterior.loc[param, 'uncertainty']:.3g} {units[param]}"
                    )
        
            
        
        return (
            f"\n{self.__class__.__name__} for {target_info}"
            "\n\n"
            "** Setup **"
            f"\n{options_info}"
            f"\n{prior_info}"
            f"\n{bounds_info}"
            "\n\n"
            "** Results **"
            f"\n{stats_info}"
            f"\n{bands_info}"
            f"\n{params_info}"
            "\n\n"
            "*****************************************************"
            )
    
    
    
    
    @property
    def target(self):
        
        return self._input['target']
    
    
    
    
    @property
    def options(self):
        
        return self._input['options']
    
    
    
    
    @property
    def sampler(self):
        
        return self._output['sampler']
    
    
    
    
    @property
    def posterior(self):
        
        return self._output['posterior']
    
    
    
    
    @property
    def photometry(self):
        
        return self._output['photometry']
    
    
    
    
    @property
    def chains(self):
        
        return self._output['chains']
    
    
    
    
    # alias of self.chains
    @property
    def posterior_chains(self):
        
        return self.chains
    
    
    
    
    @property
    def stats(self):
        
        return self._output['stats']
    
    
    
    
    def add_kwarg(self, **kwargs):
        
        for kw in kwargs:
            if kw in self._input.keys():
                self._input[kw] = kwargs[kw]
            elif kw in self._output.keys():
                self._output[kw] = kwargs[kw]
            else:
                raise KeyError(
                    f"{kw!r} not a valid keyword argument"
                    )



















