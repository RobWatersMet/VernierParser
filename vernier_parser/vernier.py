"""
File containing the Vernier class.

Author: Rob Waters
"""
import pathlib


class DoubleRecordError(Exception):
    """
    Exception to be raised when two records found for same caliper in file.
    """

    def __init__(self, record_name: str = "Record_name") -> None:
        """
        DoubleRecordError initaliser.

        Args:
            record_name (str, optional): Name of caliper region where two
            records have been found. Defaults to "Record_name".

        """
        super().__init__(f"Two records found for {record_name}")


class Vernier:
    """
    Class for parsing a vernier output file.
    """

    RECORD_LEN = 9

    def __init__(self, vernier_output_file: pathlib.Path) -> None:
        """
        Initialiser for a Vernier class instance.

        Args:
            vernier_output_file (pathlib.Path): path to the vernier output file
                to be parsed.

        """
        self.vernier_output_file = vernier_output_file
        self.threads = None
        self.timings = {}

    def process_vernier_output(self) -> None:
        """
        Method for parsing the vernier output file.
        """
        with pathlib.Path.open(self.vernier_output_file, "r",
                               encoding="utf-8") as f:

            while True:
                line = f.readline()
                if not line:
                    break
                parts = line.split(" ")
                parts = [i.strip(" ") for i in parts]
                parts = [i for i in parts if i]

                if parts[0] == "Profiling":
                    self._parse_thread_count(parts)
                    continue

                if len(parts) != self.RECORD_LEN:
                    continue

                try:
                    _ = int(parts[0])
                    self._parse_timing_line(parts)
                except ValueError:
                    print(f"Failed to pass parts: {parts}")
                    continue

    def _parse_thread_count(self, line_parts: list[str]) -> None:
        self.threads = int(line_parts[2])

    def _parse_timing_line(self, line_parts: list[str]) -> None:

        routine_name = line_parts[-1]
        if routine_name in self.timings:
            raise DoubleRecordError(routine_name)

        self.timings[routine_name] = {
            "time": float(line_parts[1]),
            "cumul": float(line_parts[2]),
            "self": float(line_parts[3]),
            "total": float(line_parts[4]),
            "num_calls": int(line_parts[5]),
            "self_per_call": float(line_parts[6]),
            "total_per_call": float(line_parts[7]),
        }
