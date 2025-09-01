import numpyro
import jax
import jax.numpy as jnp
from numpyro import distributions as dist
from numpyro.infer import MCMC, NUTS, init_to_median
from jax import random

# Want jax in 64-bit
jax.config.update('jax_enable_x64', True)

# For transforming the multivariate normal in our model
exp = dist.transforms.ExpTransform()


# A, B, C are the semi-axes of a distant ellipsoid, while theta and phi are the viewing angles
def alpha(A, B, C, theta, phi):
    return (jnp.cos(phi) / (A*C))**2 + (jnp.sin(phi) / (B*C))**2


def beta(A, B, C, theta, phi):
    return (jnp.sin(theta) / (A*B))**2 + ((jnp.cos(theta) / C)**2)*((jnp.cos(phi) / B)**2 + (jnp.sin(phi) / A)**2)


def gamma(A, B, C, theta, phi):
    return (jnp.cos(theta))*(jnp.sin(2*phi))*((1 / (B*C))**2 - (1 / (A*C))**2)


def delta(A, B, C, theta, phi):
    return (jnp.sin(theta)*jnp.cos(phi) / A)**2 + (jnp.sin(theta)*jnp.sin(phi) / B)**2 + (jnp.cos(theta) / C)**2


def a(A, B, C, theta, phi):
    """
    Projected semi-major axis
    """
    α = alpha(A, B, C, theta, phi)
    β = beta(A, B, C, theta, phi)
    γ = gamma(A, B, C, theta, phi)
    δ = delta(A, B, C, theta, phi)
    return jnp.sqrt((2*δ) / (α + β - jnp.sqrt((α - β)**2 + γ**2)))


def b(A, B, C, theta, phi):
    """
    Projected semi-minor axis
    """
    α = alpha(A, B, C, theta, phi)
    β = beta(A, B, C, theta, phi)
    γ = gamma(A, B, C, theta, phi)
    δ = delta(A, B, C, theta, phi)
    return jnp.sqrt((2*δ) / (α + β + jnp.sqrt((α - β)**2 + γ**2)))

def model(a_obs, b_obs, err):
    # Number of data points
    N = len(a_obs)
    # Defining the priors
    min = jnp.min(b_obs)
    max = jnp.max(a_obs)
    mean_lnA = numpyro.sample('mean_lnA', dist.Uniform(jnp.log(min), jnp.log(max)))
    q = numpyro.sample('q', dist.Uniform(0, 1))
    r = numpyro.sample('r', dist.Uniform(0, 1))
    ln_mean = numpyro.deterministic('ln_mean', jnp.array([mean_lnA, mean_lnA + jnp.log(q), mean_lnA + jnp.log(q)
                                                            + jnp.log(r)]))
    var = numpyro.sample('var', dist.HalfCauchy(jnp.ones(3)))
    chol = numpyro.sample('chol', dist.LKJCholesky(3))
    # Building the Cholesky factor of the covariance matrix
    std = jnp.diag(jnp.sqrt(var))
    scale_tril = jnp.matmul(std, chol)
    normal = dist.MultivariateNormal(loc=ln_mean, scale_tril=scale_tril)
    log_normal = dist.TransformedDistribution(normal, exp)
    # Generating the N ellipsoids and viewing angles and computing likelihood of observations
    with numpyro.plate('obs', N):
        axes = numpyro.sample('axes', log_normal)
        A, B, C = axes[:, 0], axes[:, 1], axes[:, 2]
        theta = jnp.arccos(numpyro.sample('cosθ', dist.Uniform(-1, 1)))
        phi = numpyro.sample('phi', dist.Uniform(0, 2*jnp.pi))
        a_true = a(A, B, C, theta, phi)
        b_true = b(A, B, C, theta, phi)
        # Allowing for 10pc measurement error
        numpyro.sample('a_obs', dist.Normal(a_true, err*a_true), obs=a_obs)
        numpyro.sample('b_obs', dist.Normal(b_true, err*b_true), obs=b_obs)


def run_inference(a_obs, b_obs, err, rng_key=random.PRNGKey(0), num_warmup=1000, num_samples=2000, num_chains=4):
    """
    Runs the logNormal MCMC inference code on the supplied data.
    
    a_obs : JAX array
        Observed projected semi-major axes (in kpc).
    b_obs : JAX array
        Observed projected semi-minor axes (in kpc).
    err : float
        Fractional error on the observed axes (e.g. 0.1 for 10% error).
    rng_key : jax.random.PRNGKey, optional
        Random seed for JAX. Default is jax.random.PRNGKey(0).
    num_warmup : int, optional
        Number of warmup steps for NUTS. Default is 1000.
    num_samples : int, optional
        Number of samples to draw from the posterior. Default is 2000.
    num_chains : int, optional
        Number of MCMC chains to run in parallel. Default is 4.
    """
    # Generate random seed
    rng_key1, rng_key2 = random.split(rng_key)

    # Run NUTS
    numpyro.set_host_device_count(num_chains)
    kernel = NUTS(model, init_strategy=init_to_median())
    mcmc = MCMC(kernel, num_warmup=num_warmup, num_samples=num_samples, num_chains=num_chains)
    mcmc.run(rng_key1, a_obs=a_obs, b_obs=b_obs, err=err)

    # Get the posterior samples
    samples = mcmc.get_samples()

    # Extract the values of interest
    ln_mean_samples = samples['ln_mean']
    var_samples = samples['var']
    chol_samples = samples['chol']
    corr_samples = jnp.matmul(chol_samples, jnp.transpose(chol_samples, axes=[0, 2, 1]))

    mean_lnA, mean_lnB, mean_lnC = ln_mean_samples[:, 0], ln_mean_samples[:, 1], ln_mean_samples[:, 2]

    var_lnA, var_lnB, var_lnC = var_samples[:, 0], var_samples[:, 1], var_samples[:, 2]

    corr_logAB, corr_logAC, corr_logBC = corr_samples[:, 0, 1], corr_samples[:, 0, 2], corr_samples[:, 1, 2]

    # Converting from log base e to base 10 because astrophysicists insist upon such things

    k = jnp.log10(jnp.e)
    mean_logA, mean_logB, mean_logC = mean_lnA*k, mean_lnB*k, mean_lnC*k
    var_logA, var_logB, var_logC = var_lnA*(k**2), var_lnB*(k**2), var_lnC*(k**2)

    samples_of_interest = {
        'mean_logA': mean_logA,
        'mean_logB': mean_logB,
        'mean_logC': mean_logC,
        'var_logA': var_logA,
        'var_logB': var_logB,
        'var_logC': var_logC,
        'corr_logAB': corr_logAB,
        'corr_logAC': corr_logAC,
        'corr_logBC': corr_logBC
    }

    return samples_of_interest
