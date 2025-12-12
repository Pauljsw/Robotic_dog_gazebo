#!/usr/bin/env python3
"""
HyperDog Keyboard Teleop Node
조이스틱 동작을 정확히 모방한 키보드 제어
"""

import sys
import termios
import tty
import time
import select
import rclpy
from rclpy.node import Node
from hyperdog_msgs.msg import JoyCtrlCmds
from geometry_msgs.msg import Pose, Vector3

# hyperdog_definitions.hpp의 상수값들
PITCH_RANGE = 40.0
ROLL_RANGE = 45.0
YAW_RANGE = 50.0
MIN_HEIGHT = 90.0
MAX_HEIGHT = 250.0
SLANT_X_MIN = -150.0
SLANT_X_MAX = 150.0
SLANT_Y_MIN = -100.0
SLANT_Y_MAX = 100.0
MAX_STEP_LENGTH_X = 250.0
MAX_STEP_LENGTH_Y = 150.0

# 키보드용 적절한 이동 속도 (조이스틱 50% 정도)
KEYBOARD_STEP_X = 100.0      # 전진/후진: 250mm의 40%
KEYBOARD_STEP_Y = 60.0       # 좌우 이동: 150mm의 40%
KEYBOARD_YAW = 20.0          # 회전: 50°의 40%

# 토글 지연 (초)
BTN_TOGGLE_DELAY = 0.3

class KeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('hyperdog_teleop_keyboard_node')
        
        # Publisher
        self.publisher = self.create_publisher(
            JoyCtrlCmds, 
            'hyperdog_joy_ctrl_cmd',
            40
        )
        
        # 제어 명령 초기화
        self.cmd = JoyCtrlCmds()
        self.cmd.states = [False, False, False]
        self.cmd.gait_type = 1  # 1=trot (일반 걷기), 0=give_hand (특수 포즈)
        self.cmd.pose = Pose()
        self.cmd.pose.position.x = 0.0
        self.cmd.pose.position.y = 0.0
        self.cmd.pose.position.z = 80.0  # cmd_manager default 높이와 동일 (hyperdog_variables.py:35)
        self.cmd.pose.orientation.x = 0.0
        self.cmd.pose.orientation.y = 0.0
        self.cmd.pose.orientation.z = 0.0
        self.cmd.gait_step = Vector3()
        self.cmd.gait_step.x = 0.0
        self.cmd.gait_step.y = 0.0
        self.cmd.gait_step.z = 30.0  # 초기 스텝 높이 설정 (발을 들어올릴 높이)
        
        # 현재 눌린 키 추적
        self.current_move_key = None
        
        # 토글 타이밍
        self.last_toggle_time = {'start': 0, 'walk': 0, 'side': 0}
        
        # 연속 퍼블리시 (40Hz)
        self.timer = self.create_timer(0.025, self.publish_command)
        
        self.get_logger().info('HyperDog Keyboard Teleop Node Started')
        self.print_instructions()
        
    def print_instructions(self):
        msg = """
        =====================================
        HyperDog 키보드 제어
        =====================================
        Enter    : 로봇 시작/정지
        V        : 걷기 모드 ON/OFF
        
        이동:
        W        : 전진
        S        : 후진
        A        : 좌회전
        D        : 우회전
        Q        : 왼쪽 이동
        E        : 오른쪽 이동
        X        : 정지
        
        높이:
        R        : 몸체 높이 +5
        F        : 몸체 높이 -5
        T        : 발 높이 +5
        G        : 발 높이 -5

        보행 패턴:
        1        : Give Hand (특수 포즈)
        2        : Trot (기본 걷기) ← 추천
        3        : Wave (한 발씩)
        4        : Trot Fast (빠른 걷기)

        ESC      : 종료
        =====================================
        """
        print(msg)
        
    def publish_command(self):
        """주기적으로 명령 퍼블리시 - 조이스틱처럼 동작"""

        # 조이스틱처럼 로봇이 시작된 후에만 높이 조절 (조이스틱 코드 82-183번 라인 참조)
        if self.cmd.states[0]:  # 로봇이 시작된 상태
            # 걷기 모드일 때 최소 높이 보장
            if self.cmd.states[1]:  # 걷기 모드
                if self.cmd.pose.position.z < 100:
                    self.cmd.pose.position.z = 100.0
                if self.cmd.gait_step.z < 10:
                    self.cmd.gait_step.z = 30.0

        # 이동 값 초기화 (조이스틱 중립 상태)
        self.cmd.gait_step.x = 0.0
        self.cmd.gait_step.y = 0.0
        self.cmd.pose.orientation.z = 0.0
        
        # 현재 눌린 키에 따라 값 설정 (조이스틱 50% 정도의 안전한 값 사용)
        if self.current_move_key == 'w':
            self.cmd.gait_step.x = KEYBOARD_STEP_X
        elif self.current_move_key == 's':
            self.cmd.gait_step.x = -KEYBOARD_STEP_X
        elif self.current_move_key == 'a':
            self.cmd.pose.orientation.z = KEYBOARD_YAW
        elif self.current_move_key == 'd':
            self.cmd.pose.orientation.z = -KEYBOARD_YAW
        elif self.current_move_key == 'q':
            self.cmd.gait_step.y = KEYBOARD_STEP_Y
        elif self.current_move_key == 'e':
            self.cmd.gait_step.y = -KEYBOARD_STEP_Y
        
        # 퍼블리시
        self.publisher.publish(self.cmd)
        
    def can_toggle(self, key_name):
        """토글 지연 체크"""
        current_time = time.time()
        if current_time - self.last_toggle_time[key_name] > BTN_TOGGLE_DELAY:
            self.last_toggle_time[key_name] = current_time
            return True
        return False
        
    def process_key(self, key):
        """키 입력 처리"""
        
        # 시작/정지
        if key == '\n':
            if self.can_toggle('start'):
                self.cmd.states[0] = not self.cmd.states[0]
                # 로봇 시작 시 안전한 초기 높이 설정 (singularity 회피)
                if self.cmd.states[0]:
                    self.cmd.pose.position.z = 150.0  # 최소 130mm 필요, 여유있게 150mm
                    self.cmd.gait_step.z = 30.0
                status = "시작" if self.cmd.states[0] else "정지"
                self.get_logger().info(f'로봇 {status}')
                return True
        
        # states[0] == True일 때만 다른 명령 처리
        if self.cmd.states[0]:
            
            # 걷기 모드
            if key == 'v':
                if self.can_toggle('walk'):
                    self.cmd.states[1] = not self.cmd.states[1]
                    status = "ON" if self.cmd.states[1] else "OFF"
                    self.get_logger().info(f'걷기 모드 {status}')
                    
                    if self.cmd.states[1] and self.cmd.pose.position.z < 100:
                        self.cmd.pose.position.z = 100.0
                        self.cmd.gait_step.z = 30.0
                        
            # 이동 명령 - current_move_key 설정
            elif key in ['w', 's', 'a', 'd', 'q', 'e']:
                self.current_move_key = key
                self.get_logger().info(f'이동: {key.upper()}')
                
            # 정지
            elif key == 'x':
                self.current_move_key = None
                self.get_logger().info('정지')
                
            # 높이 조절
            elif key == 'r':
                if self.cmd.pose.position.z < MAX_HEIGHT:
                    self.cmd.pose.position.z += 5.0
                    self.get_logger().info(f'높이: {self.cmd.pose.position.z:.1f}')
            elif key == 'f':
                if self.cmd.pose.position.z > MIN_HEIGHT:
                    self.cmd.pose.position.z -= 5.0
                    self.get_logger().info(f'높이: {self.cmd.pose.position.z:.1f}')
                    
            # 스텝 높이
            elif key == 't':
                max_step_height = self.cmd.pose.position.z - MIN_HEIGHT
                if self.cmd.gait_step.z < max_step_height:
                    self.cmd.gait_step.z += 5.0
                    self.get_logger().info(f'스텝 높이: {self.cmd.gait_step.z:.1f}')
            elif key == 'g':
                if self.cmd.gait_step.z > 10.0:
                    self.cmd.gait_step.z -= 5.0
                    self.get_logger().info(f'스텝 높이: {self.cmd.gait_step.z:.1f}')
                    
            # 보행 패턴
            elif key in ['1', '2', '3', '4']:
                self.cmd.gait_type = int(key) - 1
                self.get_logger().info(f'보행 패턴: {self.cmd.gait_type}')
                
        # 종료
        if key == '\x1b':
            self.get_logger().info('종료 중...')
            return False
            
        return True

def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleopNode()
    
    print("\n=== 조작법 ===")
    print("1. Enter: 로봇 시작")
    print("2. V: 걷기 모드")
    print("3. W/S/A/D: 이동 (한 번만 누르면 계속 이동)")
    print("4. X: 정지")
    print("5. ESC: 종료\n")
    
    # 터미널 설정
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setcbreak(fd)
        
        while rclpy.ok():
            # ROS2 spin
            rclpy.spin_once(node, timeout_sec=0.001)
            
            # 키 입력 체크
            if select.select([sys.stdin], [], [], 0.01)[0]:
                key = sys.stdin.read(1)
                
                if not node.process_key(key):
                    break
                    
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()