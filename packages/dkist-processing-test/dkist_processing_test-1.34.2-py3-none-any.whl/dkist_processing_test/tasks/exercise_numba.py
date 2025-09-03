"""
Basic exercising of numba
"""

import timeit

import numpy as np
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger
from numba import njit

__all__ = ["ExerciseNumba"]


class ExerciseNumba(WorkflowTaskBase):
    def run(self):
        bubblesort_numba = njit(self.bubblesort)
        original = np.linspace(0.0, 10.0, 1001)
        shuffled_1 = original.copy()
        np.random.shuffle(shuffled_1)
        shuffled_2 = shuffled_1.copy()
        foo_1 = timeit.Timer(lambda: self.bubblesort(shuffled_1), globals=globals())
        time_1 = foo_1.timeit(100)
        foo_2 = timeit.Timer(lambda: bubblesort_numba(shuffled_2), globals=globals())
        time_2 = foo_2.timeit(100)
        speedup = time_1 / time_2
        logger.info(f"Normal task execution time: {time_1} secs")
        logger.info(f"Numba task execution time: {time_2} secs")
        logger.info(f"ExerciseNumba: Achieved a speedup of {speedup} using numba.")
        self.speedup = speedup
        self.sorted_array = shuffled_2

    @staticmethod
    def bubblesort(x):
        """Simple bubblesort algorithm copied from numba documentation"""
        n = len(x)
        for end in range(n, 1, -1):
            for i in range(end - 1):
                cur = x[i]
                if cur > x[i + 1]:
                    tmp = x[i]
                    x[i] = x[i + 1]
                    x[i + 1] = tmp
