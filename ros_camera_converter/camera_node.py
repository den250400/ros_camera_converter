from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import pyvirtualcam
import rclpy

class CameraNode:
    def __init__(self, device: str = "/dev/video2", fps: int = 30):
        self.fps = fps
        self.device = device

        self.node = rclpy.create_node('camera_node')
        self.camera_sub = self.node.create_subscription(
            Image,
            '/camera',
            self.image_callback,
            10
        )

        self.bridge = CvBridge()
        # Placeholder for pyvirtualcam.Camera. 
        # We don't know the image resolution by the time __init__ is called, 
        # so we have to wait for it inside image_callback
        self.virtual_cam = None

    def image_callback(self, msg: Image):
        try:
            image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')

            if self.virtual_cam is None:
                self.virtual_cam = pyvirtualcam.Camera(width=image.shape[1], 
                                                       height=image.shape[0], 
                                                       fps=self.fps, 
                                                       device=self.device)

            self.virtual_cam.send(image)
            self.virtual_cam.sleep_until_next_frame()
        except Exception as e:
            print(f"Error converting image: {e}")

def main(args=None):
    rclpy.init(args=args)
    camera_node = CameraNode()
    
    try:
        rclpy.spin(camera_node.node)
    except KeyboardInterrupt:
        pass
    finally:
        camera_node.node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
