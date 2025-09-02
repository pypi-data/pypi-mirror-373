"""
This module contains various crystalographics classifications,
and the LatticeData object, that provides various informations about a lattice.
"""
from ..common.decorators import cached_property
import numpy as np
from ase2sprkkr.bindings.spglib import spglib_dataset
from ase.units import Bohr
from collections import namedtuple
from scipy.optimize import linear_sum_assignment

def reorder_matrix(target, source):
    # normalize vectors (rows)
    src_norm = source / np.linalg.norm(source, axis=1, keepdims=True)
    tgt_norm = target / np.linalg.norm(target, axis=1, keepdims=True)

    # compute similarity matrix (cosine similarity)
    sim = tgt_norm @ src_norm.T   # shape (3,3)
    # convert to cost matrix (maximize similarity -> minimize negative similarity)
    cost = -sim
    # Hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(cost)

    # reorder target rows to best match source
    reordered = target[row_ind[np.argsort(col_ind)]]
    return reordered

# Example
S = np.array([[1,0,0],
              [0,1,0],
              [0,0,1]], dtype=float)

T = np.array([[0,0,2],
              [3,0,0],
              [0,5,0]], dtype=float)


class Pearson(namedtuple("Pearson", [
    "pearson_symbol",
    "bravais_number",
    "family",
    "centering_type",
    "herman_mauguin",
    "shoenflies", #Shoenflies
    ])):
    """ This class holds informations about translation symmetry of a lattice with a given
    Pearson symbol. """

    def xband_data(self):
        """ Data used by Xband sysfile and SPRKKR to describe translation symmetry."""
        return self[1:]

    @staticmethod
    def from_symbol(pearson_symbol:str):
        """ Return the Pearson symbol (describing the translation symmetry) that corresponds to the
        given Pearson symbol """
        return Pearson.pearsons[Pearson.normalize_symbol(pearson_symbol)]

    @staticmethod
    def normalize_symbol(pearson_symbol):
      """ Normalize a Pearson symbol to its cannonical shape"""
      if pearson_symbol[1] in ('A', 'B', 'C'):
          pearson_symbol = pearson_symbol[0] + 'S'
      return pearson_symbol

    pearson=None
    """ Mapping of all possible Pearson symbols to Pearson objects"""

Pearson.pearsons = {i.pearson_symbol:i for i in [
        Pearson('aP',  1, 'triclinic',   'primitive',      '-1',     'C_i'),
        Pearson('mP',  2, 'monoclinic',  'primitive',      '2/m',    'C_2h'),
        Pearson('mS',  3, 'monoclinic',  'primitive',      '2/m',    'C_2h'),
        Pearson('oP',  4, 'orthorombic', 'primitive',      'mmm',    'D_2h'),
        Pearson('oS',  5, 'orthorombic', 'base-centered',  'mmm',    'D_2h'),
        Pearson('oI',  6, 'orthorombic', 'body-centered',  'mmm',    'D_2h'),
        Pearson('oF',  7, 'orthorombic', 'face-centered',  'mmm',    'D_2h'),
        Pearson('tP',  8, 'tetragonal',  'primitive',      '4/mmm',  'D_4h'),
        Pearson('tI',  9, 'tetragonal',  'body-centered',  '4/mmm',  'D_4h'),
        Pearson('hR', 10, 'trigonal',    'primitive',      '-3m',    'D_3d'),
        Pearson('hP', 11, 'hexagonal',   'primitive',      '6/mmm',  'D_6h'),
        Pearson('cP', 12, 'cubic',       'primitive',      'm3m',    'O_h'),
        Pearson('cF', 13, 'cubic',       'face-centered',  'm3m',    'O_h'),
        Pearson('cI', 14, 'cubic',       'body-centered',  'm3m',    'O_h')
    ]}



#: Translation of international tables numbers to A. Perlovs numbering.
international_numbers_to_AP = {
                1 : 1,
                2 : 2,
                3 : 3,
                4 : 5,
                5 : 7,
                6 :  13,
                7 :  15,
                8 :  21,
                9 :  27,
                10 : 39,
                11 : 41,
                12 : 43,
                13 : 50,
                14 : 55,
                15 : 61,
                16 : 73,
                17 : 74,
                18 : 77,
                19 : 80,
                20 : 81,
                21 : 84,
                22 : 87,
                23 : 88,
                24 : 89,
                25 : 90,
                26 : 93,
                27 : 99,
                28 : 102,
                29 : 108,
                30 : 114,
                31 : 120,
                32 : 126,
                33 : 129,
                34 : 135,
                35 : 138,
                36 : 145,
                37 : 147,
                38 : 150,
                39 : 156,
                40 : 162,
                41 : 168,
                42 : 174,
                43 : 177,
                44 : 180,
                45 : 183,
                46 : 186,
                47 : 192,
                48 : 193,
                49 : 195,
                50 : 198,
                51 : 204,
                52 : 210,
                53 : 216,
                54 : 222,
                55 : 228,
                56 : 231,
                57 : 234,
                58 : 240,
                59 : 247,
                60 : 249,
                61 : 255,
                62 : 257,
                63 : 263,
                64 : 269,
                65 : 275,
                66 : 278,
                67 : 281,
                68 : 287,
                69 : 299,
                70 : 300,
                71 : 302,
                72 : 303,
                73 : 306,
                74 : 308,
                75 : 314,
                76 : 315,
                77 : 316,
                78 : 317,
                79 : 318,
                80 : 319,
                81 : 320,
                82 : 321,
                83 : 322,
                84 : 323,
                85 : 324,
                86 : 326,
                87 : 328,
                88 : 329,
                89 : 331,
                90 : 332,
                91 : 333,
                92 : 334,
                93 : 335,
                94 : 336,
                95 : 337,
                96 : 338,
                97 : 339,
                98 : 340,
                99 : 341,
                100 : 342,
                101 : 343,
                102 : 344,
                103 : 345,
                104 : 346,
                105 : 347,
                106 : 348,
                107 : 349,
                108 : 350,
                109 : 351,
                110 : 352,
                111 : 353,
                112 : 354,
                113 : 355,
                114 : 356,
                115 : 357,
                116 : 358,
                117 : 359,
                118 : 360,
                119 : 361,
                120 : 362,
                121 : 363,
                122 : 364,
                123 : 365,
                124 : 366,
                125 : 368,
                126 : 370,
                127 : 371,
                128 : 372,
                129 : 374,
                130 : 376,
                131 : 377,
                132 : 378,
                133 : 380,
                134 : 382,
                135 : 383,
                136 : 384,
                137 : 386,
                138 : 388,
                139 : 389,
                140 : 390,
                141 : 392,
                142 : 394,
                143 : 396,
                144 : 398,
                145 : 400,
                146 : 401,
                147 : 404,
                148 : 405,
                149 : 407,
                150 : 408,
                151 : 409,
                152 : 410,
                153 : 411,
                154 : 412,
                155 : 414,
                156 : 415,
                157 : 416,
                158 : 417,
                159 : 418,
                160 : 420,
                160 : 419,
                161 : 422,
                162 : 423,
                163 : 424,
                164 : 425,
                165 : 426,
                166 : 428,
                167 : 430,
                168 : 431,
                169 : 432,
                170 : 433,
                171 : 434,
                172 : 435,
                173 : 436,
                174 : 437,
                175 : 438,
                176 : 439,
                177 : 440,
                178 : 441,
                179 : 442,
                180 : 443,
                181 : 444,
                182 : 445,
                183 : 446,
                184 : 447,
                185 : 448,
                186 : 449,
                187 : 450,
                188 : 451,
                189 : 452,
                190 : 453,
                191 : 454,
                192 : 455,
                193 : 456,
                194 : 457,
                195 : 458,
                196 : 459,
                197 : 460,
                198 : 461,
                199 : 462,
                200 : 463,
                201 : 465,
                202 : 466,
                203 : 468,
                204 : 469,
                205 : 470,
                206 : 471,
                207 : 472,
                208 : 473,
                209 : 474,
                210 : 475,
                211 : 476,
                212 : 477,
                213 : 478,
                214 : 479,
                215 : 480,
                216 : 481,
                217 : 482,
                218 : 483,
                219 : 484,
                220 : 485,
                221 : 486,
                222 : 488,
                223 : 489,
                224 : 491,
                225 : 492,
                226 : 493,
                227 : 494,
                229 : 498,
                230 : 499
                }

class LatticeData:

  def __init__(self, atoms):
      cell = atoms.get_cell()
      bl = cell.get_bravais_lattice()
      sg = spglib_dataset(atoms)
      ps = bl.pearson_symbol
      self.pearson = Pearson.from_symbol(ps)

      self.basis = 0
      self.sgno=sg.number
      self.apno=international_numbers_to_AP[sg.number]

      self.bravais = cell.get_bravais_lattice()

      self.boa = cell.cellpar()[1] / cell.cellpar()[0]
      self.coa = cell.cellpar()[2] / cell.cellpar()[0]

      self.alat = bl.a / Bohr
      self.blat = self.boa*self.alat
      self.clat = self.coa*self.alat

      self.alpha=cell.cellpar()[3]
      self.beta=cell.cellpar()[4]
      self.gamma=cell.cellpar()[5]
      self.sg = sg
      self.cell = cell

  @cached_property
  def rbas(self):
      #self.rbas = sg.scaled_primitive_cell
      sg = self.sg
      out = sg.primitive_lattice.dot(np.linalg.inv(sg.std_lattice))
      return reorder_matrix(out, self.cell)

  @property
  def bravais_number(self):
      return self.pearson.bravais_number

  @property
  def shoenflies_symbol(self):
      return pearson_to_shoenflies[self.pearson.pearson_symbol]
