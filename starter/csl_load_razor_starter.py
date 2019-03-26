"""
CMU 48721 Fall 2019
Assignment 3 part 1: "The right time"
Note:
	1: Never use "print" function, it will block the code, 
		use "logger.info()" instead.
	2: ob is a python list with the following items:
		0: hour (0-23)
		1: min (0-59)
		2: weekday (0-7, 0 is Monday)
		3: outdoor air temperature (C)
		4: outdoor air RH (%)
		5: diffuse dolar radiation (W/m2)
		6: direct solar radiation (W/m2)
		7-16: IAT of 10 zones (C)
		17-26: IAT cooling setpoint of 10 zones (C)
		27-36: PMV of 10 zones (-999 if no occupied)
		37: HVAC total electric demand (W)
		38-61: Hourly outdoor air temperature forecast (provided at 0:00, 
			for all other time, the values are -999)
"""
import gym, eplus_env, logging

logger = logging.getLogger('Ctrl-Tester');
logger.setLevel(logging.DEBUG);
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG);
logger.addHandler(ch);
logger.info('Running the simulation test...')
logger.info('Environment warm-up may take time.')
env = gym.make('CSL-load-razor-v1');
ob, is_terminal = env.reset();
logger.info('Environment warm-up is done.')

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
			act = 2; # Higher by 0 C
	# For other time, do nothing
		else: 
			act = 0;
	logger.info('This observation is: %s'%ob);
	ob, is_terminal = env.step([act])
# !!DO NOT change the following lines!!
env.end_env();