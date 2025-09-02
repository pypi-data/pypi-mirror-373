from __future__ import annotations
import logging
from typing import Dict, Any, List
import numpy as np
import xraylib
from ewokscore import Task
from xoppylib.sources.xoppy_bm_wiggler import xoppy_calc_bm
from xoppylib.sources.xoppy_bm_wiggler import xoppy_calc_wiggler_on_aperture

logger = logging.getLogger(__name__)

_NIST_ALIASES = {
    "air": "Air, Dry (near sea level)",
    "water": "Water, Liquid",
    "kapton": "Kapton Polyimide Film",
}
try:
    for n in xraylib.GetCompoundDataNISTList():
        _NIST_ALIASES[n] = n
        _NIST_ALIASES[n.lower()] = n
        _NIST_ALIASES[n.replace(" ", "")] = n
        _NIST_ALIASES[n.lower().replace(" ", "")] = n
except Exception as e:
    logger.debug(
        "Could not load NIST compound list from xraylib; using base aliases only: %s",
        e,
    )


def _is_number(x) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def _canonical_compound_name(name: str) -> str | None:
    if not name:
        return None
    key1 = name.strip()
    key2 = key1.lower()
    key3 = key2.replace(" ", "")
    return _NIST_ALIASES.get(key1) or _NIST_ALIASES.get(key2) or _NIST_ALIASES.get(key3)


def _mu_over_rho_element(Z: int, E_keV: np.ndarray) -> np.ndarray:
    # cm^2/g
    return np.array([xraylib.CS_Total(Z, e) for e in E_keV], dtype=float)


def _mu_over_rho_compound_from_nist(
    cname: str, E_keV: np.ndarray
) -> tuple[np.ndarray, float | None]:
    """
    Return (mu_over_rho [cm^2/g], density [g/cm^3 or None]) for a NIST compound name.
    mu/ρ is computed as the mass-fraction weighted sum of elemental mu/ρ.
    """
    data = xraylib.GetCompoundDataNISTByName(cname)
    Zs = data["Elements"]
    w = data["massFractions"]
    mu_over_rho = np.zeros_like(E_keV, dtype=float)
    for Z, wf in zip(Zs, w):
        mu_over_rho += wf * _mu_over_rho_element(int(Z), E_keV)
    return mu_over_rho, float(data["density"])


def _resolve_mu_density(
    material: str, density_g_cm3: Any, E_keV: np.ndarray
) -> tuple[np.ndarray, float]:
    """
    Resolve mass attenuation (mu/ρ) and density for either an element or a NIST compound.
    - If density is '?', None or missing, we auto-fill:
        * elements: xraylib.ElementDensity(Z)
        * compounds: NIST density
    """
    try:
        Z = xraylib.SymbolToAtomicNumber(material)
    except Exception as e:
        logger.debug(
            "Material is not an element symbol (%r); trying compound paths: %s",
            material,
            e,
        )
    else:
        mu_over_rho = _mu_over_rho_element(Z, E_keV)
        if _is_number(density_g_cm3):
            rho = float(density_g_cm3)
        else:
            rho = float(xraylib.ElementDensity(Z))
        return mu_over_rho, rho

    cname = _canonical_compound_name(material)
    if cname is not None:
        mu_over_rho, rho_nist = _mu_over_rho_compound_from_nist(cname, E_keV)
        rho = float(density_g_cm3) if _is_number(density_g_cm3) else float(rho_nist)
        return mu_over_rho, rho
    try:
        comp = xraylib.CompoundParser(material)
        Zs = comp["Elements"]
        w = comp["massFractions"]
        mu_over_rho = np.zeros_like(E_keV, dtype=float)
        for Z, wf in zip(Zs, w):
            mu_over_rho += wf * _mu_over_rho_element(int(Z), E_keV)
        rho = float(density_g_cm3) if _is_number(density_g_cm3) else 1.0
        return mu_over_rho, rho
    except Exception as e:
        raise ValueError(f"Unknown material '{material}': {e}")


def _transmission(
    material: str, thickness_mm: float, density_g_cm3: Any, energy_eV: np.ndarray
) -> np.ndarray:
    if thickness_mm <= 0:
        return np.ones_like(energy_eV, dtype=float)
    E_keV = np.asarray(energy_eV, dtype=float) / 1e3
    mu_over_rho, rho = _resolve_mu_density(
        material, density_g_cm3, E_keV
    )  # cm^2/g, g/cm^3
    mu = mu_over_rho * rho  # cm^-1
    t_cm = float(thickness_mm) / 10.0
    return np.exp(-mu * t_cm)


class ComputeBMSpectrum(
    Task,
    input_names=[
        "TYPE_CALC",
        "VER_DIV",
        "MACHINE_NAME",
        "RB_CHOICE",
        "MACHINE_R_M",
        "BFIELD_T",
        "BEAM_ENERGY_GEV",
        "CURRENT_A",
        "HOR_DIV_MRAD",
        "PHOT_ENERGY_MIN",
        "PHOT_ENERGY_MAX",
        "NPOINTS",
        "LOG_CHOICE",
        "PSI_MRAD_PLOT",
        "PSI_MIN",
        "PSI_MAX",
        "PSI_NPOINTS",
        "FILE_DUMP",
    ],
    output_names=["energy_eV", "flux", "spectral_power", "cumulated_power"],
):
    """
    Compute a bending-magnet (BM) spectrum using XOPPY's ``xoppy_calc_bm``.

    Inputs (units):
      - TYPE_CALC (int): must be 0.
      - VER_DIV (int): vertical divergence model, {0, 2}.
      - MACHINE_NAME (str), RB_CHOICE (int), MACHINE_R_M (m).
      - BFIELD_T (T), BEAM_ENERGY_GEV (GeV), CURRENT_A (A), HOR_DIV_MRAD (mrad).
      - PHOT_ENERGY_MIN / PHOT_ENERGY_MAX (eV), NPOINTS (int), LOG_CHOICE (0/1).
      - PSI_* (mrad) and PSI_NPOINTS (int), FILE_DUMP (bool).

    Outputs:
      - energy_eV (eV), sorted ascending.
      - flux (phot/s/0.1%bw) as returned by XOPPY.
      - spectral_power (W/eV).
      - cumulated_power (W).
    """

    def run(self):
        TYPE_CALC = getattr(self.inputs, "TYPE_CALC", 0)
        VER_DIV = getattr(self.inputs, "VER_DIV", 0)
        MACHINE_NAME = getattr(self.inputs, "MACHINE_NAME", "ESRF bending magnet")
        RB_CHOICE = getattr(self.inputs, "RB_CHOICE", 0)
        MACHINE_R_M = getattr(self.inputs, "MACHINE_R_M", 25.0)
        BFIELD_T = getattr(self.inputs, "BFIELD_T", 0.8)
        BEAM_ENERGY_GEV = getattr(self.inputs, "BEAM_ENERGY_GEV", 6.0)
        CURRENT_A = getattr(self.inputs, "CURRENT_A", 0.2)
        HOR_DIV_MRAD = getattr(self.inputs, "HOR_DIV_MRAD", 1.0)
        PHOT_ENERGY_MIN = getattr(self.inputs, "PHOT_ENERGY_MIN", 100.0)
        PHOT_ENERGY_MAX = getattr(self.inputs, "PHOT_ENERGY_MAX", 200000.0)
        NPOINTS = getattr(self.inputs, "NPOINTS", 500)
        LOG_CHOICE = getattr(self.inputs, "LOG_CHOICE", 1)
        PSI_MRAD_PLOT = getattr(self.inputs, "PSI_MRAD_PLOT", 1.0)
        PSI_MIN = getattr(self.inputs, "PSI_MIN", -1.0)
        PSI_MAX = getattr(self.inputs, "PSI_MAX", 1.0)
        PSI_NPOINTS = getattr(self.inputs, "PSI_NPOINTS", 500)
        FILE_DUMP = getattr(self.inputs, "FILE_DUMP", False)

        a6_T, fm, a, energy_eV = xoppy_calc_bm(
            TYPE_CALC=TYPE_CALC,
            MACHINE_NAME=MACHINE_NAME,
            RB_CHOICE=RB_CHOICE,
            MACHINE_R_M=MACHINE_R_M,
            BFIELD_T=BFIELD_T,
            BEAM_ENERGY_GEV=BEAM_ENERGY_GEV,
            CURRENT_A=CURRENT_A,
            HOR_DIV_MRAD=HOR_DIV_MRAD,
            VER_DIV=VER_DIV,
            PHOT_ENERGY_MIN=PHOT_ENERGY_MIN,
            PHOT_ENERGY_MAX=PHOT_ENERGY_MAX,
            NPOINTS=NPOINTS,
            LOG_CHOICE=LOG_CHOICE,
            PSI_MRAD_PLOT=PSI_MRAD_PLOT,
            PSI_MIN=PSI_MIN,
            PSI_MAX=PSI_MAX,
            PSI_NPOINTS=PSI_NPOINTS,
            FILE_DUMP=FILE_DUMP,
        )
        if TYPE_CALC != 0 or VER_DIV not in (0, 2):
            raise ValueError(
                "ComputeBMSpectrum expects TYPE_CALC=0 and VER_DIV in {0,2}"
            )

        flux = a6_T[:, 5]
        spectral_power = a6_T[:, 6]
        cum_power = a6_T[:, 7]

        order = np.argsort(energy_eV)
        self.outputs.energy_eV = energy_eV[order]
        self.outputs.flux = flux[order]
        self.outputs.spectral_power = spectral_power[order]
        self.outputs.cumulated_power = cum_power[order]


class ComputeWigglerSpectrum(
    Task,
    input_names=[
        "PHOT_ENERGY_MIN",
        "PHOT_ENERGY_MAX",
        "NPOINTS",
        "ENERGY",
        "CURRENT",
        "FIELD",
        "NPERIODS",
        "ULAMBDA",
        "K",
        "NTRAJPOINTS",
        "FILE",
        "SLIT_FLAG",
        "SLIT_D",
        "SLIT_NY",
        "SLIT_WIDTH_H_MM",
        "SLIT_HEIGHT_V_MM",
        "SLIT_CENTER_H_MM",
        "SLIT_CENTER_V_MM",
        "SHIFT_X_FLAG",
        "SHIFT_X_VALUE",
        "SHIFT_BETAX_FLAG",
        "SHIFT_BETAX_VALUE",
        "TRAJ_RESAMPLING_FACTOR",
        "SLIT_POINTS_FACTOR",
        "LOG_CHOICE",
    ],
    output_names=["energy_eV", "flux", "spectral_power", "cumulated_power"],
):
    """
    Compute a wiggler spectrum on an aperture using
    ``xoppy_calc_wiggler_on_aperture``.

    Inputs (units):
      - PHOT_ENERGY_MIN / PHOT_ENERGY_MAX (eV), NPOINTS (int).
      - ENERGY (GeV), CURRENT (mA).
      - FIELD, NPERIODS (int), ULAMBDA (m), K (–), NTRAJPOINTS (int), FILE (str).
      - SLIT_*: distances in m/mm per name; flags as ints.
      - SHIFT_X_VALUE (m), SHIFT_BETAX_VALUE (rad).
      - TRAJ_RESAMPLING_FACTOR, SLIT_POINTS_FACTOR (floats), LOG_CHOICE (0/1).

    Outputs:
      - energy_eV (eV), sorted ascending.
      - flux (phot/s/0.1%bw) as returned by XOPPY.
      - spectral_power (W/eV).
      - cumulated_power (W).
    """

    def _get(self, name: str, default: Any):
        return getattr(self.inputs, name, default)

    def run(self):
        energy, flux, sp, cum, *_ = xoppy_calc_wiggler_on_aperture(
            FIELD=int(self._get("FIELD", 1)),
            NPERIODS=int(self._get("NPERIODS", 1)),
            ULAMBDA=float(self._get("ULAMBDA", 0.15)),  # m
            K=float(self._get("K", 22.591)),
            ENERGY=float(self._get("ENERGY", 6.0)),  # GeV
            PHOT_ENERGY_MIN=float(self._get("PHOT_ENERGY_MIN", 100.0)),
            PHOT_ENERGY_MAX=float(self._get("PHOT_ENERGY_MAX", 4e5)),
            NPOINTS=int(self._get("NPOINTS", 2000)),
            NTRAJPOINTS=int(self._get("NTRAJPOINTS", 101)),
            CURRENT=float(self._get("CURRENT", 200.0)),  # mA
            FILE=str(self._get("FILE", "")),
            SLIT_FLAG=int(self._get("SLIT_FLAG", 1)),
            SLIT_D=float(self._get("SLIT_D", 56.5)),  # m
            SLIT_NY=int(self._get("SLIT_NY", 101)),
            SLIT_WIDTH_H_MM=float(self._get("SLIT_WIDTH_H_MM", 10.0)),
            SLIT_HEIGHT_V_MM=float(self._get("SLIT_HEIGHT_V_MM", 5.0)),
            SLIT_CENTER_H_MM=float(self._get("SLIT_CENTER_H_MM", 0.0)),
            SLIT_CENTER_V_MM=float(self._get("SLIT_CENTER_V_MM", 0.0)),
            SHIFT_X_FLAG=int(self._get("SHIFT_X_FLAG", 1)),
            SHIFT_X_VALUE=float(self._get("SHIFT_X_VALUE", -0.002385)),  # m
            SHIFT_BETAX_FLAG=int(self._get("SHIFT_BETAX_FLAG", 5)),
            SHIFT_BETAX_VALUE=float(self._get("SHIFT_BETAX_VALUE", 0.005)),
            TRAJ_RESAMPLING_FACTOR=float(self._get("TRAJ_RESAMPLING_FACTOR", 10000.0)),
            SLIT_POINTS_FACTOR=float(self._get("SLIT_POINTS_FACTOR", 3.0)),
        )
        energy = np.asarray(energy, dtype=float)
        order = np.argsort(energy)
        self.outputs.energy_eV = energy[order]
        self.outputs.flux = np.asarray(flux, dtype=float)[order]
        self.outputs.spectral_power = np.asarray(sp, dtype=float)[order]
        self.outputs.cumulated_power = np.asarray(cum, dtype=float)[order]


class ApplyAttenuators(
    Task,
    input_names=["energy_eV", "spectral_power", "attenuators"],
    optional_input_names=["order", "flux"],
    output_names=[
        "energy_eV",
        "attenuated_spectral_power",
        "transmission",
        "attenuated_flux",
    ],
):
    """
    Apply a stack of attenuators to the source spectrum (and optionally flux).

    Inputs:
      - energy_eV (eV).
      - spectral_power (W/eV).
      - attenuators (dict): each layer is
        ``{"material": <str>, "thickness_mm": <float>, "density_g_cm3": <float?>}``.
        * ``material`` may be an element symbol (e.g. "Al"), a NIST compound
          name/alias (e.g. "kapton", "Air, Dry (near sea level)"), or a
          chemical formula parsable by xraylib (e.g. "H2O").
        * ``thickness_mm`` is in millimetres.
        * ``density_g_cm3`` (optional) is in g/cm³; if omitted, a suitable
          default is used (element density or NIST density).
      - order (list[str], optional): explicit stacking order of attenuator keys;
        defaults to insertion order.
      - flux (optional): source flux array (phot/s/0.1%bw), same shape as energy_eV.

    Outputs:
      - energy_eV (eV) [pass-through].
      - transmission (unitless): cumulative transmission of the stack.
      - attenuated_spectral_power (W/eV): spectral_power × transmission.
      - attenuated_flux (phot/s/0.1%bw or None): flux × transmission if provided.
    """

    def run(self):
        energy_eV = self.inputs.energy_eV
        sp_in = self.inputs.spectral_power.copy()
        flux_in = getattr(self.inputs, "flux", None)

        attenuators: Dict[str, Dict[str, Any]] = dict(self.inputs.attenuators)

        # order of stacking
        if hasattr(self.inputs, "order") and self.inputs.order:
            keys: List[str] = list(self.inputs.order)
        else:
            keys = list(attenuators.keys())

        transmission = np.ones_like(energy_eV, dtype=float)
        for key in keys:
            a = attenuators[key]
            T = _transmission(
                str(a["material"]),
                float(a["thickness_mm"]),
                float(a["density_g_cm3"]),
                energy_eV,
            )
            transmission *= T

        sp_out = sp_in * transmission
        flux_out = flux_in * transmission if flux_in is not None else None

        self.outputs.energy_eV = energy_eV
        self.outputs.attenuated_spectral_power = sp_out
        self.outputs.transmission = transmission
        self.outputs.attenuated_flux = flux_out


class SpectrumStats(
    Task,
    input_names=["energy_eV", "attenuated_flux"],
    output_names=[
        "mean_energy_eV",
        "mean_idx",
        "pic_energy_eV",
        "pic_idx",
    ],
):
    """
    Stats on an attenuated spectrum.

    Inputs
     - energy_eV: array-like (eV)
     - attenuated_flux : array-like (ph/s/0.1%bw)

    Outputs
     - mean_energy_eV: Flux-weighted mean using bin weights: weights = flux * ΔE / (0.001 * E).
     - mean_idx (int): Index of energy_eV closest to mean_energy_eV (−1 if N/A).
     - pic_energy_eV: energy at which flux * ΔE / (0.001 * E) is maximal (NaN if N/A).
     - pic_idx (int): Index of that maximum (−1 if N/A).
    """

    def run(self):
        energy = np.asarray(self.inputs.energy_eV, dtype=float)
        flux = np.asarray(self.inputs.attenuated_flux, dtype=float)

        if not (energy.shape == flux.shape):
            raise ValueError("energy_eV and attenuated_flux must have identical shapes")

        mask = np.isfinite(energy) & np.isfinite(flux) & (energy > 0)
        if not mask.any():
            self.outputs.mean_energy_eV = float("nan")
            self.outputs.mean_idx = -1
            self.outputs.pic_energy_eV = float("nan")
            self.outputs.pic_idx = -1
            return

        idx_masked = np.flatnonzero(mask)
        e = energy[mask]
        f = flux[mask]

        order = np.argsort(e)
        e_sorted = e[order]
        f_sorted = f[order]
        idx_sorted = idx_masked[order]

        if e_sorted.size == 1:
            dE = np.array([1.0], dtype=float)
        else:
            dE = np.empty_like(e_sorted)
            dE[1:-1] = 0.5 * (e_sorted[2:] - e_sorted[:-2])
            dE[0] = e_sorted[1] - e_sorted[0]
            dE[-1] = e_sorted[-1] - e_sorted[-2]
            dE = np.clip(dE, 0.0, None)

        weights = f_sorted * dE / (1e-3 * e_sorted)
        wsum = float(np.sum(weights))

        if wsum > 0.0:
            mean_energy_eV = float(np.sum(e_sorted * weights) / wsum)
            mean_idx = int(np.abs(energy - mean_energy_eV).argmin())
        else:
            mean_energy_eV = float("nan")
            mean_idx = -1

        if weights.size > 0:
            rel = int(np.argmax(weights))
            pic_idx = int(idx_sorted[rel])
            pic_energy_eV = float(energy[pic_idx])
        else:
            pic_idx = -1
            pic_energy_eV = float("nan")

        self.outputs.mean_energy_eV = mean_energy_eV
        self.outputs.mean_idx = mean_idx
        self.outputs.pic_energy_eV = pic_energy_eV
        self.outputs.pic_idx = pic_idx
