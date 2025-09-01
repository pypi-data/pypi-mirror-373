from timeit import default_timer as timer #used to time the command's execution time.
import csv
from math import inf

class BenchmarkEntry:
    def __init__(self):
        self.n = 0
        #self.samples = []
        self.min = inf;
        self.max = -inf;
        self.avg = 0.0;
        
        self.innerMin = inf;
        self.innerMax = -inf;
        self.innerAvg = 0.0;
        
        self.outerMin = inf;
        self.outerMax = -inf;
        self.outerAvg = 0.0;
        
    def AddSample(self,dur,outerDur,innerDur):
        #self.samples.append(sample) #this might be to slow
        self.min = min(self.min,dur)
        self.max = max(self.max,dur)
        self.avg = (self.avg * self.n + dur) / (self.n+1)
        #outer values
        self.outerMin = min(self.outerMin,outerDur)
        self.outerMax = max(self.outerMax,outerDur)
        self.outerAvg = (self.outerAvg * self.n + outerDur) / (self.n+1)
        #inner values
        self.innerMin = min(self.innerMin,innerDur)
        self.innerMax = max(self.innerMax,innerDur)
        self.innerAvg = (self.innerAvg * self.n + innerDur) / (self.n+1)
        #increase samples
        self.n = self.n+1


class Benchmark:
    def __init__(self,maxNesting=1000):
        self.messures = {}
        self.maxNesting = maxNesting
        self.timestamps = [0.0 for i in range(self.maxNesting)] #init array
        self.durations = [0.0 for i in range(self.maxNesting)] #init array
        self.currentNesting = 0
        self.lastNesting = 0
        
    def InitMessure(self,key):
        self.messures[key] = BenchmarkEntry()
        
    def AddSample(self,key,dur,outerDur,innerDur):
        messure = None
        if(key in self.messures):
            messure = self.messures[key]
        else:
            messure = BenchmarkEntry()
            self.messures[key] = messure
        #add the new entry
        messure.AddSample(dur,outerDur,innerDur)
        
    def TimeIt(self):
        return timer()
    
    def Start(self):
        t = self.TimeIt()
        self.lastNesting = self.currentNesting # track the history of start calls
        self.currentNesting += 1
        self.timestamps[self.lastNesting] = t
        self.durations[self.currentNesting] = 0.0 #reset the inner
        return t
        
    def Stop(self,key):
        t = self.TimeIt()
        self.lastNesting = self.currentNesting # track the history of start calls
        self.currentNesting += -1
        b = self.timestamps[self.currentNesting]
        outerDur = t-b
        #store the total inner duration for the next measure at this level, but only, if this is not the lowest level.
        if(self.currentNesting>0):
            self.durations[self.currentNesting] += outerDur 
        innerDur = 0.0
        # consider the inner duration if there where nested benchmark calls.
        if(self.lastNesting>self.currentNesting):
            innerDur = self.durations[self.lastNesting]
        dur = outerDur - innerDur
        self.AddSample(key, dur, outerDur, innerDur)
        return dur
        
    def Validate(self):
        if(self.currentNesting > 0):
            print('BENCHMARK WARNING: expected benchmark nesting to be 0, but got %d. Did you have unequal number of Start() and Stop() calls?'%(self.currentNesting))
    
    def SaveToFile(self,filename):
        self.Validate()
        # open the file in the write mode
        with open(filename, 'w',newline='') as f:
            # create the csv writer
            writer = csv.writer(f,delimiter=';',quotechar ='"',quoting=csv.QUOTE_MINIMAL)
            # write header
            writer.writerow(['key','n','min','max','avg','outerMin','outerMax','outerAvg','innerMin','innerMax','innerAvg'])
            # write measures
            for k,m in self.messures.items():
                writer.writerow([k,m.n,m.min,m.max,m.avg,m.outerMin,m.outerMax,m.outerAvg,m.innerMin,m.innerMax,m.innerAvg])
        
