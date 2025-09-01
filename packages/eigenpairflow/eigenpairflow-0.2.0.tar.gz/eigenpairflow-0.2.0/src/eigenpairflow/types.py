from collections import namedtuple
import joblib
import numpy as np

_EigenTrackingResults = namedtuple(
    "_EigenTrackingResults",
    [
        "t_eval",
        "Qs",
        "Lambdas",
        "norm_errors",
        "success",
        "message",
    ],
)


class EigenTrackingResults(_EigenTrackingResults):
    """
    Results of eigenpair tracking.

    This class extends the namedtuple _EigenTrackingResults to provide
    additional methods for a better user experience, such as a custom
    string representation and serialization methods.
    """

    def __str__(self):
        """
        Provides a concise summary of the tracking results.
        """
        if not self.success:
            return f"EigenTracking failed: {self.message}"

        summary = []
        summary.append(f"success: {self.success}")
        summary.append(f"message: {self.message}")

        # Add shape information for numpy arrays
        for field in self._fields:
            value = getattr(self, field)
            if isinstance(value, np.ndarray):
                summary.append(f"  {field}: np.ndarray with shape {value.shape}")
            elif isinstance(value, list) and value and isinstance(value[0], np.ndarray):
                summary.append(
                    f"  {field}: list of {len(value)} np.ndarray(s), first shape: {value[0].shape}"
                )

        return "EigenTrackingResults Summary:\n" + "\n".join(summary)

    def save(self, filepath):
        """
        Saves the EigenTrackingResults object to a file using joblib.

        Args:
            filepath (str): The path to the file where the object will be saved.
        """
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath):
        """
        Loads an EigenTrackingResults object from a file.

        Args:
            filepath (str): The path to the file from which to load the object.

        Returns:
            EigenTrackingResults: The loaded object.
        """
        return joblib.load(filepath)
