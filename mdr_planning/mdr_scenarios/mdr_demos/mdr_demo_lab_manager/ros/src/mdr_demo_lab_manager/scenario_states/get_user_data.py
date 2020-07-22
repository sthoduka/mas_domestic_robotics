import requests
import pandas as pd
import numpy as np
import time

import rospy
from mas_execution_manager.scenario_state_base import ScenarioStateBase

class GetUserData(ScenarioStateBase):
    def __init__(self, save_sm_state=False, **kwargs):
        ScenarioStateBase.__init__(self, 'get_user_data',
                                   save_sm_state=save_sm_state,
                                   outcomes=['succeeded', 'failed', 
                                             'failed_after_retrying'])
        self.sm_id = kwargs.get('sm_id', '')
        self.state_name = kwargs.get('state_name', 'get_user_data')
        self.number_of_retries = kwargs.get('number_of_retries', 0)
        self.retry_count = 0
        self.timeout = kwargs.get('timeout', 120.)

        self._sheet_id = kwargs.get('sheet_id', '')
        self._worksheet_name = kwargs.get('worksheet_name', 'responses')
        
        self._num_known_entries = None
        self._loop_rate_s = kwargs.get('loop_rate_s', 2.)

        data = self._load_spreadsheet()
        if data:
            self._num_known_entries = data.shape[0]
            rospy.loginfo("[get_user_data] Initialized the user data query with {0} prior known users".format(self._num_known_entries))
        else:
            rospy.logerr("[get_user_data] Could not initialize!")

    def execute(self, userdata):
        if self._num_known_entries is None:
            rospy.logerr("User data was not initialized. Cannot process user input!")
            return "succeeded"

        rospy.loginfo("[get_user_data] waiting for user data")
        start_time = time.time()
        while True and time.time() - start_time < self.timeout:
            data = self._load_spreadsheet()
            num_of_new_entries = data.shape[0] - self._num_known_entries
            if num_of_new_entries > 0:
                self._num_known_entries = data.shape[0]
                new_entry = data[-1, 1:3]
                rospy.loginfo("[get_user_data] Found a new entry!\n\tName: {0}\n\tEmail: {1}".format(new_entry[0], new_entry[1]))
                # TODO Write the user data to knowledge base
                return "succeeded"
            else:
                time.sleep(self._loop_rate_s)
        rospy.logerr("[get_user_data] Query timed out!")

        if self.retry_count == self.number_of_retries:
            self.say("Sorry, I could get our name. I shall proceed without it.")
            self.retry_count = 0
            return "failed_after_retrying"

        self.say("Could you please enter your data? I still have not received it.")
        self.retry_count += 1
        return "failed"

    def _load_spreadsheet(self):
        # Construct the URL
        URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(
                self._sheet_id, self._worksheet_name)

        # Fetch and process the csv data
        data = pd.read_csv(URL, sep=",").to_numpy()
        return data
