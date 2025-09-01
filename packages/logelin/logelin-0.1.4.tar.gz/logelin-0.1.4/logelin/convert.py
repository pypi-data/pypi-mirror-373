from astropy import units as u
from astropy.coordinates import Angle
from astropy.cosmology import Planck18 as Cosmo

def arcsec_to_kpc(ang_arcsec, z):
    """
    Convert an angular extent in arcseconds to a proper distance in kiloparsecs at redshift z.
    
    ang_arcsec : float or array-like
        Angular extent(s) in arcseconds.
    z : float or array-like
        Redshift(s) at which to convert the angular extent.
    """
    ang = Angle(ang_arcsec, unit=u.arcsec)
    dist = Cosmo.kpc_proper_per_arcmin(z) * ang.arcmin * u.arcmin
    return dist.value

def kpc_to_arcsec(dist_kpc, z):
    """
    Convert a proper distance in kiloparsecs to an angular extent in arcseconds at redshift z.
    
    dist_kpc : float or array-like
        Proper distance(s) in kiloparsecs.
    z : float or array-like
        Redshift(s) at which to convert the proper distance.
    """
    dist = dist_kpc * u.kpc
    ang = Angle(dist / Cosmo.kpc_proper_per_arcmin(z), unit=u.arcmin)
    return ang.arcsec
