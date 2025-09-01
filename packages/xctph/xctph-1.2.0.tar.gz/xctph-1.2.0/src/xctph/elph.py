#region modules
import os 
import h5py 
import xmltodict
import numpy as np 
from ase.units import Hartree, Rydberg, _amu, _me
import scipy 
from xctph.utils.k_plus_q import get_all_kq_maps
import jmespath
from xctph.utils.logging import get_logger
#endregion

#region variables
logger = get_logger()
#endregion

#region functions
#endregion

#region classes
class Elph:
    def __init__(
        self,
        nocc: int,
        nc: int,
        nv: int,
        npool: int = 1,
        elph_dirname: str = './save',
        qexml_filename: str = 'wfn.xml',
    ):
        self.elph_dirname: str = elph_dirname
        self.qexml_filename: str = qexml_filename
        self.npool: int = npool
        self.nocc: int = nocc
        self.nc: int = nc
        self.nv: int = nv 

        # Other vars.
        self.param_dict: dict = None        # Combination of qexml data and input_dict data elements that are needed. 

    def _to_array(self, string):
        return np.genfromtxt(string.split())
    
    def _cart2crys(self, kk, lat, alat):
        return np.dot(kk, (lat / alat).T)

    def read_from_input_and_qe(self):
        with open(os.path.join(self.elph_dirname, self.qexml_filename), 'r')as read_stream:
            qexml = xmltodict.parse(read_stream.read())

        # Update. Order is from base file used for refactoring. 
        self.prefix = qexml[u'qes:espresso']['input']['control_variables']['prefix']
        
        # parse qexml input.
        input_node = qexml[u'qes:espresso']['input']
        self.nat = int(input_node['atomic_structure']['@nat'])
        self.alat = float(input_node['atomic_structure']['@alat'])
        self.ntyp = int(input_node['atomic_species']['@ntyp'])
        self.lat = np.zeros((3, 3), 'f8')
        self.pos = np.zeros((self.nat, 3), 'f8')
        self.species = dict()
        self.typlist = list()
        self.masses = np.zeros(self.ntyp, 'f8')
        for i in range(3):
            self.lat[i, :] = self._to_array(input_node['atomic_structure']['cell']['a{}'.format(i + 1)])
        self.recip_lat = 2 * np.pi * np.linalg.inv(self.lat)
        if self.ntyp == 1:
            self.species[str(input_node['atomic_species']['species']['@name'])] = 0
            self.masses[0] = float(input_node['atomic_species']['species']['mass'])
        else:
            for i in range(self.ntyp):
                self.species[str(input_node['atomic_species']['species'][i]['@name'])] = i
                self.masses[i] = float(input_node['atomic_species']['species'][i]['mass'])
        f_atom = input_node['atomic_structure']['atomic_positions']['atom']
        if self.nat == 1:
            self.typlist.append(f_atom['@name'])
            self.pos[0, :] = self._to_array(f_atom['#text'])
        else:
            for i in range(self.nat):
                self.typlist.append(f_atom[i]['@name'])
                self.pos[i, :] = self._to_array(f_atom[i]['#text'])

        self.typlist_num = [self.species[typ] for typ in self.typlist]

        # parse qexml output.
        output_node = qexml[u'qes:espresso']['output']['band_structure']
        self.nbnd = self.nocc + self.nc
        self.nbnd_end = self.nocc + self.nc 
        self.nbnd_begin = self.nocc - self.nv 
        self.nbnd_red = self.nc + self.nv 
        self.nk = int(output_node['nks'])
        self.nq = self.nk 
        self.kpts_cart = np.zeros((self.nk, 3), 'f8')
        for ik in range(self.nk):
            self.kpts_cart[ik, :] = self._to_array(output_node['ks_energies'][ik]['k_point']['#text'])
        self.kpts = self._cart2crys(self.kpts_cart, self.lat, self.alat)
        self.nmodes = 3 * self.nat 
        self.nk_per_pool = int(self.nk / self.npool)

        if self.nbnd_begin > self.nbnd_end:
            raise Exception('Keyword "nbnd_begin" cannot be greater than "nbnd_end".')
        elif self.nbnd_end > self.nbnd:
            raise Exception('Keyword "nbnd_begin" cannot be greater than "nbnd in QE".')
        if self.nbnd_begin < 0:
            raise Exception('Keyword "nbnd_begin" cannot be less than 0.')
        
    def read_from_epb(self):
        self.elph_cart = np.zeros((self.nbnd_red, self.nbnd_red, self.nk, self.nmodes, self.nq), 'c16')
        
        # Loop through and read epb files
        ikk = 0
        for ipool in range(self.npool):

            print('Reading in {}.epb{}'.format(self.prefix, ipool + 1))

            f_in = '{}/{}.epb{}'.format(self.elph_dirname, self.prefix, ipool + 1)
            f = scipy.io.FortranFile(f_in, mode='r')

            # Define shape of all quantities to be read in.
            nqc_dim = 'i4'
            xqc_dim = '{}f8'.format(3 * self.nq)
            et_dim = '{}f8'.format(self.nbnd * self.nk_per_pool)

            dynq_dim = '{}c16'.format(self.nmodes * self.nmodes * self.nq)
            epmatq_dim = '{}c16'.format(self.nbnd_red * self.nbnd_red * self.nmodes * self.nk_per_pool * self.nq)
            zstar_dim = '{}f8'.format(3 * self.nmodes)
            epsi_dim = '{}f8'.format(3 * 3)

            # Read in all epb file
            record = f.read_record(nqc_dim, xqc_dim, et_dim, dynq_dim, epmatq_dim, zstar_dim, epsi_dim)

            if ipool == 0:
                nq_readin = record[0][0]
                qpts_cart = record[1].reshape(3, self.nq, order='F').T
                ekq = record[2].reshape(self.nbnd, self.nk_per_pool, order='F')
                self.dynmat = record[3].reshape(self.nmodes, self.nmodes, self.nq, order='F')
                self.qpts = self._cart2crys(qpts_cart, self.lat, self.alat)
                assert nq_readin == self.nq

            gqk_readin = record[4].reshape(self.nbnd_red, self.nbnd_red, self.nk_per_pool, self.nmodes, self.nq, order='F')
            self.elph_cart[:, :, ikk:ikk + self.nk_per_pool, :, :] = gqk_readin[:, :, ...]

            ikk = (ipool + 1) * self.nk_per_pool

    def calc_dyn(self):
        pass

    def rotate_to_mode_basis(self):
        # Rotate epb matrix elements from atomic to mode basis
        self.elph_mode = np.zeros((self.nbnd_red, self.nbnd_red, self.nk, self.nmodes, self.nq), 'c16')
        self.frequencies = np.zeros((self.nmodes, self.nq), 'f8')
        self.phevecs = np.zeros((3 * self.nat, self.nmodes, self.nq), 'c16')
        self.phmasses = np.zeros((3 * self.nat), 'f8')
        self.phevecs_massred = np.zeros((3 * self.nat, self.nmodes, self.nq), 'c16') 

        print('Begin rotating from gkq from atomic to mode basis')

        for iq in range(self.nq):
            print('start iq={}'.format(iq))

            dyn = self.dynmat[..., iq]
            dynm = np.zeros((self.nmodes, self.nmodes), 'c16')

            # Compute mass reduced dyn (which we call dynm)
            for i in range(self.nat):
                for j in range(self.nat):
                    m_i = self.masses[self.typlist_num[i]]
                    m_j = self.masses[self.typlist_num[j]]

                    fac = 1.0 / (np.sqrt(m_i * m_j) * _amu/_me / 2.)

                    dynm[3 * i:3 * (i + 1), 3 * j:3 * (j + 1)] = dyn[3 * i:3 * (i + 1), 3 * j:3 * (j + 1)] * fac

            # Symmetrize dynm (which we call dynm_sym)
            dynm_sym = np.asarray((dynm + np.conj(dynm).T) / 2, 'c16')

            # frequencies.
            w2, self.phevecs[:, :, iq] = np.linalg.eigh(dynm_sym)
            for imode in range(self.nmodes):

                if iq == 0 and imode < 3:
                    self.frequencies[imode, iq] = 0.

                else:
                    if w2[imode] < 0.0:
                        print('Warning: The frequency associated with mode ' \
                            'iq = {}, imode = {} is negative w ={}.' \
                            .format(iq, imode, w2[imode]) )

                    self.frequencies[imode, iq] = np.sqrt(np.abs(w2[imode]))

            # modes. (mass reduced normal modes.)

            for i in range(self.nat):
                m_i = self.masses[self.typlist_num[i]]
                self.phevecs_massred[3 * i:3 * (i + 1), :, iq] = \
                    self.phevecs[3 * i:3 * (i + 1), :, iq] / np.sqrt(m_i * _amu/ _me / 2.)
                self.phmasses[3 * i: 3 * (i + 1)] = m_i * _amu / _me / 2.   # In Rydberg units.
                
            # Loop through gkq_ia and transform into the mode basis
            gk_ai = self.elph_cart[..., iq]
            gk_nu = np.zeros((self.nbnd_red, self.nbnd_red, self.nk, self.nmodes), 'c16')

            for ib in range(self.nbnd_red):
                for jb in range(self.nbnd_red):
                    for ik in range(self.nk):
                        for imode in range(self.nmodes):
                            gk_nu[ib, jb, ik, imode] = np.dot(gk_ai[ib, jb, ik, :], self.phevecs_massred[:, imode, iq])

            for imode in range(self.nmodes):
                if iq == 0 and imode < 3:
                    self.elph_mode[..., imode, iq] = 0.
                else:
                    self.elph_mode[..., imode, iq] = gk_nu[..., imode] / np.sqrt(2 * self.frequencies[imode, iq])

    def calc_k_plus_q_map(self):
        # We also compute the kq_maps in this
        self.k_plus_q_map = get_all_kq_maps(self.kpts, self.qpts)
        self.k_minus_q_map = get_all_kq_maps(self.kpts, self.qpts, plus_or_minus=-1.0)

    def read(self):
        self.read_from_input_and_qe()
        self.read_from_epb()
        self.calc_dyn()
        self.rotate_to_mode_basis()   
        self.calc_k_plus_q_map()

    def write(self):
        # Everything i
        sorting_dict = {
            # Header information.
            'elph_header/ns': 1,
            'elph_header/nbndskip': self.nbnd_begin,
            'elph_header/nbnd': self.nbnd_red,
            'elph_header/nocc': self.nocc,
            'elph_header/nmode': self.nmodes,
            'elph_header/nk': self.nk,
            'elph_header/nq': self.nq,
            'elph_header/kpts': self.kpts,
            'elph_header/qpts': self.qpts,
            'elph_header/recip_lat': self.recip_lat,
            
            # Information on k+q mappings.
            'elph_header/k_plus_q_map': self.k_plus_q_map,
            'elph_header/k_minus_q_map': self.k_minus_q_map,

            # Data sets.
            'elph_data/frequencies': self.frequencies,
            'elph_data/phevecs': self.phevecs,
            'elph_data/phevecs_massred': self.phevecs_massred,
            'elph_data/phmasses': self.phmasses,
            'elph_data/elph_mode': self.elph_mode,
            'elph_data/elph_cart': self.elph_cart,
        }
        
        with h5py.File('elph.h5', 'w') as f:
            for name, data in sorting_dict.items():
                f.create_dataset(name, data=data)

#endregion
