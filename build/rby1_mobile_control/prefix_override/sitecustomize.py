import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/nvidia/rby1_ros2_ws/rby1-ros2/install/rby1_mobile_control'
