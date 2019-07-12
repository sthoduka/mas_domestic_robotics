from mas_execution_manager.scenario_state_base import ScenarioStateBase

import std_msgs
import rospy
import time

class StopRecording(ScenarioStateBase):
    def __init__(self, save_sm_state=False, **kwargs):
        ScenarioStateBase.__init__(self, 'stop_recording',
                                   save_sm_state=save_sm_state,
                                   outcomes=['succeeded', 'failed'])
        self.sm_id = kwargs.get('sm_id', '')
        self.state_name = kwargs.get('state_name', 'stop_recording')
        self.timeout = kwargs.get('timeout', 8.)
        self.event_pub = rospy.Publisher('/mcr_tools/rosbag_recorder/event_in', std_msgs.msg.String, 1)
        self.event_sub = rospy.Subscriber('/mcr_tools/rosbag_recorder/event_out', std_msgs.msg.String, self.eventCallback)
        self.msg = None

    def eventCallback(self, msg):
        self.msg = msg

    def execute(self, userdata):
        self.msg = None
        self.event_pub.publish('e_stop')
        start_time = time.time()
        duration = 0.
        while duration < self.timeout:
            rospy.sleep(0.1)
            if self.msg is not None:
                break
            duration = time.time() - start_time
        if self.msg is not None and self.msg.data == 'e_stopped':
            return 'succeeded'
        else
            return 'failed'
