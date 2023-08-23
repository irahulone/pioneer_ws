import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Int32  # Import Int32 message

class GetMoveCmds(Node):

    def __init__(self):
        # Initialize the Node with the name 'movebase_kinematics'
        super().__init__('movebase_kinematics')

        # Create a subscription to the 'cmd_vel' topic with a callback function 
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.move_cmd_callback, 1)
        self.subscription  # prevent unused variable warning

        # Create a subscription to the 'cmd_vel' topic with a callback function 
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback, 1)
        self.subscription  # prevent unused variable warning

        # Create a publisher for the left & right wheel's control signal on the their topics
        self.pub_du1 = self.create_publisher(Int32MultiArray, 'ch_vals', 1)
        
        self.sub_obstacle = self.create_subscription(
            Int32,  # Subscribe to Int32 messages
            'forward_obstacle',  # Use the topic created
            self.obstacle_callback,  # Callback function
            5)
        
        self.sub_obstacle = self.create_subscription(
            Int32,  # Subscribe to Int32 messages
            'backward_obstacle',  # Use the topic created
            self.b_obstacle_callback,  # Callback function
            5)

        self.timer_du1 = self.create_timer(0.1, self.du1_callback)

         # Initialize a counters to keep track of the number of callbacks executed
        self.i_du1 = 0

        # Initialize variables to store current command values
        self.lx = 0.0
        self.az = 0.0
        self.u_du1 = 0
        self.u_du2 = 0
        self.flag = 0
        self.flag2 =0
        self.enable = 0

    def move_cmd_callback(self, msg):
        # Update 'lx' and 'az' with the linear and angular commands from the message
        self.lx = msg.linear.x
        self.az = msg.angular.z

        if self.lx < 0: #backward movement
            # Calculate control signals based on 'lx' and 'az' values
            if self.flag2 < 0:
                self.u_du1 = 0
                self.u_du2 = 0
        
            else: #change right and left wheel's velocities to 0
                self.u_du1 = int(-300 * (self.lx - self.az))
                self.u_du2 = int(300 * (self.lx + self.az))
        
        elif self.lx > 0: #forward movement
            # Calculate control signals based on 'lx' and 'az' values
            if self.flag < 0:
                self.u_du1 = 0
                self.u_du2 = 0

            else: #change right and left wheel's velocities to 0
                self.u_du1 = int(-300 * (self.lx - self.az))
                self.u_du2 = int(300 * (self.lx + self.az))

        if self.enable == 0:
            self.u_du1 = 0
            self.u_du2 = 0
    

    #Create callback for obstacle instruction
    def obstacle_callback(self, msg):
        self.flag = msg.data

     #Create callback for obstacle instruction
    def joy_callback(self, msg):
        self.enable = msg.buttons[4]
        
    #Create callback for obstacle instruction
    def b_obstacle_callback(self, msg):
        self.flag2 = msg.data

 # Callback function for the left wheel control signal publisher
    def du1_callback(self):
        msg = Int32MultiArray()
        msg.data = [self.u_du1, self.u_du2]
        print(msg.data)

        # Publish the message on the 'ch_vals' topic
        self.pub_du1.publish(msg)
        self.i_du1 += 1

def main(args=None):
    # Initialize the ROS2 node
    rclpy.init(args=args)

    # Create an instance of the 'GetMoveCmds' class, which starts the subscription and timers
    sub_move_cmds = GetMoveCmds()

    # Enter the ROS2 event loop and wait for callbacks to be triggered
    rclpy.spin(sub_move_cmds)

    # Clean up and destroy the node when the event loop exits
    sub_move_cmds.destroy_node()
    
    # Shutdown the ROS2 client library
    rclpy.shutdown()

if __name__ == '__main__':
    main()

