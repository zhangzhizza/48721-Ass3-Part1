# CMU 48721 Fall 2019
# Assignment 3 part 1: "The right time"
import gym, eplus_env

env = gym.make('CSL-short-cycle-v1');
ob, is_terminal = env.reset();
cycle_count = 9999;

while is_terminal == False:
# !!DO NOT change the above lines!!
# The following lines are the baseline control strategy
# You should implement your control strategy here
	all_pmvs = ob[27:37]
	eff_pmvs = [];
	for pmv in all_pmvs:
		if pmv != -999:
			eff_pmvs.append(pmv);
	min_pmv = min(eff_pmvs) if len(eff_pmvs) > 0 else 0;
	all_iats = ob[7:17];
	min_iat = min(all_iats);
	dx_status = 1 if ob[37] > 0 else 0;
	print (min_pmv, min_iat, dx_status, cycle_count)
	act = dx_status;
	if cycle_count >= 3:
		if min_pmv < -0.5 or min_iat < 18:
			act = 1;
		else:
			act = 0;
	if act == dx_status:
		cycle_count += 1;
	else:
		cycle_count = 1;
	print (act)
	ob, is_terminal = env.step([act])
# !!DO NOT change the following lines!!
env.end_env();