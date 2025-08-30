############### PB configuration file ###############
import math
import torch 
import torch.nn as nn
import torchvision.models.resnet as resnet
import sys

pbTracker = []

debuggingMemoryLeak = True
debuggingInputDimensions = 0

verbose = False
silent = False
extraVerbose = False
unwrappedModulesConfirmed = False
#usingPAIDataParallel = False
saveOldGraphScores = True
testingDendriteCapacity = True
weightDecayAccepted = False
countTrainingParams = False


# Prevent flow of error back to network after candidates and dendrites (Doing Perforation)
candidateGraphMode = True #default True
dendriteGraphMode = True #default True
# Do Correlation learning (Doing CC)
dendriteLearnMode = True #default True
# Allow dendrite weights to continue to learn (unfreeze Dendrite weights)
dendriteUpdateMode = False #default False

usingSafeTensors = True
noBackwardWorkaround = False

'''
This take in an array of layers.  for example:

    PBG..PBSequential([nn.Linear(2 * hidden_dim, seqWidth),
            nn.LayerNorm(seqWidth)])
    
    This should be used for:
        -all normalization layers
    This can be used for:
        -final output layer and softmax - showed final layer has a better score, but whole network did worse so might have to try it both ways
    This doesn't seem to be needed for:
        -max pooling layers for score but also might be effecting it somehow

'''


class PBSequential(nn.Sequential):
        def __init__(self, layerArray):
            super(PBSequential, self).__init__()
            self.model = nn.Sequential(*layerArray)
        def forward(self, *args, **kwargs):
            return self.model(*args, **kwargs)

'''
This should but models in a similar form to 

        self.out = nn.Sequential(
            PBM.layerBatch(nn.Linear(2 * hidden_dim, seqWidth),
            nn.LayerNorm(seqWidth)),
            nn.ReLU(inplace=True))
generally the idea is that everything in between the non-linearity functions should be within a single PB block
'''

#this is just a subset of PBSequential, but keeping it just to remember order should be lin then bn
'''
class layerBatch(nn.Sequential):
        def __init__(self, linLayer, bnLayer):
            super(layerBatch, self).__init__()
            self.model = nn.Sequential(
                linLayer,bnLayer)
        def forward(self, x):
            return self.model(x)
'''
'''
class layerBatch(nn.Sequential):
        def __init__(self, linLayer, bnLayer):
            super(layerBatch, self).__init__()
            self.model = nn.Sequential(
                linLayer,bnLayer)
        def forward(self, x):
            return self.model(x)

'''


#why is this a thing?
'''
class moduleWrapper(nn.Module):
        def __init__(self, module):
            super(moduleWrapper, self).__init__()
            self.model = module
        def forward(self, x, extras=None):
            if(extras is None):
                return self.model(x)
            return self.model(x, extras)
'''
use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")

#modules = types
#names = str(types)
#IDs = str of moduleName within network

modulesToConvert = [nn.Conv1d, nn.Conv2d, nn.Conv3d, nn.Linear]
moduleNamesToConvert = ['PBSequential']
# All Modules should either be converted or tracked
modulesToTrack = []
moduleNamesToTrack = []
# IDs are for if you want to pass only a single module by its assigned ID rather than the module type by name
moduleIDsToTrack = []
#relacement modules happen before the conversion, so replaced modules will then also be run through the converstion steps
modulesToReplace = []
replacementModules = []
modulestoSkip = []
modulesWithProcessing = []
moduleProcessingClasses = []
moduleNamesWithProcessing = []
moduleByNameProcessingClasses = []
moduleIDsToSkip = []

moduleNamesToNotSave = ['.base_model']

internalBatchNorm = False
variableP = 142

#Typically the best way to do correlation scoring is to do a sum over each index, but sometimes for large convolutional layers this
#can cause exploding gradients.  To correct this, the mean can be used instead.
correlationsByMean = False

#debugging sizes.  this will slow things down very slightly and is not neccisary but can help catch when dimensions were not filled in correctly.  Might never be needed since we check earlier
confirmCorrectSizes = False

gradSumFirst = True
globalCandidates = 1
#this is for whether or not to batch norm the PB outputs
defaultPBBatch = False
defaultRandomPBtoCandidates = False
defaultPbDropout = 0.0

#drawing
drawingPB = True
#saving test intermediary models
testSaves = True
#setup saving for pai locations and formats
paiSaves = False

#inputDimensions needs to be set every time. It is set to what format of planes you are expecting.  Node index should be set to 0, variable indexes should be set to -1.  For example, if your format is [batchsize, nodes, x, y] inputDimensions is [batchsize,0,-1-1].  if your format is, [batchsize, timestep, nodes] indexesBeforeNode is [batchsize,timestep,0]

inputDimensions = [-1, 0, -1, -1]


#constants
improvementThreshold = 0.0005 #percentage Improvement increase needed to call a new best validation score
improvementThresholdRaw = 1e-5# raw increase needed, if its lower than this its not really learning anyway

#this is if even a single node has gone up by at least 10% over the total number of epochs to switch.
pbImprovementThreshold = 0.1 #improvement increase needed to call a new best PBScore

pbImprovementThresholdRaw = 1e-5# raw increase needed, if its lower than this its not really learning 

candidateWeightInitializationMultiplier = 0.01

doingMeanBest = 0
#if(doingMeanBest):
    #pbImprovementThreshold *= 0.1

formulaType = 0

#   SWITCH MODE SETTINGS
doingSwitchEveryTime = 0
#switch for doingHistory
doingHistory = 1
nEpochsToSwitch = 10  #be sure this is higher than scheduler patience, 
pEpochsToSwitch = 10  
#pPatience = 1
capAtN = False #Makes sure PB rounds last max as long as first N round
#resets score on switch
#this can be useful if you need many epochs to catch up to the baseline accuracy
resetBestScoreOnSwitch = False


#number to average validation scores over
historyLookback = 1
#intitially after switches number of epochs to wait to make sure you have a fair initialization score before tracking any new maxes and and allowing switches to happen
initialHistoryAfterSwitches = 0

doingFixedSwitch = 2
#switch for doingFixedSwitch
fixedSwitchNum = 250
firstFixedSwitchNum = 249

#if you set doing PB to be false but still have a switch mode it will do learning rate restart
#this mode sets it to actually never switch
doingNoSwitch = 3

#default
switchMode = doingHistory


#if doinghistory make sure this value is always shorter, scheduler will update learning rate after this many epochs so need to give average history time to catch up
schedulerPatience = 3
schedulerEps = 1e-15 #if lr gets below this value scheudler wont step
if(schedulerPatience > nEpochsToSwitch or schedulerPatience > pEpochsToSwitch):
    print('patience is set too high')
    sys.exit(0)

doingThing = 0

#if one is true both should be true.
#seems to be better for conv but may or may not be better for linear
learnPBLive = False
noExtraNModes = False

dType = torch.float
retainAllPB = False
saveAllEpochs = False
findBestLR = True
switchOnLRChange = False

# Set to 1 if you want to quit as soon as one dendrite fails
maxDendriteTries = 5
maxDendrites = 100

dontGiveUpUnlessLearningRateLowered = True

#this number is to check how many batches to average out the initial correlation score over
initialCorrelationBatches = 100#this should be at least 100 and up to 10% of a whole epoch


#have learning rate params be by total epoch
paramValsByTotalEpoch = 0
#reset the params at every switch
paramValsByUpdateEpoch = 1
#reset params for PBStarts but not for Normal restarts
paramValsByNormalEpochStart = 2
#initial setting
paramValsSetting = paramValsByUpdateEpoch


doingDropoutForSmall = True
doingDropoutForSmallInput = False
checkedSkippedLayers = False

reluMode = 'relu'
sigmoidMode = 'sigmoid'
tanHMode = 'tanH'
leakyReluMode = 'leakyRelu'
noNonliniarityMode = 'noNonliniarity'
softmaxTopLayerMode = 'softmaxTopLayer'


PBForwardFunction = torch.sigmoid






