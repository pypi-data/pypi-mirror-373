import random
import uuid
import datetime
import tzlocal
import psutil
from .generator import Generators as g
import time
from threading import Thread, Event
from queue import Queue
import statistics


class KawaBenchmark:

    def __init__(self,
                 kawa_client,
                 metrics_output_file,
                 view_ids,
                 user_ids,
                 num_users,
                 benchmark_name='Benchmark',
                 num_seconds_between_two_computations=1,
                 test_duration_in_seconds=60):

        """
        Creates a new KAWA benchmark object.
        In order to run it, just call benchmark.run()

        :param kawa_client: An instance of the kawa client,
                            connected to the workspace in which you want to run your tests.
        :param benchmark_name: The name of the benchmark will appear in the output csv file.
        :param metrics_output_file: Path to the benchmark output file. It will be a csv.
        :param view_ids: The pool of view to compute during the benchmark.
        :param user_ids: The pool of users that will be used to compute the views.
        :param num_users: The total number of users that will be simulated in the benchmark
        :param num_seconds_between_two_computations:
        :param test_duration_in_seconds:
        """

        self._k = kawa_client
        self._benchmark_name = benchmark_name
        self._metrics_output_file = metrics_output_file
        self._view_ids = [str(v) for v in view_ids]
        self._user_ids = [str(v) for v in user_ids]
        self._num_users = num_users
        self._num_seconds_between_two_computations = num_seconds_between_two_computations
        self._test_duration_in_seconds = test_duration_in_seconds
        self._cache_hit_ratio = 35

        # Reporting
        self._computation_times_per_user = {}
        for user_id in self._user_ids:
            self._computation_times_per_user[user_id] = []

        self._computation_times_per_view = {}
        for view_id in self._view_ids:
            self._computation_times_per_view[view_id] = []

        # Synchronization
        self._end_of_test_event = Event()
        self._test_timing_queue = Queue()

    def run(self):
        computation_threads = []
        metrics_thread = Thread(target=self._system_metrics_thread)
        try:
            for thread_id in range(0, self._nb_threads()):
                thread = Thread(target=self._computing_thread)
                computation_threads.append(thread)
            [t.start() for t in computation_threads]
            metrics_thread.start()
            [t.join() for t in computation_threads]
        finally:
            self._end_of_test_event.set()
            if metrics_thread.is_alive():
                metrics_thread.join()
            self._print_results()

    def _print_results(self):
        all_compute_times = []

        print('--- STATS PER VIEW')
        for view_id, computation_times in self._computation_times_per_view.items():
            all_compute_times.extend(computation_times)
            self.extract_stats(timings=computation_times, item_to_print='View {}'.format(view_id))

        print('--- STATS PER USER')
        for user_id, computation_times in self._computation_times_per_user.items():
            self.extract_stats(timings=computation_times, item_to_print='User {}'.format(user_id))

        print('--- OVERALL STATS')
        self.extract_stats(timings=all_compute_times, item_to_print='Overall')

    def _nb_threads(self):
        # Each thread will start one computation every second
        # Hence: The number of threads is equal to the number of computations per second
        num_computations_per_second = int(self._num_users / self._num_seconds_between_two_computations)

        if num_computations_per_second < 1:
            raise Exception('The computation frequency is too low, please ensure at least 1 computation/s')

        return num_computations_per_second

    def _random_filter(self):
        random_between_1_and_100 = random.randint(1, 100)
        cache_hit = random_between_1_and_100 < self._cache_hit_ratio
        return 'וָו' if cache_hit else 'וָו' + str(uuid.uuid4())

    def _compute_one_view(self, view_id, user_id):
        lazy_frame = (self._k.sheet(no_output=True)
                      .view_id(view_id=view_id)
                      .as_user_id(as_user_id=user_id)
                      .filter(self._k.col('{--}{=æ=}{--}').does_not_start_with(self._random_filter()))
                      .limit(300))
        start = time.time()
        lazy_frame.compute()
        computation_time = time.time() - start

        self._computation_times_per_user[user_id].append(computation_time)
        self._computation_times_per_view[view_id].append(computation_time)
        self._test_timing_queue.put_nowait(computation_time)

    def _computing_thread(self):
        thread_start = time.time()
        while True:

            random_sleep = random.random()
            time.sleep(random_sleep)

            view_id = g.get_random_element_in(self._view_ids)
            user_id = g.get_random_element_in(self._user_ids)
            self._compute_one_view(view_id, user_id)

            time.sleep(1.0 - random_sleep)

            thread_seconds_elapsed = time.time() - thread_start
            if thread_seconds_elapsed > self._test_duration_in_seconds:
                break

    def _system_metrics_thread(self):
        print('Dumping system metrics in {}'.format(self._metrics_output_file))
        with open(self._metrics_output_file, 'w') as f:
            counter = 0
            header = 'TIME,TEST NAME,CPU %,MEM %,NB READ,NB WRITE,NB BYTES READ,NB BYTES WRITE,NUM TESTS,MIN,MAX,AVG'
            f.write(header + '\n')
            print(header)

            initial_io = psutil.disk_io_counters(perdisk=False)
            prev_io = initial_io

            while not self._end_of_test_event.is_set():

                test_timings = []
                while not self._test_timing_queue.empty():
                    test_timings.append(self._test_timing_queue.get(block=False))

                time.sleep(1)
                counter = counter + 1

                dt = datetime.datetime.now(tz=tzlocal.get_localzone())
                cpu_percent = psutil.cpu_percent(percpu=False)
                virtual_mem = psutil.virtual_memory()
                mem_percent = virtual_mem.percent

                metrics = [dt.strftime('%Y-%m-%d %H:%M:%S'), self._benchmark_name, cpu_percent, mem_percent]

                current_io = psutil.disk_io_counters(perdisk=False)
                delta_read_count = int(current_io.read_count - prev_io.read_count)
                delta_write_count = int(current_io.write_count - prev_io.write_count)
                delta_read_bytes = int(current_io.read_bytes - prev_io.read_bytes)
                delta_write_bytes = int(current_io.write_bytes - prev_io.write_bytes)

                metrics.extend([delta_read_count, delta_write_count, delta_read_bytes, delta_write_bytes])
                metrics.extend(self.extract_stats(test_timings))

                line = ','.join([str(m) for m in metrics])

                print(line)
                f.write(line + '\n')

                prev_io = current_io

    @staticmethod
    def extract_stats(timings, item_to_print=None):
        if not timings:
            s = [0, 0.0, 0.0, 0.0]
        else:
            average = round(statistics.mean(timings), 2)
            minimum = round(min(timings), 2)
            maximum = round(max(timings), 2)
            s = [len(timings), minimum, maximum, average]

        if item_to_print:
            print("[{}] {} computations: MIN={} MAX={} AVG={}".format(item_to_print, s[0], s[1], s[2], s[3]))

        return s
