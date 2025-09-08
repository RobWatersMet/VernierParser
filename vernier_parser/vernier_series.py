"""
File containing the VernierSeries class.

Author: Rob Waters
"""
import pathlib
import statistics

from vernier_parser.vernier import Vernier


class VernierRecordsNotParsedError(Exception):
    """
    Exception for when methods called without results being parsed.
    """

    def __init__(self) -> None:
        """
        VernierRecordsNotParsedError initialiser.
        """
        super().__init__("Records not found in class - have you run "
                         "self.load_series()?")


class MissingRegionError(Exception):
    """
    Exception for when an expected caliper region is missing from a file.
    """

    def __init__(self, region_name: str, rank: int) -> None:
        """
        MissingRegionError initialiser.

        Args:
            region_name (str): the name of the caliper region expected.
            rank (int): the mpi rank file missing.

        """
        super().__init__("The following region was missing from mpi rank "
                         f"{rank}: {region_name}")


class VernierSeries:
    """
    Class for holding a series of data from many Vernier files.
    """

    def __init__(self, run_path: str) -> None:
        """
        VernierSeries initialiser.

        Args:
            run_path (str): path to the run folder, which should contain a
                vernier output file per mpi rank

        Raises:
            FileNotFoundError: if the input run_path does not exist.

        """
        self.run_path = pathlib.Path(run_path)

        if not self.run_path.exists():
            raise FileNotFoundError(self.run_path)

        self.mpi_ranks = None
        self.determine_mpi_ranks()

        self.vernier_results = None
        self.self_per_call_summary = None
        self.region_list = None

    def determine_mpi_ranks(self) -> None:
        """
        Method to determine the mpi ranks for a run from the contents of a run
        folder.

        Raises:
            FileNotFoundError: when an expected mpi rank file is not found.

        """
        print(self.run_path)

        files = sorted(self.run_path.glob("vernier-output*"))
        self.mpi_ranks = len(files)

        for rank in range(self.mpi_ranks):
            rank_filename = f"vernier-output-{rank}"
            path = pathlib.Path(self.run_path, rank_filename)
            if not path.exists():
                raise FileNotFoundError(rank_filename)

    def load_series(self) -> None:
        """
        Method to load in a series of Vernier data.
        """
        self.vernier_results = {}

        for rank in range(self.mpi_ranks):
            rank_filename = f"vernier-output-{rank}"
            path = pathlib.Path(self.run_path, rank_filename)
            self.vernier_results[str(rank)] = Vernier(path)
            self.vernier_results[str(rank)].process_vernier_output()

        self._get_caliper_region_list()

    def _get_caliper_region_list(self) -> None:

        if self.vernier_results is None:
            raise VernierRecordsNotParsedError

        self.region_list = {key for rank in self.vernier_results
             for key in self.vernier_results[rank].timings}

        for rank in self.vernier_results:
            for region in self.region_list:
                if region not in self.vernier_results[rank].timings:
                    raise MissingRegionError(region, int(rank))

    def summarise_self_per_call(self) -> None:
        """
        Method to create a summary of the self_per_call records from a vernier
        series.
        """
        self.self_per_call_summary = self._summarise_key("self_per_call")

    def _summarise_key(self, key: str) -> dict:

        results = {}
        for region in self.region_list:
            timings = [self.vernier_results[str(rank)].timings[
                region][key] for rank in range(self.mpi_ranks)]

            results[region] = {
                "mean": statistics.mean(timings),
                "max": max(timings),
                "min": min(timings),
            }

        return results
