import system_configuration as conf

# Get the parameters either from main parameters.py, or from a previous simulation 
if(conf.RUN_SIMULATION == True):
    import parameters as env
else:
    import importlib
    env = importlib.import_module('parameters', conf.RUN_SIMULATION)

import simulate as s
import graphs as g
from os import mkdir
from datetime import datetime
from multiprocessing import cpu_count, Pool

    
# MULTI-PROCESSING EXAMPLE
if __name__ == "__main__":  # If main function
    allSimulations = s.getAllSimulationPossibilities()
    # Process new simulation if requested,
    if(conf.RUN_SIMULATION == True):
        cpuCount = cpu_count()
        print("Number of cpu : ", cpuCount)
        pool = Pool(processes=int(cpuCount*(conf.PERCENTAGE_OF_CPU_CORES/100)))

        # -- PREPARE DIRECTORY FOR OUTPUT
        directoryName = datetime.now().strftime("%Y%m%d-%H%M%S")
        mkdir(directoryName)
        filePath = directoryName+'/output.csv'

        # Prepare and print total number of simulations
        simulationNumber = 0
        simulationTypeNumber = 0  # Allows for averaging of seeds
        print("Simulation "+str(simulationNumber)+" of "+str(s.TOTAL_SIMULATIONS))

        for cacheAlgorithm, xPatternFeature, nPattern, learningRate, maxSizeOfTransientMemory, maintenanceCostOfTransientMemory in allSimulations:
            simulationTypeNumber += 1
            for seed in env.SEEDS:
                simulationNumber += 1
                #TODO: Print status when verbose == true
                result = pool.apply_async(s.simulate, args=(
                    simulationNumber, simulationTypeNumber, s.TOTAL_SIMULATIONS, cacheAlgorithm, xPatternFeature, nPattern, learningRate, maxSizeOfTransientMemory, maintenanceCostOfTransientMemory, seed, filePath, directoryName))
        pool.close()
        pool.join()
        print("A csv file has been produced and is available at: (location of this script)/"+str(filePath))
        print("Now producing graphs...")

    else:
        directoryName = conf.RUN_SIMULATION
    

    # If only the N_PATTERNS and X_PATTERN_FEATURES are varied... 
    if(( (env.ENSURE_N_PATTERNS_EQUALS_X_PATTERNS_FEATURES != True) & \
         (s.TOTAL_SIMULATIONS == (len(env.N_PATTERNS) * len(env.X_PATTERN_FEATURES) * len(env.SEEDS))) \
         ) or \
        ((env.ENSURE_N_PATTERNS_EQUALS_X_PATTERNS_FEATURES == True) & (s.TOTAL_SIMULATIONS == (len(s.COMMON_N_PATTERNS_X_PATTERN_FEATURES) * len(env.SEEDS))))):
        fig1c = g.makeFigure1c(directoryName)
        fig1d = g.makeFigure1d(directoryName)
    else:
        print("Skipped producing Figure 1c and 1d. To produce this figure, fix all parameters but N_PATTERNS and X_PATTERN_FEATURES")

    if(s.TOTAL_SIMULATIONS == (len(env.MAX_SIZES_OF_TRANSIENT_MEMORY))):
        fig2b = g.makeFigure2b(directoryName)
    else:
        print("Skipped producing Figure 2b. To produce this figure, fix all parameters but MAX_SIZES_OF_TRANSIENT_MEMORY. You may have to check the neurone and memory types are set correctly too. ")

    if(s.TOTAL_SIMULATIONS == (len(env.MAINTENANCE_COSTS_OF_TRANSIENT_MEMORY))):
        fig4b = g.makeFigure4b(directoryName)
    else:
        print("Skipped producing Figure 4b. To produce this figure, fix all parameters but MAINTENANCE_COSTS_OF_TRANSIENT_MEMORY. You may have to check the neurone and memory types are set correctly too.")

    g.showFigures()
