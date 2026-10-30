#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class HedefeGitNode(Node):
    def __init__(self):
        super().__init__('hedefe_git_node')

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.timer = self.create_timer(0.1, self.hareket_kontrol)

        self.anlik_x = 0.0
        self.anlik_y = 0.0
        self.anlik_yaw = 0.0
        self.odom_alindi = False
                                                
        self.hedef_x = 1.5
        self.hedef_y = 1.0

        self.mesafe_toleransi = 0.05  
        self.hedefe_varildi = False

        self.get_logger().info(
            f"Node baslatildi! Hedef koordinat: X={self.hedef_x}, Y={self.hedef_y}"
        )

    def odom_callback(self, msg: Odometry):
        self.anlik_x = msg.pose.pose.position.x
        self.anlik_y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.anlik_yaw = math.atan2(siny_cosp, cosy_cosp)

        self.odom_alindi = True

    def aci_normalize_et(self, aci):
        while aci > math.pi:
            aci -= 2.0 * math.pi
        while aci < -math.pi:
            aci += 2.0 * math.pi
        return aci

    def hareket_kontrol(self):
        if not self.odom_alindi or self.hedefe_varildi:
            return

        dx = self.hedef_x - self.anlik_x
        dy = self.hedef_y - self.anlik_y
        mesafe = math.sqrt(dx**2 + dy**2)

        hedef_acisi = math.atan2(dy, dx)
        aci_hatasi = self.aci_normalize_et(hedef_acisi - self.anlik_yaw)

        hiz_mesaji = Twist()

        if mesafe > self.mesafe_toleransi:
            hiz_mesaji.linear.x = min(0.3 * mesafe, 0.20)

            hiz_mesaji.angular.z = max(min(1.2 * aci_hatasi, 1.0), -1.0)

            self.publisher_.publish(hiz_mesaji)
            self.get_logger().info(
                f"Konum: ({self.anlik_x:.2f}, {self.anlik_y:.2f}) | "
                f"Kalan Mesafe: {mesafe:.2f} m"
            )
        else:
            hiz_mesaji.linear.x = 0.0
            hiz_mesaji.angular.z = 0.0
            self.publisher_.publish(hiz_mesaji)
            self.hedefe_varildi = True
            self.get_logger().info(
                f"HEDEFE VARILDI! Son Konum: ({self.anlik_x:.2f}, {self.anlik_y:.2f}). "
                f"Hiz sifirlandi (0.0 m/s)."
            )

def main(args=None):
    rclpy.init(args=args)
    node = HedefeGitNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.publisher_.publish(Twist())
            rclpy.shutdown()
        node.destroy_node()

if __name__ == '__main__':
    main()