#region modules
import numpy as np 
import glob 
import h5py 
from ase.units import Ry, eV
#endregion

#region variables
#endregion

#region functions
#endregion

#region classes
class Xct:
    def __init__(self, xct_dir_glob: str = './bseq_for_xctph/Q_*/eigenvectors.h5'):
        self.xct_dir_glob: str = xct_dir_glob  

    def read(self):
        # search for eigenvectors
        fnames = np.sort(glob.glob(self.xct_dir_glob))
        self.nQ = len(fnames)

        # allocate space for Qpts
        self.exciton_Q_shift = np.zeros((self.nQ, 3), 'f8')

        for iQ, fname in enumerate(fnames):

            # Reads in exciton header associated with current q-point.
            with h5py.File(fname, 'r') as f:

                # if iQ=0, store header information.
                if iQ == 0:

                    self.exciton_Q_shift[iQ, :] = f['exciton_header/kpoints/exciton_Q_shifts'][()]
                    self.nevecs = f['exciton_header/params/nevecs'][()]
                    self.ns = f['exciton_header/params/ns'][()]
                    self.nv = f['exciton_header/params/nv'][()]
                    self.nc = f['exciton_header/params/nc'][()]
                    self.nk = f['exciton_header/kpoints/nk'][()]
                    self.kpts = f['exciton_header/kpoints/kpts'][()]

                    # some other info needed
                    self.blat = f['mf_header/crystal/blat'][()]
                    self.bvec = f['mf_header/crystal/bvec'][()]

                    eigenvalues = np.zeros((self.nevecs, self.nQ), 'f8')
                    eigenvectors = np.zeros((2, self.ns, self.nv, self.nc, self.nk, self.nevecs, self.nQ), 'f8')

                # otherwise, check values 
                else:

                    self.exciton_Q_shift[iQ, :] = f['exciton_header/kpoints/exciton_Q_shifts'][()]
                    assert self.nevecs == f['exciton_header/params/nevecs'][()]
                    assert self.ns == f['exciton_header/params/ns'][()]
                    assert self.nv == f['exciton_header/params/nv'][()]
                    assert self.nc == f['exciton_header/params/nc'][()]
                    assert self.nk == f['exciton_header/kpoints/nk'][()]


                # reads in energies and exciton coefficients
                eigenvalues[:, iQ] = f['exciton_data/eigenvalues'][:self.nevecs]
                eigenvectors[..., iQ] = f['exciton_data/eigenvectors'][0,:self.nevecs,...].T

        self.eigs = eigenvalues / (Ry / eV)
        self.evecs = eigenvectors[0,...] + 1j * eigenvectors[1,...]

    def write(self):
        ex_data = {
            '/exciton_header/nevecs' : self.nevecs,
            '/exciton_header/ns' : self.ns,
            '/exciton_header/nv' : self.nv,
            '/exciton_header/nc' : self.nc,
            '/exciton_header/nk' : self.nk,
            '/exciton_header/nQ' : self.nQ,
            '/exciton_header/kpts' : self.kpts,
            '/exciton_header/center_of_mass_Q' : -1.0 * self.exciton_Q_shift,

            '/exciton_data/eigenvalues' : self.eigs,
            '/exciton_data/eigenvectors' : self.evecs,

            '/mf_header/crystal/blat' : self.blat,
            '/mf_header/crystal/bvec' : self.bvec,
        }
        with h5py.File('xct.h5', 'w') as f:
            f.create_group('exciton_header')
            f.create_group('exciton_data')
            for name, data in ex_data.items():
                f.create_dataset(name, data=data)

#endregion
