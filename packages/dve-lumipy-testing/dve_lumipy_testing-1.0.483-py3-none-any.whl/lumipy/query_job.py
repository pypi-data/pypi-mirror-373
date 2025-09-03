from typing import NoReturn, Optional, Callable
from lumipy.helpers.backoff_handler import BackoffHandler
import pandas as pd
from lumipy.common import indent_str
import typing
if typing.TYPE_CHECKING:
    from lumipy.client import Client


class QueryJob:
    """Class representing a query that has been submitted to Luminesce.

    """

    def __init__(self, ex_id: str, client: 'Client', _print_fn: Optional[Callable] = None):
        """__init__ method of the Job class

        Args:
            ex_id (str): the execution ID of the query.
            client (Client): a lumipy client instance that can be used to manage the query.
            _print_fn (Optional[callable]): alternative print function for showing progress. This is mainly for internal use with
            the streamlit utility functions that show query progress in a cell. Defaults to the normal python print() fn.

        """
        self.ex_id = ex_id
        self._client = client
        self._progress_lines = []
        self._row_count = -1
        self._status = None
        self._state = None
        self._print_fn = print if _print_fn is None else _print_fn
        self.get_status()
        self.backoff_handler = BackoffHandler()

    def _print(self, quiet, string):
        if not quiet:
            self._print_fn(string)

    def delete(self) -> NoReturn:
        """Delete the query. Query can be running or finished. If running the query will be cancelled
        if it's running the query result will be deleted if it still exists.

        """
        self._print(False, f"Deleting query ({self.ex_id})")
        self._client.delete_query(self.ex_id)
        self._print(False, f"  💥")

    def get_status(self) -> str:
        """Get the status of the query in Luminesce

        Returns:
            str: string containing the query status value.
        """
        status = self._client.get_status(self.ex_id)
        lines = status['progress'].split('\n')
        new_lines = [line for line in lines if line not in self._progress_lines]
        self._progress_lines += new_lines
        self._row_count = int(status['row_count'])
        self._status = status['status']
        self._state = status['state']

        return self._status

    def interactive_monitor(self, quiet=False,  stop_trigger: Callable = None) -> NoReturn:
        """Start interactive monitoring mode. Interactive monitoring mode will give a live printout of the
        query status and allow you to cancel the query using a keyboard interupt.

        """
        self._print(quiet, "Query launched! 🚀")
        self._print(quiet, '[Use ctrl+c or the stop button in jupyter to cancel]\n\n')

        try:
            self.monitor(quiet, stop_trigger)
        except KeyboardInterrupt as ki:
            self.delete()
            raise ki
        except Exception as e:
            raise e

    def get_progress(self) -> str:
        """Get progress log of the query.

        Returns:
            str: the progress log string.
        """
        if len(self._progress_lines) == 0:
            self.get_status()
        return '\n'.join(self._progress_lines)

    def get_result(
            self,
            quiet: Optional[bool] = False,
            **read_csv_params
    ) -> pd.DataFrame:
        """Get the result of a successful query back as a Pandas DataFrame.

        Args:
            quiet (Optional[bool]): whether to not print out information while getting the data.
            **read_csv_params (Any): keyword arguments to pass down to pandas read_csv. See https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Returns:
            DataFrame: pandas dataframe containing the query result.
        """
        return self._client.get_result(self.ex_id, verbose=not quiet, **read_csv_params)

    def wait(self):
        """Wait until completion

        """
        self.monitor(quiet=True)

    def is_running(self) -> bool:
        """Check whether the query is running or has ended.

        Returns:
            bool: true if the query is running false if not.
        """
        status = self.get_status()
        return status == 'WaitingForActivation'

    def monitor(self, quiet=False, stop_trigger: Callable = None) -> NoReturn:
        """Start a monitoring session that prints out the live progress of the query. Refreshes with a period of one
        second. A keyboard interrupt during this method will not delete the query.

        """
        self._print(quiet, f"Progress of Execution ID: {self.ex_id}")

        start_i = 0
        while self.is_running():

            if stop_trigger is not None and stop_trigger():
                self.delete()
                return

            if start_i != len(self._progress_lines):
                new_progress_lines = '\n'.join(self._progress_lines[start_i:])
                self._print(quiet, indent_str(new_progress_lines))

            start_i = len(self._progress_lines)
            self.backoff_handler.sleep()

        self._print(quiet, indent_str('\n'.join(self._progress_lines[start_i:])))

        if self._status == 'RanToCompletion':
            self._print(quiet, f"\nQuery finished successfully! 🛰🪐")
        else:
            info_str = f"Status: {self._status}\nExecution ID: {self.ex_id}"
            self._print(quiet, f"\nQuery was unsuccessful... 💥\n{indent_str(info_str, n=4)}")
