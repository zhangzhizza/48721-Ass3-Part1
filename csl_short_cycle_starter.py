"""
CMU 48721 Fall 2019
Assignment 3 part 1: "The right time"
Note:
	1: DO NOT use "print" function, it will block the code, 
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
		37: DX heating coil electric demand (W)
		38: HVAC total electric demand (W)
"""
import gym, eplus_env, logging

logger = logging.getLogger('Ctrl-Tester');
logger.setLevel(logging.DEBUG);
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG);
logger.addHandler(ch);
logger.info('Running the simulation test...')
logger.info('Environment warm-up may take time.')
env = gym.make('CSL-short-cycle-v1');
ob, is_terminal = env.reset();
logger.info('Environment warm-up is done.')
cycle_count = 9999;

while is_terminal == False:
# !!DO NOT change the above lines!!
# The following lines are the baseline control strategy
# You should implement your control strategy here
	all_pmvs = ob[27:37] # Get all PMVs
	eff_pmvs = []; # Remove -999 from the PMVs
	for pmv in all_pmvs:
		if pmv != -999:
			eff_pmvs.append(pmv);
	min_pmv = min(eff_pmvs) if len(eff_pmvs) > 0 else 0; # The min occupied PMV
	all_iats = ob[7:17];
	min_iat = min(all_iats); # The min IAT
	dx_status = 1 if ob[37] > 0 else 0; # DX heating on/off state
	act = dx_status;
	if cycle_count >= 3:
		# Turn on heating if the conditions allow
		if min_pmv < -0.5 or min_iat < 18:
			act = 1;
		else:
			act = 0;
	if act == dx_status:
		# Remember cycle number
		cycle_count += 1;
	else:
		cycle_count = 1;
	logger.info('This observation is: %s'%ob);
	ob, is_terminal = env.step([act])
# !!DO NOT change the following lines!!
env.end_env();