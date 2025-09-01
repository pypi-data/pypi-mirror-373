#!/usr/bin/env python

import numpy as np
import h5py
from mpi4py import MPI
from xctph.kpoints import get_all_kq_maps


# TODO: Generalize to an shape. Currently only supports 2D shapes.
class ParSize:
    def __init__(self, shape, comm: MPI.Comm):
        self.shape = shape
        self.array_size: int = int(np.prod(np.array(shape)))
        self.comm: MPI.Comm = comm

        # Do the setup here.
        self.mpi_size = comm.Get_size()
        self.mpi_rank = comm.Get_rank()
        self._calc_local_ranges()

    def _calc_local_ranges(self):
       self.local_size_avg = self.array_size // self.mpi_size
       self.local_size_max = self.local_size_avg + self.array_size -  (self.array_size // self.mpi_size ) * self.mpi_size
       self.local_size = self.local_size_avg if self.mpi_rank != self.mpi_size-1 else self.local_size_max
       self.local_start = self.local_size_avg * self.mpi_rank  
       self.local_end = self.local_start + self.local_size 

    def get_local_range(self):
        return (self.local_start, self.local_end)

    def get_idx(self, linear_idx):
        return (linear_idx // self.shape[1], linear_idx % self.shape[0]) 

def compute_xctph(fname_eph_h5, fname_xct_h5, nbnd_xct, add_electron_part, add_hole_part):
    """ Compute the exciton-phonon matrix elements. """

    with h5py.File(fname_eph_h5, 'r') as f:
        nmodes = f['gkq_header/nmode'][()]
        nk_elph = f['gkq_header/nk'][()]
        kpts_elph = f['gkq_header/kpts'][()]
        nq = f['gkq_header/nq'][()]
        qpts = f['gkq_header/qpts'][()]
        k_plus_q_map = f['gkq_mappings/k_plus_q_map'][()]
        frequencies = f['gkq_data/frequencies'][()]
        gkq = f['gkq_data/g_nu'][()]

    with h5py.File(fname_xct_h5, 'r') as f:
        nbnd = f['/exciton_header/nevecs'][()]
        nv = f['/exciton_header/nv'][()]
        nc = f['/exciton_header/nc'][()]
        nk = f['/exciton_header/nk'][()]
        kpts = f['/exciton_header/kpts'][()]
        nQ = f['/exciton_header/nQ'][()]
        Qpts = f['/exciton_header/center_of_mass_Q'][()]
        energies = f['/exciton_data/eigenvalues'][()]
        avck = f['/exciton_data/eigenvectors'][()]


    # consistency checks:
    assert nk_elph == nk
    assert nbnd >= nbnd_xct

    # generate additional kq maps
    Q_plus_q_map = get_all_kq_maps(Qpts, qpts)
    k_minus_Q_map = get_all_kq_maps(kpts, Qpts, -1.0)

    # xct-ph matrix elements are packaged the same way as el-ph
    # gQq = np.zeros((nbnd_xct, nbnd_xct, nQ, nmodes, nq), 'c16')
    # Parallel version.
    comm = MPI.COMM_WORLD
    xctbnd_parsize = ParSize(shape=(nbnd_xct, nbnd_xct), comm=comm)
    xct_start, xct_end = xctbnd_parsize.get_local_range()
    gQq: np.ndarray = np.zeros((xct_end - xct_start, nQ, nmodes, nq), 'c16')

    cb = slice(nv, nv + nc)
    vb = slice(0, nv)

    for iQ in range(nQ):
      for iq in range(nq):
        iQ_plus_q = Q_plus_q_map[iQ, iq]

        for ik in range(nk):
          ik_plus_q = k_plus_q_map[ik, iq]
          ik_minus_Q = k_minus_Q_map[ik, iQ]

        #   for mb in range(nbnd_xct):
        #     for nb in range(nbnd_xct):

        #         # electron channel
        #         aQ_e = avck[0, :, :, ik, nb, iQ]
        #         aQq_e = avck[0, :, :, ik_plus_q, mb, iQ_plus_q]
        #         gkq_e = gkq[cb, cb, ik, :, iq]

        #         if add_electron_part:
        #             gQq[mb, nb, iQ, :, iq] += np.einsum('vc,cdn,vd->n', aQq_e.conj(), gkq_e, aQ_e)

        #         # hole channel
        #         aQ_h = avck[0, :, :, ik_plus_q, nb, iQ]
        #         aQq_h = avck[0, :, :, ik_plus_q, mb, iQ_plus_q]
        #         gkq_h = gkq[vb, vb, ik_minus_Q, :, iq][::-1, ::-1, :]

        #         if add_hole_part:
        #             gQq[mb, nb, iQ, :, iq] -= np.einsum('vc,wvn,wc->n', aQq_h.conj(), gkq_h, aQ_h)

        # Parallel version. 
          for mnb in range(xct_start, xct_end):
            mb, nb = xctbnd_parsize.get_idx(mnb)
            # electron channel
            aQ_e = avck[0, :, :, ik, nb, iQ]
            aQq_e = avck[0, :, :, ik_plus_q, mb, iQ_plus_q]
            gkq_e = gkq[cb, cb, ik, :, iq]

            if add_electron_part:
                gQq[mnb - xct_start, iQ, :, iq] += np.einsum('vc,cdn,vd->n', aQq_e.conj(), gkq_e, aQ_e)

            # hole channel
            aQ_h = avck[0, :, :, ik_plus_q, nb, iQ]
            aQq_h = avck[0, :, :, ik_plus_q, mb, iQ_plus_q]
            gkq_h = gkq[vb, vb, ik_minus_Q, :, iq][::-1, ::-1, :]

            if add_hole_part:
                gQq[mnb - xct_start, iQ, :, iq] -= np.einsum('vc,wvn,wc->n', aQq_h.conj(), gkq_h, aQ_h)



    xctph_dict = {
        # header information.
        'ns': 1,
        'nbndskip': 0,
        'nbnd': nbnd_xct,
        'nocc': 0,
        'nmode': nmodes,
        'nQ': nQ,
        'nq': nq,
        'Qpts': Qpts,
        'qpts': qpts,

        # Q+q mappings.
        'Q_plus_q_map': Q_plus_q_map,

        # energies, frequencies, and matrix elements.
        'energies': energies[:nbnd_xct, :],
        'frequencies': frequencies,
        'xctph' : gQq,

    }

    # f = h5py.File('xctph.h5', 'w')
    # for name, data in xctph_dict.items():
    #     f.create_dataset(name, data=data)
    # f.close()

    # Parallel version. 
    with h5py.File('xctph.h5', 'w', driver='mpio', comm=comm) as f:
        # Write everything except the xctph data array, as that needs to be written in parallel.
        for name, data in xctph_dict.items():
            if name != 'xctph':
                f.create_dataset(name, data=data)
            else:
                # Write the xctph array in parallel.
                ds_xctph_linear = f.create_dataset('xctph_linear', shape=(nbnd_xct*nbnd_xct, nQ, nmodes, nq), dtype=gQq.dtype)
                ds_xctph_linear[xct_start:xct_end, ...] = data

    # # Reshape only on main node.
    if xctbnd_parsize.mpi_rank==0:
        with h5py.File('xctph.h5', 'a') as w:
            xctph = w['xctph_linear'][:].reshape(nbnd_xct, nbnd_xct, nQ, nmodes, nq)
            del w['xctph_linear']
            w.create_dataset('xctph', data=xctph)

    comm.Barrier()

    return


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname_eph_h5')
    parser.add_argument('fname_xct_h5')
    parser.add_argument('nbnd_xct', type=int)
    parser.add_argument('--add_electron_part', action='store_true', help='Add electron part to xctph computation')
    parser.add_argument('--add_hole_part', action='store_true', help='Add hole part to xctph computation')
    args = parser.parse_args()

    compute_xctph(**vars(args))
