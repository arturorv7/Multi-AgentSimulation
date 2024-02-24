from owlready2 import *
import agentpy as ap
from kqml import *
import itertools
import random

cwd = os.getcwd()
onto = get_ontology("file://" + os.path.abspath("evidencia1.rdf")).load()

trucksSeen = 0
trucksExpected = int(input("Trucks expected: "))

global lim, Broadcast, apts, pagado, ts
lim = 20
Broadcast = []
apts = False
pagado = []
ts = []

class kqml_query:
    def __init__(self, type, sender, receiver, content, in_reply_to):
        types = ["tell", "reply"]
        if type not in types: 
            raise ValueError(f"Type {type} is not valid.")

        self.type = type
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.in_reply_to = in_reply_to

    def __str__(self):
        res = f"({self.type}\n"
        res += f" :sender {self.sender}\n"
        res += f" :receiver {self.receiver}\n"
        res += f" :content {self.content}\n"
        if self.in_reply_to != "":
            res += f" :in-reply-to {self.in_reply_to}\n"
        res += ")"
        return res

def GET_SPEED():
    speed = 50
    return speed

def GET_LOOPS():
    loops = 3
    return loops

class GoodTruckAgent(ap.Agent):
    beenSeen = False
    id_iter = itertools.count()
    def setup(self):
        self.agentID = 1
        self.id = next(self.id_iter)
        self.thisTruck = onto.GoodTruck()
        self.thisTruck.hasSpeed = 0
        self.thisTruck.hasDirt = False
        self.thisTruck.isInX = 0
        self.thisTruck.isInY = 0
        self.actions = ["cargar", "salir", "pagar"]

    def speed(self, spd):
        self.thisTruck.hasSpeed = GET_SPEED()
        return self.thisTruck.hasSpeed

    def see(self, e):
        seeRange = 6
        p = [a for a in e.neighbors(self, distance = seeRange) if a.agentID == 3]
        if not p:
            pass
        else:
            self.beenSeen = True

        self.thisTruck.isInX = self.model.grid.positions[self][0]
        self.thisTruck.isInY = self.model.grid.positions[self][1]
        self.thisTruck.hasDirt = self.thisTruck.hasDirt
        self.thisTruck.hasSpeed = self.thisTruck.hasSpeed

    def teoria(self, action):
        if self.thisTruck.hasDirt == False and action == "cargar":
            return True
        elif self.thisTruck.hasDirt == True and action == "salir":
            return True
        elif action == "pagar":
            return True
        else:
            return False
        
    def ejecutar(self):
        select = ""
        for action in self.actions:
            if self.teoria(action):
                select = action
                break
        if select != "":
            if select == "cargar":
                self.model.grid.move_by(self, (1, 1))
                self.thisTruck.isInX = self.thisTruck.isInX + 1
                self.thisTruck.isInY = self.thisTruck.isInX + 1
            if select == "salir":
                self.model.grid.move_by(self, (-1, -1))
                self.thisTruck.isInX = self.thisTruck.isInX - 1
                self.thisTruck.isInY = self.thisTruck.isInY - 1
        
        if (self.thisTruck.isInX == 15) and (self.thisTruck.isInY == 15):
            self.thisTruck.hasDirt = True
            select = "salir"
            Broadcast.append(kqml_query("tell", f"GoodTruckAgent, ID:{self.id}", "-", "Estoy cargando material.", "-"))
            print("GOOD TRUCK: Estoy cargando material.")
        
        if (self.thisTruck.isInX == lim) and (self.thisTruck.isInY == lim+1) and (f"GoodTruck id:{self.id}" not in pagado):
            select = "pagar"
            Broadcast.append(kqml_query("tell", f"GoodTruckAgent, ID:{self.id}", "-", "Pagado", "-"))
            pagado.append(f"GoodTruck id:{self.id}")
 
    def step(self, e):
        self.see(e)
        self.ejecutar()
        Broadcast.append(kqml_query("tell", f"GoodTruckAgent, ID:{self.id}", "-", "Estoy en " + str(self.thisTruck.isInX) + ", " + str(self.thisTruck.isInY), "-"))
        print("GOOD TRUCK: Estoy en " + str(self.thisTruck.isInX) + ", " + str(self.thisTruck.isInY))

class BadTruckAgent(ap.Agent):
    beenSeen = False
    id_iter = itertools.count()
    def setup(self):
        self.agentID = 2
        self.id = next(self.id_iter)
        self.thisTruck = onto.BadTruck()
        self.thisTruck.hasSpeed = 10
        self.thisTruck.hasDirt = False
        self.thisTruck.isInX = 0
        self.thisTruck.isInY = 0
        self.actions = ["cargar", "salir"]

    def speed(self, spd):
        self.thisTruck.hasSpeed = GET_SPEED()
        return self.thisTruck.hasSpeed

    def see(self, e):
        seeRange = 6
        p = [a for a in e.neighbors(self, distance = seeRange) if a.agentID == 3]
        if not p:
            pass
        else:
            self.beenSeen = True

        self.thisTruck.isInX = self.model.grid.positions[self][0]
        self.thisTruck.isInY = self.model.grid.positions[self][1]
        self.thisTruck.hasDirt = self.thisTruck.hasDirt
        self.thisTruck.hasSpeed = self.thisTruck.hasSpeed

    def teoria(self, action):
        if self.thisTruck.hasDirt == False and action == "cargar":
            return True
        if self.thisTruck.hasDirt == True and action == "salir":
            return True
        else:
            return False
        
    def ejecutar(self):
        select = ""
        for action in self.actions:
            if self.teoria(action):
                select = action
                break
        if select != "":
            if select == "cargar":
                self.model.grid.move_by(self, (1, 1))
                self.thisTruck.isInX = self.thisTruck.isInX + 1
                self.thisTruck.isInY = self.thisTruck.isInX + 1
            if select == "salir":
                self.model.grid.move_by(self, (-1, -1))
                self.thisTruck.isInX = self.thisTruck.isInX - 1
                self.thisTruck.isInY = self.thisTruck.isInX - 1

        if (self.thisTruck.isInX == 15) and (self.thisTruck.isInY == 15):
            self.thisTruck.hasDirt = True
            select = "salir"
            Broadcast.append(kqml_query("tell", f"BadTruckAgent, ID:{self.id}", "-", "Estoy cargando material.", "-"))
            print("BAD TRUCK: Estoy cargando material.")

    def step(self, e):
        self.see(e)
        self.ejecutar()
        Broadcast.append(kqml_query("tell", f"BadTruckAgent, ID:{self.id}", "-", "Estoy en " + str(self.thisTruck.isInX) + ", " + str(self.thisTruck.isInY), "-"))
        print("BAD TRUCK: Estoy en " + str(self.thisTruck.isInX) + ", " + str(self.thisTruck.isInY))
        
class CameraAgent(ap.Agent):
    def setup(self):
        self.agentID = 3
        self.thisCamera = onto.Camera()
        self.actions = ["ver"]
        self.counter = 0

    def see(self, e):
        seeRange = 6
        global trucksSeen, apts
        p = [a for a in e.neighbors(self, distance = seeRange) if a.beenSeen == False]
        cv = len(p)
        if apts == True:
            self.counter += cv
            trucksSeen += self.counter
            if cv>0:
                for i in p:
                    ts.append(i)
        else:
            pass
        return p

    def teoria(self, action):
        pass
        
    def ejecutar(self):
        pass

    def step(self, e):
        global apts
        Broadcast.append(kqml_query("tell", "CameraAgent, ID: 0", "TruckModel", f"Camiones vistos: {self.see(e)}\nCamiones vistos en total: {self.counter}", "-"))
        print("\nCAMARA: He visto a: ")
        apts = True
        print(*self.see(e), sep="\n")
        apts = False
        print("        He visto: " + str(self.counter) + " camiones.")
        self.ejecutar()

class TruckModel(ap.Model):
    def setup(self):
        self.goodTrucks = ap.AgentList(self, trucksExpected, GoodTruckAgent)
        self.badTrucks = ap.AgentList(self, 3, BadTruckAgent)
        self.cameras = ap.AgentList(self, 1, CameraAgent)

        self.grid = ap.Grid(self, shape = (lim, lim))

        self.grid.add_agents(self.goodTrucks, [(random.randrange(1, lim-13), random.randrange(1, lim-13)) for x in range(trucksExpected)])
        self.grid.add_agents(self.badTrucks, [(random.randrange(1, lim-13), random.randrange(1, lim-13)), (random.randrange(1, lim-13), random.randrange(1, lim-13)), (random.randrange(1, lim-13), random.randrange(1, lim-13))])
        self.grid.add_agents(self.cameras, [(x + 10, x + 10) for x in range(2)])
        pass

    def step(self):
        print("\n\n")
        self.goodTrucks.step(self.grid)
        self.badTrucks.step(self.grid)
        self.cameras.step(self.grid)
        pass

    def update(self):
        pass

    def end(self):
        pass

parameters = {
    "steps" : lim
}

model = TruckModel(parameters)
results = model.run()
difference = trucksExpected - trucksSeen

with open('queries.txt', 'w') as archivo:
    for m in Broadcast:
        archivo.write(str(m) + '\n')

z = len(ts) - len(pagado)
if z<0:
    z = 0

print(" ================")    
print(" || Resultados ||")
print(" ================")    

print("\n  Camiones que pagaron: ")
print(*pagado, sep="\n")
print("\n  Camiones vistos por la cámara: ")
print(*ts, sep="\n")

print(f"\nCamiones esperados (Buenos):   {trucksExpected}")
print(f"Camiones que pagaron:          {len(pagado)}")
print(f"Camiones Malos:                3")
print(f"Total de camiones:             {trucksExpected+3}")
print(f"Camiones vistos por la cámara: {len(ts)}")
print(f"Camiones Sospechosos (C. vistos por la cámara - C. que pagaron): {z}")

