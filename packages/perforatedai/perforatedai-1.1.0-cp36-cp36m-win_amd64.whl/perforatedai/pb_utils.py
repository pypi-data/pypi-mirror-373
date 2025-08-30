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
import warnings
from perforatedai import pb_globals as PBG
from perforatedai import pb_layer as PB
from perforatedai import pb_models as PBM
from perforatedai import check_license
from perforatedai import cleanLoad as CL
from perforatedai import blockwisePB as BPB
from perforatedai import pb_neuron_layer_tracker as PBT

import copy

from safetensors.torch import load_file
from safetensors.torch import save_file


def initializePB(model, doingPB=True, saveName='PB', makingGraphs=True, maximizingScore=True, num_classes=10000000000, values_per_train_epoch=-1, values_per_val_epoch=-1, zoomingGraph=True):
    PBG.pbTracker = PBT.pb_neuron_layer_tracker(doingPB=doingPB,saveName=saveName)
    PBG.saveName = saveName
    model = PBG.pbTracker.initialize(model, doingPB=doingPB, saveName=saveName, makingGraphs=makingGraphs, maximizingScore=maximizingScore, num_classes=num_classes, values_per_train_epoch=-values_per_train_epoch, values_per_val_epoch=values_per_val_epoch, zoomingGraph=zoomingGraph)
    return model

def check_requires_grad(module):
  for param in module.parameters():
    if param.requires_grad:
      return True
  return False

def debug_printGradModules(net, depth, nameSoFar):
    print('%s: has req grads: %d' % (nameSoFar, check_requires_grad(net)))
    allMembers = net.__dir__()
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submoduleID, layer in net.named_children():
            subName = nameSoFar + '.' + str(submoduleID)
            if(net != net.get_submodule(submoduleID)):
                debug_printGradModules(net.get_submodule(submoduleID), depth + 1, subName)
    else:
        for member in allMembers:
            subName = nameSoFar + '.' + member
            try:
                getattr(net,member,None)
            except:
                continue
            if issubclass(type(getattr(net,member,None)),nn.Module):
                #pdb.set_trace()
                if(net != getattr(net,member)):
                    debug_printGradModules(getattr(net,member), depth+1, subName)

def getPBModules(net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    allMembers = net.__dir__()
    thisList = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submoduleID, layer in net.named_children():
            #if there is a self pointer ignore it
            if net.get_submodule(submoduleID) is net:
                continue
            if type(net.get_submodule(submoduleID)) is PB.pb_neuron_layer:
                thisList = thisList + [net.get_submodule(submoduleID)]

            else:
                #print('sub list not one so continuing')
                thisList = thisList + getPBModules(net.get_submodule(submoduleID), depth + 1)            
    else:
        for member in allMembers:        
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if getattr(net,member,None) is net:
                continue
            if type(getattr(net,member,None)) is PB.pb_neuron_layer:
                #print('sub is one so converting')
                thisList = thisList + [getattr(net,member)]
                #print(thisList)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                thisList = thisList + getPBModules(getattr(net,member), depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(thisList)
    return thisList

def getTrackedModules(net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    allMembers = net.__dir__()
    thisList = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submoduleID, layer in net.named_children():
            #if there is a self pointer ignore it
            if net.get_submodule(submoduleID) is net:
                continue
            if type(net.get_submodule(submoduleID)) is PB.tracked_neuron_layer:
                thisList = thisList + [net.get_submodule(submoduleID)]

            else:
                #print('sub list not one so continuing')
                thisList = thisList + getTrackedModules(net.get_submodule(submoduleID), depth + 1)            
    else:
        for member in allMembers:        
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if getattr(net,member,None) is net:
                continue
            if type(getattr(net,member,None)) is PB.tracked_neuron_layer:
                #print('sub is one so converting')
                thisList = thisList + [getattr(net,member)]
                #print(thisList)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                thisList = thisList + getTrackedModules(getattr(net,member), depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(thisList)
    return thisList 

def getPBModuleParams(net, depth):
    #print('calling get params on %s, depth %d' % (type(net).__name__, depth))
    allMembers = net.__dir__()
    thisList = []
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submoduleID, layer in net.named_children():
            if type(net.get_submodule(submoduleID)) is PB.pb_neuron_layer:
                #print('sub list is one so converting')
                for param in net.get_submodule(submoduleID).parameters():
                    if(param.requires_grad):
                        thisList = thisList + [param]
                #print(thisList)

            else:
                #print('sub list not one so continuing')
                thisList = thisList + getPBModuleParams(net.get_submodule(submoduleID), depth + 1)            
    else:
        for member in allMembers:
            if(getattr(net,member,None) == net):
                continue  
            #if(type(net).__name__ == 'ConvModule'):
                #pdb.set_trace()
            if type(getattr(net,member,None)) is PB.pb_neuron_layer:
                #print('sub is one so converting')
                for param in getattr(net,member).parameters():
                    if(param.requires_grad):
                        thisList = thisList + [param]
                #print(thisList)            
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                thisList = thisList + getPBModuleParams(getattr(net,member), depth+1)
            #else:
                #print('not calling convert on %s depth %d' % (member, depth))            
            
    #print('finish depth %d' % depth)
    #print(thisList)
    return thisList



def getPBNetworkParams(net):
    paramList = getPBModuleParams(net, 0)
    #pdb.set_trace()
    return paramList


def replacePredefinedModules(startModule,  pretrainedPB):
    index = PBG.modulesToReplace.index(type(startModule))
    return PBG.replacementModules[index](startModule)

def getPretrainedPBAttr(pretrainedPB, member):
    if(pretrainedPB is None):
        return None
    else:
        return getattr(pretrainedPB,member)

def getPretrainedPBVar(pretrainedPB, submoduleID):
    if(pretrainedPB is None):
        return None
    else:
        return pretrainedPB.get_submodule(submoduleID)


def convertModule(net,  pretrainedPB, depth, nameSoFar, convertedList, convertedNamesList):
    if(PBG.verbose):
        print('calling convert on %s depth %d' % (net, depth))
        print('calling convert on %s: %s, depth %d' % (nameSoFar, type(net).__name__, depth))
    if((type(net) is PB.pb_neuron_layer)
       or type(net) is PB.tracked_neuron_layer):
        if(PBG.verbose):
            print('This is only being called because something in your model is pointed to twice by two different variables.  Highest thing on the list is one of the duplicates')
        return net
    allMembers = net.__dir__()
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList):
        for submoduleID, layer in net.named_children():
            subName = nameSoFar + '.' + str(submoduleID)
            if(subName in PBG.moduleIDsToTrack):
                if(PBG.verbose):
                    print('Seq sub is in track IDs: %s' % subName)
                setattr(net,submoduleID,PB.tracked_neuron_layer(net.get_submodule(submoduleID), subName))
                continue
            if type(net.get_submodule(submoduleID)) in PBG.modulesToReplace:
                if(PBG.verbose):
                    print('Seq sub is in replacement module so replaceing: %s' % subName)
                setattr(net,submoduleID,replacePredefinedModules(net.get_submodule(submoduleID),  getPretrainedPBVar(pretrainedPB, submoduleID)))
            if ((type(net.get_submodule(submoduleID)) in PBG.modulesToTrack)
                or
                (type(net.get_submodule(submoduleID)).__name__ in PBG.moduleNamesToTrack)
                or (subName in PBG.moduleIDsToTrack)):
                if(PBG.verbose):
                    print('Seq sub is in tracking list so initing tracked for: %s' % subName)
                setattr(net,submoduleID,PB.tracked_neuron_layer(net.get_submodule(submoduleID),subName))
            elif (type(net.get_submodule(submoduleID)) in PBG.modulesToConvert
                or
                type(net.get_submodule(submoduleID)).__name__ in PBG.moduleNamesToConvert):
                if(PBG.verbose):
                    print('Seq sub is in conversion list so initing PB for: %s' % subName)
                if(issubclass(type(net.get_submodule(submoduleID)), torch.nn.modules.batchnorm._BatchNorm) or issubclass(type(net.get_submodule(submoduleID)), torch.nn.modules.instancenorm._InstanceNorm) or
                issubclass(type(net.get_submodule(submoduleID)), torch.nn.modules.normalization.LayerNorm)):
                #and PBG.internalBatchNorm:
                    print('You have an unwrapped normalizaiton layer, this is not reccomended: ' + nameSoFar)
                    pdb.set_trace()    
                setattr(net,submoduleID,PB.pb_neuron_layer(net.get_submodule(submoduleID), subName, pretrainedPB=getPretrainedPBVar(pretrainedPB, submoduleID)))
            else:
                if(net != net.get_submodule(submoduleID)):
                    convertedList += [id(net.get_submodule(submoduleID))]
                    convertedNamesList += [subName]
                    setattr(net,submoduleID,convertModule(net.get_submodule(submoduleID),  getPretrainedPBVar(pretrainedPB, submoduleID), depth + 1, subName, convertedList, convertedNamesList))
                #else:
                    #print('%s is a self pointer so skipping' % (nameSoFar + '[' + str(submoduleID) + ']'))
    elif(type(net) in PBG.modulestoSkip):
        #print('skipping type for returning from call to: %s' % (nameSoFar)) 
        return net
    else:
        for member in allMembers:
            subName = nameSoFar + '.' + member
            if(subName in PBG.moduleIDsToTrack):
                if(PBG.verbose):
                    print('Seq sub is in track IDs: %s' % subName)
                setattr(net,member,PB.tracked_neuron_layer(getattr(net,member),subName))
                continue
            if(id(getattr(net,member,None)) == id(net)):
                if(PBG.verbose):
                    print('Seq sub is a self pointer: %s' % subName)
                continue
            if(subName in PBG.moduleNamesToNotSave):
                if(PBG.verbose):
                    print('Skipping %s during convert' % subName)
                else:
                    if(subName == '.base_model'):
                        print('By default skipping base_model.  See \"Safetensors Errors\" section of customization.md to include it.')
                continue
            if(id(getattr(net,member,None)) in convertedList):
                print('The following module has a duplicate pointer within your model: %s' % subName)
                print('It is shared with: %s' % convertedNamesList[convertedList.index(id(getattr(net,member,None)))])
                print('One of these must be added to PBG.moduleNamesToNotSave (with the .)')
                sys.exit(0)

            #if(type(net).__name__ == 'ConvModule'):
            # Torch Lightning throws an error when trying to get variables that aren't set yet.  If an error is thrown, just continue.
            try:
                getattr(net,member,None)
            except:
                continue
                
            if type(getattr(net,member,None)) in PBG.modulesToReplace:
                if(PBG.verbose):
                    print('sub is in replacement module so replaceing: %s' % subName)
                setattr(net,member,replacePredefinedModules(getattr(net,member,None),  getPretrainedPBAttr(pretrainedPB, member)))
            if (type(getattr(net,member,None)) in PBG.modulesToTrack
                or
                type(getattr(net,member,None)).__name__ in PBG.moduleNamesToTrack
                or subName in PBG.moduleIDsToTrack):
                if(PBG.verbose):
                    print('sub is in tracking list so initing tracked for: %s' % subName)
                setattr(net,member,PB.tracked_neuron_layer(getattr(net,member),subName))
            elif (type(getattr(net,member,None)) in PBG.modulesToConvert
                or
                type(getattr(net,member,None)).__name__ in PBG.moduleNamesToConvert):
                if(PBG.verbose):
                    print('sub is in conversion list so initing PB for: %s' % subName)
                setattr(net,member,PB.pb_neuron_layer(getattr(net,member),subName, pretrainedPB=getPretrainedPBAttr(pretrainedPB,member)))
            elif issubclass(type(getattr(net,member,None)),nn.Module):
                #pdb.set_trace()
                if(net != getattr(net,member)):
                    convertedList += [id(getattr(net,member))]
                    convertedNamesList += [subName]
                    setattr(net,member,convertModule(getattr(net,member),  getPretrainedPBAttr(pretrainedPB,member), depth+1, subName, convertedList, convertedNamesList))
                #else:
                    #print('%s is a self pointer so skipping' % (subName))

            if (issubclass(type(getattr(net,member,None)), torch.nn.modules.batchnorm._BatchNorm) or issubclass(type(getattr(net,member,None)), torch.nn.modules.instancenorm._InstanceNorm) or
                 issubclass(type(getattr(net,member,None)), torch.nn.modules.normalization.LayerNorm)):
                if(not PBG.unwrappedModulesConfirmed):
                    print('potentially found a batchNorm Layer that wont be convereted2, this is not reccomended: %s' % (subName))
                    print('Set PBG.unwrappedModulesConfirmed to True to skip this next time')
                    print('Type \'net\' + enter to inspect your network and see what the module type containing this layer is.')
                    print('Then do one of the following:')
                    print(' - Add the module type to PBG.moduleNamesToConvert to wrap it entirely')
                    print(' - If the norm layer is part of a sequential wrap it and the previous layer in a PBSequential')
                    print(' - If you do not want to add dendrites to this module add tye type to PBG.moduleNamesToTrack')
                    pdb.set_trace()
            else:
                # don't print private variables with _.  just makes it harder to read
                if(PBG.verbose):
                    if(member[0] != '_' or PBG.extraVerbose == True):
                        print('not calling convert on %s depth %d' % (member, depth))            
    if(PBG.verbose):
        print('returning from call to: %s' % (nameSoFar)) 
    #pdb.set_trace()
    return net


#putting pretrainedNormal, pretrainedPB as a flag here becqause might want to replace modules 
#pretraiend PB is required isntead of just loading in case a system needs to do any specific instantiation stuff
#that PB conflicts with and then convert network needs to be called after that is setup
#update later - i dont understand the above comment.  I think these were added when duplicating the main module rather than just adding it by reference. why would you ever want to load a pretrained PB but then convert something else?
def convertNetwork(net, pretrainedPB = None, layerName=''):

    license_file = './license.yaml'
    status = check_license.valid_license(license_file)

    if not status:
        print("License Invalid. Quiting...")
        sys.exit(1)

    #if youre loading from a pretrained PB make sure to reset the tracker to be this ones, otherwise it will load the other ones 
    #now that we are loading the tracker based on the state buffer it doesn't need to be reinitializd
    #if(not pretrainedPB is None):
        #PBG.reInitPB = True
    if type(net) in PBG.modulesToReplace:
        net = replacePredefinedModules(net,  pretrainedPB)
    if((type(net) in PBG.modulesToConvert) or
        (type(net).__name__ in PBG.moduleNamesToConvert)):
        if(layerName == ''):
            print('converting a single layer without a name, add a layerName param to the call')
            sys.exit(-1)
        net = PB.pb_neuron_layer(net, layerName, pretrainedPB=pretrainedPB)
    else:
        net = convertModule(net,  pretrainedPB, 0, '', [], [])
    #pdb.set_trace()
    missedOnes = []
    trackedOnes = []
    for name, param in net.named_parameters():
        wrapped = 'wrapped' in param.__dir__()
        if(wrapped):
            if(PBG.verbose):
                print('param %s is now wrapped' % (name))
        else:
            tracked = 'tracked' in param.__dir__()
            if(tracked):
                trackedOnes.append(name)
            else:
                missedOnes.append(name)
    if((len(missedOnes) != 0 or len(trackedOnes) != 0) 
       and PBG.unwrappedModulesConfirmed == False):
        print('\n------------------------------------------------------------------')
        print('The following params are not wrapped.\n------------------------------------------------------------------')
        for name in trackedOnes:
            print(name)
        print('\n------------------------------------------------------------------')
        print('The following params are not tracked or wrapped.\n------------------------------------------------------------------')
        for name in missedOnes:
            print(name)
        print('\n------------------------------------------------------------------')
        print('Modules that are not wrapped will not have Dendrites to optimize them')
        print('Modules that are not tracked can cause errors and is NOT reccomended')
        print('Any modules in the second list should be added to moduleNamesToTrack')
        print('Any parameters in the second list can be ignored')
        '''
        Parameters cause a problem with the __getattr__ function.  They also aren't modules, so calling model.param * x for example will cause a problem since its not a forward function.
        '''
        print('------------------------------------------------------------------\nType \'c\' + enter to continue the run to confirm you do not want them to be refined')
        print('Set PBG.unwrappedModulesConfirmed to True to skip this next time')
        print('Type \'net\' + enter to inspect your network and see what the module types of these values are to add them to PGB.moduleNamesToConvert')
        import pdb; pdb.set_trace()
        #TODO: could also print here the type of the missed ones to find what types should be converted
        print('confirmed')
    net.register_buffer('trackerString', torch.tensor([]))
    if(pretrainedPB):
        PBG.pbTracker.resetLayerVector(net,False)
    return net


'''
def stringToTensor(string):
    ords = list(map(ord, string))
    return torch.tensor(ords)
    
def stringFromTensor(stringTensor):
    # Convert tensor to python list.
    ords = stringTensor.tolist()
    # Convert ordinal values to characters and join them into a string.
    return "".join(map(chr, ords))
'''

def stringToTensor(string):
    ords = list(map(ord, string))
    ords = torch.tensor(ords)
    #needs to be over 100 or else when deviding by 100 in stringFromTensor can get div by 0
    increment = torch.randint(low=101, high=32767, size=[1])
    ords = ords * increment
    offset = torch.randint(low=0, high=99, size=[1])
    ords = torch.cat((ords, increment*100+offset))
    return ords
    
def stringFromTensor(stringTensor):
    # Convert tensor to python list.
    ords = stringTensor.tolist()
    increment = int(ords[-1]/100)
    ords = (torch.tensor(ords[:-1])/increment).int()
    toReturn = ''
    while(len(ords) != 0):
        remainingOrds = ords[100000:]
        ords = ords[:100000]
        toAppend = ''.join(map(chr, ords))
        toReturn = toReturn + toAppend
        ords = remainingOrds
    # Convert ordinal values to characters and join them into a string.
    return toReturn

def saveSystem(net, folder, name):
    if(PBG.verbose):
        print('saving system %s' % name)
    temp = stringToTensor(PBG.pbTracker.toString())
    if hasattr(net, 'trackerString'):
        net.trackerString = stringToTensor(PBG.pbTracker.toString()).to(next(net.parameters()).device)
    else:
        net.register_buffer('trackerString', stringToTensor(PBG.pbTracker.toString()).to(next(net.parameters()).device))
    oldList = PBG.pbTracker.PBNeuronLayerVector
    PBG.pbTracker.PBNeuronLayerVector = []
    saveNet(net, folder, name)
    PBG.pbTracker.PBNeuronLayerVector = oldList
    #also save a cleaned copy at every point
    paiSaveSystem(net, folder, name)

def loadSystem(net, folder, name, loadFromRestart = False, switchCall=False, loadFromManualSave=False):
    if(PBG.verbose):
        print('loading system %s' % name)
    net = loadNet(net, folder,name)
    PBG.pbTracker.resetLayerVector(net,loadFromRestart)

    PBG.pbTracker.fromString(stringFromTensor(net.trackerString))
    #always reset the timer, this should get rid of those epochs that take crazy long becuse they are using an old time
    PBG.pbTracker.savedTime = time.time()
    
    PBG.pbTracker.loaded=True
    #always reset this to 0 so networks will know if they are continuing to improve. dont need to reset running accuracy for this and dont 
    PBG.pbTracker.memberVars['currentBestValidationScore'] = 0
    PBG.pbTracker.memberVars['epochLastImproved'] = PBG.pbTracker.memberVars['numEpochsRun']
    if(PBG.verbose):
        print('after loading epoch last improved is %d mode is %c' % (PBG.pbTracker.memberVars['epochLastImproved'], PBG.pbTracker.memberVars['mode']))
    # Saves take place before the final call to start Epoch
    # so when loading from that point must start with a startEpoch
    # unless there was a manual save outside of the add validation score functions
    if (not switchCall) and (not loadFromManualSave):
        PBG.pbTracker.startEpoch(internalCall=True)
    return net

    
def saveNet(net, folder, name):
    #if running a DDP only save with first thread
    if('RANK' in os.environ):
        if(int(os.environ["RANK"]) != 0):
            return
    #if(not dontSaveLocally or (not (folder[:5] == '/tmp/'))):
        #print('saving extra things function is for internal use only')
        #sys.exit()
    #print('calling save: %s' % name)
    #PBG.pbTracker.archiveLayer()
    if not os.path.isdir(folder):
        os.makedirs(folder)
    save_point = folder + '/'
    if not os.path.isdir(save_point):
        os.mkdir(save_point)
    #net.pbTracker = PBG.pbTracker
    for param in net.parameters(): param.data = param.data.contiguous()
    if(PBG.usingSafeTensors):
        save_file(net.state_dict(), save_point + name + '.pt')
    else:
        torch.save(net, save_point + name + '.pt')
    #this is needed because archive taggers deletes everything because tagger objects cant be pickled




#add a flag to ignore all warnings
def addFutureWarning():
    warnings.filters.insert(0,('ignore', None, Warning, None, 0))

#delete the warning we just set
def removeFutureWarning():
    del warnings.filters[0]
    
    


def loadNet(net, folder, name):
    save_point = folder + '/'
    if(PBG.usingSafeTensors):
        stateDict = load_file(save_point + name + '.pt')
    else:
        addFutureWarning()
        #Different versions of torch require this change
        try:
            stateDict = torch.load(save_point + name + '.pt', map_location=torch.device('cpu'), weights_only=False).state_dict()
        except:
            stateDict = torch.load(save_point + name + '.pt', map_location=torch.device('cpu')).state_dict()
        removeFutureWarning()
    return loadNetFromDict(net, stateDict)
    
def loadNetFromDict(net, stateDict):
    pbModules = getPBModules(net,0)
    if(pbModules == []):
        print('PAI loadNet and loadSystem uses a state_dict so it must be called with a net after convertNetwork has been called')
        sys.exit()
    for module in pbModules:
        #Set up name to be what will be saved in the state dict
        moduleName = module.name
        #this should always be true
        if moduleName[0] == '.':
            #strip "."
            moduleName = moduleName[1:]
        # if it was a dataparallel it will also have a module at the start
        if moduleName[:6] == 'module':
            #strip the "module."
            moduleName = moduleName[7:]
        # if there were no cycles then assume the arrays need to be initialized
        #if module.pb.numCycles == 0:
        module.clearDendrites()
        for tracker in module.pb.pbValues:
            try:
                tracker.setupArrays(len(stateDict[moduleName + '.pb.pbValues.0.topPBCandidateAverage']))
            except Exception as e:
                print(e)
                print('When missing this value it typically means you converted a module but didn\'t actually use it in your forward and backward pass')
                print('module was: %s' % moduleName)
                print('check your model definition and forward function and ensure this module is being used properly')
                print('or add it to PBG.moduleIDsToTrack to leave it out of conversion')
                print('This can also occur if you are only fine tuning some of the network, just add the modules that are being fine tuned.')
                print('Additionally this can happen if you adjusted your model definition after calling intitializePB')
                print('for example with torch.compile.  If the module name printed above does not contain all modules leading to the main definition')
                print('this is likely the case for your problem. Fix by calling initializePB after all other model initialization steps')
                
                import pdb; pdb.set_trace()
                
        #then also perform as many cycles as the state dict has
        numCycles = int(stateDict[moduleName + '.pb.numCycles'].item())
        if(numCycles > 0):
            simulateCycles(module, numCycles, doingPB = True)    
    #net.classifier.classifier[0].pb.pbValues[0].thisNodeIndex
    if hasattr(net, 'trackerString'):
        net.trackerString = stateDict['trackerString']
    else:
        net.register_buffer('trackerString', stateDict['trackerString'])
    net.load_state_dict(stateDict)
    net.to(PBG.device)
    return net


def paiSaveSystem(net, folder, name):
    #print('saving system %s' % name)
    net.memberVars = {}
    for memberVar in PBG.pbTracker.memberVars:
        if memberVar == 'schedulerInstance' or memberVar == 'optimizerInstance':
            continue
        net.memberVars[memberVar] = PBG.pbTracker.memberVars[memberVar]
    paiSaveNet(net, folder, name)

def deepCopyPAI(net):
    PBG.pbTracker.clearAllProcessors()
    return copy.deepcopy(net)

#This returns a clean version of the network for parameter counting and inference
def cleanNet(net):
    net2 = BPB.blockwiseNetwork(net)
    net2 = deepCopyPAI(net2)
    net2 = CL.refreshNet(net2)
    return net2

def paiSaveNet(net, folder, name):
    #if running a DDP only save with first thread
    if('RANK' in os.environ):
        if(int(os.environ["RANK"]) != 0):
            return

    #print('calling save: %s' % name)
    #PBG.pbTracker.archiveLayer()
    #These deep copys are required or the real model will also have its layers replaced
    net = deepCopyPAI(net)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    save_point = folder + '/'
    if not os.path.isdir(save_point):
        os.mkdir(save_point)
    net = BPB.blockwiseNetwork(net)
    net = deepCopyPAI(net)
    net = CL.refreshNet(net)
    #for _pai versions trackerString is not needed
    del net.trackerString
    for param in net.parameters(): param.data = param.data.contiguous()

    if(PBG.usingSafeTensors):
        save_file(net.state_dict(), save_point + name + '_pai.pt')
    else:
        torch.save(net, save_point + name + '_pai.pt')


def simulateCycles(module, numCycles, doingPB):
    checkSkipped = PBG.checkedSkippedLayers
    if(doingPB == False):
        return
    PBG.checkedSkippedLayers = True
    mode = 'n'
    for i in range(numCycles):
        if(mode == 'n'):
            module.setMode('p')
            module.addPBLayer()
            mode = 'p'
        else:
            module.setMode('n')
            mode = 'n'
    PBG.checkedSkippedLayers = checkSkipped

def countParams(net):
    if(not PBG.countTrainingParams):
        net = deepCopyPAI(net)
        cleaned = cleanNet(net)
    parameters = list(cleaned.parameters())
    unique_params = {p.data_ptr(): p for p in parameters}.values()
    return sum(p.numel() for p in unique_params)
    
def changeLearningModes(net, folder, name, doingPB):    
    if(doingPB == False):
        #do keep track of times it switched here so other things work out
        #this is so that if you set doingPB to be false it still does learning rate restart
        PBG.pbTracker.memberVars['switchEpochs'].append(PBG.pbTracker.memberVars['numEpochsRun'])
        PBG.pbTracker.memberVars['lastSwitch'] = PBG.pbTracker.memberVars['switchEpochs'][-1]
        PBG.pbTracker.resetValsForScoreReset()
        return net
    if(PBG.pbTracker.memberVars['mode'] == 'n'):
        currentEpoch = PBG.pbTracker.memberVars['numEpochsRun']
        overWrittenEpochs = PBG.pbTracker.memberVars['overWrittenEpochs']
        overWrittenExtra = PBG.pbTracker.memberVars['extraScores']
        if(PBG.drawingPB):
            overWrittenVal = PBG.pbTracker.memberVars['accuracies']
        else:
            overWrittenVal = PBG.pbTracker.memberVars['nAccuracies']
        #preloadPBs = PBG.pbTracker.memberVars['numPBNeuronLayers']
        '''
        The only reason that retainAllPB should ever be used is to test GPU memory and 
        configuration.  So just dont load the best system which will be the previous best 
        if this didn't improve things
        '''
        if(not PBG.retainAllPB):
            if(not PBG.silent):
                print('Importing best Model for switch to PB...')
            net = loadSystem(net, folder, name, switchCall=True)
        else:
            if(not PBG.silent):
                print('Not importing new model since retaining all PB')
        PBG.pbTracker.setPBTraining()        
        PBG.pbTracker.memberVars['overWrittenEpochs'] = overWrittenEpochs
        PBG.pbTracker.memberVars['overWrittenEpochs'] += currentEpoch - PBG.pbTracker.memberVars['numEpochsRun']
        PBG.pbTracker.memberVars['totalEpochsRun'] = PBG.pbTracker.memberVars['numEpochsRun'] + PBG.pbTracker.memberVars['overWrittenEpochs']
        
        if(PBG.saveOldGraphScores):
            PBG.pbTracker.memberVars['overWrittenExtras'].append(overWrittenExtra)
            PBG.pbTracker.memberVars['overWrittenVals'].append(overWrittenVal)
        else:
            PBG.pbTracker.memberVars['overWrittenExtras'] = [overWrittenExtra]
            PBG.pbTracker.memberVars['overWrittenVals'] = [overWrittenVal]
        if(PBG.drawingPB):
            PBG.pbTracker.memberVars['nswitchEpochs'].append(PBG.pbTracker.memberVars['numEpochsRun'])
        else:
            #append the last switch minus the length of this epoch set
            if(len(PBG.pbTracker.memberVars['switchEpochs']) == 0):
                #add the first switch
                PBG.pbTracker.memberVars['nswitchEpochs'].append(PBG.pbTracker.memberVars['numEpochsRun'])
            else:
                #lastImprovedPoint = (len(self.memberVars['nAccuracies'])-1) - (self.memberVars['numEpochsRun']-self.memberVars['numEpochsRun'])
                PBG.pbTracker.memberVars['nswitchEpochs'].append(PBG.pbTracker.memberVars['nswitchEpochs'][-1] + ((PBG.pbTracker.memberVars['numEpochsRun'])-(PBG.pbTracker.memberVars['switchEpochs'][-1])))
            
        PBG.pbTracker.memberVars['switchEpochs'].append(PBG.pbTracker.memberVars['numEpochsRun'])
        PBG.pbTracker.memberVars['lastSwitch'] = PBG.pbTracker.memberVars['switchEpochs'][-1]
    else:
        if(not PBG.silent):
            print('Switching back to N...')
        setBest = PBG.pbTracker.memberVars['currentNSetGlobalBest']
        PBG.pbTracker.setNormalTraining()
        #append the last switch minus the length of this epoch set
        if(len(PBG.pbTracker.memberVars['pswitchEpochs']) == 0):
            #need to account for the first one starting at 0
            PBG.pbTracker.memberVars['pswitchEpochs'].append(((PBG.pbTracker.memberVars['numEpochsRun']-1)-(PBG.pbTracker.memberVars['switchEpochs'][-1])))
        else:
            PBG.pbTracker.memberVars['pswitchEpochs'].append(PBG.pbTracker.memberVars['pswitchEpochs'][-1] + ((PBG.pbTracker.memberVars['numEpochsRun'])-(PBG.pbTracker.memberVars['switchEpochs'][-1])))
        PBG.pbTracker.memberVars['switchEpochs'].append(PBG.pbTracker.memberVars['numEpochsRun'])
        PBG.pbTracker.memberVars['lastSwitch'] = PBG.pbTracker.memberVars['switchEpochs'][-1]
        #if want to retain all PB or learning PBLive and this last one did in fact improve global score
        if(PBG.retainAllPB or (PBG.learnPBLive and setBest)):
            if(not PBG.silent):
                print('Saving model before starting normal training to retain PBNodes regardless of next N Phase results')
            saveSystem(net, folder, name)
        #if its just doing P for learn PB live then switch back immdetealy
        if(PBG.noExtraNModes):
            net = changeLearningModes(net, folder, name, doingPB)
            
    PBG.pbTracker.memberVars['paramCounts'].append(countParams(net))
    
    return net



