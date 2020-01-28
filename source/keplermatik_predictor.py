import multiprocessing as mp
from time import gmtime, time, sleep
import psutil

class PredictEngine():
    def __init__(self):
        self.predictor = Predictor()
        self.first_pass_resolution = 60
        self.final_resolution = 0.3




#todo: thread this for progress bar
class Predictor():
    def __init__(self, satellites):
        self.satellites = satellites
        self.queue_complete = 0
        self.initial_queue_depth = 0
        self.in_queue = mp.Queue()
        self.out_queue = mp.Queue()
        self.cpus = psutil.cpu_count(logical=False)
        #self.cpus = 6
        #self.worker_count = self.cpus - 1
        self.worker_count = 4

        print("SPAWNING WORKERS | " + str(self.worker_count) + " PREDICTION WORKERS ON " + str(self.cpus) + " AVAILABLE CORES")

        self.workers = [PredictorWorker(str(worker_name), self.in_queue, self.out_queue) for worker_name in range(self.worker_count)]

        for worker in self.workers:
            worker.daemon = True
            worker.start()

    def predict(self):

        timing = {}
        start_time = time()

        for norad_cat_id, satellite in self.satellites.items():
            self.in_queue.put(satellite)
            self.initial_queue_depth += 1

        timing['queue_load'] = round(time() - start_time, 3)
        start_time = time()
        #in_queue.join()

        while self.out_queue.qsize() != self.initial_queue_depth:
            self.queue_complete = self.out_queue.qsize()
            #print(psutil.cpu_percent())
            print(self.progress)
            sleep(1)

        timing['prediction'] = round(time() - start_time, 3)
        start_time = time()

        while not self.out_queue.empty():
            satellite = self.out_queue.get()
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