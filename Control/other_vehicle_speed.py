import time

class VehicleTracker:
    def __init__(self):
        self.prev_distances = {"vehicle": None}  # Stores previous distances {label: (distance, timestamp)}

    def estimate_speed(self, label, distance):
        """
        Estimate speed of a detected vehicle using only distance changes.
        :param label: Detected object label
        :param distance: Estimated distance to the vehicle (cm)
        :return: Estimated speed (cm/s)
        """
        current_time = time.time()

        if label == "vehicle":
            prev_distance, prev_time = self.prev_distances[label]

            # Calculate change in distance and time
            distance_diff = prev_distance - distance  # Positive if getting closer
            time_diff = current_time - prev_time if current_time - prev_time > 0 else 1e-6

            # Compute speed
            speed = distance_diff / time_diff  # cm/s

        else:
            speed = 0  # First detection, assume stationary

        # Update previous values
        self.prev_distances[label] = (distance, current_time)

        return speed
