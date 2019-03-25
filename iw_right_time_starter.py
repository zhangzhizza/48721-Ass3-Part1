# CMU 48721 Fall 2019
# Assignment 3 part 1: "The right time"
import gym, eplus_env

env = gym.make('IW-right-time-v1');
ob, is_terminal = env.reset();

while is_terminal == False:
# !!DO NOT change the above lines!!
# The following lines are the baseline control strategy
# You should implement your control strategy here
	weekday = ob[2];
	hour = ob[0];
	# For all the weekends
	if weekday >= 5: 
	# Step down the setpoint
		act = 1; 
	# For all the weekdays
	else: 
	# Before 7:00 AM or after 8:00 PM, step down the setpoint
		if hour < 7 or hour >= 20: 
			act = 1;
	# For other time, step up the setpoint
		else: 
			act = 0;
	ob, is_terminal = env.step([act])
# !!DO NOT change the following lines!!
env.end_env();