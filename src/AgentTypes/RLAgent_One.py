# -*- coding: utf-8 -*-
"""
@author: berend
"""

from src.AgentModule import AgentClass
from random import sample, random
from collections import defaultdict
import itertools
import src.StateModule
import numpy as np
import json

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(itertools.islice(iterable, n, None), default)


def takeAction(actionOptions, Unit, Qtable, ground_troop, air_troop):
    epsilon = 0.4
    actions_list = list(actionOptions[0]) 
    nA = len(actions_list) 
    
    takenAction = None 
    
    update_q_table = False 
    type__ = str(type(Unit)) 
    prob_list = None 
    
    if type__ in ground_troop:
        ty_ = 'land'
        nA = 12 
        # prob = np.ones(nA) * epsilon / nA
        update_q_table = True 
    elif type__ in air_troop:
        ty_ = 'air'
        update_q_table = True 
        nA = 26
        # prob = np.ones(nA) * epsilon / nA
    else:
        ty_ = 'flag' 
    
    
    if update_q_table:
        
        position_ = ""+ str(int(Unit.Position[0])) + ", " + str(int(Unit.Position[1]))   
        orientation_ = ""+str(int(Unit.Orientation[0])) + ", " + str(int(Unit.Orientation[1]))  
    
            
        q_values_state_action = Qtable[ty_][position_][orientation_]
        
        original_action_list = list(q_values_state_action.keys())
        
                
        values_list = [] 
        for key in q_values_state_action.keys():
            if key in actions_list:
                values_list.append(q_values_state_action[key]) 
            else:
                values_list.append(-1000) 
        
        # prob = np.ones(nA) * epsilon / nA
        # prob[np.argmax(values_list)] += 1 - epsilon 

        max_index = np.argmax(values_list) 

        prob_other = 1 * epsilon / len(actions_list) 
        prob_max = prob_other + 1 - epsilon 
        
        prob_list = [None] * nA     

        index = 0
        for key in q_values_state_action.keys():
            if key in actions_list and index == max_index:
                prob_list[index] = prob_max 
            elif key in actions_list:
                prob_list[index] = prob_other
            else:
                prob_list[index] = 0 

            index += 1

        print("", end="") 
        
        
 
        
        index = np.random.choice(np.arange(len(prob_list)), p=prob_list)
        takenAction =  (Unit.ID, [original_action_list[index]] ) 
        
    
    else:
        takenAction = (Unit.ID, [actions_list[0]])  

    
    return takenAction
   
    
class Qlearning_1(AgentClass):
    
    def __init__(self, ID):
        AgentClass.__init__(self, ID)
        self.PrintOn = False

    def chooseActions(self, ObservedState, State, Qtable):
        
        ground_troop = [] 
        for t in list(State.GroundOnlyUnits):
            ground_troop.append(str(t))   
            
        air_troop = [str(State.AirOnlyUnits[0])]  
        
        
        if self.PrintOn:
            print("with in the RL agent class ") 
        Actions = [] 
        for UnitID, Units in ObservedState.items():
            if len(Units)== 1 and nth(Units,0).Owner == self.ID:
                Unit = nth(Units,0) 
                # Generate possible actions for the unit based on BoardSize and Position
                # calling the function from the 
                ActionOptions = Unit.possibleActions(State) 
                
                # take the Action from ActionOptions using the RL Agent 
                TakenAction = takeAction(ActionOptions, Unit, Qtable, ground_troop, air_troop)  
                                
                Actions.append(TakenAction) 
                if self.PrintOn:
                    print("Agent ID=",self.ID, " takes action ", TakenAction[1]," with Unit ID=", UnitID, " of type ", type(Unit),".\n") 
        
        return Actions

    def updateDecisionModel(self, Observations, PriorActions): 
        # print("update Decision Model empty---") 
        pass



