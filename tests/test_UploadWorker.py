import unittest
import queue
from cisco_ios_upgrader import UploadWorker, get_logger, HostModel

TEST_LOGGER = get_logger(name="TEST-LOGGER", with_threads=True, verbosity=5)


class TestUploadWorker(unittest.TestCase):

    def test_01(self):

        task_queue = queue.Queue()
        result_queue = queue.Queue()
        for i in range(10):
            task_queue.put(i)

        workers = UploadWorker.worker_factory(
            task_queue=task_queue,
            result_queue=result_queue,
            logger=TEST_LOGGER,
            num_workers=2
        )

        UploadWorker.start_workers(task_queue=task_queue, workers=workers)

        print(result_queue.qsize())


if __name__ == '__main__':
    unittest.main()