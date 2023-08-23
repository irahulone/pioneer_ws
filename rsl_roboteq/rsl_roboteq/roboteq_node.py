import re
import sys
sys.path.append('src/rsl_roboteq/rsl_roboteq/PyRoboteq')

from PyRoboteq import RoboteqHandler
from PyRoboteq import roboteq_commands as cmds

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32
from std_msgs.msg import Int32MultiArray

controller = RoboteqHandler(debug_mode=False)
connected = controller.connect("/dev/ttyUSB0")
class motor_driver(Node):

    def __init__(self):
        super().__init__('roboteq_node')

        # Subscribers
        self.inCmd = 0.0
        self.subscription = self.create_subscription(
            Int32MultiArray,
            'ch_vals',
            self.cmd_callback_ch,
            5)
        self.subscription  # prevent unused variable warning

        # Publishers
        self.volt_pub = self.create_publisher(Float32, 'bus_voltage', 10)
        self.encoder_pub = self.create_publisher(Int32MultiArray, 'encoder_counts', 10)
        
        # Publisher timer.
        encoder_timer = 0.1  # seconds
        bus_volt_timer = 0.1
        self.volt_timer = self.create_timer(bus_volt_timer, self.roboteq_voltage_callback)
        self.encoder_timer = self.create_timer(encoder_timer, self.roboteq_encoder_callback)
        self.i = 0

    # Writes the subscriber values to the roboteq drivers.
    def cmd_callback_ch(self, msg):
        ch_val_1 = msg.data[0]
        ch_val_2 = msg.data[1]
        controller.dual_motor_control(ch_val_1, ch_val_2)
        
    
    # Retrieves telemetry on the encoder values from the driver channels.
    def roboteq_encoder_callback(self):
        msg = Int32MultiArray()

        # Reads the encoder values from the roboteq drivers.
        encoder_val = controller.read_value(cmds.READ_ABSCNTR)
        
        # Parses the text to obtain an array of encoder values for 2 channels.
        regex = "\d+"
        encoder_val = re.findall(regex, encoder_val)
        
        # Converts the values to integers.
        msg.data = [int(val) for val in encoder_val]

        self.encoder_pub.publish(msg)
        

    # Retrieves telemetry on the bus voltage for the roboteq drivers.
    def roboteq_voltage_callback(self):
        msg = Float32()

        # Reads the voltage values from the roboteq drivers.
        volt = controller.read_value(cmds.READ_VOLTS)

        # Parses the text to only obtain the bus voltage.
        regex ="\:([0-9]+)\:"
        volt = re.findall(regex, volt)

        # Converts the bus voltage to a float.
        if not(len(volt) == 0):  
            msg.data = float(volt[0])/10

        self.volt_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = motor_driver()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
