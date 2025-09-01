from setuptools import setup

setup(
    name='logelin',
    version='0.1.5',
    description='A tool which, by modelling the sampled galaxies as ' \
    'ellipsoids with intrinsic semi-axes drawn from a multivariate ' \
    'log-normal distribution, uses Bayesian inference to generate ' \
    'posteriors for parameters describing the underlying distribution ' \
    'of shapes and sizes of galaxies given projected angular extents '
    'and redshifts. Built using NumPyro and astropy.',
    url='https://github.com/dmjwentworth/lognormal-ellipsoid-inferrer',
    author='Dougal Wentworth',
    author_email='dw619@cantab.ac.uk',
    license='MIT license',
    packages=['logelin'],
    install_requires=['jax',                        
                      'astropy',                     
                      'numpyro',
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ]
)