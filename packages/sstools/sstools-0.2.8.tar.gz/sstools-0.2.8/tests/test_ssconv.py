import logging.config
import unittest

from sstools.ssconv import ssconv

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(name)-30s %(levelname)-8s %(message)s',
            '()': 'multiline_formatter.formatter.MultilineMessagesFormatter',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        # '' root logger
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
})

logger = logging.getLogger()




class ConverterTest(unittest.TestCase):
    # Conversion is verified with the FINA Points Calculator 6.47605
    @classmethod
    def setUpClass(cls):
        pass

    # preparing to test
    def setUp(self):
        """ Setting up for the test """

    def tearDown(self):
        """Cleaning up after the test"""

    def test_finapts(self):
        finapts_refs = [1, 999, 1000, 1001]
        available_styles = ssconv.get_available_styles()
        genders = ['M', 'F']
        courses = ['SCM', 'LCM']
        for finapts_ref in finapts_refs:
            for style in available_styles:
                for gender in genders:
                    for course in courses:
                        if style != '100m Medley' and course != 'LCM':
                            swimtime = ssconv.get_seconds_from_finapts(course, gender, style, finapts_ref)
                            finapts = ssconv.get_finapts_from_seconds(course, gender, style, swimtime)
                            self.assertAlmostEqual(finapts_ref, finapts, delta=1)


    def test_get_rudolphpts_from_seconds(self):
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 9, 20), 20)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 9, [76.07, 75, 74], 2024), [14.9, 15.9, 16.8])


        # # https://www.swimrankings.net/index.php?page=athleteDetail&athleteId=4605725&pbest=2013
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 8, 106.65, 2024), 0)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 9, 76.07, 2024), 14.9)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 10, 66.99, 2024), 18.7)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 11, 61.2, 2024), 18.9)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 12, 57.16, 2024), 18.9)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 13, 55.56, 2024), 17.4)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 14, 52.67, 2024), 18.6)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 15, 50.9, 2024), 19.1)
        self.assertEqual(ssconv.get_rudolphpts_from_seconds('M', '100m Freestyle', 16, 50.68, 2024), 18.5)


    def test_get_seconds_from_rudolphpts(self):
        self.assertEqual(ssconv.get_seconds_from_rudolphpts('M', '100m Freestyle', 9, [15.3, 16.2, 17.2], 2024), [75.633, 74.652, 73.562])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(ConverterTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
