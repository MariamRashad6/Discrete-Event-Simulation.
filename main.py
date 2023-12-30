import random
import simpy
import numpy as np

RANDOM_SEED = 42
SIM_TIME = 800
# number of machines in each workstation
NUM_MILLING_MACHINES = 4
NUM_DRILLING_MACHINES = 3
NUM_SPRAY_BOOTHS = 2
NUM_TRUCKS = 2
NUM_POLISHING_WORKERS = 1

j=0

# intializiing a queue for locations of truck
LOCATIONS = []

# dictionary for distances among job shop locations
DISTANCES = {'arrival_milling':100,'arrival_drilling':100,'arrival_arrival':0,'arrival_paint':250,'arrival_polishing':250,'arrival_exit':550
            ,'milling_drilling':300,'milling_paint':400,'milling_polishing':150,'milling_milling':0,'milling_arrival':100,'milling_exit':300
            ,'paint_polishing':300,'paint_paint':0,'paint_drilling':150,'drilling_exit':500
            ,'drilling_paint':150,'drilling_polishing':400,'drilling_drilling':0,'drilling_arrival':100,'drilling_milling':300
            ,'paint_arrival':250,'paint_paint':0,'paint_milling':400,'paint_exit':400
            ,'polishing_arrival':250,'polishing_exit':200,'polishing_polishing':0,'polishing_millling':150,'polishing_paint':300,'polishing_drilling':400,'polishing_exit':200
            ,'exit_arrival':550,'exit_drilling':500,'exit_milling':300,'exit_paint':400,'exit_polishing':200,'exit_exit':0}

# wait
WAIT_MIILING = []
WAIT_DRILLING = []
WAIT_PAINTING = []
WAIT_POLISHING = []

# system
TYPE_ONE = []
TYPE_TWO = []
TYPE_THREE = []

END_SYSTEM_MILLLING = 0
END_SYSTEM_DRILLING = 0
END_SYSTEM_POLISHING = 0
END_SYSTEM_PAINTING = 0
# idle
IDLE_MILLING = []
IDLE_DRILLING = []
IDLE_PAINTING = []
IDLE_POLISHING = []

class JobShop(object):
    def __init__(self, env):
        self.env = env
        self.machine = simpy.Resource(env, NUM_MILLING_MACHINES)
        self.drillingMachine = simpy.Resource(env, NUM_DRILLING_MACHINES)
        self.truck = simpy.Resource(env, NUM_TRUCKS)
        self.spray_booth = simpy.Resource(env, NUM_SPRAY_BOOTHS)
        self.polishing_worker = simpy.Resource(env, NUM_POLISHING_WORKERS)

    # milling process
    def millling(self, gear,time):
        yield self.env.timeout(time)
        print(str(gear)+" milled at "+str(env.now))


    # drilling process
    def drilling(self, gear,time):
        yield self.env.timeout(time)
        print(str(gear)+" drilled at "+str(env.now))
        

    # painting process
    def painting(self, gear,time):
        yield self.env.timeout(time)
        print(str(gear)+" painted at "+str(env.now)) 
        

    # polishing process
    def polishing(self, gear,time):
        yield self.env.timeout(time)
        print(str(gear)+" polished at "+str(env.now))
            

    # truck transporation process from location to location            
    def transport(self,gear,source,distination):
        loc = LOCATIONS.pop(0) 
        sour = source+"_"+loc
        dist = source+"_"+distination
        total_distance = DISTANCES[sour]+DISTANCES[dist]
        yield self.env.timeout(total_distance/100) 
        LOCATIONS.append(distination)   
        print(str(gear)+" transported at "+str(env.now)) 

# function to handle gears process 
def gear(env,name,jobshop,type): # name -> gear + i (number pf gear)
    print('%s of type %d arrives at the jobshop at %.2f.' % (name, type,env.now))
    global END_SYSTEM_MILLLING 
    global END_SYSTEM_DRILLING 
    global END_SYSTEM_POLISHING 
    global END_SYSTEM_PAINTING 
    
    # type 1
    if type == 1:
        arrival = env.now
        # transporting by truck from arrival dock to milling work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from arrival dock to milling work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"arrival","milling"))
        # milling
        with jobshop.machine.request() as request:
            req = env.now
            yield request
            if(env.now > END_SYSTEM_MILLLING):
                IDLE_MILLING.append(env.now-END_SYSTEM_MILLLING)
            WAIT_MIILING.append(env.now - req)
            print('%s enters the milling workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.millling(name,35))
            END_SYSTEM_MILLLING = env.now

        # transporting by truck from milling dock to drilling work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from milling dock to drilling work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"milling","drilling"))    
        # drilling
        with jobshop.drillingMachine.request() as request:
            req2 = env.now
            yield request
            if(env.now > END_SYSTEM_DRILLING):
                IDLE_DRILLING.append(env.now-END_SYSTEM_DRILLING)
            WAIT_DRILLING.append(env.now - req2)
            print('%s enters the drilling workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.drilling(name,20))
            END_SYSTEM_DRILLING = env.now

        # transporting by truck from drilling dock to painting work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from drilling dock to painting work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"drilling","paint"))     
        # painting
        with jobshop.spray_booth.request() as request:
            req3 = env.now
            yield request
            if(env.now > END_SYSTEM_PAINTING):
                IDLE_PAINTING.append(env.now-END_SYSTEM_PAINTING)
            WAIT_PAINTING.append(env.now - req3)
            print('%s enters the painting workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.painting(name,55))
            END_SYSTEM_PAINTING = env.now

        # transporting by truck from painting to polishing work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from painting to polishing work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"paint","polishing"))     
        # polishing
        with jobshop.polishing_worker.request() as request:
            req4 = env.now
            yield request
            if(env.now > END_SYSTEM_POLISHING):
                IDLE_POLISHING.append(env.now-END_SYSTEM_POLISHING)
            WAIT_POLISHING.append(env.now - req4)
            print('%s enters the polishing workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.polishing(name,15))
            END_SYSTEM_POLISHING = env.now    

        # transporting by truck from polishing to shop exit
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from polishing to shop exit at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"polishing","exit"))     

        print('%s leaves the jobshop at %.2f.' % (name, env.now))
        leave = env.now
        TYPE_ONE.append(leave-arrival) # to calculate average system time (gear flow)

    # type 2
    elif type == 2:
        arrival = env.now
        # transporting by truck from arrival dock to milling work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from arrival dock to milling work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"arrival","milling"))
        # milling
        with jobshop.machine.request() as request:
            req = env.now
            yield request
            if(env.now > END_SYSTEM_MILLLING):
                IDLE_MILLING.append(env.now-END_SYSTEM_MILLLING)
            WAIT_MIILING.append(env.now - req)
            print('%s enters the milling workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.millling(name,35))
            END_SYSTEM_MILLLING = env.now

        # transporting by truck from milling dock to painting work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from milling dock to painting work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"milling","paint"))     
        # painting
        with jobshop.spray_booth.request() as request:
            req3 = env.now
            yield request
            if(env.now > END_SYSTEM_PAINTING):
                IDLE_PAINTING.append(env.now-END_SYSTEM_PAINTING)
            WAIT_PAINTING.append(env.now - req3)
            print('%s enters the painting workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.painting(name,55))
            END_SYSTEM_PAINTING = env.now

        # transporting by truck from painting to polishing work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from painting to polishing work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"paint","polishing"))     
        # polishing
        with jobshop.polishing_worker.request() as request:
            req4 = env.now
            yield request
            if(env.now > END_SYSTEM_POLISHING):
                IDLE_POLISHING.append(env.now-END_SYSTEM_POLISHING)
            WAIT_POLISHING.append(env.now - req4)
            print('%s enters the polishing workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.polishing(name,15))
            END_SYSTEM_POLISHING = env.now     

        # transporting by truck from polishing to shop exit
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from polishing to shop exit at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"polishing","exit"))     

        print('%s leaves the jobshop at %.2f.' % (name, env.now)) 
        leave = env.now
        TYPE_TWO.append(leave-arrival) # to calculate average system time (gear flow)
    # type 3
    else:
        arrival = env.now
        # transporting by truck from arrival dock to drilling work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from arrival dock to drilling work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"arrival","drilling"))    
        # drilling
        with jobshop.drillingMachine.request() as request:
            req2 = env.now
            yield request
            if(env.now > END_SYSTEM_DRILLING):
                IDLE_DRILLING.append(env.now-END_SYSTEM_DRILLING)
            WAIT_DRILLING.append(env.now - req2)
            print('%s enters the drilling workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.drilling(name,20))
            END_SYSTEM_DRILLING = env.now

        # transporting by truck from drilling dock to painting work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from drilling dock to painting work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"drilling","paint"))     
        # painting
        with jobshop.spray_booth.request() as request:
            req3 = env.now
            yield request
            if(env.now > END_SYSTEM_PAINTING):
                IDLE_PAINTING.append(env.now-END_SYSTEM_PAINTING)
            WAIT_PAINTING.append(env.now - req3)
            print('%s enters the painting workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.painting(name,55))
            END_SYSTEM_PAINTING = env.now    

        # transporting by truck from painting to polishing work station
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from painting to polishing work station at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"paint","polishing"))     
        # polishing
        with jobshop.polishing_worker.request() as request:
            req4 = env.now
            yield request
            if(env.now > END_SYSTEM_POLISHING):
                IDLE_POLISHING.append(env.now-END_SYSTEM_POLISHING)
            WAIT_POLISHING.append(env.now - req4)
            print('%s enters the polishing workstation at %.2f.' % (name, env.now))
            yield env.process(jobshop.polishing(name,15))
            END_SYSTEM_POLISHING = env.now     

        # transporting by truck from polishing to shop exit
        with jobshop.truck.request() as request:
            yield request
            print('%s being transported from polishing to shop exit at %.2f.' % (name, env.now))
            yield env.process(jobshop.transport(name,"polishing","exit"))     

        print('%s leaves the jobshop at %.2f.' % (name, env.now))
        leave = env.now
        TYPE_THREE.append(leave-arrival) # to calculate average system time (gear flow)   

# function creates an instance of jobshop, generates gears arrival 
def setup(env):
    # Create the jobshop
    jobshop = JobShop(env)
    global j

    # batches arrive uniformally every 400 to 600 minutes
    yield env.timeout(random.uniform(400,600))
    global END_SYSTEM_MILLLING 
    global END_SYSTEM_DRILLING 
    global END_SYSTEM_POLISHING 
    global END_SYSTEM_PAINTING 

    END_SYSTEM_MILLLING = env.now
    END_SYSTEM_DRILLING = env.now
    END_SYSTEM_POLISHING = env.now
    END_SYSTEM_PAINTING = env.now

    # Create more gears while the simulation is running
    while True:
        # Of arriving batches, 50% are of type G1, 30% are of type G2, and 20% are of type G3.
        # gear_types = [1,2,3]
        # gears =np.random.choice(gear_types, 10, p=[0.5,0.3,0.2])
        gears = [1,2,1,3,1,1,2,3,2,1]
        # Create 10  gears
        for i in range(10):
            j = j + 1 # keeps track of number of gears
            env.process(gear(env, 'Gear %d' % j, jobshop,gears[i]))

        yield env.timeout(random.uniform(400,600))    

# statistics 
def calculate():
    print("======= Statistics =======")
    # Gear delays at operations locations (average wait)
    # milling
    sum =0
    for i in range(len(WAIT_MIILING)):
        sum = sum + WAIT_MIILING[i]
    print("Delay at Milling Location %.2f"%(sum/len(WAIT_MIILING)))

    # drilling
    sum =0
    for i in range(len(WAIT_DRILLING)):
        sum = sum + WAIT_DRILLING[i]
    print("Delay at Drilling Location %.2f"%(sum/len(WAIT_DRILLING)))

    # painting
    sum =0
    for i in range(len(WAIT_PAINTING)):
        sum = sum + WAIT_PAINTING[i]
    print("Delay at Painting Location %.2f"%(sum/len(WAIT_PAINTING)))

    # polishing 
    sum =0
    for i in range(len(WAIT_POLISHING)):
        sum = sum + WAIT_POLISHING[i]
    print("Delay at Polishing Location %.2f"%(sum/len(WAIT_POLISHING)))

    # Gear flow times (by type) (average system)
    print("Gear flow times:")
    # type 1
    sum =0
    for i in range(len(TYPE_ONE)):
        sum = sum + TYPE_ONE[i]
    print("Gear Flow Type 1 %.2f"%(sum/len(TYPE_ONE)))
    # type 2
    sum =0
    for i in range(len(TYPE_TWO)):
        sum = sum + TYPE_TWO[i]
    print("Gear Flow Type 2 %.2f"%(sum/len(TYPE_TWO)))
    # type 3
    sum =0
    for i in range(len(TYPE_THREE)):
        sum = sum + TYPE_THREE[i]
    print("Gear Flow Type 2 %.2f"%(sum/len(TYPE_THREE)))

    # Machine utilizations
    # milling machine
    sum =0
    for i in range(len(IDLE_MILLING)):
        sum = sum + IDLE_MILLING[i]
    print("Milling Utilization: %.2f"%((SIM_TIME-sum)/SIM_TIME))
    # drilling machine
    sum =0
    for i in range(len(IDLE_DRILLING)):
        sum = sum + IDLE_DRILLING[i]
    print("Drilling Utilization: %.2f"%((SIM_TIME-sum)/SIM_TIME))
    # painting machine
    sum =0
    for i in range(len(IDLE_PAINTING)):
        sum = sum + IDLE_PAINTING[i]
    print("painting Utilization: %.2f"%((SIM_TIME-sum)/SIM_TIME))
    # polishing machine
    sum =0
    for i in range(len(IDLE_POLISHING)):
        sum = sum + IDLE_POLISHING[i]
    print("polishing Utilization: %.2f"%((SIM_TIME-sum)/SIM_TIME))

# Setup and start the simulation
print('JobShop')
LOCATIONS.append("arrival")
LOCATIONS.append("arrival")

random.seed(RANDOM_SEED)  # This helps reproducing the results

# Create an environment and start the setup process
env = simpy.Environment()
env.process(setup(env))

# Execute!
env.run(until=SIM_TIME)

calculate()