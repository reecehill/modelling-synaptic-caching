import parameters as env
import learning as l
import energy as e
import graphs as g
import time
from pandas import DataFrame
from os import path, mkdir
from datetime import datetime
from multiprocessing import cpu_count, Pool


def simulate(simulationNumber, simulationTypeNumber, totalSimulations, xPatternFeature, nPattern, learningRate, maxSizeOfTransientMemory, seed, filePath, directoryName):
    env.setXPatternFeature(xPatternFeature)
    env.setNPattern(nPattern)
    env.setLearningRate(learningRate)
    env.setMaxSizeOfTransientMemory(maxSizeOfTransientMemory)
    env.setSeed(seed)
    start = time.time()
    # Generate datasets
    trainingDatasetX, trainingDatasetY, testingDatasetX, testingDatasetY = l.getDatasets()

    # Use training dataset to estimate weights, where each row of weights is a new epoch.
    epochIndexForConvergence, weightsByEpoch, consolidationsByEpoch = l.trainWeights(
        trainingDatasetX, trainingDatasetY)

    # Get performance metrics for seen data
    trainNLL, trainAccuracy, trainPrecision, trainSensitivity, trainSpecificity = l.testWeights(
        trainingDatasetX, trainingDatasetY, weightsByEpoch)
    # Get performance metrics for UNSEEN data
    testNLL, testAccuracy, testPrecision, testSensitivity, testSpecificity = l.testWeights(
        testingDatasetX, testingDatasetY, weightsByEpoch)

    # Calculate energy expenditure
    theoreticalEfficiency = e.calculateTheoreticalEfficiency()
    metabolicEnergy = e.calculateMetabolicEnergy(weightsByEpoch)
    theoreticalMinimumEnergy = e.calculateTheoreticalMinimumEnergy(
        weightsByEpoch)
    efficiency = e.calculateEfficiency(
        metabolicEnergy, theoreticalMinimumEnergy)
    maintenanceEnergy = e.calculateEnergyFromMaintenance(
        weightsByEpoch)
    consolidationEnergy = e.calculateEnergyFromConsolidations(
        consolidationsByEpoch)

    report = {
        simulationNumber:
        {
            'time_elapsed': str(time.time() - start),
            'simulationTypeNumber': simulationTypeNumber,
            'seed': seed,
            'learning_rate': learningRate,
            'n_pattern': nPattern,
            'n_pattern_features': xPatternFeature,  # TODO: notice it is x not n
            'max_epochs': env.MAX_EPOCHS,
            'energy_exponent': env.ENERGY_EXPONENT,
            'preset_simulation': env.PRESET_SIMULATION,
            'Learning was complete at epoch #': epochIndexForConvergence,
            'Theoretical: random-walk efficiency': str(theoreticalEfficiency),
            'Simulated: efficiency (m_perc/m_min)': str(efficiency),
            'Simulated-Theoretical efficiency difference': str(round((efficiency - theoreticalEfficiency), 3)),
            'Theoretical: minimum energy for learning': str(theoreticalMinimumEnergy),
            'Simulated: energy actually used by learning': str(metabolicEnergy),
            'Simulated-Theoretical min difference for learning': str(round((metabolicEnergy - theoreticalMinimumEnergy), 3)),
            'Energy expended by simulations for consolidations': str(consolidationEnergy),
            'Energy expended by simulations for maintenance': str(maintenanceEnergy),
            'Energy expended total': str(round((consolidationEnergy + maintenanceEnergy), 3)),
            '(seen) NLL': str(trainNLL)+'%',
            '(seen) Accuracy': str(trainAccuracy)+'%',
            '(seen) Precision': str(trainPrecision)+'%',
            '(seen) Sensitivity': str(trainSensitivity)+'%',
            '(seen) Specificity': str(trainSpecificity)+'%',
            '(unseen) NLL': str(testNLL)+'%',
            '(unseen) Accuracy': str(testAccuracy)+'%',
            '(unseen) Precision': str(testPrecision)+'%',
            '(unseen) Sensitivity': str(testSensitivity)+'%',
            '(unseen) Specificity': str(testSpecificity)+'%',
            'weights_initialised_as': str(env.WEIGHTS_INITIALISED_AS),
            'max_size_of_transient_memory': str(maxSizeOfTransientMemory),
        }
    }

    if path.isfile(filePath):
        mode = 'a'
        header = 0
        columns = list(report[simulationNumber].keys())
    else:
        mode = 'w'
        header = list(report[simulationNumber].keys())
        columns = header

    DataFrame.from_dict(report).transpose().to_csv(
        filePath, header=header, columns=columns, mode=mode)
    print("Simulation "+str(simulationNumber) +
          " of "+str(totalSimulations))
    timeElapsed = time.time() - start
    print("Finished simulation (time elapsed: "+str(timeElapsed))


# MULTI-PROCESSING EXAMPLE
if __name__ == "__main__":  # If main function

    # Process new simulation if requested,
    if(env.RUN_SIMULATION == True):
        cpuCount = cpu_count()
        print("Number of cpu : ", cpuCount)
        pool = Pool(processes=int(cpuCount*(env.PERCENTAGE_OF_CPU_CORES/100)))

        # -- PREPARE DIRECTORY FOR OUTPUT
        directoryName = datetime.now().strftime("%Y%m%d-%H%M%S")
        mkdir(directoryName)
        filePath = directoryName+'/output.csv'

        # Calculate number of possibilities so that total number of simulations can be printed.
        nXPatternFeaturesAboveNPatterns = 0
        for xPatternFeature in env.X_PATTERN_FEATURES:
            n = [x for x in env.N_PATTERNS if (
                (x != xPatternFeature) & env.ENSURE_N_PATTERNS_EQUALS_X_PATTERNS_FEATURES) or env.ENSURE_N_PATTERNS_EQUALS_X_PATTERNS_FEATURES == False]
            nXPatternFeaturesAboveNPatterns += len(n)

        # Prepare and print total number of simulations
        simulationNumber = 0
        totalSimulations = nXPatternFeaturesAboveNPatterns * \
            len(env.LEARNING_RATES) * \
            len(env.MAX_SIZES_OF_TRANSIENT_MEMORY) * len(env.SEEDS)
        print("Simulation "+str(simulationNumber)+" of "+str(totalSimulations))

        # Loop through all possible global settings.
        simulationTypeNumber = 0  # Allows for averaging of seeds

        for xPatternFeature in env.X_PATTERN_FEATURES:
            if(env.VERBOSE):
                print("xPattern = "+str(xPatternFeature))
            for nPattern in env.N_PATTERNS:
                if(
                    ((nPattern != xPatternFeature) & env.ENSURE_N_PATTERNS_EQUALS_X_PATTERNS_FEATURES) or
                    (nPattern == 0)
                ):  # Avoid dividing by zero error by ensuring <
                    continue
                if(env.VERBOSE):
                    print("nPattern = "+str(nPattern))
                for learningRate in env.LEARNING_RATES:
                    if(env.VERBOSE):
                        print("learningRate = "+str(learningRate))
                    for maxSizeOfTransientMemory in env.MAX_SIZES_OF_TRANSIENT_MEMORY:
                        if(env.VERBOSE):
                            print("maxSizeOfTransientMemory = " +
                                  str(maxSizeOfTransientMemory))
                        simulationTypeNumber += 1
                        for seed in env.SEEDS:
                            simulationNumber = simulationNumber + 1
                            if(env.VERBOSE):
                                print("seed = "+str(seed))
                            result = pool.apply_async(simulate, args=(
                                simulationNumber, simulationTypeNumber, totalSimulations, xPatternFeature, nPattern, learningRate, maxSizeOfTransientMemory, seed, filePath, directoryName))

        pool.close()
        pool.join()
        print("A csv file has been produced and is available at: (location of this script)/"+str(filePath))
        print("Now producing graphs...")
    # Use data from old simulation.
    else:
        directoryName = env.RUN_SIMULATION

    #fig1c = g.makeFigure1c(directoryName)
    #fig1d = g.makeFigure1d(directoryName)
    fig2b = g.makeFigure2b(directoryName)
    g.showFigures()
