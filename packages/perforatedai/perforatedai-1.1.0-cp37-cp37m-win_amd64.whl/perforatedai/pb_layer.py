import torch
import torch.nn as nn
import torch.nn.init as init
import torch.nn.functional as F
import math
import sys
import numpy as np
import pdb
import os 

import time
from itertools import chain

from datetime import datetime
from perforatedai import pb_globals as PBG
from perforatedai import pb_models as PBM
from perforatedai import pb_neuron_layer_tracker as PBT
from perforatedai import pb_utils as PBU
import copy


pretrainedPBLoadValues = ['out_channels', 'pbLayersAdded', 'PBtoTop', 'mainModule', 'name']
pretrainedPBDendriteLoadValues = ['out_channels']

dendriteTensorValues = ['topPBCandidateAverage', 
                        'PrevPBCandidateCorrelation', 
                        'currentCorrelationsForParallel', 
                        'bestScore',
                        'previousBestScore',
                        'PrevPBCandidateAverage',
                        'mainGradAverageForScaling',
                        'candidateGradAverageForScaling',
                        'indexesOfbest',
                        'nodesBestImprovedThisEpoch',
                        'parentsAverageDvector',
                        #'parentsAverageDMags',
                        'normalPassAverageD',
                        #'normalPassAverageDMags',
                        #'normalPassAverageDSq'
                        ]
dendriteSingleValues = ['breaking',
                        'locked',
                        'bestScoreImprovedThisTimeStep',
                        'bestScoreImprovedThisEpoch',
                        #'parentsAverageDSq'
                        ]

#These are included above, they just get skipped for reinit if not live
nonLiveSkipValues = [   'normalPassAverageD',
                        #'normalPassAverageDMags',
                        #'normalPassAverageDSq'
                        ]    



if(PBG.doingThing):
    dendriteSingleValues = dendriteSingleValues + ['normalPassMaxMeanAct', 'parentMaxMeanAct']
    nonLiveSkipValues = nonLiveSkipValues + ['normalPassMaxMeanAct']

dendriteInitValues = ['initialized',
                       'parallelBuffersInitialized',
                      'currentDInit']
#This is intentionally before adding the data parallel values which dont get zeroed at rinit
dendriteReinitValues = dendriteTensorValues + dendriteSingleValues
#if(PBG.usingPAIDataParallel):
    #dendriteTensorValues.append('currentDSum')
    ##dendriteTensorValues.append('currentDMagsSum')
    #dendriteSingleValues.append('currentDSqSum')

dendriteSaveValues = dendriteTensorValues + dendriteSingleValues + dendriteInitValues

valueTrackerArrays = ['currentParentD', 'pbOuts']

    
def fakeCopy(net):
    return PBU.deepCopyPAI(net)

def filterBackward(grad_out, Values, candidateNonlinearOuts):
    
    if(PBG.extraVerbose):
        print('%s calling backward' % Values[0].layerName)

    #This assumes that no matter what is happening you will always get batch_size, neurons, otherdims... as setup
    
    with torch.no_grad():
        val = grad_out.detach()
        if(not Values[0].currentDInit.item()):
            #make sure all dimensions are accounted for
            
            if(len(Values[0].thisInputDimensions) != len(grad_out.shape)):
                print('The following layer has not properly set thisInputDimensions')
                print(Values[0].layerName)
                print('it is expecting:')
                print(Values[0].thisInputDimensions)
                print('but recieved')
                print(grad_out.shape)
                print('to check these all at once set PBG.debuggingInputDimensions = 1')
                print('Call setThisInputDimensions on this layer after initializePB')
                
                if(not PBG.debuggingInputDimensions):
                    sys.exit(0)
                else:
                    PBG.debuggingInputDimensions = 2
                    return


                #return
            #make sure the ones that should be fixed are correct
            for i in range(len(Values[0].thisInputDimensions)):
                if(Values[0].thisInputDimensions[i] == 0):
                    break
                if(not (grad_out.shape[i] == Values[0].thisInputDimensions[i])
                    and not Values[0].thisInputDimensions[i] == -1):
                    print('The following layer has not properly set thisInputDimensions with this incorrect shape')
                    print(Values[0].layerName)
                    print('it is expecting:')
                    print(Values[0].thisInputDimensions)
                    print('but recieved')
                    print(grad_out.shape)
                    print('to check these all at once set PBG.debuggingInputDimensions = 1')
                    if(not PBG.debuggingInputDimensions):
                        sys.exit(0)
                    else:
                        PBG.debuggingInputDimensions = 2
                        return
                    #return
            
            with(torch.no_grad)():
                if(PBG.verbose):
                    print('setting d shape for')
                    print(Values[0].layerName)
                    print(val.size())
                
                Values[0].setOutChannels(val.size())
                Values[0].setupArrays(Values[0].out_channels)
            #why would we not want to set this for data parallel?
            #if(PBG.usingPAIDataParallel == False):
            Values[0].currentDInit[0] = 1
        #self.currentD = val
        
        mathTuple = []
        viewTuple = []
        fullMult = 1
        for i in range(len(val.size())):
            if i == Values[0].thisNodeIndex:
                viewTuple.append(-1)
                continue
            fullMult *= val.shape[i]
            mathTuple.append(i)
            viewTuple.append(1)
        if(PBG.pbTracker.memberVars['mode'] =='p'):
            for i in range(0,PBG.globalCandidates):
                #this is where the grad_in is actually set for the tagger
                averageDMatrix = Values[i].parentsAverageDvector.view(viewTuple)
                if(val.device.type=='cpu'):
                    deviceIndex = 0
                else:
                    deviceIndex = val.device.index
                if(PBG.debuggingMemoryLeak and len(Values[i].currentParentD[deviceIndex]) != 0):
                    print('%s called backward but then didnt get PAIified.  This can cause a memory leak. Check processors.' % Values[i].layerName)
                if(len(candidateNonlinearOuts) == 0):
                    print('Trying to call backwards but module %s wasn\'t PAIified' % Values[i].layerName)
                    sys.exit(0)
                if(PBG.dendriteLearnMode):
                    Values[i].currentParentD[deviceIndex].append((val - (averageDMatrix)).detach())
                    candidateNonlinearOuts[i].register_hook(lambda grad: Values[i].currentParentD[deviceIndex][-1].to(val.device))
                #pretty sure this next line is the right way to do this, not above.  doesnts eem to really have any significant impact though.  should run normal unit tests and xor_main with it to be sure.
                #Values[i].currentParentD = (val).detach()
                #candidateNonlinearOuts[i].register_hook(lambda grad: (Values[i].currentParentD  - (Values[i].parentsAverageDmatrix)))
        if(True):
            Values[0].normalPassAverageD *= 0.99
            '''
            print('val and tuple')
            print(val.shape)
            print(mathTuple)
            print(Values[0].layerName)
            '''
            try:
                Values[0].normalPassAverageD += (val.sum(mathTuple) * 0.01) / fullMult
            except:
                print('Error with type shape in %s' % Values[i].layerName)
                print(val.shape)
                print(mathTuple)
                print(fullMult)
                exit(0)
            #Values[0].normalPassAverageDMags *= 0.99
            #Values[0].normalPassAverageDMags += (val.abs().sum(mathTuple) * 0.01) / fullMult
            #Values[0].normalPassAverageDStd = Values[0].normalPassAverageDStd * 0.99 + val.std((mathTuple))*0.01

            #this is **2 after everything because it is a scalar to scale the final grad_in.  The final gradient that actually gets applied is gradient.sum(mathTuple)
            #final weight adjustment/actual grad value is net.module.mainModule[0].pbNeuronLayer.currentD.sum(mathTuple)
            #You can tell this by looking at the bias values in grad.  It will be similar for the convolution kernel weight values in grad
            '''
            Values[0].normalPassAverageDSq *= 0.99
            if(PBG.gradSumFirst):
                Values[0].normalPassAverageDSq += ((val)**2).sum(mathTuple) * 0.01# / fullMult #if changing here change previous in dataparallel
            else:
                Values[0].normalPassAverageDSq += ((val)).sum(mathTuple)**2 * 0.01# / fullMult
            '''
                    
                #Values[0].currentDout = grad_output
            if(PBG.learnPBLive):
                fullMult = 1
                viewTuple = []
                for dim in range(len(val.shape)):
                    if dim == Values[0].thisNodeIndex:
                        viewTuple.append(-1)
                        continue
                    fullMult *= val.shape[dim]
                    viewTuple.append(1)
                    
                #Keep these values updated on the fly  if this works, might only need to do mean, above and will stay the same and be faster.
                #Values[0].parentsAverageDMags.copy_(Values[0].normalPassAverageDMags.double().detach().clone()/(fullMult))
                Values[0].parentsAverageDvector.copy_(Values[0].normalPassAverageD.detach().clone()/(fullMult))
                #Values[0].parentsAverageDSq.copy_(Values[0].normalPassAverageDSq.double().mean().detach().clone())#/fullMult)

                Values[0].parentsAverageDvector.requires_grad = False
                #Values[0].parentsAverageDSq.requires_grad = False
                #Values[0].parentsAverageDMags.requires_grad = False


def setGrad_params(model, toSet):
    for p in model.parameters():
        p.requires_grad = toSet

def setWrapped_params(model):
    for p in model.parameters():
        p.wrapped = True

def setTracked_params(model):
    for p in model.parameters():
        p.tracked = True

class pb_neuron_layer(nn.Module):
    
    #Why did I make an option to load with a pretrainedPB?  I dont know what the use case would be.  pretrained regular just happens automatically now.
    def __init__(self, startModule, name, pretrainedPB=None):
        super(pb_neuron_layer, self).__init__()

        if(pretrainedPB is None):
            self.mainModule = startModule
            self.name = name
        else:
            self.mainModule = pretrainedPB.mainModule
            self.name = pretrainedPB.name
            
        setWrapped_params(self.mainModule)
        if(PBG.verbose):
            print('initing a layer %s with main type %s' % (self.name, type(self.mainModule)))
            print(startModule)
        if(type(self.mainModule) in PBG.modulesWithProcessing):
            moduleIndex = PBG.modulesWithProcessing.index(type(self.mainModule))
            self.processor = PBG.moduleProcessingClasses[moduleIndex]()
            if(PBG.verbose):
                print('with processor')
                print(self.processor)
        elif(type(self.mainModule).__name__ in PBG.moduleNamesWithProcessing):
            moduleIndex = PBG.moduleNamesWithProcessing.index(type(self.mainModule).__name__)
            self.processor = PBG.moduleByNameProcessingClasses[moduleIndex]()
            if(PBG.verbose):
                print('with processor')
                print(self.processor)
        else:
            self.processor = None
            
        self.randomPBtoCandidates = PBG.defaultRandomPBtoCandidates
        self.activationFunctionValue = -1
        self.type = 'neuronLayer'
        
        self.register_buffer('thisInputDimensions', (torch.tensor(PBG.inputDimensions)))
        if((self.thisInputDimensions == 0).sum() != 1):
            print('5 Need exactly one 0 in the input dimensions: %s' % self.name)
            print(self.thisInputDimensions)
            sys.exit(-1)
        self.register_buffer('thisNodeIndex', torch.tensor(PBG.inputDimensions.index(0)))
        self.pbLayersAdded = 0
        #have to do it like this because .cat to make it bigger returns a variable instead of a parameter so it cant just keep being made bigger
        self.PBtoTop = nn.ParameterList()
        self.register_parameter('newestPBtoTop', None)
        self.CandidatetoTop = nn.ParameterList()
        self.register_parameter('currentCandidatetoTop', None)
        if(pretrainedPB is None):
            self.pb = pb_dendrite_layer(self.mainModule,
                                        pb_dropout_rate = PBG.defaultPbDropout, 
                                        randomPBtoCandidates = self.randomPBtoCandidates,
                                        activationFunctionValue = self.activationFunctionValue,
                                        name = self.name,
                                        inputDimensions = self.thisInputDimensions)
        else:
            self.pb = pretrainedPB.pb
        if ((issubclass(type(startModule),nn.Linear) or #if this is a linear
            (issubclass(type(startModule),PBG.PBSequential) and issubclass(type(startModule.model[0]),nn.Linear))) #or its layer batch with a linear
            and (np.array(self.thisInputDimensions)[2:] == -1).all()): #and everything past 2 is a negative 1
            self.setThisInputDimensions(self.thisInputDimensions[0:2])        
        if(not pretrainedPB is None):
            self.loadFromPretrainedPB(pretrainedPB)
        PBG.pbTracker.addPBNeuronLayer(self)        
        
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.mainModule, name)
            

    # If processors save values they must be cleared in order to call DeepCopy
    def clearProcessors(self):
        if not self.processor:
            return
        else:
            self.processor.clear_processor()
            self.pb.clearProcessors()

    # before loading from a state dict Dendrites should be cleared and reset.
    # this may not be the most effecient way to do things, but clearing and then
    # simulating cycles is the easeiest way to ensure the state dict and the
    # current network have the same number of dendrites
    def clearDendrites(self):
        self.pbLayersAdded = 0
        self.PBtoTop = nn.ParameterList()
        self.CandidatetoTop = nn.ParameterList()
        self.pb = pb_dendrite_layer(self.mainModule,
            pb_dropout_rate = PBG.defaultPbDropout, 
            randomPBtoCandidates = self.randomPBtoCandidates,
            activationFunctionValue = self.activationFunctionValue,
            name = self.name,
            inputDimensions = self.thisInputDimensions)

    #This was to hide that modules are wrapped, but now thats getting patented and part of instructions
    
    def __str__(self):
        if(PBG.verbose):
            totalString = self.mainModule.__str__()
            totalString = 'PAILayer(' + totalString + ')'
            return totalString + self.pb.__str__()
        else:
            totalString = self.mainModule.__str__()
            totalString = 'PAILayer(' + totalString + ')'
            return totalString
    def __repr__(self):
        return self.__str__()
    
    def loadFromPretrainedPB(self, pretrainedPB):
        for valueName in pretrainedPBLoadValues:
            setattr(self,valueName, getattr(pretrainedPB,valueName))
        #self.pb.dendriteLoadFromPretrainedPB(pretrainedPB.pb)


    def setThisInputDimensions(self, newInputDimensions):
        if type(newInputDimensions) is list:
            newInputDimensions = torch.tensor(newInputDimensions)

        #if hasattr(self,'thisInputDimensions'):
        delattr(self, 'thisInputDimensions')
        self.register_buffer('thisInputDimensions', newInputDimensions.detach().clone())
        if (newInputDimensions == 0).sum() != 1:
            print('6 need exactly one 0 in the input dimensions: %s' % self.name)
            print(newInputDimensions)
        self.thisNodeIndex.copy_((newInputDimensions == 0).nonzero(as_tuple=True)[0][0])
        self.pb.setThisInputDimensions(newInputDimensions)

        

    def setMode(self, mode):
        if(PBG.verbose):
            print('%s calling set mode %c' % (self.name, mode))
        if(mode == 'n'):
            self.pb.setMode(mode)
            if(self.pbLayersAdded > 0):
                if(PBG.learnPBLive):
                    values = torch.cat((self.PBtoTop[self.pbLayersAdded-1],nn.Parameter(self.CandidatetoTop.detach().clone())),0)
                else:
                    values = torch.cat((self.PBtoTop[self.pbLayersAdded-1],nn.Parameter(torch.zeros((1,self.out_channels), device=self.PBtoTop[self.pbLayersAdded-1].device, dtype=PBG.dType))),0)
                self.PBtoTop.append(nn.Parameter(values.detach().clone().to(PBG.device), requires_grad=True))
                #self.register_parameter('newestPBtoTop'+str(self.pbLayersAdded), self.PBtoTop[self.pbLayersAdded])
            else:
                if(PBG.learnPBLive):
                    self.PBtoTop.append(nn.Parameter(self.CandidatetoTop.detach().clone(), requires_grad=True))
                else:
                    self.PBtoTop.append(nn.Parameter(torch.zeros((1,self.out_channels), device=PBG.device, dtype=PBG.dType).detach().clone(), requires_grad=True))
                #self.register_parameter('newestPBtoTop'+str(self.pbLayersAdded), self.PBtoTop[self.pbLayersAdded])
            self.pbLayersAdded += 1
            setGrad_params(self.mainModule, True)
            #pbto top [x] is a nodesXPBlayers array, old one of one smaller is deleted and never used again
            if(self.pbLayersAdded > 0):
                self.PBtoTop[self.pbLayersAdded-1].requires_grad = True
                for param in self.pb.PBtoPB:
                    param.requires_grad = False
        else:
            #this gets set in n mode and isnt needed till first p mode so set here
            '''
            DEBUG: If you are getting here but out_channels has not been set
            A common reason is that this layer never had gradients flow through it.
            I have seen this happen because:
                The weights were frozen (requires_grad = False)
                something was added but not used. e.g. self.layer was then added to self.layerPB 
                    but forward is only called on layerPB.  in these cases remove self from the original
                
            '''
            try:
                self.out_channels = self.pb.pbValues[0].out_channels
                self.pb.out_channels = self.pb.pbValues[0].out_channels
            except Exception as e:
                #if this is happening just stop this layer from being converted and remove it from places that it should be
                print(e)
                print('this occured in layer: %s' % self.pb.pbValues[0].layerName)
                print('If you are getting here but out_channels has not been set')
                print('A common reason is that this layer never had gradients flow through it.')
                print('I have seen this happen because:')
                print('-The weights were frozen (requires_grad = False)')
                print('-A model is added but not used so it was convereted but never PB initialized')
                print('-A module was converted that doesn\'t have weights that get modified so backward doesnt flow through it')
                print('If this is normal behavior set PBG.checkedSkippedLayers = True in the main to ignore')
                print('You can also set right now in this pdb terminal to have this not happen more after checking all layers this cycle.')
                if(not PBG.checkedSkippedLayers):
                    import pdb; pdb.set_trace()
                return False
            #only change mode if it actually is learning and calculating grads
            self.pb.setMode(mode)
            if(PBG.learnPBLive):
                self.CandidatetoTop = nn.Parameter(torch.zeros((1,self.out_channels), device=PBG.device, dtype=PBG.dType).detach().clone(), requires_grad=True)
                self.register_parameter('currentCandidatetoTop', self.CandidatetoTop)    
                
                #THIS SHOULDNT BE NEEDED BUT MESSED IT UP IN THIS RUN
                setGrad_params(self.mainModule, True)
                #pbto top [x] is a nodesXPBlayers array, old one of one smaller is deleted and never used again
                if(self.pbLayersAdded > 0):
                    self.PBtoTop[self.pbLayersAdded-1].requires_grad = True
                    for param in self.pb.PBtoPB:
                        param.requires_grad = True



            #set normal layers to no longer learn
            else:
                setGrad_params(self.mainModule, False)
                if(self.pbLayersAdded > 0):
                    self.PBtoTop[self.pbLayersAdded-1].requires_grad = False
                    for param in self.pb.PBtoPB:
                        param.requires_grad = False
        return True

        
    def addPBLayer(self):
        self.pb.addPBLayer()
    def addLoadedPBLayer(self):
        self.pb.addLoadedPBLayer()
    
    def loadTaggerValues(self):
        self.pb.loadTaggerValues()
    def addPBNodes(self, numberNodes):
        self.pb.in_channels = self.in_channels
        self.pb.out_channels = self.out_channels
        self.pb.stride = self.stride
        self.pb.padding = self.padding
        self.pb.kernel_size = self.kernel_size
        self.pb.addPBNodes(numberNodes)
            
    def forward(self, *args, **kwargs):
        if(PBG.debuggingInputDimensions == 2):
            print('all input dim problems now printed')
            sys.exit(0)
        if(PBG.extraVerbose):
            print('%s calling forward' % self.name)
        out = self.mainModule(*args, **kwargs)
        if not self.processor is None:
            out = self.processor.post_n1(out)
        pbOuts, candidateOuts, candidateNonlinearOuts, candidateOutsNonZeroed = self.pb(*args, **kwargs)


        if(self.pbLayersAdded > 0):
            for i in range(0,self.pbLayersAdded):
                toTop = self.PBtoTop[self.pbLayersAdded-1][i,:]
                for dim in range(len(pbOuts[i].shape)):
                    if(dim == self.thisNodeIndex):
                        continue
                    toTop = toTop.unsqueeze(dim)
                if(PBG.confirmCorrectSizes):
                    toTop = toTop.expand(list(pbOuts[i].size())[0:self.thisNodeIndex] + [self.out_channels] + list(pbOuts[i].size())[self.thisNodeIndex+1:])
                #PARALELL HACK TODO what does this mean?
                out = ( out + (pbOuts[i].to(out.device) * toTop.to(out.device)))
        
        #if pb is not in p mode it means this one isnt doing a grad
        if(PBG.pbTracker.memberVars['mode'] == 'p' and self.pb.mode == 'p'):
            ## NEED LOOP HERE
            for i in range(0,PBG.globalCandidates):
                if(PBG.learnPBLive):
                    toTop = self.CandidatetoTop[i,:]
                    for dim in range(len(candidateOutsNonZeroed[i].shape)):
                        if(dim == self.thisNodeIndex):
                            continue
                        toTop = toTop.unsqueeze(dim)
                    if(PBG.confirmCorrectSizes):
                        toTop = toTop.expand(list(candidateOutsNonZeroed[i].size())[0:self.thisNodeIndex] + [self.out_channels] + list(candidateOutsNonZeroed[i].size())[self.thisNodeIndex:])                    
                    out = ( out + (candidateOutsNonZeroed[i].to(out.device) * toTop.to(out.device)))
                        
                #also try this before the next out thing
                out = (out + candidateOuts[i].to(out.device))                 
        #POINT1    
        if(PBG.pbTracker.memberVars['mode'] == 'n' and PBG.doingThing):
            if(out.abs().max() > self.pb.pbValues[0].normalPassMaxMeanAct):
                self.pb.pbValues[0].normalPassMaxMeanAct[0] = out.abs().max().item()
                if(PBG.learnPBLive):
                    self.pb.pbValues[0].parentMaxMeanAct.copy_(self.pb.pbValues[0].normalPassMaxMeanAct[0].detach().clone())
                    self.pb.pbValues[0].parentMaxMeanAct.requires_grad = False
            if(self.pb.pbValues[0].normalPassMaxMeanAct[0] == 0):
                print('An entire layer got exactly 0 Correlation')
                
                import pdb; pdb.set_trace()

        #POINT2
        if(type(out) is tuple):
            print(self)
            print('The output of the above module %s is a tuple when it must be a single tensor')
            print('Look in the API at section 2.2 regarding processors to fix this.')
            import pdb; pdb.set_trace()
        if(out.requires_grad):
            if candidateNonlinearOuts == {}:
                out.register_hook(lambda grad: filterBackward(grad, self.pb.pbValues, {}))
            else:
                candidateNonlinearOuts[0] = candidateNonlinearOuts[0].to(out.device)
                out.register_hook(lambda grad: filterBackward(grad, self.pb.pbValues, candidateNonlinearOuts))
        if not self.processor is None:
            out = self.processor.post_n2(out)
        return out
        


'''
This class exists to wrap the modules you dont want to add Dendrites to.
These will still be correctly changed to learning and not leraning
with calls to setMode
'''
class tracked_neuron_layer(nn.Module):
    
    def __init__(self, startModule, name):
        super(tracked_neuron_layer, self).__init__()

        self.mainModule = startModule
        self.name = name
            
        self.type = 'trackedLayer'
        setTracked_params(self.mainModule)
        if(PBG.verbose):
            print('tracking a layer %s with main type %s' % (self.name, type(self.mainModule)))
            print(startModule)
        PBG.pbTracker.addTrackedNeuronLayer(self)        
        
    def __getattr__(self, name):
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.mainModule, name)
            
    def setMode(self, mode):
        if(PBG.verbose):
            print('%s calling set mode %c' % (self.name, mode))
        if(mode == 'n'):
            setGrad_params(self.mainModule, True)
        else:
            setGrad_params(self.mainModule, False)
        return True
           
    def forward(self, *args, **kwargs):
        return self.mainModule(*args, **kwargs)

def init_params(model):
    for p in model.parameters():
        p.data=torch.randn(p.size(), dtype=p.dtype)*PBG.candidateWeightInitializationMultiplier#Random weight initialisation

class pb_dendrite_layer(nn.Module):
    def __init__(self, initialModule, pb_dropout_rate=0.0,  
                 #resNetLayer=False,
                 randomPBtoCandidates=False, activationFunctionValue=0.3, name='noNameGiven',
                 inputDimensions = []):
        super(pb_dendrite_layer, self).__init__()
        
        if(pb_dropout_rate > 0.0000001):
            print('initing with dropout')
            self.doingDropout = True
            self.pb_dropout_rate = pb_dropout_rate
            self.pbDropoutLayers = nn.ModuleList([])
        else:
            self.doingDropout = False
        self.layers = nn.ModuleList([])
        self.processors = []
        self.candidateProcessors = []
        self.numPBLayers = 0
        self.register_buffer('numCycles', torch.zeros(1, device=PBG.device, dtype=PBG.dType))
        #default to n mode
        self.mode = 'n'
        
        self.name=name
        #this deep copy shouldn't specifically be required but huggingface save complains without it
        self.parentModule = PBU.deepCopyPAI(initialModule)
                            
        #base layer options
        self.currentRecurrentPassTensors = []
        self.currentRecurrentPassCandidateTensors = []
        if(inputDimensions == []):
            self.register_buffer('thisInputDimensions', torch.tensor(PBG.inputDimensions))
        else:
            self.register_buffer('thisInputDimensions', inputDimensions.detach().clone())
        if((self.thisInputDimensions == 0).sum() != 1):
            print('1 need exactly one 0 in the input dimensions: %s' % self.name)
            print(self.thisInputDimensions)
            sys.exit(-1)
        self.register_buffer('thisNodeIndex', torch.tensor(PBG.inputDimensions.index(0)))


        #self.resNetLayer = resNetLayer
        #PB VALUES
        #self.pbValues = nn.ModuleList([])
        self.normalLearningTaggers = {}
        #self.pbOuts = {}
        self.internalRecurrent = False

        self.bestWeights = {}
        self.bestBiases = {}
        self.bestBNWeights = {}
        self.bestBNBiases = {}
        self.PBtoCandidates = nn.ParameterList()
        self.PBtoPB = nn.ParameterList()
        self.addedTaggers = False
        self.randomPBtoCandidates = randomPBtoCandidates
        self.activationFunctionValue = activationFunctionValue
        self.pbValues = nn.ModuleList([])
        for j in range(0, PBG.globalCandidates):
            if(PBG.verbose):
                print('creating pb Values for %s' % (self.name))
            self.pbValues.append(pbValueTracker(False, self.activationFunctionValue, self.name, self.thisInputDimensions))

    def setThisInputDimensions(self, newInputDimensions):
        if type(newInputDimensions) is list:
            newInputDimensions = torch.tensor(newInputDimensions)
        delattr(self, 'thisInputDimensions')
        self.register_buffer('thisInputDimensions', newInputDimensions.detach().clone())
        if (newInputDimensions == 0).sum() != 1:
            print('2 Need exactly one 0 in the input dimensions: %s' % self.name)
            print(newInputDimensions)
            sys.exit(-1)
        self.thisNodeIndex.copy_((newInputDimensions == 0).nonzero(as_tuple=True)[0][0])
        for j in range(0, PBG.globalCandidates):
            self.pbValues[j].setThisInputDimensions(newInputDimensions)


    def dendriteLoadFromPretrainedPB(self, pretrainedPB):
        for j in range(0, PBG.globalCandidates):
            self.pbValues[j].setupArrays(pretrainedPB.pbValues[j].out_channels)
            for valueName in (dendriteSaveValues + pretrainedPBDendriteLoadValues):
                setattr(self.pbValues[j],valueName, getattr(pretrainedPB.pbValues[j],valueName))
            self.pbValues[j].activationFunctionValue = pretrainedPB.activationFunctionValue            

    def addPBLayer(self):
                
        self.candidateLayer = nn.ModuleList([])
        self.candidateBestLayer = nn.ModuleList([])
        if(PBG.verbose):
            print(self.name)
            print('setting candidate processors')
        self.candidateProcessors = []
        with torch.no_grad():
            for i in range(0, PBG.globalCandidates):
                
                newModule = fakeCopy(self.parentModule)
                init_params(newModule)
                setGrad_params(newModule, True)
                self.candidateLayer.append(newModule)
                self.candidateBestLayer.append(fakeCopy(newModule))
                if(type(self.parentModule) in PBG.modulesWithProcessing):
                    moduleIndex = PBG.modulesWithProcessing.index(type(self.parentModule))
                    self.candidateProcessors.append(PBG.moduleProcessingClasses[moduleIndex]())
                elif(type(self.parentModule).__name__ in PBG.moduleNamesWithProcessing):
                    moduleIndex = PBG.moduleNamesWithProcessing.index(type(self.parentModule).__name__)
                    self.candidateProcessors.append(PBG.moduleByNameProcessingClasses[moduleIndex]())

                

        for i in range(0, PBG.globalCandidates):
            self.candidateLayer[i].to(PBG.device)
            self.candidateBestLayer[i].to(PBG.device)
            

        #normalize AverageDSq?
        #normalPassAverageDSq = normalPassAverageDSq/((normalPassAverageDSq*normalPassAverageDSq).sum()).sqrt()
        # for i in range(0, self.out_channels):
        for j in range(0, PBG.globalCandidates):
            self.pbValues[j].reinitializeForPB(0)
        
        self.addedTaggers = True
            
            

        if(self.numPBLayers > 0):
            self.PBtoCandidates = nn.ParameterList()
            for j in range(0,PBG.globalCandidates): #Loopy Loops
                self.PBtoCandidates.append(nn.Parameter(torch.zeros((self.numPBLayers, self.out_channels), device=PBG.device, dtype=PBG.dType), requires_grad=True))
                self.PBtoCandidates[j].data.pbWrapped = True
                if(self.randomPBtoCandidates):
                    with torch.no_grad():
                        self.PBtoCandidates[j].normal_(0, math.sqrt(2. / self.out_channels))
                #self.register_parameter(('PBtoCandidates'+str(j)), self.PBtoCandidates[j])


 
    def clearProcessors(self):
        for processor in self.processors:
            if not processor:
                continue
            else:
                processor.clear_processor()
        for processor in self.candidateProcessors:
            if not processor:
                continue
            else:
                processor.clear_processor()

        
    def setMode(self, mode):
        self.mode = mode
        self.numCycles += 1
        if(PBG.verbose):
            print('pb calling set mode %c : %d' % (mode, self.numCycles))
        if(mode == 'n'):
            if(PBG.verbose):
                print('so calling all the things to add to layers')
            for i in range(0,PBG.globalCandidates):
                self.pbValues[i].locked[0] = 1
                
                
            if(self.doingDropout):
                self.pbDropoutLayers.append(nn.Dropout(p=self.pb_dropout_rate).to(PBG.device))

            #copy weights/bias from correct candidates
            if(self.numPBLayers == 1):
                self.PBtoPB = nn.ParameterList()
                self.PBtoPB.append(torch.tensor([]))
            if(self.numPBLayers >= 1):
                self.PBtoPB.append(torch.nn.Parameter(torch.zeros([self.numPBLayers,self.out_channels], device=PBG.device, dtype=PBG.dType), requires_grad=PBG.dendriteUpdateMode))#NEW
            with torch.no_grad():
                if(PBG.globalCandidates > 1):
                    print('This was a flag that will be needed if using multiple candidates.  It\'s not set up yet but nice work finding it.')
                    pdb.set_trace()
                planeMaxIndex = 0
                self.layers.append(fakeCopy(self.candidateBestLayer[planeMaxIndex]))
                self.layers[self.numPBLayers].to(PBG.device)
                if(self.numPBLayers > 0):
                    if(PBG.verbose):
                        print('this maybe shuould have a clone and data')
                    self.PBtoPB[self.numPBLayers].copy_(self.PBtoCandidates[planeMaxIndex])
                if(type(self.parentModule) in PBG.modulesWithProcessing):
                    self.processors.append(self.candidateProcessors[planeMaxIndex])
                if(type(self.parentModule).__name__ in PBG.moduleNamesWithProcessing):
                    self.processors.append(self.candidateProcessors[planeMaxIndex])

            #set PB nodes to no longer learn
            
            setGrad_params(self.layers[self.numPBLayers], PBG.dendriteUpdateMode)
            for param in self.PBtoPB:
                param.requires_grad = PBG.dendriteUpdateMode
            if(self.numPBLayers > 0):
                for j in range(0,PBG.globalCandidates): #Loopy Loops
                    self.PBtoCandidates[j].requires_grad = False


            del self.candidateLayer, self.candidateBestLayer

            self.numPBLayers += 1
        
    def killerRecursive(self, inVals, killing):
        device = None
        if type(inVals) is list:
            if(len(inVals) == 0):
                return inVals, None
            for index in range(len(inVals)):
                inVals[index], device2 = self.killerRecursive(inVals[index], killing)
                if(not device2 is None):
                    device = device2
        elif type(inVals) is tuple:
            if(len(inVals) == 0):
                return inVals, None
            for index in range(len(inVals)):
                inVals = list(inVals)
                inVals[index], device2 = self.killerRecursive(inVals[index], killing)
                if(not device2 is None):
                    device = device2
                inVals = tuple(inVals)
        elif type(inVals) is dict:
            if(len(inVals.keys()) == 0):
                return inVals, None
            for index in inVals.keys():
                inVals[index], device2 = self.killerRecursive(inVals[index], killing)
                if(not device2 is None):
                    device = device2
        elif issubclass(torch.Tensor, type(inVals)):
            with torch.cuda.device_of(inVals):
                if(killing):
                    toReturn = gradKiller(inVals).detach().clone()
                else:
                    toReturn = inVals
                return toReturn, inVals.device
        else:
            return inVals, None
        return inVals, device

    def killerRecursiveOld(self, inVals):
        if type(inVals) is list:
            for index in range(len(inVals)):
                inVals[index] = self.killerRecursive(inVals[index])
        elif type(inVals) is tuple:
            for index in range(len(inVals)):
                inVals = list(inVals)
                inVals[index] = self.killerRecursive(inVals[index])
                inVals = tuple(inVals)
        elif type(inVals) is dict:
            for index in inVals.keys():
                inVals[index] = self.killerRecursive(inVals[index])
        elif issubclass(torch.Tensor, type(inVals)):
            return gradKiller(inVals).detach().clone()
        return inVals
        
    def forward(self, *args, **kwargs):
        outs = {}
            
        for c in range(0,self.numPBLayers):
            args2, device = self.killerRecursive(args, PBG.dendriteGraphMode)
            kwargs2, device2 = self.killerRecursive(kwargs, PBG.dendriteGraphMode)
            #args2, = self.killerRecursive(args)
            #kwargs2 = self.killerRecursive(kwargs)
            if(self.processors != []):
                args2, kwargs2 = self.processors[c].pre_d(*args2, **kwargs2)
            outValues = self.layers[c](*args2, **kwargs2)
            if(self.processors != []):
                outs[c] = self.processors[c].post_d(outValues)
            else:
                outs[c] = outValues




        for outIndex in range(0,self.numPBLayers):
            currentOut = outs[outIndex]
            viewTuple = []
            for dim in range(len(currentOut.shape)):
                if dim == self.thisNodeIndex:
                    viewTuple.append(-1)
                    continue
                viewTuple.append(1)

            for inIndex in range(0,outIndex):
                #PARALLEL HACK
                if(viewTuple == [1]): #This is only the case when passing a single datapoint rather than a batch
                    currentOut += self.PBtoPB[outIndex][inIndex,:].to(currentOut.device) * outs[inIndex]            
                else:
                    currentOut += self.PBtoPB[outIndex][inIndex,:].view(viewTuple).to(currentOut.device) * outs[inIndex]            
            currentOut.copy_( PBG.PBForwardFunction(currentOut))
            if(self.doingDropout):
                for outIndex in range(0,self.numPBLayers):
                    currentOut.copy_( self.pbDropoutLayers[outIndex](currentOut))
        candidateOuts = {}
        candidateNonlinearOuts = {}
        candidateNonZeroed = {}
        for i in range(0,PBG.globalCandidates):
            #self.mode will only not also be p if this is not learning
            if(PBG.pbTracker.memberVars['mode'] == 'p' and self.mode == 'p'):
                args2, device = self.killerRecursive(args, PBG.candidateGraphMode)
                kwargs2, device2  = self.killerRecursive(kwargs, PBG.candidateGraphMode)
                if device is None:
                    device = device2

                '''
                DEBUG: if youre here this layer should have PB nodes which means
                candidate processors should have been initialized.  If its not you are likely
                still pointing to the old model that doesnt have PB nodes added.  make sure
                when you call add validation score you are properly setting the model
                '''
                if(self.candidateProcessors != []):
                    args2, kwargs2 = self.candidateProcessors[i].pre_d(*args2, **kwargs2)
                
                '''
                DEBUG:
                If you are getting a cpu vs gpu issue on this line its because the model is receiving args that are on the wrong thing, but within the forward function it gets passed to the correct spot.  don't ever call to() in the forward function, call it before it gets passed in
                '''
                candidateOutValues = self.candidateLayer[i].to(device)(*args2, **kwargs2)
                if(self.candidateProcessors != []):
                    candidateOuts[i] = self.candidateProcessors[i].post_d(candidateOutValues)
                else:
                    candidateOuts[i] = candidateOutValues

                for inIndex in range(self.numPBLayers):
                    #PARALLEL HACK
                    if(viewTuple == [1]): #This is only the case when passing a single datapoint rather than a batch
                        candidateOuts[i] = candidateOuts[i].to(device) + self.PBtoCandidates[i][inIndex,:].to(device) * outs[inIndex]
                    else:
                        candidateOuts[i] = candidateOuts[i].to(device) + self.PBtoCandidates[i][inIndex,:].view(viewTuple).to(device) * outs[inIndex]

                if(PBG.dendriteLearnMode):
                    candidateOuts[i] = pbTagger(candidateOuts[i], self.pbValues[i].to(device))
                #import pdb; pdb.set_trace()
                candidateNonlinearOuts[i] = PBG.PBForwardFunction(candidateOuts[i]).to(device)
                    
                #candidateNonlinearOuts chosen randomly, just generally saying dont do this during inference, only training.
                if(self.training):
                    #no it seems like this should be cleared on the main module so when its replicated it should work properly.
                    if(device.type=='cpu'):
                        deviceIndex = 0
                    else:
                        deviceIndex = device.index
                    if(PBG.debuggingMemoryLeak and len(self.pbValues[i].pbOuts[deviceIndex]) != 0):
                        if(PBG.noBackwardWorkaround):
                            del self.pbValues[i].pbOuts[deviceIndex][-1] 
                            # This may also be requried for noBackwardWorkaround.  Found it earlier, but didnt have a noBackwards problem to debug with
                            #del self.pbValues[i].currentParentD[deviceIndex][-1]
                        else:
                            print("%s is in backwards graph multiple times.  This will cause a memory leak unless it is a recurrent layer.  Currently stacked (%d/%d) times" % (self.name, len(self.pbValues[0].pbOuts[0]), len(self.pbValues[0].currentParentD[0])))
                            print('If this is coming up before a memory leak that happens anywhere other than the first batch of an epoch you NEED to debug this.')
                            print('Check the Memory Leak section of the debugging MD file.')
                            print('If this is just being printed but there is not a memory leak you can set PBG.debuggingMemoryLeak = False')
                            print('If you don\'t have any recurrent layers you can also clear this by in a more memory effecient way by setting PBG.noBackwardWorkaround = True')
                            print('If you set PBG.noBackwardWorkaround = True and it causes a IndexError: list index out of range error, that means you do have a recurrent layer')
                            #import pdb; pdb.set_trace()
                    if(PBG.dendriteLearnMode):
                        self.pbValues[i].pbOuts[deviceIndex].append(candidateNonlinearOuts[i].detach().clone().to(device))
                        if(PBG.extraVerbose and candidateNonlinearOuts[i].isnan().any()):
                            print('got candidate out nan')
                            import pdb; pdb.set_trace()
                candidateNonZeroed[i] = candidateNonlinearOuts[i].detach().clone().to(device)
                candidateOuts[i] = noForward(candidateNonlinearOuts[i])
        
        return outs, candidateOuts, candidateNonlinearOuts, candidateNonZeroed
    

from torch.amp import custom_fwd, custom_bwd

def pbTagger(inp, Values):
    class Tagger(torch.autograd.Function):
        @staticmethod
        @custom_fwd(device_type='cuda', cast_inputs=torch.float32)
        def forward(ctx, inp):
            return inp
        @staticmethod
        @custom_bwd(device_type='cuda')
        def backward(ctx, grad_out):
            yoloTesting = False

            with torch.no_grad():
                savedValues = Values
                if(savedValues.layerName == '.layers.29' and yoloTesting):
                    PBG.extraVerbose = True

                if(savedValues.locked):
                    return grad_out*0, None

                mathTuple = []
                viewTuple = []
                for i in range(len(grad_out.size())):
                    if i == Values.thisNodeIndex:
                        viewTuple.append(-1)
                        continue
                    mathTuple.append(i)
                    viewTuple.append(1)

                eps = 0.00000001
                if(grad_out.device.type=='cpu'):
                    deviceIndex = 0
                else:
                    deviceIndex = grad_out.device.index
                if (len(savedValues.pbOuts[deviceIndex]) == 0):
                    print('Dendrite does not have output Value for layer %s' % savedValues.layerName)
                    print('This is caused by your model being in eval mode when you call loss.backwards()')
                    import pdb; pdb.set_trace()
                lastPbOuts = savedValues.pbOuts[deviceIndex][-1].detach().clone().to(grad_out.device)
                lastParentD = savedValues.currentParentD[deviceIndex][-1].detach().clone().to(grad_out.device)
                direction = savedValues.PrevPBCandidateCorrelation.sign()
                tempReshapeDirection = direction.view(viewTuple)
                currentCorrelations = lastPbOuts * (lastParentD)
                
                #shouldn't this be the avarege?  its * all of the current outputs and parent errors. why would it sum them before subtracting them from the average output * the average errors.
                #retain all PB is currently broken. doesnt seem to actually work and also messages up saving     graphs.

                #looks lke this is worse, but not sure why.  Switch back to the original and move on.                
                # if every coming back to this remember to chance cor calculation to just be this later
                #currentCorrelations = (lastPbOuts.to(lastParentD.device)-aveOut) * (lastParentD)
                #currentCorrelations = currentCorrelations.mean(mathTuple)

                #can also try one where it switcheds to mean if the sum is > 1. or allow it to be set by layer manually
                if(PBG.correlationsByMean):
                    currentCorrelations = currentCorrelations.mean((mathTuple))
                else:
                    currentCorrelations = currentCorrelations.sum((mathTuple))
                    
                #got rid of averagedsq because doing a proportional scaling later so this scaling doesnt matter.
                if(PBG.formulaType == 0):
                    grad_in = -(grad_out.detach() * (tempReshapeDirection))# / ((savedValues.parentsAverageDSq + eps))
                elif(PBG.formulaType == 1):
                    grad_in = -(grad_out.detach() * currentCorrelations.view(viewTuple) * (tempReshapeDirection))# / ((savedValues.parentsAverageDSq + eps))
                #this doesnt work, the second gradin is just the same since its average and not actual sum
                elif(PBG.formulaType == 2):
                    grad_in = -(grad_out.detach() * currentCorrelations.view(viewTuple) * (tempReshapeDirection))# / ((savedValues.parentsAverageDSq + eps))
                    grad_in /= (grad_out.pow(2) * currentCorrelations.view(viewTuple).pow(2)).sqrt()
                elif(PBG.formulaType == 3):
                    grad_in = -(grad_out.detach() * (lastPbOuts - savedValues.PrevPBCandidateAverage.view(viewTuple)) * (tempReshapeDirection))
                # same as 2
                elif(PBG.formulaType == 4):
                    grad_in = -(grad_out.detach() * (lastPbOuts - savedValues.PrevPBCandidateAverage.view(viewTuple)) * (tempReshapeDirection))
                    grad_in /= (grad_out.pow(2) * (lastPbOuts - savedValues.PrevPBCandidateAverage.view(viewTuple)).pow(2)).sqrt()

                #print('top')
                #print(savedValues.topPBCandidateAverage)
                #print('ave')
                #print(savedValues.PrevPBCandidateAverage)

                #adjust correlations
                
                
                
                savedValues.topPBCandidateAverage.copy_(lastPbOuts.mean((mathTuple)))

                        
                savedValues.PrevPBCandidateAverage *= 0.99
                savedValues.PrevPBCandidateAverage += savedValues.topPBCandidateAverage * 0.01


                if(PBG.extraVerbose):
                    print('new top')
                    print(savedValues.topPBCandidateAverage)
                    print('new ave')
                    print(savedValues.PrevPBCandidateAverage)
                    print('parentsAverageD')
                    print(savedValues.parentsAverageDvector)
                    print('lastPbOuts')
                    print(lastPbOuts)
                    print('lastParentD')
                    print(lastParentD)
                    print('currentCorrelations')
                    print(currentCorrelations)
                #if(not PBG.usingPAIDataParallel):
                if(True):
                    #TODO: Should this use topPBCandidateAverage until initialized has completed?
                    cor = currentCorrelations - (savedValues.PrevPBCandidateAverage * savedValues.parentsAverageDvector) # / net['layers'][l]['sumSqError'][j]
                    if(PBG.extraVerbose):
                        print('prev')
                        print(savedValues.PrevPBCandidateCorrelation)
                        print('cor')
                        print(cor)
                        print('currentCorrelations')
                        print(currentCorrelations)
                    savedValues.PrevPBCandidateCorrelation *= 0.99
                    savedValues.PrevPBCandidateCorrelation += cor * 0.01
                    if(PBG.extraVerbose):
                        print('next prev')
                        print(savedValues.PrevPBCandidateCorrelation)
                        if((savedValues.parentsAverageDvector).isnan().any()
                           or (savedValues.PrevPBCandidateAverage).isnan().any()
                           or (savedValues.topPBCandidateAverage).isnan().any()
                           or (currentCorrelations).isnan().any()):
                            print('got a nan in correlation score')
                            import pdb; pdb.set_trace()
                        


                    
                    tempAbs = savedValues.PrevPBCandidateCorrelation.detach().abs()
                    
                    #best score is the max score of the previous best score and the current recently averaged correlation
                    
                    
                    [bestScore, tempBestIndices] =  torch.max(torch.cat((savedValues.bestScore.unsqueeze(0),tempAbs.unsqueeze(0)), 0),0)
                    savedValues.bestScore.copy_(bestScore)
                    
                    #print(savedValues.bestScore)
                    #if that best score has improved enough or this is the very first iteration
                    if(((
                        (savedValues.bestScore*(1.0-PBG.pbImprovementThreshold))-savedValues.previousBestScore).max()>0.00000001
                        and (savedValues.bestScore - savedValues.previousBestScore).max() > PBG.pbImprovementThresholdRaw)

                        or savedValues.initialized.item() == 0):
                        
                        if(savedValues.bestScoreImprovedThisEpoch[0] == 0 and PBG.verbose):
                            print('Score from %.16f to %.16f for %s with initialized %d' % (savedValues.previousBestScore.mean(), 
                                                                                            savedValues.bestScore.mean(), 
                                                                                            savedValues.layerName,
                                                                                            savedValues.initialized.item()))
                        # say that best score did improve this epoch and time step
                        savedValues.bestScoreImprovedThisEpoch[0].copy_(torch.tensor(1))
                        #print('setting best score improved this timestep with')
                        #print(savedValues.bestScore)
                        #print(savedValues.previousBestScore)
                        #print(savedValues.initialized.item())
                        savedValues.bestScoreImprovedThisTimeStep[0].copy_(torch.tensor(1))
                        #set the indexes of the best candidate
                        savedValues.indexesOfbest.copy_(tempBestIndices)
                        
                        ##check where tempabs = bestscore and save the weights for those candidates in forward for the layer next itearation
                            #this is where that saveBest function was maybe called?
                        [values,indexes] = torch.max(savedValues.indexesOfbest,0)
                        savedValues.nodesBestImprovedThisEpoch += savedValues.indexesOfbest
                        #only replace the ones that are bigger                            
                        savedValues.previousBestScore.copy_(torch.max(savedValues.bestScore, savedValues.previousBestScore).detach())
                        
                        
                        
                            
                        
                    else:
                        #print('setting best score improved this timestep with')
                        #print(savedValues.bestScore)
                        #print(savedValues.previousBestScore)
                        #print(savedValues.initialized.item())
                        savedValues.bestScoreImprovedThisTimeStep[0].copy_(torch.tensor(0))
                        savedValues.indexesOfbest *= 0
                    if(savedValues.breaking.item()):
                        pdb.set_trace()
                #else: # if not new dataparallel all of this is being done in gather
                    #savedValues.currentCorrelationsForParallel = currentCorrelations
                    
                if(savedValues.initialized.item() < PBG.initialCorrelationBatches):#*2?
                    #for the first 10 iterations average out the initial conditions a little bit
                    #at the beggining have it equal the actual average, not the abs average
                    #this is because the best is the abs of running best, but running best is average of a bunch of positives and negatives, so to just initialize as a single value it it a high positive or negative
                
                    savedValues.candidateGradAverageForScaling *= savedValues.initialized
                    savedValues.candidateGradAverageForScaling += grad_in.abs().mean(mathTuple)
                    savedValues.candidateGradAverageForScaling /= (savedValues.initialized + 1.0)
                    savedValues.mainGradAverageForScaling *= savedValues.initialized
                    savedValues.mainGradAverageForScaling += lastParentD.abs().mean(mathTuple)
                    savedValues.mainGradAverageForScaling /= (savedValues.initialized + 1.0)

                    #if(not PBG.usingPAIDataParallel):
                    if(True):
                        savedValues.PrevPBCandidateAverage *= savedValues.initialized
                        savedValues.PrevPBCandidateAverage += savedValues.topPBCandidateAverage
                        savedValues.PrevPBCandidateAverage /= savedValues.initialized + 1.0
                        #print('init update PrevPBCandidateAverage')
                        #print(savedValues.PrevPBCandidateAverage)

                        cor = currentCorrelations - (savedValues.PrevPBCandidateAverage * savedValues.parentsAverageDvector) # / net['layers'][l]['sumSqError'][j]
                        #print('init update cor')
                        #print(cor)

                        savedValues.PrevPBCandidateCorrelation *= savedValues.initialized
                        savedValues.PrevPBCandidateCorrelation += cor
                        savedValues.PrevPBCandidateCorrelation /= savedValues.initialized + 1.0
                        #print('init update prev')
                        #print(savedValues.PrevPBCandidateCorrelation)
                    #else:
                        #savedValues.currentCorrelationsForParallel.copy_(currentCorrelations)
                    #and other values should be zeroed so they dont effect things during this initialization step
                    savedValues.bestScore.copy_(savedValues.bestScore.detach() * 0)
                    savedValues.previousBestScore.copy_(savedValues.previousBestScore.detach() * 0)
                    savedValues.initialized += 1.0
                    #print('initialized')
                    #print(savedValues.initialized.item())
                    scalar = 0.0000000
                else:
                    '''
                    if this candidate is getting errors so low that the average at this point is 0 it is likely because vanishing gradient has died so theres not much to do here anyway
                    just set scalar to 0 and move on.  TODO: see if there is a better way to to this?  When it was caught with with autograd.detect_anomaly(): around forward->backward .normalPassAverageD was actually
                    just a super small number but not exactly 0.  this means there is some amount of error it just is getting deleted after averaging because of float resolution.
                    '''
                    if(savedValues.candidateGradAverageForScaling.mean().item() == 0):
                        #pdb.set_trace()
                        scalar = 0.0
                    else:
                        #savedValues.candidateGradAverageForScaling = grad_in.abs().mean(mathTuple) * 0.001 + savedValues.candidateGradAverageForScaling * 0.999
                        #grad_in = (grad_in * (savedValues.parentsAverageDvector.abs().mean()/savedValues.candidateGradAverageForScaling.abs().mean())) / savedValues.currentParentD.abs().std()#.view(1,-1,1,1))
                        #scalar = savedValues.parentsAverageDvector.abs().mean()/savedValues.candidateGradAverageForScaling.abs().mean()
                        scalar = savedValues.mainGradAverageForScaling.mean()/savedValues.candidateGradAverageForScaling.mean()
                        #print('\n\n%s scaler ended up as ' % savedValues.layerName)
                        #print(scalar)
                        #print('with')
                        #print(savedValues.parentsAverageDMags.mean())
                        #print('from')
                        #print(savedValues.mainGradAverageForScaling.mean())
                        #print('and')
                        #print(savedValues.candidateGradAverageForScaling.mean())
                        
                        #scalar = (1/savedValues.parentsAverageDSq)
                        #scalar = 1 seems to not make things die.  gotta figure out a way to do this scalar reasonably.  Why would this not work if its scaling it to the same magnitude as the main gradient is learning?
                        #scalar = 1
                if(PBG.doingThing):
                    scalar /= savedValues.parentMaxMeanAct.item()

                if(savedValues.layerName == '.layers.29' and yoloTesting):
                    PBG.extraVerbose = False


                grad_in = grad_in * scalar#.view(1,-1,1,1))
                del savedValues.currentParentD[deviceIndex][-1]
                del savedValues.pbOuts[deviceIndex][-1]
                
                return grad_in, None
            
    return Tagger.apply(inp)


def gradKiller(inp):
    class Killer(torch.autograd.Function):
        @staticmethod
        def forward(ctx, inp):
            #print('forward called')
            return inp
        @staticmethod
        def backward(ctx, grad_out):
            #print('backward called')
            return grad_out * 0, None
    return Killer.apply(inp)


def noForward(inp):
    class noForward(torch.autograd.Function):
        @staticmethod
        def forward(ctx, inp):
            return inp * 0
        @staticmethod
        def backward(ctx, grad_out):
            return grad_out     
    return noForward.apply(inp)

    
 


        
class pbValueTracker(nn.Module):
    def __init__(self, initialized, activationFunctionValue, name, inputDimensions, out_channels=-1):
        super(pbValueTracker, self).__init__()
        
        self.layerName = name
        
        for valName in dendriteInitValues:
            self.register_buffer(valName, torch.zeros(1, device=PBG.device, dtype=PBG.dType))
        self.initialized[0] = initialized
        self.activationFunctionValue = activationFunctionValue
        self.register_buffer('thisInputDimensions', inputDimensions.clone().detach())
        if((self.thisInputDimensions == 0).sum() != 1):
            print('3 need exactly one 0 in the input dimensions: %s' % self.layerName)
            print(self.thisInputDimensions)
            sys.exit(-1)
        self.register_buffer('thisNodeIndex', (inputDimensions == 0).nonzero(as_tuple=True)[0])
        if(out_channels != -1):
            self.setupArrays(out_channels)   
        else:
            self.out_channels = -1

    def print(self):
        totalString = 'Value Tracker:'
        for valName in dendriteInitValues:
            totalString += '\t%s:\n\t\t' % valName
            totalString += getattr(self,valName).__repr__()
            totalString += '\n'
        for valName in dendriteTensorValues:
            if(not getattr(self,valName,None) is None):
                totalString += '\t%s:\n\t\t' % valName
                totalString += getattr(self,valName).__repr__()
                totalString += '\n'
        print(totalString)
    
    def setThisInputDimensions(self, newInputDimensions):
        if type(newInputDimensions) is list:
            newInputDimensions = torch.tensor(newInputDimensions)
        delattr(self, 'thisInputDimensions')
        self.register_buffer('thisInputDimensions', newInputDimensions.detach().clone()) 
        if (newInputDimensions == 0).sum() != 1:
            print('4 need exactly one 0 in the input dimensions: %s' % self.layerName)
            print(newInputDimensions)
            sys.exit(-1)
        self.thisNodeIndex.copy_((newInputDimensions == 0).nonzero(as_tuple=True)[0][0])

    def setOutChannels(self, shapeValues):
        if(type(shapeValues) == torch.Size):
            self.out_channels = int(shapeValues[self.thisNodeIndex])
        else:
            self.out_channels = int(shapeValues[self.thisNodeIndex].item())
    def setupArrays(self, out_channels):
        self.out_channels = out_channels
        for valName in dendriteTensorValues:
            self.register_buffer(valName, torch.zeros(out_channels, device=PBG.device, dtype=PBG.dType))
 
        for name in valueTrackerArrays:
            # if its not copying then just make arrays so they can get deleted every time
            #if(not PBG.usingPAIDataParallel):
            setattr(self,name,{})
            count = 1
            if torch.cuda.device_count() > count:
                count = torch.cuda.device_count()
            for i in range(count):
                getattr(self,name)[i] = []
            #else: # if it is copying make parameter lists so they are separtae and deleiton is not required
                #setattr(self,name,torch.nn.ParameterList())

        #parent values
        for valName in dendriteSingleValues:
            self.register_buffer(valName, torch.zeros(1, device=PBG.device, dtype=PBG.dType))            
        
    def reinitializeForPB(self, initialized):
        if(self.out_channels == -1):
            print('You have a converted module that was never initialized')
            print('This likely means it not being added to the autograd graph')
            print('Check your forward function that it is actually being used')
            print('If its not you should really delete it, but you can also add')
            print('the name below to PBG.moduleIDsToTrack to not convert it')
            print(self.layerName)
            print('with:')
            print('PBG.moduleNamesToTrack += [\'' + self.layerName + '\']')
            print('This can also happen while testingDendriteCapactity if you')
            print('run a validation cycle and try to add Dendrites before doing any training.\n')
            
        self.initialized[0] = initialized
        for valName in dendriteReinitValues:
            if((not valName in nonLiveSkipValues) or PBG.learnPBLive):
                setattr(self,valName,getattr(self,valName) * 0)

        if(PBG.doingThing):
            self.parentMaxMeanAct.copy_(self.normalPassMaxMeanAct.detach().clone())
            self.parentMaxMeanAct.requires_grad = False
        #self.parentsAverageDMags.copy_(self.normalPassAverageDMags.double().detach().clone())
        self.parentsAverageDvector.copy_(self.normalPassAverageD.detach().clone())
        #self.parentsAverageDSq.copy_(self.normalPassAverageDSq.double().mean().detach().clone())
        self.parentsAverageDvector.requires_grad = False
        #self.parentsAverageDSq.requires_grad = False
        #self.parentsAverageDMags.requires_grad = False
        
        
        
        
