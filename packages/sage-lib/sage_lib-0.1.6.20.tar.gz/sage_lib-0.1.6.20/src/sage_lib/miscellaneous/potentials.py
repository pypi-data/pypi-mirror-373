import numpy as np

def harmonic(kappa, xstar):
    """
    Returns vectorized umbrella potential
    U(x) = (kappa/2) * (x - xstar)^2
    """
    return lambda x: (kappa / 2) * np.square(x - xstar)

def linear(phi):
    """
    Returns vectorized umbrella potential
    U(x) = phi * x
    """
    return lambda x: phi * x

def harmonic_DD(kappa, xstar):
    """
    Returns vectorized umbrella potential
    U(x) = (1/2) * sum(kappa_i * (x_i - xstar_i)^2)
    kappa and xstar have shape (D,)
    x has shape (N, D)
    U(x) has shape (N,)
    """
    kappa = np.asarray(kappa).reshape(-1)
    xstar = np.asarray(xstar).reshape(-1)
    
    if kappa.shape != xstar.shape:
        raise ValueError(f"kappa and xstar must have the same shape, but got {kappa.shape} and {xstar.shape}")
    
    def potential(x):
        if x.ndim != 2 or x.shape[1] != kappa.shape[0]:
            raise ValueError(f"x must be 2D with shape (N, {kappa.shape[0]}), but got shape {x.shape}")
        return 0.5 * np.sum(kappa * np.square(x - xstar), axis=1)
    
    return potential

def linear_DD(phi):
    """
    Returns vectorized umbrella potential
    U(x) = sum(phi_i * x_i)
    phi has shape (D,)
    x has shape (N, D)
    U(x) has shape (N,)
    """
    phi = np.asarray(phi).reshape(-1)
    
    def potential(x):
        if x.ndim != 2 or x.shape[1] != phi.shape[0]:
            raise ValueError(f"x must be 2D with shape (N, {phi.shape[0]}), but got shape {x.shape}")
        return np.dot(x, phi)
    
    return potential

def morse(D, a, r_e):
    """
    Returns vectorized Morse potential
    U(r) = D * (1 - exp(-a*(r - r_e)))^2
    D: well depth
    a: controls width of potential
    r_e: equilibrium bond distance
    """
    return lambda r: D * np.square(1 - np.exp(-a * (r - r_e)))

def lennard_jones(epsilon, sigma):
    """
    Returns vectorized Lennard-Jones potential
    U(r) = 4 * epsilon * ((sigma/r)^12 - (sigma/r)^6)
    epsilon: well depth
    sigma: distance at which potential is zero
    """
    return lambda r: 4 * epsilon * (np.power(sigma/r, 12) - np.power(sigma/r, 6))

def gaussian(A, sigma):
    """
    Returns vectorized Gaussian potential
    U(x) = A * exp(-x^2 / (2*sigma^2))
    A: amplitude of the Gaussian
    sigma: standard deviation
    """
    return lambda x: A * np.exp(-np.square(x) / (2 * sigma**2))

def double_well(a, b):
    """
    Returns vectorized double well potential
    U(x) = x^4 - a*x^2 + b*x
    a, b: parameters controlling the shape of the double well
    """
    return lambda x: np.power(x, 4) - a * np.square(x) + b * x

def periodic(k, L):
    """
    Returns vectorized periodic potential
    U(x) = k * (1 - cos(2*pi*x/L))
    k: strength of the potential
    L: periodicity
    """
    return lambda x: k * (1 - np.cos(2 * np.pi * x / L))

# Función de utilidad para graficar potenciales
def plot_potential(potential_func, x_range, label):
    import matplotlib.pyplot as plt
    x = np.linspace(*x_range, 1000)
    y = potential_func(x)
    plt.plot(x, y, label=label)
    plt.xlabel('x')
    plt.ylabel('U(x)')
    plt.legend()
    plt.title('Potential Energy')
    plt.grid(True)