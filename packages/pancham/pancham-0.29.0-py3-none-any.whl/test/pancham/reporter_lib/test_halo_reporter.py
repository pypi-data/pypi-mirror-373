from pandas import DataFrame

from pancham.reporter_lib.halo_reporter import HaloReporter


class TestHaloReporter:

    def test_halo_reporter(self):
        reporter = HaloReporter()
        file = 'abc'

        reporter.report_start(file)
        reporter.report_end(file, DataFrame())
        reporter.report_end('other', DataFrame())

        assert len(reporter.spinners) == 1