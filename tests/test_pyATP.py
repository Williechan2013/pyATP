#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pyATP
----------------------------------

Tests for `pyATP` module.
"""
from __future__ import print_function, unicode_literals

import pytest

import os


import pyATP
import lineZ
import numpy as np


ATP_TEST_DIR = r'C:\Users\pdbrown\Documents\ATPdata\work\Test\\'
ATP_TMP_FILENAME = 'test_tmp.atp'

def assert_round_equals(n1, n2, **kwargs):
    if isinstance(n1, dict):
        # Check all keys exist
        for k in n1:
            assert k in n2
        # Check key existence the other way and verify values
        for k in n2:
            assert_round_equals(n1[k], n2[k], **kwargs)
        return
    try:
        assert np.allclose(n1, n2, equal_nan=True)
    except (TypeError):
        # Types that can't be rounded are checked for equivalence
        assert n1 == n2



@pytest.mark.parametrize('ATP_template, current_key, switch_key, '
                         'in_port, out_port, atp_segs',
                         [('Test.atp', '5432.1', '-7.654',
                           ('SRC', 'S0'), ('S1', 'TERRA'), ['LATIC', 'LATIC']),
                          ('Test2.atp', '5432.1', '-7.654',
                           ('SRC', 'S0'), ('S1', 'TERRA'), ['LATIC'])
                          ])
def test_extract_ABCD(ATP_template, current_key, switch_key,
                 in_port, out_port, atp_segs):
    ATP_file = ATP_TEST_DIR + ATP_template

    ABCD_atp = pyATP.extract_ABCD(ATP_file, ATP_TMP_FILENAME, current_key,
                                  switch_key, in_port, out_port)

    params = []
    for seg in atp_segs:
        with open(os.path.join(ATP_TEST_DIR, seg + '.pch')) as pch_file:
            pch_lines = pch_file.readlines()
            params_pch = pyATP.LineConstPCHCards()
            params_pch.read(pch_lines)
            params.append(params_pch)

    ABCD_pch_list = [p.ABCD for p in params]
    ABCD_eq = lineZ.combine_ABCD(ABCD_pch_list)
    assert_round_equals(ABCD_atp, ABCD_eq)


tc_line_const_pch = pyATP.LineConstPCHCards()

tt_line_const_pch = """
C  <++++++>  Cards punched by support routine on  05-May-16  14:58:52  <++++++>
C LINE CONSTANTS
C $ERASE
C BRANCH  IN___AOUT__AIN___BOUT__BIN___COUT__C
C ENGLISH
C   1  0.0    .344 0    .465    .642   -14.5     50.     25.
C   2  0.0    .344 0    .465    .642     0.0     50.     25.
C   3  0.0    .344 0    .465    .642    14.5     50.     25.
C   0  0.0    6.93 0    1.44     .36   -8.75   63.25   48.25
C   0  0.0    6.93 0    1.44     .36    8.75   63.25   48.25
C BLANK CARD ENDING CONDUCTOR CARDS
C      50.       60.           000001 001000 0    38.9     0        44
$VINTAGE, 1
$UNITS,  60.,  60.
 1IN___AOUT__A              1.91723657E+01  5.20611375E+01  1.80065993E+02
 2IN___BOUT__B              5.86703718E+00  2.12997966E+01 -2.77788794E+01
                            1.93343406E+01  5.19575791E+01  1.85084922E+02
 3IN___COUT__C              5.77782472E+00  1.80816951E+01 -1.06703365E+01
                            5.86703718E+00  2.12997966E+01 -2.77788794E+01
                            1.91723657E+01  5.20611375E+01  1.80065993E+02
$VINTAGE, -1,
$UNITS, -1., -1., { Restore values that existed b4 preceding $UNITS
""".splitlines()[1:]

line_const_values = [{'PH': 1, 'BUS1': 'IN___A', 'BUS2': 'OUT__A',
                      'R': 1.91723657E+01, 'L': 5.20611375E+01,
                      'C': 1.80065993E+02},
                     {'PH': 2, 'BUS1': 'IN___B', 'BUS2': 'OUT__B',
                      'R': 5.86703718E+00, 'L': 2.12997966E+01,
                      'C': -2.77788794E+01},
                     {'R': 1.93343406E+01, 'L': 5.19575791E+01,
                      'C': 1.85084922E+02},
                     {'PH': 3, 'BUS1': 'IN___C', 'BUS2': 'OUT__C',
                      'R': 5.77782472E+00, 'L': 1.80816951E+01,
                      'C': -1.06703365E+01},
                     {'R': 5.86703718E+00, 'L': 2.12997966E+01,
                      'C': -2.77788794E+01},
                     {'R': 1.91723657E+01, 'L': 5.20611375E+01,
                      'C': 1.80065993E+02}]

line_const_Z_mat = np.array([[1.91723657E+01 + 5.20611375E+01j,
                              5.86703718E+00 + 2.12997966E+01j,
                              5.77782472E+00 + 1.80816951E+01j],
                             [5.86703718E+00 + 2.12997966E+01j,
                              1.93343406E+01 + 5.19575791E+01j,
                              5.86703718E+00 + 2.12997966E+01j],
                             [5.77782472E+00 + 1.80816951E+01j,
                              5.86703718E+00 + 2.12997966E+01j,
                              1.91723657E+01 + 5.20611375E+01j]])


line_const_Y_mat = np.array([[1e-6j *  1.80065993E+02,
                              1e-6j * -2.77788794E+01,
                              1e-6j * -1.06703365E+01],
                             [1e-6j * -2.77788794E+01,
                              1e-6j *  1.85084922E+02,
                              1e-6j * -2.77788794E+01],
                             [1e-6j * -1.06703365E+01,
                              1e-6j * -2.77788794E+01,
                              1e-6j *  1.80065993E+02]])


@pytest.mark.parametrize("m", [line_const_Z_mat, line_const_Y_mat])
def test_symmetrical_matrix(m):
    assert_round_equals(m, m.T)


@pytest.mark.parametrize("test_card, card_text, values_dict_list, Z, Y",
                         [(tc_line_const_pch, tt_line_const_pch,
                           line_const_values, line_const_Z_mat,
                           line_const_Y_mat)])
class TestParseCard:
    def test_match(self, test_card, card_text, values_dict_list, Z, Y):
        test_card.read(card_text, read_all_or_none=False)
        assert test_card.match(card_text) is True

    def test_values(self, test_card, card_text, values_dict_list, Z, Y):
        test_card.read(card_text)
        for idx, values_dict in enumerate(values_dict_list):
            for k, v in values_dict.items():
                assert_round_equals(test_card.data['RLC_params'][idx][k], v)

    def test_Z(self, test_card, card_text, values_dict_list, Z, Y):
        test_card.read(card_text, read_all_or_none=False)
        assert_round_equals(test_card.Z, Z)

    def test_Y(self, test_card, card_text, values_dict_list, Z, Y):
        test_card.read(card_text, read_all_or_none=False)
        assert_round_equals(test_card.Y, Y)

    def test_ABCD(self, test_card, card_text, values_dict_list, Z, Y):
        test_card.read(card_text, read_all_or_none=False)
        assert_round_equals(test_card.ABCD, lineZ.ZY_to_ABCD(Z, Y))