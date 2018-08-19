import heapq
import random
import numpy
import matplotlib.pyplot as plt

# Parameters
class Params:
    def __init__(self, lambd):
        self.lambd = lambd

# States and statistical counters        
class States:
    def __init__(self):
        
        # States
        self.queue = []

        #extra
        self.berths = [-1 for i in range(2)]
        self.cranes = 2
        self.total_time_in_harbor = 0.0
        self.min_time_in_harbor = 1000000000.0
        self.max_time_in_harbor = 0.0
        self.total_berth1_util = 0.0
        self.total_berth2_util = 0.0
        self.curShipNum = 1
        self.isNowServing = False
        self.isDepartureSchedule = False
        
        # Statistics
        self.berth1_util = 0.0
        self.berth2_util = 0.0
        self.avg_time_in_harbor = 0.0
        self.total_served = 0

    def update(self, sim, event):
        #xtra
        if event.eventType == 'START':
            pass


        #update statistics
        time_since_last_event = float(event.eventTime - sim.simclock)
        #self.totalQLength += float(len(self.queue) * time_since_last_event)


        if sim.states.berths[0] != -1:
            self.total_berth1_util += time_since_last_event
        if sim.states.berths[1] != -1:
            self.total_berth2_util += time_since_last_event





        #print('total harbor time',self.total_time_in_harbor)


    
    def finish(self, sim):
        self.avg_time_in_harbor = float(self.total_time_in_harbor / (1.0 * self.total_served))
        self.berth1_util = float(self.total_berth1_util / sim.simclock)
        self.berth2_util = float(self.total_berth2_util / sim.simclock)
        
    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        #print('MMk Results: lambda = %lf, omega = %lf, k = %d' % (sim.params.lambd, sim.params.omega, sim.params.k))
        print('MG2 Total ships unloaded: %d' % (self.total_served))
        print('MG2 Minimum time ships are in harbor: %lf days' % (self.min_time_in_harbor))
        print('MG2 Maximum time ships are in harbor: %lf days' % (self.max_time_in_harbor))
        print('MG2 Average time ships are in harbor: %lf days' % (self.avg_time_in_harbor))
        print('MG2 Expected utility for berth 1: %lf' % (self.berth1_util))
        print('MG2 Expected utility for berth 2: %lf' % (self.berth2_util))
     
    def getResults(self, sim):
        return (self. avgQlength, self.avgQdelay, self.util)
   
class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None
        
    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')
    
    def __repr__(self):
        return self.eventType

class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim



        
    def process(self, sim):
        #new_arrival_time = -(1.0/sim.params.lambd)*numpy.log(numpy.random.random_sample())
        new_arrival_time = -(1.0 / sim.params.lambd) * numpy.log(sim.randomStream1.random_sample())


        if new_arrival_time <= 90.0:
            sim.scheduleEvent(ArrivalEvent(new_arrival_time, sim, sim.states.curShipNum))
            sim.states.curShipNum += 1

                
class ExitEvent(Event):    
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    
    def process(self, sim):
        None

                                
class ArrivalEvent(Event):
    def __init__(self, eventTime, sim, sNo):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim
        self.shipNo = sNo


    def process(self, sim):




        #---------------#

        arrival_time_of_nextShip = -(1.0 / sim.params.lambd) * numpy.log(sim.randomStream1.random_sample())
        arrival_time_of_nextShip += sim.simclock
        nextShipNo = sim.states.curShipNum
        sim.states.curShipNum += 1
        isNextArrivalScheduled  = False

        if arrival_time_of_nextShip <= 90.0:
            isNextArrivalScheduled = True

        if sim.states.berths[0] != -1 and sim.states.berths[1] != -1:
            sim.states.queue.append([self.eventTime, self.shipNo])
            if isNextArrivalScheduled == True:
                sim.scheduleEvent(ArrivalEvent(arrival_time_of_nextShip, sim, nextShipNo))
        else:
            #if both berths are free
            if sim.states.berths[0] == -1 and sim.states.berths[1] == -1:



                service_time_of_curShip = sim.randomStream2.uniform(0.5, 1.51) / 2.0
                departure_time_of_curShip = service_time_of_curShip + sim.simclock

                #if another ship is arrived before current ship's departure
                if arrival_time_of_nextShip <= departure_time_of_curShip and isNextArrivalScheduled == True:
                    sim.states.berths[0] = 1
                    sim.states.berths[1] = 1

                    #serve cur ship and schedule its departure
                    departure_time_of_curShip = sim.simclock + (arrival_time_of_nextShip - self.eventTime) + (departure_time_of_curShip - arrival_time_of_nextShip) * 2.0
                    total_time_of_curShip_in_harbor = (departure_time_of_curShip - self.eventTime)
                    sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, self.shipNo,0,1))


                    # serve the next ship and schedule its departure
                    print(arrival_time_of_nextShip, 'Event', 'ARRIVAL_OF_SHIPNO_' + str(nextShipNo))
                    service_time_of_nextShip = sim.randomStream2.uniform(0.5, 1.51)
                    departure_time_of_nextShip = service_time_of_nextShip + arrival_time_of_nextShip
                    total_time_of_nextShip_in_harbor = (departure_time_of_nextShip - sim.simclock)
                    sim.scheduleEvent(DepartureEvent(departure_time_of_nextShip, sim, nextShipNo,1,1))

                    # now update avg,min,max time in harbor
                    sim.states.total_time_in_harbor += total_time_of_curShip_in_harbor
                    sim.states.total_time_in_harbor += total_time_of_nextShip_in_harbor
                    sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                    sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_nextShip_in_harbor))
                    sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))
                    sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_nextShip_in_harbor))



                    #schedule an extra arrival event
                    arrival_time_of_extraShip = -(1.0 / sim.params.lambd) * numpy.log(sim.randomStream1.random_sample())
                    arrival_time_of_extraShip += arrival_time_of_nextShip
                    if arrival_time_of_extraShip <= 90.0:
                        sim.scheduleEvent(ArrivalEvent(arrival_time_of_extraShip, sim, sim.states.curShipNum))
                        sim.states.curShipNum += 1








                else:
                    #schedule arrival time of next ship and calculate for current ship
                    if isNextArrivalScheduled == True :
                        sim.scheduleEvent(ArrivalEvent(arrival_time_of_nextShip, sim, nextShipNo))
                    which = sim.randomStream3.randint(0, 2)
                    sim.states.berths[which] = 1




                    # now update avg,min,max time in harbor
                    total_time_of_curShip_in_harbor = (departure_time_of_curShip - sim.simclock)
                    sim.states.total_time_in_harbor += total_time_of_curShip_in_harbor
                    sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                    sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))

                    sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, self.shipNo,which,2))


            # if berth 1 is free
            elif sim.states.berths[0] == -1:
                service_time_of_curShip = sim.randomStream2.uniform(0.5, 1.51)
                departure_time_of_curShip = service_time_of_curShip + sim.simclock
                if isNextArrivalScheduled == True:
                    sim.scheduleEvent(ArrivalEvent(arrival_time_of_nextShip, sim, nextShipNo))

                sim.states.berths[0] = 1


                # now update avg,min,max time in harbor
                total_time_of_curShip_in_harbor = (departure_time_of_curShip - sim.simclock)
                sim.states.total_time_in_harbor += total_time_of_curShip_in_harbor
                sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))

                sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, self.shipNo,0,1))


            # if berth 2 is free
            else :
                service_time_of_curShip = sim.randomStream2.uniform(0.5, 1.51)
                departure_time_of_curShip = service_time_of_curShip + sim.simclock
                if isNextArrivalScheduled == True:
                    sim.scheduleEvent(ArrivalEvent(arrival_time_of_nextShip, sim, nextShipNo))

                sim.states.berths[1] = 1


                # now update avg,min,max time in harbor
                total_time_of_curShip_in_harbor = (departure_time_of_curShip - sim.simclock)
                sim.states.total_time_in_harbor += total_time_of_curShip_in_harbor
                sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))

                sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, self.shipNo,1,1))



    def __repr__(self):
        s = 'ARRIVAL_OF_SHIPNO_' + str(self.shipNo)
        return s



        
class DepartureEvent(Event):
    def __init__(self, eventTime, sim, sNo, b, c):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim
        self.shipNo = sNo
        self.berth = b
        self.cranes = c

    def process(self, sim):



        sim.states.berths[self.berth] = -1
        sim.states.total_served += 1

        if(len(sim.states.queue) > 0):




            #calculate next departure schedule


            arrival_time_of_curShip,curShipNo = sim.states.queue[0]
            del sim.states.queue[0]
            total_time_of_curShip_in_harbor = sim.simclock - arrival_time_of_curShip


            #if both berths are now free
            if sim.states.berths[0] == -1 and sim.states.berths[1] == -1:

                #if another ship on the queue apart from cuurent ship, schedule it also
                if len(sim.states.queue) > 0:
                    #sim.states.total_time_in_harbor += (sim.simclock - sim.states.queue[0])

                    arrival_time_of_nextShip, nextShipNo = sim.states.queue[0]
                    del sim.states.queue[0]
                    total_time_of_nextShip_in_harbor = sim.simclock - arrival_time_of_nextShip

                    service_time_of_curShip = sim.randomStream2.uniform(0.5, 1.51)
                    departure_time_of_curShip = service_time_of_curShip + sim.simclock
                    service_time_of_nextShip = sim.randomStream2.uniform(0.5, 1.51)
                    departure_time_of_nextShip = service_time_of_nextShip + sim.simclock

                    #serve two ships
                    #use both berths now
                    sim.states.berths[0] = 1
                    sim.states.berths[1] = 1

                    total_time_of_curShip_in_harbor += (departure_time_of_curShip - sim.simclock)
                    total_time_of_nextShip_in_harbor +=  (departure_time_of_nextShip - sim.simclock)

                    #now update avg,min,max time in harbor
                    sim.states.total_time_in_harbor += total_time_of_curShip_in_harbor
                    sim.states.total_time_in_harbor += total_time_of_nextShip_in_harbor
                    sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                    sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_nextShip_in_harbor))
                    sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))
                    sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_nextShip_in_harbor))

                    # ----------#
                    # crane nia kaj korte hobe
                    # ----------#
                    sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, curShipNo,0,1))
                    sim.scheduleEvent(DepartureEvent(departure_time_of_nextShip, sim, nextShipNo,0,1))

                else:
                    service_time_of_curShip = sim.randomStream2.uniform(0.5, 1.51) / 2.0
                    departure_time_of_curShip = service_time_of_curShip + sim.simclock
                    which = sim.randomStream3.randint(0, 2)
                    sim.states.berths[which] = 1


                    # now update avg,min,max time in harbor
                    total_time_of_curShip_in_harbor += (departure_time_of_curShip - sim.simclock)
                    sim.states.total_time_in_harbor +=  total_time_of_curShip_in_harbor
                    sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                    sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))

                    sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, curShipNo,which,2))

            #if berth 1 is now free
            elif sim.states.berths[0] == -1:
                service_time_of_curShip = sim.randomStream2.uniform(0.5, 1.51)
                departure_time_of_curShip = service_time_of_curShip + sim.simclock
                sim.states.berths[0] = 1

                # now update avg,min,max time in harbor
                total_time_of_curShip_in_harbor += (departure_time_of_curShip - sim.simclock)
                sim.states.total_time_in_harbor += total_time_of_curShip_in_harbor
                sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))

                sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, curShipNo, 0, 1))

            #if berth 2 is now free
            else:
                service_time_of_curShip = sim.randomStream2.uniform(0.5, 1.51)
                departure_time_of_curShip = service_time_of_curShip + sim.simclock
                sim.states.berths[1] = 1

                # now update avg,min,max time in harbor
                total_time_of_curShip_in_harbor += (departure_time_of_curShip - sim.simclock)
                sim.states.total_time_in_harbor += total_time_of_curShip_in_harbor
                sim.states.min_time_in_harbor = min(float(sim.states.min_time_in_harbor),float(total_time_of_curShip_in_harbor))
                sim.states.max_time_in_harbor = max(float(sim.states.max_time_in_harbor),float(total_time_of_curShip_in_harbor))

                sim.scheduleEvent(DepartureEvent(departure_time_of_curShip, sim, curShipNo, 1, 1))


    def __repr__(self):
        s = self.eventType + '_OF_SHIPNO_' + str(self.shipNo) + '_FROM_BERTH_NO_'+ str(self.berth + 1) + '_SERVED_BY_'+ str(self.cranes) +'_CRANE'
        return s




class Simulator:
    def __init__(self, seed1,seed2):
        self.eventQ = []
        self.simclock = 0.0
        self.seed1 = seed1
        self.seed2 = seed2
        self.randomStream1 = None
        self.randomStream2 = None
        self.params = None
        self.states = None
        
    def initialize(self):
        self.simclock = 0.0
        #numpy.random.seed(self.seed)
        self.randomStream1 = numpy.random.RandomState(self.seed1)
        self.randomStream2 = numpy.random.RandomState(self.seed2)
        self.randomStream3 = numpy.random.RandomState()
        self.scheduleEvent(StartEvent(0.0, self))
        
    def configure(self, params, states):
        self.params = params
        self.states = states
        #self.states.initialize(self.params.k)
            
    def now(self):
        return self.simclock
        
    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))
    
    def run(self):

        self.initialize()
        


        while len(self.eventQ) > 0:

            time, event = heapq.heappop(self.eventQ)
            
            if event.eventType == 'EXIT':
                break
            
            if self.states != None:
                self.states.update(self, event)
                
            print (event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)
            #print('total harbor time',self.states.total_time_in_harbor)


     
        self.states.finish(self)   
    
    def printResults(self):
        self.states.printResults(self)
        
    def getResults(self):
        return self.states.getResults(self)
        

def experiment():
    seed1 = 51
    seed2 = 101
    sim = Simulator(seed1,seed2)
    sim.configure(Params(1/1.25), States())
    sim.run()
    sim.printResults()




def main():

	experiment()


          
if __name__ == "__main__":
    main()
                  
