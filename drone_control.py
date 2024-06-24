import time
from djitellopy import Tello
import cv2
from network_utils import connect_to_wifi
from firebase_upload import upload_images_to_firebase
from app import TELLO_SSID, WIFI_SSID, WIFI_PASSWORD

class DroneController:
    def __init__(self):
        self.drone = Tello()

    def capture_images(self):
        # Connect to Tello drone's WiFi
        if not connect_to_wifi(TELLO_SSID, ""):
            print("Failed to connect to Tello drone's WiFi.")
            return []

        self.drone.connect()
        self.drone.streamon()
        images = self.flight_routine()
        self.drone.streamoff()
        self.drone.end()

        # Connect to WiFi with internet access
        if connect_to_wifi(WIFI_SSID, WIFI_PASSWORD):
            urls = upload_images_to_firebase(images)
            print(f"Uploaded to Firebase: {urls}")
            return urls
        else:
            print("Failed to connect to WiFi with internet access.")
            return []

    def flight_routine(self):
        images = []
        try:
            self.drone.takeoff()
            self.drone.set_speed(10)

            for action in [("up", 50), ("down", 50)]:
                direction, distance = action
                if direction == "up":
                    self.drone.move_up(distance)
                elif direction == "down":
                    self.drone.move_down(distance)
                
                frame = self.drone.get_frame_read().frame
                images.append(frame)
                time.sleep(1)

            self.drone.land()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.drone.land()

        return images

def perform_flight():
    controller = DroneController()
    return controller.capture_images()
