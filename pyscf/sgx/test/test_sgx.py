# Copyright 2014-2020 The PySCF Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Qiming Sun <osirpt.sun@gmail.com>
#

import unittest
from pyscf import gto
from pyscf import scf, dft
from pyscf.sgx import sgx


class KnownValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_grids = dft.radi.ATOM_SPECIFIC_TREUTLER_GRIDS
        dft.radi.ATOM_SPECIFIC_TREUTLER_GRIDS = False

    @classmethod
    def tearDownClass(cls):
        dft.radi.ATOM_SPECIFIC_TREUTLER_GRIDS = cls.original_grids

    def test_reset(self):
        mol = gto.M(atom='He')
        mol1 = gto.M(atom='C')
        mf = scf.RHF(mol).COSX()
        mf.reset(mol1)
        self.assertTrue(mf.mol is mol1)
        self.assertTrue(mf.with_df.mol is mol1)
        self.assertEqual(mf.undo_sgx().__class__.__name__, 'RHF')

    def test_sgx_scf(self):
        mol = gto.Mole()
        mol.build(
            atom = [["O" , (0. , 0.     , 0.)],
                    [1   , (0. , -0.757 , 0.587)],
                    [1   , (0. , 0.757  , 0.587)] ],
            basis='ccpvdz',
            verbose=0,
        )
        mf = sgx.sgx_fit(scf.RHF(mol), 'weigend')
        mf.with_df.dfj = True
        mf.with_df.use_opt_grids = False
        mf.with_df.grids_level_f = 1
        mf.with_df._symm_ovlp_fit = False
        energy = mf.kernel()
        self.assertAlmostEqual(energy, -76.02686422219752, 9)

        mf = sgx.sgx_fit(scf.RHF(mol))
        mf.with_df.use_opt_grids = False
        mf.with_df.grids_level_f = 1
        mf.with_df.optk = False
        mf.with_df.dfj = False
        energy = mf.kernel()
        self.assertAlmostEqual(energy, -76.02673747035047, 8)

    def test_sgx_pjs(self):
        mol = gto.Mole()
        atom0 = [["O" , (0. , 0.     , 0.)],
                 [1   , (0. , -0.757 , 0.587)],
                 [1   , (0. , 0.757  , 0.587)],]
        atom = []
        for i in range(3):
            atom = atom + [[z, (c[0] + i * 5, c[1], c[2])] for z, c in atom0]
        mol.build(
            atom=atom,
            basis='sto-3g',
            verbose=0,
        )
        mf = sgx.sgx_fit(mol.RHF())
        mf.with_df.dfj = True
        mf.with_df.use_opt_grids = False
        mf.with_df.grids_level_f = 1
        mf.with_df.sgx_tol_energy = None
        mf.with_df.sgx_tol_potential = None
        energy = mf.kernel()
        mf = sgx.sgx_fit(mol.RHF())
        mf.with_df.dfj = True
        mf.with_df.use_opt_grids = False
        mf.with_df.grids_level_f = 1
        mf.with_df.sgx_tol_energy = None
        mf.with_df.sgx_tol_potential = None
        mf.with_df.sgx_tol_energy = 1e-9
        mf.with_df.sgx_tol_potential = "auto"
        energy2 = mf.kernel()
        self.assertAlmostEqual(energy, energy2, 9)

    def test_check_extra_convergence(self):
        mol = gto.M(atom='He', basis='sto-3g', verbose=0)
        mf = sgx.sgx_fit(scf.RHF(mol))
        base_envs = {
            'e_tot': 0.0,
            'last_hf_e': 0.0,
            'conv_tol': 1e-11,
            'norm_gorb': 0.0,
            'conv_tol_grad': 3e-6,
        }
        cases = (
            ('both pass', 0.5e-11, 0.5e-6, True),
            ('energy only', 0.5e-11, 4e-6, False),
            ('gradient only', 2.6267343855579384e-10,
             4.0347904631078535e-9, False),
            ('neither', 2e-11, 4e-6, False),
        )
        for name, delta_e, norm_gorb, expected in cases:
            with self.subTest(name):
                envs = dict(base_envs, e_tot=delta_e, norm_gorb=norm_gorb)
                self.assertEqual(mf.check_extra_convergence(envs), expected)


if __name__ == "__main__":
    print("Full Tests for SGX")
    unittest.main()
