import logging
import time

from attr import dataclass

logger = logging.getLogger(__name__)


class FPSTracker:
    def __init__(self, id: str):
        self.id = id
        self.last_update_time = time.perf_counter() - 0.04
        self.total_frames = 0
        self.total_frames_time = 0
        self.partial_fps_history = []
        self.fps_history = []
        self.partial_frames = 0
        self.last_partial_time = time.perf_counter() - 0.04
        self.total_partial_time = 0 
        self.start()

    def start(self):
        # This method should be called when the first frame is generated
        # We are assuming first frame takes exactly 40ms for a proper average. Ditto actually takes around 1s to generate the first frame               
        self.is_running = True
        self.last_update_time = time.perf_counter() - 0.04
        self.last_partial_time = time.perf_counter() - 0.04

    def stop(self):
        self.partial_fps_history = []
        self.fps_history = []
        self.is_running = False
        self.partial_frames = 0
        self.total_partial_time = 0
        self.total_frames = 0
        self.total_frames_time = 0
        self.last_update_time = 0

    def update(self, num_frames: int):
        self.total_frames += num_frames
        self.total_frames_time += time.perf_counter() - self.last_update_time
        self.last_update_time = time.perf_counter()

        self.partial_frames += num_frames
        self.total_partial_time += time.perf_counter() - self.last_partial_time
        self.last_partial_time = time.perf_counter()

    @property
    def average_fps(self) -> float:
        if self.total_frames <= 1:
            return 0

        return (self.total_frames) / (self.total_frames_time)
    
    def register_history(self):
        self.fps_history.append(self.average_fps)
        self.partial_fps_history.append(self.partial_average_fps)     

    def get_partial_fps_history(self):
        return self.partial_fps_history

    def get_fps_history(self):
        return self.fps_history
    
    @property
    def partial_average_fps(self) -> float:
        if self.partial_frames <= 1:
            return 0

        return (self.partial_frames) / (self.total_partial_time)

    def reset_partial_average(self):
        self.partial_frames = 0
        self.total_partial_time = 0
    
    def log(self):
        """Log current statistics."""
        logger.info(
            f"{self.id} : FPS={self.average_fps:.4f} PartialFPS: {self.partial_average_fps:.4f} total_frames:{self.total_frames} partial_frames:{self.partial_frames} "
        )
        self.partial_frames = 0
        self.total_partial_time = 0


@dataclass
class LatencyMeasure:
    id: str
    start_time: float = 0
    end_time: float = 0


class LatencyTracker:
    _instance = None
    _measures: dict[str, list[LatencyMeasure]] = {}

    @classmethod
    def start_latency_measure(cls, measure_id: str):
        logger.info(f"Starting latency measure {measure_id}")

        if measure_id not in cls._measures:
            cls._measures[measure_id] = []

        if len(cls._measures[measure_id]) > 0:
            last_measure = cls._measures[measure_id][-1]
            if last_measure.end_time == 0:
                logger.warning(
                    f"Latency measure {measure_id} is already running, discarging older one"
                )
                cls._measures[measure_id].pop()

        cls._measures[measure_id].append(
            LatencyMeasure(measure_id, time.perf_counter())
        )

    @classmethod
    def stop_latency_measure(cls, measure_id: str):
        if measure_id in cls._measures:
            last_measure = cls._measures[measure_id][-1]
            if last_measure.end_time == 0:
                last_measure.end_time = time.perf_counter()
                logger.info(
                    f"Stopping latency measure {measure_id}: {last_measure.end_time - last_measure.start_time:.4f}s"
                )

    @classmethod
    def average(cls, measure_id: str):
        if measure_id in cls._measures:
            if len(cls._measures[measure_id]) == 0:
                return 0
            return sum(
                (m.end_time - m.start_time) for m in cls._measures[measure_id]
            ) / len(cls._measures[measure_id])
        return 0

    @classmethod
    def max(cls, measure_id: str):
        if measure_id in cls._measures:
            if len(cls._measures[measure_id]) == 0:
                return 0
            return max((m.end_time - m.start_time) for m in cls._measures[measure_id])
        return 0

    @classmethod
    def min(cls, measure_id: str):
        if measure_id in cls._measures:
            if len(cls._measures[measure_id]) == 0:
                return 0
            return min((m.end_time - m.start_time) for m in cls._measures[measure_id])
        return 0

    @classmethod
    def clean_measure(cls, measure_id: str):
        if measure_id in cls._measures:
            cls._measures[measure_id] = [
                m for m in cls._measures[measure_id] if m.end_time != 0
            ]
            if len(cls._measures[measure_id]) == 0:
                cls._measures.pop(measure_id)

    @classmethod
    def log(cls):
        # Create a copy of keys to avoid modification during iteration
        measure_ids = list(cls._measures.keys())
        for measure_id in measure_ids:
            # clean up measures
            cls.clean_measure(measure_id)
            # Check if the key still exists after cleaning
            if measure_id not in cls._measures:
                continue
            if cls._measures[measure_id] is None:
                continue

            logger.info(
                f"Latency {measure_id} NumMeasures: {len(cls._measures[measure_id])} Avg: {cls.average(measure_id):.4f}s Max: {cls.max(measure_id):.4f}s Min: {cls.min(measure_id):.4f}s"
            )
        cls._measures = {}
