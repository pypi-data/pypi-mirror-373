import datetime
import time
import logging
import threading


logger = logging.getLogger(__name__)


class ZTimer:

    @classmethod
    def str2msecond(cls):
        """年_月_日_时_分_秒_毫秒"""
        return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")

    @classmethod
    def str2second(cls):
        """年_月_日_时_分_秒"""
        return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    @classmethod
    def str2day(cls):
        """年_月_日"""
        return datetime.datetime.now().strftime("%Y_%m_%d")

    @classmethod
    def str_hms(cls):
        """时_分_秒"""
        return datetime.datetime.now().strftime("%H_%M_%S")

    @classmethod
    def str_hmsms(cls):
        """时_分_秒_毫秒"""
        return datetime.datetime.now().strftime("%H_%M_%S_%f")

    @classmethod
    def stamp(cls):
        return datetime.datetime.now().timestamp()

    @classmethod
    def timing(self, f, n=1):
        t0 = time.time()
        for i in range(n):
            f()
        return time.time() - t0

    time_costs = {}

    thread_count_time = None

    count_time_print = 20

    @classmethod
    def start_count_time_cost(cls, delta=5):

        def _print():
            while True:
                sorted_times = sorted(cls.time_costs.items(), key=lambda a: a[1], reverse=True)

                print("----" * 30)
                total = sum([k[1] for k in sorted_times])
                for k, v in sorted_times[:cls.count_time_print]:
                    print(f"{k:<35}percent={str(round(v/(total+0.001)*100,2)):<10}cost {v:.03f}")
                print("----" * 30)
                time.sleep(delta)

        cls.thread_count_time = threading.Thread(target=_print)
        cls.thread_count_time.start()

    @classmethod
    def add_time_cost(cls, key, value):
        cls.time_costs[key] = cls.time_costs.get(key, 0) + value
