import numpy as np
from sim_setup import get_sim

# make simulation object :
sim = get_sim()

# generate simulation parameters :
x = np.array([], dtype=np.float32)

# run simulation :
sim(x)

# get results :
results = sim.get_results(0)
