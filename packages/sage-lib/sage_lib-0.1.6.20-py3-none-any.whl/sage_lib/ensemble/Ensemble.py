from __future__ import annotations
from typing import Dict, Optional, Sequence, Tuple
import os, time

import numpy as np
from scipy.stats import entropy
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans

import unittest

import copy
from joblib import Parallel, delayed, parallel_backend
from tqdm import tqdm

from sage_lib.partition.Partition import Partition 
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge

_EPS = 1e-12

class Ensemble:
    """
    Container for managing and comparing sets of vibrational‐mode ensembles,
    with utilities for Boltzmann weighting, information‐theoretic metrics,
    and weighted k‐means clustering.
    """

    def __init__(self, global_classification:bool=True, weights_mode:str='boltzmann') -> None:
        """
        Initialize an empty Ensemble container.
        """
        self.ensembles: List[Partition] = []  # each entry is a Partition instance
        # attributes created after initial global fit
        self._global_labels: Optional[np.ndarray] = None
        self._n_clusters: Optional[int] = None
        self.global_classification = global_classification
        self.weights_mode = weights_mode

    def add_ensemble(self, data: object) -> None:
        """
        Add a new ensemble to the container.

        Parameters
        ----------
        data : np.ndarray
            Array of vibrational data (e.g., frequencies or mode amplitudes).
        """
        self.ensembles.append(data) 

    def read_ensembles(self, ensembles_path: Optional[Dict[str, str]] = None) -> None:
        """
        Load ensemble data from disk for all registered file paths.

        Parameters
        ----------
        ensembles_path : Optional[Dict[str, str]]
            If provided, overrides `self.ensembles_path`. Keys are ensemble
            identifiers and values are file paths.

        Notes
        -----
        This method assumes each file at `file_path` can be read into a
        NumPy array via `np.loadtxt`. Adjust as needed for other formats.
        """
        PT = Partition()
        PT.read_files( file_location=ensembles_path, verbose=True, )
        self.add_ensemble( PT )

    @staticmethod
    def boltzmann_weights_raw(energies: Sequence[float], temperature: float, kB:float=1.0) -> np.ndarray:
        """
        Compute unnormalized Boltzmann weights for a set of energies.

        Parameters
        ----------
        energies : Sequence[float]
            Energies (E_i) in the same units as k_B * T.
        temperature : float
            Absolute temperature (same units as energies / k_B).

        Returns
        -------
        np.ndarray
            Array of weights ∝ exp(–E_i / (k_B T)). Not normalized.
        """
        energies = np.asarray(energies, dtype=float)
        beta = 1.0 / (kB * (temperature + _EPS))
        return np.exp(-beta * energies)

    @staticmethod
    def shannon_conditional(mass: np.ndarray) -> float:
        """
        Compute the Shannon entropy of a non‐normalized distribution.

        H = –∑ p_i log p_i, where p_i = mass_i / ∑ mass_i.

        Parameters
        ----------
        mass : np.ndarray
            Array of nonnegative weights.

        Returns
        -------
        float
            Shannon entropy in nats.
        """
        total = mass.sum() + 1e-20
        p = mass / total
        p = np.clip(p, 1e-12, None)
        return entropy(p, base=np.e)

    @staticmethod
    def shared_new_abs(
        massA: np.ndarray, massB: np.ndarray
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float]]:
        """
        Compute shared and unique mass fractions between two ensembles.

        The output is:
          – (shared_fraction, newA_fraction, newB_fraction)
          – (fraction_A_total, fraction_B_total)

        Parameters
        ----------
        massA : np.ndarray
            Weights for ensemble A.
        massB : np.ndarray
            Weights for ensemble B.

        Returns
        -------
        Tuple[Tuple[float, float, float], Tuple[float, float]]
        """
        W_A = massA.sum()
        W_B = massB.sum()
        W = W_A + W_B
        shared_raw = np.minimum(massA, massB).sum()
        newA_raw = W_A - shared_raw
        newB_raw = W_B - shared_raw
        return (shared_raw / W, newA_raw / W, newB_raw / W), (W_A / W, W_B / W)


    @staticmethod
    def jsd_abs(massA: np.ndarray, massB: np.ndarray, attenuation:bool=False) -> float:
        """
        Compute the attenuated Jensen–Shannon divergence between two mass distributions.

        JSD_abs = (W_A/W)*(W_B/W) * JSD(PA, PB)
        where PA and PB are normalized distributions.

        Parameters
        ----------
        massA : np.ndarray
            Weights for ensemble A.
        massB : np.ndarray
            Weights for ensemble B.

        Returns
        -------
        float
            Attenuated Jensen–Shannon divergence.
        """
        W_A = massA.sum()
        W_B = massB.sum()
        W = W_A + W_B

        PA = massA / (W_A + 1e-20)
        PB = massB / (W_B + 1e-20)
        M = 0.5 * (PA + PB)

        klA = np.sum(PA * np.log((PA + 1e-12) / (M + 1e-12)))
        klB = np.sum(PB * np.log((PB + 1e-12) / (M + 1e-12)))
        J = 0.5 * (klA + klB)

        return (W_A / W) * (W_B / W) * J if attenuation else J

    # ------------------------------------------------------------------
    # Smooth clustering interface
    # ------------------------------------------------------------------

    def initialise_global_clustering(
        self,
        freqs: np.ndarray,
        n_clusters: int = 500,
        random_state: int = 42,
        batch_size: int = 2048,
    ) -> None:
        """Fit a single temperature‑independent K‑means model."""
        X = freqs

        #km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        #km.fit(X)
        mbk = MiniBatchKMeans(
            n_clusters=n_clusters,
            batch_size=batch_size,
            random_state=random_state,
            max_no_improvement=10,
            verbose=0
        )

        mbk.fit(X)
        self._n_clusters = int(mbk.n_clusters)
        self._global_labels = mbk.labels_.astype(np.int64, copy=False)
        #self._global_labels = km.labels_
        #self._n_clusters = n_clusters

    def _cluster_masses_fixed(self, w: np.ndarray, L: np.ndarray) -> np.ndarray:
        """Accumulate weights per global cluster index."""
        L = np.asarray(L, dtype=np.int64)
        w = np.asarray(w, dtype=np.float64)

        # length must be the global number of clusters
        if self._n_clusters is None:
            # fallback: infer from labels if global clustering not initialised
            k = int(L.max()) + 1 if L.size else 0
        else:
            k = int(self._n_clusters)

        # (defensive) ensure all labels < k
        if L.size and L.max() >= k:
            # clip rather than crash; optionally log a warning
            L = np.minimum(L, k - 1)

        return np.bincount(L, weights=w, minlength=k)


    def kmeans_weighted_abs(
        self,
        freqs_A: np.ndarray,
        freqs_B: np.ndarray,
        E_A: Sequence[float],
        E_B: Sequence[float],
        T: float,
        n_clusters: int = 50,
        random_state: int = 0,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform weighted k‐means clustering on two ensembles.

        Clusters are formed over the concatenated frequency arrays,
        with sample weights given by the unnormalized Boltzmann weights.

        Parameters
        ----------
        freqs_A : np.ndarray
            Feature matrix for ensemble A (shape: n_A × d).
        freqs_B : np.ndarray
            Feature matrix for ensemble B (shape: n_B × d).
        E_A : Sequence[float]
            Energy values for A (length n_A).
        E_B : Sequence[float]
            Energy values for B (length n_B).
        T : float
            Temperature for Boltzmann weighting.
        n_clusters : int, optional
            Number of clusters (default: 50).
        random_state : int, optional
            Random seed for reproducibility (default: 0).

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Arrays of cluster‐mass weights for A and B (each length n_clusters).
        """
        # Compute raw (unnormalized) Boltzmann weights
        energies = np.concatenate([E_A, E_B])
        weights = self.boltzmann_weights_raw(energies, T)
        wA, wB = weights[: len(E_A)], weights[len(E_A) :]

        # Stack feature vectors and weights
        X = np.vstack([freqs_A, freqs_B])
        sample_weights = np.concatenate([wA, wB])

        # Fit weighted k-means
        km = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            n_init=5,
        )
        sample_weights = np.nan_to_num(sample_weights, nan=0.0)
        if np.sum(sample_weights) < 1e-8:
            sample_weights = np.ones_like(sample_weights)

        km.fit(X, sample_weight=sample_weights)
        labels = km.labels_

        # Separate labels and compute cluster masses
        LA = labels[: len(freqs_A)]
        LB = labels[len(freqs_A) :]
        massA = np.bincount(LA, weights=wA, minlength=n_clusters)
        massB = np.bincount(LB, weights=wB, minlength=n_clusters)

        return massA, massB

    def evaluate_over_mus(
        self,
        Ef_A_all: np.ndarray,
        Ef_B_all: np.ndarray,
        counts_A: np.ndarray,
        counts_B: np.ndarray,
        LA: np.ndarray,
        LB: np.ndarray,
        temperature_array: np.ndarray,
        n_jobs: int = 4,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        nT, nM = temperature_array.size, Ef_A_all.shape[1]
        mats = [np.empty((nT, nM)) for _ in range(8)]

        def _compute_metrics(j: int):
            EfA_col = Ef_A_all[:, j]
            EfB_col = Ef_B_all[:, j]
            out = np.empty((8, nT))
            for i, T in enumerate(temperature_array):
                out[:, i] = self.estimate_metrics(
                    freqs_A=counts_A,
                    freqs_B=counts_B,
                    energies_A=EfA_col,
                    energies_B=EfB_col,
                    energies_all=self.FE_all[:, j],
                    LA=LA,
                    LB=LB,
                    temperature=T,
                    n_clusters=self._n_clusters,
                )
            return j, out

        with parallel_backend('threading', n_jobs=1):
            results = Parallel()(delayed(_compute_metrics)(j) for j in range(nM))

        for j, out in results:
            for k in range(8):
                mats[k][:, j] = out[k]

        return tuple(mats)


    def evolution_ensembles(
        self,
        max_clusters: int = 10,
        cluster_model: str = 'minibatch-kmeans',
        print_results: bool = False,
        temperature_min: float = .0255,
        temperature_max: float = .0256,
        reference_potentials: dict = None,
        reference_state: str = None,
        save_figures: bool = False,
        save_data: bool = False,
        fig_dir: str = '.',
        sub_sample: int = None, 
    ):  
        """
        Analyse the structural evolution of an ensemble across (µ, T) space.

        Parameters
        ----------
        max_clusters : int, default = 10
            Maximum number of local-environment clusters used to describe
            each structure.
        cluster_model : {'kmeans', 'minibatch-kmeans', 'agglomerative', …}
            Unsupervised model employed for environment clustering.
        print_results : bool, default = False
            If ``True``, print intermediate diagnostics to STDOUT.
        temperature_min, temperature_max : float
            Temperature bounds [Ha / k_B] for the evaluation grid.  A linear
            grid with *nM* = 2 points is created between these limits.
        reference_potentials : dict[label, μ], optional
            Pre-defined elemental chemical potentials.  When omitted a
            ridge-regression fit to the entire data set is employed to
            generate “self-consistent” references.
        reference_state : str, optional
            Species whose chemical potential is perturbed along the µ-axis.
            If ``None`` the scan is performed at fixed composition.
        save_figures, save_data : bool, default = False
            Persist figures (PDF/PNG) and NumPy data arrays respectively to
            *fig_dir*.
        fig_dir : str, default = '.'
            Target directory for figures and data.
        sub_sample : int, optional
            Random sub-sampling of structures prior to clustering.  Useful for
            extremely large data sets to reduce memory load.

        Notes
        -----
        * Stores formation-energy matrix **FE_all** and the global cluster
          labels **_global_labels** as instance attributes for downstream
          analysis.
        * Returns an *n_gen × 7* NumPy array (*g*, *H_A*, *H_B*, *J*, *shared*,
          *new_A*, *new_B*) suitable for direct plotting with
          :py:meth:`plot_evolution_metrics`.
        """
        # ---------------------------------------------------------------- #
        # (1) Gather all structures from the first ensemble.
        # ---------------------------------------------------------------- #
        # Combine structures
        PT_all = Partition()
        PT_all.add_container( self.ensembles[0].containers )
        unique_labels = list(PT_all.uniqueAtomLabels)

        # ---------------------------------------------------------------- #
        # (2) Build stoichiometry matrix X_all and target energy vector y_all
        #     for linear‐regression estimation of chemical potentials.
        # ---------------------------------------------------------------- #
        # Build count matrix and energy vector
        X_all = np.array([
            [
                np.count_nonzero(s.AtomPositionManager.atomLabelsList == lbl)
                for lbl in unique_labels
            ] for s in PT_all.containers
        ])
        y_all = np.array(
            [(getattr(s.AtomPositionManager, 'E', 0.0) or 0.0) for s in PT_all.containers],
            dtype=float
        )

        # ---------------------------------------------------------------- #
        # (3) Obtain base chemical potentials μ₀ (either supplied or fitted).
        # ---------------------------------------------------------------- #
        # Determine base chemical potentials
        if reference_potentials is None:
            model = Ridge(alpha=1e-5, fit_intercept=False)
            model.fit(X_all, y_all)
            cp_base = model.coef_
        else:
            cp_base = np.array([reference_potentials.get(lbl, 0.0) for lbl in unique_labels])

        # ---------------------------------------------------------------- #
        # (4) Construct a 2-point µ grid along one species (if requested).
        # ---------------------------------------------------------------- #
        # Vectorize Ef across mu grid
        nM = 2
        mu_array = np.linspace(-1, -1.1, num=nM)
        d_mu = np.zeros_like(cp_base)

        idx = unique_labels.index(reference_state) if reference_state else None
        if idx is not None:
            d_mu[idx] = 1.0

        # Chemical potentials per species per mu
        CP_mat = cp_base[:, None] + d_mu[:, None] * mu_array[None, :]

        # ---------------------------------------------------------------- #
        # (5) Normalised formation energies (baseline set to zero per column).
        # ---------------------------------------------------------------- #
        # Formation energies: (N_structures × nM)
        FE_all = (y_all[:, None] - X_all.dot(CP_mat)) / (X_all.sum(axis=1)[:, None] + _EPS)
        FE_all -= FE_all.min(axis=0)
        self.FE_all = FE_all.astype(float, copy=False)

        # ---------------------------------------------------------------- #
        # (6) Local-environment clustering and global labelling.
        # ---------------------------------------------------------------- #
        # Prepare clustering counts
        (_, cluster_counts, _) = PT_all.compute_structure_cluster_counts(
            r_cut = 4.0,
            n_max = 2,
            l_max = 2,
            sigma = 0.1,
            max_clusters=max_clusters,
            compress_model='pca',
            cluster_model=cluster_model,
            save=False,
            sub_sample=sub_sample,
        )

        counts_all = cluster_counts / np.linalg.norm(cluster_counts, axis=1, keepdims=True)

        # Global clustering
        if self.global_classification:
            self.initialise_global_clustering(counts_all, n_clusters=4000)
        
        class_array = np.array([ int(c.AtomPositionManager.info_system['generation']) for c in self.ensembles[0].containers ])

        # ---------------------------------------------------------------- #
        # (7) Loop through successive generations and compute similarity /
        #     novelty metrics across the (μ, T) grid.
        # ---------------------------------------------------------------- #
        temperature_array = np.linspace(temperature_min, temperature_max, num=nM)
        res = []

        for g in range( np.max(class_array) ):
            # Split per ensemble
            nA = len(self.ensembles[0].containers)
            mask = class_array<=g
            self.mask = mask

            Ef_A_all = FE_all[mask, :]
            counts_A = cluster_counts[mask] / np.linalg.norm(cluster_counts[mask], axis=1, keepdims=True)

            LA = self._global_labels[mask]

            start = time.time()
            # Compute all metrics
            (
                HconA_mat, HconB_mat, Jabs_mat, 
                shared_mat, newA_mat, newB_mat,
                HabsA_mat, HabsB_mat
            ) = self.evaluate_over_mus(
                Ef_A_all=Ef_A_all,
                Ef_B_all=FE_all,
                counts_A=counts_A,
                counts_B=counts_all,
                LA=LA,
                LB=self._global_labels,
                temperature_array=temperature_array,
                n_jobs=-1
            )

            res.append(
                [
                    g,
                    HabsA_mat[1, 1],
                    HabsB_mat[1, 1],
                    Jabs_mat[1, 1],
                    shared_mat[1, 1],
                    newA_mat[1, 1],
                    newB_mat[1, 1],
                ]
            )

        res = np.array(res)

        # Optionally export as *.npy for external reuse
        if save_data:
            np.save(f"{fig_dir}/evolution_metrics.npy", res)

        # Quick-look figure (kept for backward compatibility)
        if save_figures:
            self.plot_evolution_metrics(
                res,
                metric_names=("Hₐ", "H_b", "J", "shared", "newₐ", "new_b"),
                figsize=(7.5, 5.0),
                dpi=300,
                save_path=f"{fig_dir}/evolution_overview.png",
            )

        return res

    def evolution_two_ensembles(
        self,
        reference_potentials: Mapping[str, float] | None = None,
        reference_state: str | None = None,
        max_clusters: int = 10,
        cluster_model: str = 'minibatch-kmeans',
        temperature_min: float = 0.0155,
        temperature_max: float = 0.0156,
        sub_sample: int | None = None,
        save_figures: bool = False,
        save_data: bool = False,
        fig_dir: str = '.',
    ):
        """
        Evolution of the similarity/novelty metrics between **two** ensembles
        as both grow generation by generation.

        At generation *g* the comparison is:
            Ensemble-A(g)  = {structures in ensemble[0] with gen ≤ g}
            Ensemble-B(g)  = {structures in ensemble[1] with gen ≤ g}

        The chemical-potential grid and temperature grid are treated exactly
        as in :meth:`compare_ensembles_abs`.

        Returns
        -------
        ndarray, shape (n_gen, 7)
            Columns: g, H_abs_A, H_abs_B, JSD_abs, shared, new_A, new_B
        """
        if len(self.ensembles) != 2:
            raise ValueError("Exactly two ensembles must be present.")

        # -------------------------------------------------------------- #
        # (0)  Concatenate structures from *both* ensembles once only    #
        #      → reuse code path of compare_ensembles_abs to build       #
        #      FE_all, counts_all, global labels, etc.                   #
        # -------------------------------------------------------------- #
        PT_all = Partition()
        PT_all.add_container(self.ensembles[0].containers +
                             self.ensembles[1].containers)
        unique_labels = list(PT_all.uniqueAtomLabels)

        # Stoichiometry & energies
        X_all = np.array([[np.count_nonzero(s.AtomPositionManager.atomLabelsList == lbl)
                           for lbl in unique_labels] for s in PT_all.containers])
        # Build energies as float, replacing None with 0.0 at comprehension time
        y_all = np.array(
            [(getattr(s.AtomPositionManager, 'E', 0.0) or 0.0) for s in PT_all.containers],
            dtype=float
        )

        # ---------- chemical potentials, formation energies ------------ #
        if reference_potentials is None:
            model = Ridge(alpha=1e-5, fit_intercept=False)
            model.fit(X_all, y_all)
            cp_base = model.coef_
        else:
            cp_base = np.array([reference_potentials.get(lbl, 0.0)
                                for lbl in unique_labels])

        mu_grid = np.linspace(-1.0, -1.1, num=2)
        d_mu = np.zeros_like(cp_base)
        if reference_state is not None:
            d_mu[unique_labels.index(reference_state)] = 1.0
        CP = cp_base[:, None] + d_mu[:, None] * mu_grid[None, :]

        FE_all = ((y_all[:, None] - X_all.dot(CP)) /
                  (X_all.sum(axis=1)[:, None] + _EPS))
        FE_all -= FE_all.min(axis=0)
        self.FE_all = FE_all.astype(float, copy=False)

        # ---------- local-environment counts and optional global K-means #
        _, counts_all, _ = PT_all.compute_structure_cluster_counts(
            r_cut=4.0, n_max=2, l_max=2, sigma=0.1,
            max_clusters=max_clusters,
            compress_model='pca',
            cluster_model=cluster_model,
            save=False,
            sub_sample=sub_sample,
        )

        counts_all = counts_all.astype(np.float64, copy=False)          # ① cast once
        norms = np.linalg.norm(counts_all, axis=1, keepdims=True) + 1e-20
        counts_all /= norms                                             # ② safe in-place divide

        if self.global_classification:
            self.initialise_global_clustering(counts_all, n_clusters=4000)

        # ---------- generation labels for each ensemble separately ----- #
        gen_A = np.array([int(c.AtomPositionManager.info_system['generation'])
                          for c in self.ensembles[0].containers])
        gen_B = np.array([int(c.AtomPositionManager.info_system['generation'])
                          for c in self.ensembles[1].containers])
        g_max = max(gen_A.max(), gen_B.max())

        # Map row slices
        len_A, len_B = len(gen_A), len(gen_B)
        slice_A = slice(0, len_A)
        slice_B = slice(len_A, len_A + len_B)

        # Full arrays split once for convenience
        FE_A_full, FE_B_full = FE_all[slice_A], FE_all[slice_B]
        cnt_A_full, cnt_B_full = counts_all[slice_A], counts_all[slice_B]
        lab_A_full, lab_B_full = (self._global_labels[slice_A],
                                  self._global_labels[slice_B])

        T_grid = np.linspace(temperature_min, temperature_max, num=2)
        res = []

        # -------------------------------------------------------------- #
        # (1)  MAIN LOOP OVER GENERATIONS                               #
        # -------------------------------------------------------------- #
        for g in range(g_max + 1):
            mask_A = gen_A <= g
            mask_B = gen_B <= g
            # quick skip if nothing yet in one ensemble
            if not mask_A.any() or not mask_B.any():
                continue

            mats = self.evaluate_over_mus(
                Ef_A_all=FE_A_full[mask_A],
                Ef_B_all=FE_B_full[mask_B],
                counts_A=cnt_A_full[mask_A],
                counts_B=cnt_B_full[mask_B],
                LA=lab_A_full[mask_A],
                LB=lab_B_full[mask_B],
                temperature_array=T_grid,
                n_jobs=-1,
            )
            HconA, HconB, JSD, shared, newA, newB, HabsA, HabsB = mats
            # take the *last* (T, μ) point for a single scalar per metric;
            # adjust to taste
            res.append([g,
                        HabsA[-1, -1],
                        HabsB[-1, -1],
                        JSD[-1, -1],
                        shared[-1, -1],
                        newA[-1, -1],
                        newB[-1, -1]])

        res = np.asarray(res)

        if save_data:
            np.save(os.path.join(fig_dir, "evolution_two_ensembles.npy"), res)

        if save_figures and res.size:
            self.plot_evolution_metrics(
                res,
                metric_names=("Hₐ", "H_b", "J", "shared", "newₐ", "new_b"),
                save_path=os.path.join(fig_dir, "evolution_two_ensembles.png"),
            )

        return res

    # --------------------------------------------------------------------- #
    #  2.  PUBLICATION-QUALITY PLOTTING
    # --------------------------------------------------------------------- #
    def plot_evolution_metrics(
        self,
        res: np.ndarray,
        metric_names: tuple[str, ...] | None = None,
        figsize: tuple[float, float] = (6.0, 4.0),
        dpi: int = 300,
        ax: plt.Axes | None = None,
        save_path: str | None = None,
    ):
        """
        Render the evolution metrics obtained from :py:meth:`evolution_ensembles`
        as a high-resolution figure suitable for direct inclusion in a
        manuscript.

        Parameters
        ----------
        res : ndarray, shape (n_gen, 7)
            Output array returned by :py:meth:`evolution_ensembles`.
        metric_names : tuple[str, …], optional
            Descriptive labels for each metric column after *g*.
            When omitted, default LaTeX-style symbols are used.
        figsize : tuple[float, float], default = (6.0, 4.0)
            Figure size in inches.
        dpi : int, default = 300
            Rasterisation resolution.
        ax : matplotlib.axes.Axes, optional
            Existing Axes handle; if supplied the figure is drawn there.
            Otherwise, a new figure is created internally.
        save_path : str, optional
            Path (including file extension) for saving.  The backend is
            inferred from the extension (e.g. “.pdf”, “.png”).
        """
        if metric_names is None:
            metric_names = (
                r"$H_\mathrm{A},norm$",
                r"$H_\mathrm{B},norm$",
                r"$J$",
                "shared",
                r"new$_\mathrm{A}$",
                r"new$_\mathrm{B}$",
            )
        if len(metric_names) != 6:
            raise ValueError("metric_names must contain exactly six elements.")

        # ---------------------------------------------------------------- #
        # (1)  Prepare figure / axes.
        # ---------------------------------------------------------------- #
        created_ax = False
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize, dpi=dpi, constrained_layout=True)
            created_ax = True

        # ---------------------------------------------------------------- #
        # (2)  Plot each metric with a consistent line style.
        # ---------------------------------------------------------------- #
        generations = res[:, 0].astype(int)
        res[:, 1] /= (np.max(res[:, 2]) + _EPS)
        res[:, 2] /= (np.max(res[:, 2]) + _EPS)
        for i in range(1, 7):
            ax.plot(
                generations,
                res[:, i],
                marker="o",
                linestyle="-",
                linewidth=1.4,
                markersize=4.0,
                label=metric_names[i - 1],
            )

        # ---------------------------------------------------------------- #
        # (3)  Cosmetic adjustments compliant with journal guidelines.
        # ---------------------------------------------------------------- #
        ax.set_xlabel("Generation index, $g$", fontsize=11)
        ax.set_ylabel("Metric value (dimensionless)", fontsize=11)
        ax.tick_params(axis="both", labelsize=10)
        ax.legend(fontsize=9, frameon=False, ncol=2)
        ax.grid(alpha=0.3, linestyle="--", linewidth=0.5)

        # ---------------------------------------------------------------- #
        # (4)  Persist or return figure.
        # ---------------------------------------------------------------- #
        if save_path is not None:
            ax.figure.savefig(save_path, dpi=dpi, bbox_inches="tight")

        if created_ax:
            plt.close(ax.figure)  # prevent display in non-interactive contexts
            return ax.figure
        return ax


    def compare_ensembles_abs(
        self,
        reference_potentials: Mapping[str, float] | None = None,
        reference_state: str | None = None,

        max_clusters: int = 10,
        cluster_model: str = 'minibatch-kmeans',
        print_results: bool = False,

        states_fraction: float = .8,
        T: tuple = (0.005, 0.025),
        mu: tuple = (0, 1),
        save_figures: bool = False,
        save_data: bool = False,

        fig_dir: str = '.',
        sub_sample: int = None, 

    ) -> Dict[Tuple[int, int], Dict[str, np.ndarray]]:

        """
        Compare *all* loaded ensembles pair-wise and return the metrics.

        Parameters
        ----------
        max_clusters, cluster_model, temperature_min, temperature_max, …
            Same meaning as in the original two-ensemble implementation.

        Returns
        -------
        Dict[(int,int), Dict[str, np.ndarray]]
            Outer keys are ensemble-index pairs ``(i,j)`` with ``i<j``.
            Inner dict maps metric names
            ('H_abs_A', 'H_abs_B', 'JSD_abs', 'Shared',
             'Novelty_A', 'Novelty_B', 'H_abs_A-B', 'Novelty_A-B')
            to 2-D arrays *(nT × n_mu)* just like before.
        """
        if len(self.ensembles) < 2:
            raise ValueError("≥2 ensembles required for comparison.")

        # ------------------------------------------------------------------ #
        # (1) Merge all structures once and build global descriptor matrices #
        # ------------------------------------------------------------------ #
        # Combine structures
        PT_all = Partition()
        PT_all.add_container( sum([c.containers for c in self.ensembles], []) )
        unique_labels = list(PT_all.uniqueAtomLabels)

        # Build count matrix and energy vector
        X_all = np.array([
            [
                np.count_nonzero(s.AtomPositionManager.atomLabelsList == lbl)
                for lbl in unique_labels
            ] for s in PT_all.containers
        ])
        # Build energies as float, replacing None with 0.0 at comprehension time
        y_all = np.array(
            [(getattr(s.AtomPositionManager, 'E', 0.0) or 0.0) for s in PT_all.containers],
            dtype=float
        )

        # ---------- chemical potentials & formation energies --------------- #
        # Determine base chemical potentials
        if reference_potentials is None:
            model = Ridge(alpha=1e-5, fit_intercept=False)
            model.fit(X_all, y_all)
            cp_base = model.coef_
        else:
            cp_base = np.array([reference_potentials.get(lbl, 0.0) for lbl in unique_labels])

        # Vectorize Ef across mu grid
        nM = 200
        mu_array = np.linspace(mu[0], mu[1], num=nM)
        d_mu = np.zeros_like(cp_base)

        idx = unique_labels.index(reference_state) if reference_state else None
        if idx is not None:
            d_mu[idx] = 1.0

        # Chemical potentials per species per mu
        CP_mat = cp_base[:, None] + d_mu[:, None] * mu_array[None, :]

        # Formation energies: (N_structures × nM)
        FE_all = (y_all[:, None] - X_all.dot(CP_mat)) / (X_all.sum(axis=1)[:, None] + _EPS)
        FE_all -= FE_all.min(axis=0)
        self.FE_all = FE_all.astype(float, copy=False)

        # ---------------- global count vectors (SOAP → PCA → cluster) ------ #
        _, cluster_counts, _ = PT_all.compute_structure_cluster_counts(
            r_cut = 7.0,
            n_max = 6,
            l_max = 6,
            sigma = 0.1,
            max_clusters=max_clusters,
            compress_model='pca',
            cluster_model=cluster_model,
            save=False,
            sub_sample=sub_sample,
        )

        # Ensure a float array (avoids integer in-place errors)
        X = np.asarray(cluster_counts, dtype=float)

        # Row-wise L2 norms with shape (n_rows, 1)
        norms = np.linalg.norm(X, ord=2, axis=1, keepdims=True)

        # Safe division: rows with zero norm become zeros
        counts_all = np.divide(X, norms, out=np.zeros_like(X), where=norms > 0)

        # ----------------------- prepare grids ----------------------------- #
        temperature_array = np.linspace(T[0], T[1], num=nM)

        # --------------- optional *single* global K-means fit -------------- #
        if self.global_classification:
            self.initialise_global_clustering(counts_all, n_clusters= int(y_all.shape[0]*states_fraction) )

        # --------------------- map slice indices per ensemble -------------- #
        ens_lengths = [len(e.containers) for e in self.ensembles]
        starts = np.cumsum([0] + ens_lengths[:-1])
        stops  = np.cumsum(ens_lengths)

        def _slice(mat, i):
            """Utility to get rows that belong to ensemble i."""
            return mat[starts[i] : stops[i]]
     
        # ------------------------------------------------------------------ #
        # (2) Iterate over *all* pairs (i,j) and compute metrics             #
        # ------------------------------------------------------------------ #
        for idx1, e1 in enumerate(self.ensembles):
            for idx2, e2 in enumerate(self.ensembles[idx1+1:], start=idx1+1):
                Ef_A_all, Ef_B_all = _slice(FE_all, idx1), _slice(FE_all, idx2)
                counts_A, counts_B = _slice(counts_all, idx1), _slice(counts_all, idx2)

                LA, LB = _slice(self._global_labels, idx1), _slice(self._global_labels, idx2)

                start = time.time()
                # Compute all metrics
                mats = self.evaluate_over_mus(
                    Ef_A_all=Ef_A_all,
                    Ef_B_all=Ef_B_all,
                    counts_A=counts_A,
                    counts_B=counts_B,
                    LA=LA,
                    LB=LB,
                    temperature_array=temperature_array,
                    n_jobs=-1
                )
                HconA_mat, HconB_mat, Jabs_mat, shared_mat, newA_mat, newB_mat, HabsA_mat, HabsB_mat = mats
                print(f"Elapsed: {time.time() - start:.6f} s")
                # Plot and save logic unchanged


                # Plot with new interface
                metrics = {
                    'HabsA': HabsA_mat,
                    'HabsB': HabsB_mat,
                    'HabsA-B': HabsA_mat-HabsB_mat,
                    'JSD': Jabs_mat,
                    'shared': shared_mat,
                    'newA': newA_mat,
                    'newB': newB_mat,
                    'newA-B': newA_mat-newB_mat
                }
                self._plot_metrics(
                    temperatures=temperature_array,
                    metrics=metrics,
                    mu=mu_array[-1],
                    save_figures=save_figures,
                    fig_dir=fig_dir
                )

                matrix_dict = {
                    'H_abs_A': HabsA_mat,
                    'H_abs_B': HabsB_mat,
                    'H_abs_A-B': HabsA_mat-HabsB_mat,
                    'JSD_abs': Jabs_mat,
                    'Shared': shared_mat,
                    'Novelty_A': newA_mat,
                    'Novelty_B': newB_mat,
                    'Novelty_A-B': newA_mat-newB_mat,
                }
                self._plot_heatmaps(
                    matrix_dict=matrix_dict,
                    temperatures=temperature_array,
                    mu_values=mu_array,
                    save_figures=save_figures,
                    fig_dir=fig_dir
                )

                if save_data:
                    np.savetxt("newA_matrix.dat", newA_mat, fmt="%.4f")
                    np.savetxt("newB_matrix.dat", newB_mat, fmt="%.4f")
                    np.savetxt("HabsA_matrix.dat", HabsA_mat, fmt="%.4f")
                    np.savetxt("HabsB_matrix.dat", HabsB_mat, fmt="%.4f")
                    np.savetxt("Jabs_matrix.dat", Jabs_mat, fmt="%.4f")
                    np.savetxt("shared_matrix.dat", shared_mat, fmt="%.4f")
                    np.savetxt("temperature_array.dat", temperature_array, fmt="%.4f")
                    np.savetxt("mu_array.dat", mu_array, fmt="%.4f")

                if print_results:
                    i, j = -1, -1
                    print(f"T={temperature_array[i]:.4f}, "
                          f"HabsA={HabsA_mat[i,j]:.6f}, "
                          f"HabsB={HabsB_mat[i,j]:.6f}, "
                          f"JSD={Jabs_mat[i,j]:.6f}, "
                          f"shared={shared_mat[i,j]:.4f}, "
                          f"newA={newA_mat[i,j]:.4f}, "
                          f"newB={newB_mat[i,j]:.4f}")

        return HconA_mat, HconB_mat, Jabs_mat, shared_mat, newA_mat, newB_mat, HabsA_mat, HabsB_mat

    def _plot_metrics(self,
                       temperatures: np.ndarray,
                       metrics: Dict[str, np.ndarray],
                       mu: float,
                       save_figures: bool = False,
                       fig_dir: str = 'figures') -> None:
        """
        Plot multiple metrics vs temperature for a given mu and optionally save.

        Parameters
        ----------
        temperatures : np.ndarray
            Array of temperature values (eV).
        metrics : Dict[str, np.ndarray]
            Dictionary where keys are metric names and values are 2D arrays
            of shape (n_temps, n_series).
        mu : float
            Chemical potential (eV).
        save_figures : bool, optional
            If True, saves figure as PNG in fig_dir.
        fig_dir : str, optional
            Directory where figures are saved.
        """
        # Define groups of metrics to plot together
        from matplotlib import cm

        """
        Plot multiple metrics vs temperature for a given mu and optionally save.
        """
        groups = [
            ("primary", {
                'H_abs_A': metrics['HabsA'],
                'H_abs_B': metrics['HabsB'],
                #'H_abs_A-B': metrics['HabsA-B'],
                'JSD_abs': metrics['JSD'],
            }),
            ("novelty", {
                'Shared':   metrics['shared'],
                'Novelty A': metrics['newA'],
                'Novelty B': metrics['newB'],
                #'Novelty A-B': metrics['newA-B'],
            })
        ]

        for group_name, metric_dict in groups:
            fig, ax = plt.subplots(figsize=(10, 7))

            # 1) Pick one base colour per metric
            cmap = cm.viridis
            n_metrics = len(metric_dict)
            base_colors = cmap(np.linspace(0, 1, n_metrics))

            markers = {
                'H_abs_A':'o', 'H_abs_B':'s', 'H_abs_A-B':'^', 'JSD_abs':'D',
                'Shared':'o',   'Novelty A':'s', 'Novelty B':'D', 'Novelty A-B':'^'
            }

            # 2) Loop metrics & their base colours
            for (label, data), base_color in zip(metric_dict.items(), base_colors):
                arr = np.atleast_2d(data)           # shape (n_temps, n_series)
                n_series = arr.shape[1]
                # If you really want to vary shade for sub-series:
                shade_factors = np.linspace(0.5, 1.0, n_series)

                for i in range(n_series):
                    series = arr[:, i]
                    # darken/lighten the base colour if >1 series
                    color = base_color * shade_factors[i] \
                            if n_series > 1 else base_color
                    ax.plot(temperatures, series,
                            color=color,
                            marker=markers.get(label, 'o'),
                            label=label if i == 0 else None,
                            alpha=.85 if i == 0 else .05,
                            ms=.1,)

            ax.set_title(f"Metrics ({group_name}) vs Temperature (μ={mu:.2f} eV)")
            ax.set_xlabel("Temperature (eV)")
            ax.set_ylabel("Value")
            ax.legend(ncol=2, loc='upper left')
            ax.grid(True)
            fig.tight_layout()

            if save_figures:
                os.makedirs(fig_dir, exist_ok=True)
                fname = f"metrics_{group_name}_mu_{mu:.2f}.png"
                fig.savefig(os.path.join(fig_dir, fname), dpi=300)
                plt.close(fig)

    def _plot_heatmaps(self,
                       matrix_dict: Dict[str, np.ndarray],
                       temperatures: np.ndarray,
                       mu_values: np.ndarray,
                       save_figures: bool = False,
                       fig_dir: str = 'figures') -> None:
        """
        Plot heatmaps of multiple matrices over mu and temperature.

        Parameters
        ----------
        matrix_dict : Dict[str, np.ndarray]
            Keys are titles and values are 2D arrays (temps × mu).
        temperatures : np.ndarray
            Array of temperature values (eV).
        mu_values : np.ndarray
            Array of chemical potentials (eV).
        save_figures : bool, optional
            If True, saves figure as PNG in fig_dir.
        fig_dir : str, optional
            Directory where figures are saved.
        """
        for title, matrix in matrix_dict.items():
            fig, ax = plt.subplots(figsize=(6, 5))
            im = ax.imshow(matrix,
                           aspect='auto',
                           origin='lower',
                           extent=[mu_values[0], mu_values[-1],
                                   temperatures[0], temperatures[-1]])
            ax.set_title(f"{title} Heatmap")
            ax.set_xlabel("mu (eV)")
            ax.set_ylabel("Temperature (eV)")
            fig.colorbar(im, ax=ax)
            fig.tight_layout()
            if save_figures:
                fname = f"heatmap_{title.replace(' ', '_')}.png"
                fig.savefig(os.path.join(fig_dir, fname), dpi=300)

    def estimate_metrics(self, freqs_A, freqs_B, energies_A, energies_B, energies_all, LA, LB,
            temperature=0.0256, n_clusters=100, random_state=None):
        energies_A = np.asarray(energies_A, dtype=float)
        energies_B = np.asarray(energies_B, dtype=float)
        energies_all = np.asarray(energies_all, dtype=float)

        if self.global_classification:
            if self.weights_mode == 'boltzmann':
                weights = self.boltzmann_weights_raw(np.concatenate([energies_A, energies_B]), temperature)
            else:
                weights = np.ones(energies_A.size + energies_B.size, dtype=float)

            weights = np.asarray(weights, dtype=float)
            wA, wB = weights[: len(energies_A)], weights[len(energies_A) :]
            massA, massB = self._cluster_masses_fixed(wA, LA), self._cluster_masses_fixed(wB, LB)

            if self.weights_mode == 'boltzmann':
                global_weights = self.boltzmann_weights_raw(energies_all, temperature)
            else:
                global_weights = np.ones_like(energies_all)
                global_weights /= np.linalg.norm(global_weights)

            mass_global = self._cluster_masses_fixed(global_weights, self._global_labels)
            denom = mass_global.sum() + _EPS

        else:
            massA, massB = self.kmeans_weighted_abs(freqs_A, freqs_B, energies_A, energies_B, temperature, n_clusters=n_clusters)
            denom = (massA.sum() + massB.sum()) + _EPS

        HcondA = self.shannon_conditional(massA)
        HcondB = self.shannon_conditional(massB)

        F_A, F_B = massA.sum()/denom, massB.sum()/denom
        #plt.plot(massA)
        #plt.plot(massB)
        #plt.show()

        HabsA = F_A * HcondA 
        HabsB = F_B * HcondB

        (shared, newA, newB), _ = self.shared_new_abs(massA, massB)
        
        Jabs = self.jsd_abs(massA, massB)

        return HcondA, HcondB, Jabs, shared, newA, newB, HabsA, HabsB

class TestEnsembleMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate small synthetic data for testing
        np.random.seed(42)
        cls.N = 100
        cls.K = 5
        cls.freqs_A = np.random.rand(cls.N, cls.K)
        cls.freqs_A /= cls.freqs_A.sum(axis=1, keepdims=True)
        cls.freqs_B = np.random.rand(cls.N, cls.K)
        cls.freqs_B /= cls.freqs_B.sum(axis=1, keepdims=True)
        cls.E_A = np.random.rand(cls.N) / 2.0
        cls.E_B = np.random.rand(cls.N) / 2.0 + 0.1
        cls.T = 0.1
        cls.ensemble = Ensemble()

    def test_boltzmann_weights_raw(self):
        # Simple energy array
        energies = [0.0, 1.0, 2.0]
        T = 1.0
        w = Ensemble.boltzmann_weights_raw(energies, T)
        # Weights should be exp(-E/T): [1, exp(-1), exp(-2)]
        expected = np.exp(-np.array(energies))
        np.testing.assert_allclose(w, expected)

    def test_shannon_conditional_uniform(self):
        # Uniform mass should give log(n)
        mass = np.ones(10)
        H = Ensemble.shannon_conditional(mass)
        self.assertAlmostEqual(H, np.log(10), places=6)

    def test_shared_new_abs_extremes(self):
        # Non-overlapping masses
        massA = np.array([1.0, 0.0])
        massB = np.array([0.0, 1.0])
        (shared, newA, newB), (fA, fB) = Ensemble.shared_new_abs(massA, massB)
        # shared=0, newA=fA, newB=fB
        self.assertEqual(shared, 0.0)
        self.assertEqual(newA, fA)
        self.assertEqual(newB, fB)

    def test_jsd_abs_symmetry(self):
        # JSD should be symmetric
        massA = np.array([0.5, 0.5])
        massB = np.array([0.2, 0.8])
        jsd1 = Ensemble.jsd_abs(massA, massB)
        jsd2 = Ensemble.jsd_abs(massB, massA)
        self.assertAlmostEqual(jsd1, jsd2, places=8)

    def test_kmeans_weighted_abs_basic(self):
        # Ensure output shapes and non-negative masses
        massA, massB = self.ensemble.kmeans_weighted_abs(
            self.freqs_A, self.freqs_B, self.E_A, self.E_B, self.T,
            n_clusters=10, random_state=0
        )
        # Check shape
        self.assertEqual(massA.shape, (10,))
        self.assertEqual(massB.shape, (10,))
        # Check non-negativity
        self.assertTrue(np.all(massA >= 0))
        self.assertTrue(np.all(massB >= 0))
        # Sum of masses should equal sum of weights
        total_weight = np.sum(
            Ensemble.boltzmann_weights_raw(
                np.concatenate([self.E_A, self.E_B]), self.T
            )
        )
        self.assertAlmostEqual(massA.sum() + massB.sum(), total_weight, places=6)

def Ef(structures, reference_potentials=None):
    partition = Partition()
    partition.containers = structures
    
    X = np.array([
        [
            np.count_nonzero(structure.AtomPositionManager.atomLabelsList == label)
            for label in partition.uniqueAtomLabels
        ]
        for structure in structures
        ])
    y = np.array([getattr(s.AtomPositionManager, 'E', 0.0) for s in structures])

    if reference_potentials is not None:
        # Subtract the sum of reference potentials from total energy
        chemical_potentials = np.array([reference_potentials.get(ual, 0) for ual in partition.uniqueAtomLabels])
        formation_energies = y - X.dot(chemical_potentials)
    else:
        model = Ridge(alpha=1e-5, fit_intercept=False)
        model.fit(X, y)
        chemical_potentials = model.coef_
        formation_energies = y - X.dot(chemical_potentials)

    return np.array(formation_energies) / np.sum(X, axis=1)

'''
ens = Ensemble()
pa = '/Users/dimitry/Documents/Data/CuO/structures/config_2timesb.xyz'
ens.read_ensembles(pa)
#HabsA, HabsB, Jabs, shared, newA, newB
python_obj = ens.geenerate_Hobj(**kwars)
Hn = python_obj.compare( Ln ) -> float 
'''


'''
ens = Ensemble()
ens.read_ensembles('/Users/dimitry/Documents/Data/GA/CuO/alpha1/config_04.xyz')   # ensemble[0]
ens.read_ensembles('/Users/dimitry/Documents/Data/GA/CuO/alpha1/config_00.xyz')  # ensemble[1]

res = ens.evolution_two_ensembles(
    reference_potentials={'Cu': -14.916443703626898/4,
                          'O': (-9.87396191 + 0.096)/2},
    reference_state='O',
    max_clusters=12,
    save_figures=True,
    save_data=True,
)
'''

'''
ens = Ensemble( weights_mode='boltzmann1' ) # weights_mode='uniform'

#pa = '/Users/dimitry/Documents/Data/CuO/structures/config_2timesb.xyz'
#pb = '/Users/dimitry/Documents/Data/CuO/structures/config.xyz'

pa = '/Users/dimitry/Documents/Data/Hash/Benchmarks/LJ38_MD/subsampled/basin_0001.extxyz'
pb = '/Users/dimitry/Documents/Data/Hash/Benchmarks/LJ38_MD/config_sample.xyz'

#pa = '/Users/dimitry/Documents/Data/NiO/representatives.xyz'
#pb = '/Users/dimitry/Documents/Data/NiO/lib.xyz'
ens.read_ensembles(pa)
ens.read_ensembles(pb)

#HabsA, HabsB, Jabs, shared, newA, newB
# JS Symmetric measure, bounded [0, ln2]; 0 if identical, higher = more different
HconA_mat, HconB_mat, Jabs_mat, shared_mat, newA_mat, newB_mat, HabsA_mat, HabsB_mat = ens.compare_ensembles_abs(
    #reference_potentials = {'Cu':-14.916443703626898/4, 'O':(-9.87396191+0.096)/2 }, 
    #reference_state='O', 
    max_clusters=15,
    states_fraction=.1,

    )

HabsA, HabsB = np.max(HabsA_mat), np.max(HabsB_mat)
HconA, HconB = np.max(HconA_mat), np.max(HconB_mat)
#print(HabsA, HabsB)
#print(HconA, HconB)
#print(np.max(newA_mat), np.max(newB_mat ))
#print(np.max(Jabs_mat), np.max(shared_mat))
'''

'''
from sage_lib.ensemble.Ensemble import Ensemble
ens = Ensemble()
pa = '/Users/dimitry/Documents/Data/CuO/structures/config_2timesb.xyz'
pa = '/Users/dimitry/Documents/Data/GA/CuO/alpha0/config_00.xyz'

ens.read_ensembles(pa)

#HabsA, HabsB, Jabs, shared, newA, newB
ens.evolution_ensembles(
    reference_potentials = {'Cu':-14.916443703626898/4, 'O':(-9.87396191+0.096)/2 }, 
    reference_state='O', 
    max_clusters=10,
    sub_sample=None,
    save_figures = True,
    save_data = True,
        )
plt.show()
'''

if __name__ == "__main__":
    unittest.main()
