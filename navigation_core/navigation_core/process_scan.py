import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan

#Int32 is a predefined blueprint for a 32-bit integer value that can be used to communicate between nodes.
from std_msgs.msg import Int32  # Import the Int32 message type


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('rplidar_node')
        self.subscription = self.create_subscription(
            LaserScan,
            'scan',
            self.lidar_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.range_sum_f = 0
        self.range_sum_b = 0

        # Create a publisher for Int32 messages
        self.publisher_f = self.create_publisher(Int32, 'forward_obstacle', 10)  
        self.publisher_b = self.create_publisher(Int32, 'backward_obstacle', 10)  

    def lidar_callback(self, msg):
        self.scan_array = msg.ranges
        self.obstacle_forward()
        self.obstacle_backward()


    def obstacle_forward(self):
        scan = self.scan_array
        for index, value in enumerate(scan):
            if 0 <= index <= 225 or 1575 <= index <= 1800:

                if (0.1 <= value <= 0.5): #if obstacle within range
                    self.range_sum_f = self.range_sum_f - 1
                elif (0.5 < value <= 10.0): #if obstacle not in range
                    self.range_sum_f = self.range_sum_f + 1

                #based on 100 totaled values (to ignore outliers), 
                #publish an intruction to change or keep velocities
                if self.range_sum_f > 100:
                    self.range_sum_f = 1 
                elif self.range_sum_f < -100:
                    self.range_sum_f = -1 
            #print(" ", self.sum2)


        # Create an Int32 message
        msg = Int32()
        msg.data = self.range_sum_f

        # Publish the message
        self.publisher_f.publish(msg)



    def obstacle_backward(self):
        scan = self.scan_array
        for index, value in enumerate(scan):
            if 675 <= index <= 1125:

                if (0.1 <= value <= 0.5): #if obstacle within range
                    self.range_sum_b = self.range_sum_b - 1
                elif (0.5 < value <= 10.0): #if obstacle not in range
                    self.range_sum_b = self.range_sum_b + 1

                #based on 100 totaled values (to ignore outliers), 
                #publish an intruction to change or keep velocities
                if self.range_sum_b > 100:
                    self.range_sum_b = 2 
                elif self.range_sum_b < -100:
                    self.range_sum_b = -2
            #print(" ", self.sum2)


        # Create an Int32 message
        msg = Int32()
        msg.data = self.range_sum_b

        # Publish the message
        self.publisher_b.publish(msg)



def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()
    # minimal_subscriber.object()

    rclpy.spin(minimal_subscriber)
    
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()