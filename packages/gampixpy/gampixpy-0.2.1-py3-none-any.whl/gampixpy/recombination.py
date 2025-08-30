import torch

class RecombinationModel:
    """
    RecombinationModel(physics_config)

    Parent class for specific recombination models.

    See Also
    --------
    BoxRecombinationModel : Box recombination model
        (R. Acciarri et al JINST 8 (2013) P08005).
    BirksRecombinationModel : Birks recombination model
        (Amoruso, et al NIM A 523 (2004) 275).
    """
    def __init__(self, physics_config):
        self.physics_config = physics_config
        self.init_params()

    def __call__(self, *args, **kwargs):
        return self.recombination_factor(*args, **kwargs)

class BoxRecombinationModel (RecombinationModel):
    """
    BoxRecombinationModel

    Implementation of the Box recombination model
    (R. Acciarri et al JINST 8 (2013) P08005).

    See Also
    --------
    BirksRecombinationModel : Birks recombination model
        (Amoruso, et al NIM A 523 (2004) 275).

    """
    def init_params(self):
        self.E_field = self.physics_config['charge_drift']['drift_field']
        self.LAr_density = self.physics_config['material']['density']

        self.alpha = self.physics_config['box_model']['box_alpha']
        self.beta = self.physics_config['box_model']['box_beta']
        
    def recombination_factor(self, dE, dx, dEdx, **kwargs):
        """
        model.recombination_factor(dE, dx, dEdx)

        Calculate the recombination factor for an array of segments.
        
        Parameters
        ----------
        dE : array-like[float]
            Energy deposition per input segment.
        dx : array-like[float]
            Length of each input segment.
        dEdx : array-like[float]
            Energy deposition desity per input segment.

        Returns
        -------
        R : array-like[float]
            Recombination model for the given input parameters
            given the additional physics parameters supplied by
            the config.
        
        """
        xi = self.beta*dEdx/(self.E_field*self.LAr_density)
        recomb = torch.max(torch.stack([torch.zeros_like(dE),
                                        torch.log(self.alpha + xi)/xi]),
                           dim = 0)[0]

        return recomb

class BirksRecombinationModel (RecombinationModel):
    """
    BirksRecombinationModel(physics_config)

    Implementation of the Birks recombination model
    (Amoruso, et al NIM A 523 (2004) 275).

    See Also
    --------
    BoxRecombinationModel : Box recombination model
        (R. Acciarri et al JINST 8 (2013) P08005).
    
    """
    def init_params(self):
        self.E_field = self.physics_config['charge_drift']['drift_field']
        self.LAr_density = self.physics_config['material']['density']

        self.ab = self.physics_config['birks_model']['birks_ab']
        self.kb = self.physics_config['birks_model']['birks_kb']
        
    def recombination_factor(self, dE, dx, dEdx, **kwargs):
        """
        model.recombination_factor(dE, dx, dEdx)

        Calculate the recombination factor for an array of segments.
        
        Parameters
        ----------
        dE : array-like[float]
            Energy deposition per input segment.
        dx : array-like[float]
            Length of each input segment.
        dEdx : array-like[float]
            Energy deposition desity per input segment.

        Returns
        -------
        R : array-like[float]
            Recombination model for the given input parameters
            given the additional physics parameters supplied by
            the config.
        
        """
        recomb = torch.max(torch.stack([torch.zeros_like(dE),
                                        self.ab/(1 + self.kb*dEdx/(self.E_field*self.LAr_density))]),
                           dim = 0)[0]

        return recomb
