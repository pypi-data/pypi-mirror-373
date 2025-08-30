from perforatedai import pb_globals as PBG
from perforatedai import pb_layer as PB
from perforatedai import pb_models as PBM
from perforatedai import pb_utils as PBU
from perforatedai import pb_neuron_layer_tracker as PBT

from safetensors.torch import load_file
import copy

import torch.nn as nn
import torch
import pdb


'''
import pb_layer as PB
import pb_utils as PBU
import cleanPB as CPB

net = PBU.loadSystem('sigmoidLinear', 'system') 
net = CPB.obfusicateNetwork(net)

import torch
torch.save(net, 'temp/temp.pt')

import cleanLoad as CL
import torch

net = torch.load('temp/temp.pt')
net = CL.refreshNet(net)

import torch
net.forward(torch.ones(128,1,29,29).to('cuda'))




import pb_layer as PB
import pb_utils as PBU
import cleanPB as CPB
from transformers.models.wav2vec2.modeling_wav2vec2 import *

net = PBU.loadSystem('temp', 'system')    
net = CPB.obfusicateNetwork(net)
import torch
torch.save(net, 'temp/temp.pt')

import cleanLoad as CL
import torch

net = torch.loadB('temp/temp.pt')
net = CL.refreshNet(net)

import torch
net.forward(torch.ones(8,16000).to('cuda'))
'''

#function to convert layers which had to be customized back into their original form. eg Wav2Vec2Projector back to just using a regular projector and not wprojector

#from now on when creating a module to replace, also need to make a backward replacement function to put things back.

from threading import Thread


doingThreading = False
loadedFullPrint = False

class PAIModulePyThread(nn.Module):
    def __init__(self, originalModule):
        super(PAIModulePyThread, self).__init__()
        self.layerArray = originalModule.layerArray
        self.processorArray = originalModule.processorArray
        self.skipWeights = originalModule.skipWeights
        self.register_buffer('nodeIndex', originalModule.nodeIndex.clone().detach())
        self.register_buffer('moduleID', originalModule.moduleID.clone().detach())
        self.register_buffer('numCycles', originalModule.numCycles)
        self.register_buffer('viewTuple', originalModule.viewTuple)

    #this was to hide that modules are wrapped but now thats part of instructions
    '''
    def __str__(self):
        if(loadedFullPrint):
            totalString = 'PAILayer(\n\t'
            totalString += self.layerArray[-1].__str__().replace('\n','\n\t')
            totalString += '\n)'
        else:
            totalString = 'PAILayer('
            totalString += self.layerArray[-1].__class__.__name__
            totalString += ')'
        return totalString
    def __repr__(self):
        return self.__str__()
    '''
    def processAndForward(self, *args2, **kwargs2):
        c = args2[0]
        pbOuts = args2[1]
        args2 = args2[2:]
        if(self.processorArray[c] != None):
            args2, kwargs2 = self.processorArray[c].pre(*args2, **kwargs2)
        outValues = self.layerArray[c](*args2, **kwargs2)
        if(self.processorArray[c] != None):
            out = self.processorArray[c].post(outValues)
        else:
            out = outValues
        pbOuts[c] = out
    
    def processAndPre(self, *args, **kwargs):
        pbOuts = args[0]
        args = args[1:]
        out = self.layerArray[-1].forward(*args, **kwargs)
        if not self.processorArray[-1] is None:
            out = self.processorArray[-1].pre(out)
        pbOuts[len(self.layerArray)-1] = out
        
    def forward(self, *args, **kwargs):
        #this is currently false anyway, just remove the doing multi idea
        doingMulti = doingThreading
        pbOuts = [None] * len(self.layerArray)
        threads = {}
        for c in range(0,len(self.layerArray)-1):
            args2, kwargs2 = args, kwargs
            if(doingMulti):
                threads[c] = Thread(target=self.processAndForward, args=(c, pbOuts, *args), kwargs=kwargs)
            else:
                self.processAndForward(c, pbOuts, *args2, **kwargs2)
        if(doingMulti):
            threads[len(self.layerArray)-1] = Thread(target=self.processAndPre, args=(pbOuts, *args), kwargs=kwargs)
        else:
            self.processAndPre(pbOuts, *args, **kwargs)
        if(doingMulti):
            for i in range(len(pbOuts)):
                threads[i].start()
            for i in range(len(pbOuts)):
                threads[i].join()
        for outIndex in range(0,len(self.layerArray)):
            currentOut = pbOuts[outIndex]
            if(len(self.layerArray) > 1):
                for inIndex in range(0,outIndex):
                    currentOut += self.skipWeights[outIndex][inIndex,:].view(self.viewTuple.tolist()).to(currentOut.device) * pbOuts[inIndex]    
                if(outIndex < len(self.layerArray)-1):
                    currentOut = PBG.PBForwardFunction(currentOut)
            pbOuts[outIndex] = currentOut
        if not self.processorArray[-1] is None:
            currentOut = self.processorArray[-1].post(currentOut)
        return currentOut

'''
class PAIModule_jit_thread(nn.Module):
    def __init__(self, originalModule):
        super(PAIModule_jit_thread, self).__init__()
        self.layerArray = nn.Sequential(*(originalModule.layerArray))
        self.processorArray = originalModule.processorArray
        self.skipWeights = originalModule.skipWeights
        self.nodeIndex = originalModule.nodeIndex
        self.viewTuple = []

    def processAndForward(self, args2):
        c = args2[0]
        args2 = args2[1:]
        if(self.processorArray[c][1] != None):
            args2, kwargs2 = self.processorArray[c][1].pre(args2)
        outValues = self.layerArray[c](args2)
        if(self.processorArray[c][2] != None):
            out = self.processorArray[c][2].post(outValues)
        else:
            out = outValues
        return out
    
    def processAndPre(self, args):
        out = self.layerArray[-1].forward(args)
        if not self.processorArray[-1][0] is None:
            out = self.processorArray[-1][0].pre(out)
        return out
    def forward(self, args):
        doingMulti = True
        pbOuts = {}            
        for c in range(0,len(self.layerArray)-1):
            args2 = args, 
            if(doingMulti):
                pbOuts[c] = torch.jit._fork(self.processAndForward, c, args)
            else:
                pbOuts[c] = self.processAndForward(c, args2)
        if(doingMulti):
            pbOuts[len(self.layerArray)-1] = torch.jit._fork(self.processAndPre, args)
        else:
            pbOuts[len(self.layerArray)-1] = self.processAndPre(args)
        if(doingMulti):
            for i in range(len(pbOuts)):
                pbOuts[i] = torch.jit._wait(pbOuts[i])
        for outIndex in range(0,len(self.layerArray)):
            currentOut = pbOuts[outIndex]
            if(self.viewTuple == []):
                for dim in range(len(currentOut.shape)):
                    if dim == self.nodeIndex:
                        self.viewTuple.append(-1)
                        continue
                    self.viewTuple.append(1)
            if(len(self.layerArray) > 1):
                for inIndex in range(0,outIndex):
                    currentOut += self.skipWeights[outIndex][inIndex,:].view(self.viewTuple).to(currentOut.device) * pbOuts[inIndex]    
                if(outIndex < len(self.layerArray)-1):
                    currentOut = PBG.PBForwardFunction(currentOut)
            pbOuts[outIndex] = currentOut
        if not self.processorArray[-1][3] is None:
            currentOut = self.processorArray[-1][3].post(currentOut)
        return currentOut

    
class PAIModule_jit_thread2(nn.Module):
    def __init__(self, originalModule):
        super(PAIModule_jit_thread2, self).__init__()
        self.layerArray = originalModule.layerArray
        self.processorArray = originalModule.processorArray
        self.skipWeights = originalModule.skipWeights
        self.nodeIndex = originalModule.nodeIndex
        self.viewTuple = []

    def processAndForward(self, *args2, **kwargs2):
        c = args2[0]
        args2 = args2[1:]
        if(self.processorArray[c][1] != None):
            args2, kwargs2 = self.processorArray[c][1].pre(*args2, **kwargs2)
        outValues = self.layerArray[c](*args2, **kwargs2)
        if(self.processorArray[c][2] != None):
            out = self.processorArray[c][2].post(outValues)
        else:
            out = outValues
        return out
    
    def processAndPre(self, *args, **kwargs):
        out = self.layerArray[-1].forward(*args, **kwargs)
        if not self.processorArray[-1][0] is None:
            out = self.processorArray[-1][0].pre(out)
        return out
    def forward(self, *args, **kwargs):
        doingMulti = True
        pbOuts = {}            
        for c in range(0,len(self.layerArray)-1):
            args2, kwargs2 = args, kwargs
            if(doingMulti):
                pbOuts[c] = torch.jit._fork(self.processAndForward, c, *args, **kwargs)
            else:
                pbOuts[c] = self.processAndForward(c, *args2, **kwargs2)
        if(doingMulti):
            pbOuts[len(self.layerArray)-1] = torch.jit._fork(self.processAndPre, *args, **kwargs)
        else:
            pbOuts[len(self.layerArray)-1] = self.processAndPre(*args, **kwargs)
        if(doingMulti):
            for i in range(len(pbOuts)):
                pbOuts[i] = torch.jit._wait(pbOuts[i])
        for outIndex in range(0,len(self.layerArray)):
            currentOut = pbOuts[outIndex]
            if(self.viewTuple == []):
                for dim in range(len(currentOut.shape)):
                    if dim == self.nodeIndex:
                        self.viewTuple.append(-1)
                        continue
                    self.viewTuple.append(1)
            if(len(self.layerArray) > 1):
                for inIndex in range(0,outIndex):
                    currentOut += self.skipWeights[outIndex][inIndex,:].view(self.viewTuple).to(currentOut.device) * pbOuts[inIndex]    
                if(outIndex < len(self.layerArray)-1):
                    currentOut = PBG.PBForwardFunction(currentOut)
            pbOuts[outIndex] = currentOut
        if not self.processorArray[-1][3] is None:
            currentOut = self.processorArray[-1][3].post(currentOut)
        return currentOut
'''
'''
class PAIModule2(nn.Module):
    def __init__(self, originalModule):
        super(PAIModule2, self).__init__()
        self.layerArray = originalModule.layerArray
        self.processorArray = originalModule.processorArray
        self.votingLayers = originalModule.votingLayers
    def processAndForward(*args2, **kwargs2):
        if(self.processorArray[c][1] != None):
            args2, kwargs2 = self.processorArray[c][1].pre(*args2, **kwargs2)
        outValues = self.layerArray[c](*args2, **kwargs2)
        if(self.processorArray[c][2] != None):
            outs = self.processorArray[c][2].post(outValues)
        else:
            outs = outValues
        return outs
    def forward(self, *args, **kwargs):
        pbOuts = {}            
        for c in range(0,len(self.layerArray)-1):
            args2, kwargs2 = args, kwargs
            pbOuts[c] = self.processAndForward(c, *args2, **kwargs2)
        out = self.layerArray[-1](*args, **kwargs)
        if not self.processorArray[-1][0] is None:
            out = self.processorArray[-1][0].pre(out)
        pbOuts[len(self.layerArray)-1] = out
        for outIndex in range(0,len(self.layerArray)):
            currentOut = pbOuts[outIndex]
            if(len(self.layerArray) > 1):
                for inIndex in range(0,outIndex):
                    currentOut += self.votingLayers[outIndex][inIndex](pbOuts[inIndex])
                if(outIndex < len(self.layerArray)-1):
                    currentOut = PBG.PBForwardFunction(currentOut)
            pbOuts[outIndex] = currentOut
        if not self.processorArray[-1][3] is None:
            currentOut = self.processorArray[-1][3].post(currentOut)
        return currentOut
'''
'''
class PAIModuleOld(nn.Module):
    def __init__(self, originalModule):
        super(PAIModuleOld, self).__init__()
        self.layerArray = originalModule.layerArray
        self.processorArray = originalModule.processorArray
        self.votingLayers = originalModule.votingLayers
        
    def forward(self, *args, **kwargs):
        #pdb.set_trace()
        pbOuts = {}            
        for c in range(0,len(self.layerArray)-1):
            args2, kwargs2 = args, kwargs
            if(self.processorArray[c][1] != None):
                args2, kwargs2 = self.processorArray[c][1].pre(*args2, **kwargs2)
            outValues = self.layerArray[c](*args2, **kwargs2)
            if(self.processorArray[c][2] != None):
                pbOuts[c] = self.processorArray[c][2].post(outValues)
            else:
                pbOuts[c] = outValues
        try:
            out = self.layerArray[-1](*args, **kwargs)
        except:
            pdb.set_trace()
        if not self.processorArray[-1][0] is None:
            out = self.processorArray[-1][0].pre(out)
        pbOuts[len(self.layerArray)-1] = out
        for outIndex in range(0,len(self.layerArray)):
            currentOut = pbOuts[outIndex]
            if(len(self.layerArray) > 1):
                for inIndex in range(0,outIndex):
                    currentOut += self.votingLayers[outIndex][inIndex](pbOuts[inIndex])
                if(outIndex < len(self.layerArray)-1):
                    currentOut = PBG.PBForwardFunction(currentOut)
            pbOuts[outIndex] = currentOut
        if not self.processorArray[-1][3] is None:
            currentOut = self.processorArray[-1][3].post(currentOut)
        return currentOut
'''
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


'''
This is to set if want to try doing threading or not
'''

ModuleType = PAIModulePyThread
doingThreading = False

def makeModule(module):
    #if(ModuleType is PAIModule_jit_thread):
        #torch.jit.script(ModuleType(module))
    #else:
    return ModuleType(module)

def refreshPAI(net, depth, nameSoFar, convertedList):
    if(PBG.verbose):
        print('CL calling convert on %s depth %d' % (net, depth))
        print('CL calling convert on %s: %s, depth %d' % (nameSoFar, type(net).__name__, depth))
    if(type(net) is ModuleType):
        if(PBG.verbose):
            print('this is only being called because something in your model is pointed to twice by two different variables.  Highest thing on the list is one of the duplicates')
        return net
    allMembers = net.__dir__()
    if issubclass(type(net),nn.Sequential) or issubclass(type(net),nn.ModuleList) or issubclass(type(net),list):
        for submoduleID, layer in net.named_children():
            if(net != net.get_submodule(submoduleID)):
                convertedList += [ nameSoFar + '[' + str(submoduleID) + ']']
                setattr(net,submoduleID,refreshPAI(net.get_submodule(submoduleID), depth + 1, nameSoFar + '[' + str(submoduleID) + ']', convertedList))
            #else:
                #print('%s is a self pointer so skipping' % (nameSoFar + '[' + str(submoduleID) + ']'))
            if (type(net.get_submodule(submoduleID)).__name__ == 'PAILayer'):
                #print('Seq sub is in conversion list so initing PB for: %s' % nameSoFar + '[' + str(submoduleID) + ']')
                setattr(net,submoduleID,makeModule(getPretrainedPBVar(net, submoduleID)))
    elif(type(net) in PBG.modulestoSkip):
        #print('skipping type for returning from call to: %s' % (nameSoFar)) 
        return net
    else:
        for member in allMembers:
            subName = nameSoFar + '.' + member

            if(member == 'device' or member == 'dtype'):
                continue
            if(subName in PBG.moduleNamesToNotSave):
                continue
            if(nameSoFar == ''):
                if(subName in PBG.moduleNamesToNotSave
                    or subName in convertedList):
                    if(PBG.verbose):
                        print('Skipping %s during save' % subName)
                    continue
           
            
            if issubclass(type(getattr(net,member,None)),nn.Module) or member == 'layerArray':
                convertedList += [subName]
                #pdb.set_trace()
                if(net != getattr(net,member)):
                    setattr(net,member,refreshPAI(getattr(net,member), depth+1, subName, convertedList))
                #else:
                    #print('%s is a self pointer so skipping' % (nameSoFar + '.' + member))
            if (type(getattr(net,member,None)).__name__ == 'PAILayer'):
                #print('sub is in conversion list so initing PB for: %s' % nameSoFar + '.' + member)
                setattr(net,member,makeModule(getPretrainedPBAttr(net,member)))            
    #print('returning from call to: %s' % (nameSoFar)) 
    if (type(net).__name__ == 'PAILayer'):
        net = makeModule(net)
    #pdb.set_trace()
    return net


#putting pretrainedNormal, pretrainedPB as a flag here becqause might want to replace modules 
#pretraiend PB is required isntead of just loading in case a system needs to do any specific instantiation stuff
#that PB conflicts with and then convert network needs to be called after that is setup
def refreshNet(pretrainedPB):

    net = refreshPAI(pretrainedPB, 0, '', [])
    #del net.trackerString
    return net
