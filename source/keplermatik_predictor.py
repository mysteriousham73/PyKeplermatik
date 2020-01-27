import multiprocessing as mp
from time import gmtime, time, sleep

#todo: thread this for progress bar
class Predictor():
    def __init__(self, satellites):
        self.satellites = satellites
        self.queue_complete = 0
        self.initial_queue_depth = 0

    def predict(self):
        in_queue = mp.Queue()
        out_queue = mp.Queue()

        workers = [PredictorWorker(str(worker_name), in_queue, out_queue) for worker_name in range(4)]
        timing = {}

        for worker in workers:
            worker.daemon = True
            worker.start()


        start_time = time()

        for norad_cat_id, satellite in self.satellites.items():
            in_queue.put(satellite)
            self.initial_queue_depth += 1

        timing['queue_load'] = round(time() - start_time, 3)
        start_time = time()
        #in_queue.join()


        while out_queue.qsize() != self.initial_queue_depth:
            self.queue_complete = out_queue.qsize()
            sleep(0.05)

        timing['prediction'] = round(time() - start_time, 3)
        start_time = time()
        while not out_queue.empty():
            satellite = out_queue.get()
            self.satellites[satellite.norad_cat_id] = satellite

        timing['queue_unload'] = round(time() - start_time, 3)

        return timing

    @property
    def progress(self):
        return round(self.queue_complete / self.initial_queue_depth * 100, 0)


class PredictorWorker(mp.Process):

    def __init__(self, name, in_queue, out_queue):
        super(PredictorWorker, self).__init__()
        self.name = name
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            satellite = self.in_queue.get()

            try:
                satellite.predict_gmtime(gmtime())
                self.out_queue.put(satellite)
            finally:
                pass
                #self.in_queue.task_done()