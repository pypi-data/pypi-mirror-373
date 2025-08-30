from gampixpy.units import *

class MobilityModel:
    """
    MobilityModel(physics_config)

    Return a model object which can be called to compute mobility parameters
    (charge mobility, diffusion constants, etc.) from a physics parameter
    specification.

    Parameters
    ----------
    physics_config : PhysicsConfig
        A dict-like config object for physics params.

    Returns
    -------
    out : dict
        A dict object containing computed mobility parameters. This can be used
        to update the physics config (as it is called by the PhysicsConfig init
        method), or on its own.

    Examples
    --------
    >>> physics_config = gampixpy.config.default_phsyics_params
    >>> mobility_model = MobilityModel(physics_config)
    >>> mobility_model.compute_parameters()
    {'electron_mobility': 320.22680490595025,
     'drift_energy': 2.069477981671871e-08,
     'diffusion_longitudinal': 6.627023218939979e-06,
     'diffusion_ratio': 0.5005312849756938,
     'diffusion_transverse': 1.323997803506287e-05,
     'drift_speed': 0.16011340245297512}

    """
    def __init__(self, physics_config):
        self.physics_config = physics_config

    def compute_parameters(self):
        # compute drift velocity, diffusion model

        # Using the mobility model described in https://arxiv.org/abs/1508.07059
        drift_params = self.physics_config['charge_drift']
        
        a0 = drift_params['mobility_parameter_a0'] # cm^2/V/s
        a1 = drift_params['mobility_parameter_a1']
        a2 = drift_params['mobility_parameter_a2']
        a3 = drift_params['mobility_parameter_a3']
        a4 = drift_params['mobility_parameter_a4']
        a5 = drift_params['mobility_parameter_a5']
        T0 = drift_params['mobility_reference_T0']

        b0 = drift_params['mobility_parameter_b0']
        b1 = drift_params['mobility_parameter_b1']
        b2 = drift_params['mobility_parameter_b2']
        b3 = drift_params['mobility_parameter_b3']
        T1 = drift_params['mobility_reference_T1']

        E = drift_params['drift_field']
        T = self.physics_config['material']['temperature']

        numerator = a0 + a1*E/(kV/cm) + a2*pow(E/(kV/cm), 3./2) + a3*pow(E/(kV/cm), 5./2)
        denominator = 1 + (a1/a0)*E/(kV/cm) + a4*pow(E/(kV/cm), 2) + a5*pow(E/(kV/cm), 3)
        mu = (numerator*pow(T/T0, -3./2)/denominator)*cm*cm/V/s
        
        dMudE = ((a1 + 3./2*a2*pow(E/(kV/cm), 1./2) + 5./2*a3*pow(E/(kV/cm), 3./2))*denominator - numerator*(a1/a0 + 2*a4*E/(kV/cm) + 3*a5*pow(E/(kV/cm), 2)))*pow(T/T0, -3./2)/pow(denominator, 2)*cm*cm*cm/V/kV/s

        drift_energy = (b0 + b1*E/(kV/cm) + b2*pow(E/(kV/cm), 2))*(T/T1)/(1 + (b1/b0)*E/(kV/cm) + b3*pow(E/(kV/cm), 2))*eV

        R = 1 + E/mu*dMudE

        computed_params = {}
        computed_params['electron_mobility'] = mu
        computed_params['drift_energy'] = drift_energy
        computed_params['diffusion_longitudinal'] = mu*drift_energy/e
        computed_params['diffusion_ratio'] = R
        computed_params['diffusion_transverse'] = mu*drift_energy/R/e
        computed_params['drift_speed'] = mu*E

        return computed_params
