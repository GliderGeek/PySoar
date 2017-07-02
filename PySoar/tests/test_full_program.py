import os
import unittest
import pandas as pd
from pandas.util.testing import assert_frame_equal

from PySoar.analysis import run


class TestFullProgram(unittest.TestCase):
    """These tests assure that the performance data-frame of the full flight are as expected"""

    def test_race_task(self):
        """This test checks the results of a race task"""

        url = 'http://www.soaringspot.com/en/sallandse-tweedaagse-2014/results/club/task-1-on-2014-06-21/daily'
        result = run(url, return_performance_dfs=True)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        expected_result = pd.read_json(os.path.join(dir_path, 'racetask.json'))
        assert_frame_equal(result[0], expected_result, check_like=True, check_dtype=False)

    def test_aat(self):
        """This test checks the results of an AAT"""

        url = 'http://www.soaringspot.com/en_gb/cae-nls-nederlandse-kampioenschappen-zweefvliegen-2012/results/club/task-10-on-2012-05-26/daily'
        result = run(url, return_performance_dfs=True)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        expected_result = pd.read_json(os.path.join(dir_path, 'aat.json'))
        assert_frame_equal(result[0], expected_result, check_like=True, check_dtype=False)

