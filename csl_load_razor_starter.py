# CMU 48721 Fall 2019
# Assignment 3 part 1: "The right time"
import gym, eplus_env

env = gym.make('CSL-load-razor-v1');
ob, is_terminal = env.reset();

while is_terminal == False:
# !!DO NOT change the above lines!!
# The following lines are the baseline control strategy
# You should implement your control strategy here
	weekday = ob[2];
	hour = ob[0];
	# For all the weekends
	if weekday >= 5: 
	# Do not do anything
		act = 0; 
	# For all the weekdays
	else: 
	# 10:00 AM to 12:00 PM, lower the setpoint
		if hour >= 10 and hour < 12: 
			act = -2; # Lower by 2 C
	# 12:00 PM to 16:00 PM, higher the setpoint
		elif hour >= 12 and hour < 16:
			act = 0; # Higher by 0 C
	# For other time, do nothing
		else: 
			act = 0;
	ob, is_terminal = env.step([act])
# !!DO NOT change the following lines!!
env.end_env();