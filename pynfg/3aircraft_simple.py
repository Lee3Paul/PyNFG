# -*- coding: utf-8 -*-
"""
A simple iterSemiNFG example of three aircraft avoiding each other en route

Part of: PyNFG - a Python package for modeling and solving Network Form Games

Created on Mon Feb 11 14:40:51 2013

Copyright (C) 2013 James Bono (jwbono@gmail.com)

GNU Affero General Public License

"""
from numpy.linalg import norm
from math import acos

#parameters
actions = [pi/2, pi/4, 0, -pi/4, -pi/2]

loca = np.array([0,0])
locb = np.array([5,0])
locc = np.array([2.5, 4.33])

veca = np.array([1,1])/norm(np.array([1,1]))
vecb = np.array([-1,1])/norm(np.array([-1,1]))
vecc = np.array([0,-1])

acta = 0
actb = 0
actc = 0

goal = [np.array([5,5]), np.array([0,5]), np.array([2.5, 4.33-7.07])]

speed = [.5, .5, 1]

redzone = 1
orangezone = 2
redrew = -5
orangerew = -1

termzone = 1.5
landzone = 0.5
termrew = 1
landrew = 3

#functions used
def frootfunc(locvec=[[loca, locb, locc], [veca, vecb, vecc]]):
    #a dummy function that just spits out the starting loc & vec
    return locvec

def rotmat(angle):
    #returns the rotation matrix for a given angle
    r = np.array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
    return r

def observe(locvec, p):
    loc = locvec[0]
    vec = locvec[1]
    dist = [norm(loc[p]-x) for x in loc] #list of distances from p
    dist[p] = 3000 #change from 0 to big number so argmin is an opponent
    opp = argmin(dist) #index of opponent
    diff = loc[opp]-loc[p] #location - relative to p - of nearest opponent
    oppquad = get_quad(diff, vec[p])
    #distance to opponent
    if dist[opp]<=redzone: #within redzone
        oppdist = 1 
    elif dist[opp]<=orangezone: #within orangezone
        oppdist = 2
    else: #in safezone
        oppdist = 3
    #angle to airport
    diff = goal[p]-loc[p]
    goalquad = get_quad(diff, vec[p])
    #distance to airport
    gdist = norm(diff)
    if: gdist<=termzone: #within terminal zone
        goaldist = 1
    else: #outside terminal zone
        goaldist = 2
    return [oppquad, oppdist, goalquad, goaldist]

def get_quad(diff, vec):
    ang = acos(dot(diff,vec)/(norm(diff))) #angle between airport and vec[p]
    if ang<1/1000: #straight ahead
        quad = 0
    elif norm(dot(rotmat(ang),vec)-diff)<norm(dot(rotmat(-ang),vec)-diff):
        if ang<pi/2: #NE orthant
            quad = 1
        else: #NW orthant
            quad = 2
    else:
        if ang<pi/2: #SE orthant
            quad = 4
        else: #SW orthant
            quad = 3
    return quad

def updateloc(locvec=[[loca, locb, locc],[veca, vecb, vecc]], \
                                                        acta=0, actb=0, actc=0):
    #updates loc and vec according to act
    loc = locvec[0]
    vec = locvec[1]
    act = [acta, actb, actc]
    newloc = []
    newvec = []
    for p in range(len(loc)):
        if norm(loc[p]-goal[p]) <= landed: #no change to loc or vec
            newloc.append(loc[p])
            newvec.append(vec[p])
        else: #still en route, so calculate new loc and vec
            newloc.append(loc[p]+speed[p]*dot(rotmat(act[p]),vec[p]))
            newvec.append((newloc[p]-loc[p])/norm(newloc[p]-loc[p]))
    return [newloc, newvec]
    
# The Nodes
paramsf = {'locvec': [[loca, locb, locc], [veca, vecb, vecc]]}
continuousf = True
Fr = DeterNode('Froot0', frootfunc, paramsf, continuousf, basename='Froot', \
                time=0)

paramsfa = {'locvec': Fr, 'p': 0}
continuousfa = False
spacefa = [(w,x,y,z) for w in range(5) for x in [1,2,3] \
            for y in range(5) for z in [1,2]]
FA = DeterNode('FA0', observe, paramsfa, continuousfa, space=spacefa, \
                basename='FA', time=0)
                
paramsfb = {'locvec': Fr, 'p': 1}
FB = DeterNode('FB0', observe, paramsfb, continuousfa, space=spacefa, \
                basename='FB', time=0)

paramsfc = {'locvec': Fr, 'p': 2}
FC = DeterNode('FC0', observe, paramsfc, continuousfa, space=spacefa, \
                basename='FC', time=0)

DA = DecisionNode('DA0', 'A', actions, parents=[FA], basename='DA', time=0)
DB = DecisionNode('DB0', 'B', actions, parents=[FB], basename='DB', time=0)
DC = DecisionNode('DC0', 'C', actions, parents=[FC], basename='DC', time=0)

paramsf = {'locvec': Fr, 'acta': DA, 'actb': DB, 'actc': DC}
continuousf = True
F = DeterNode('F0', updateloc, paramsf, continuousf, basename='F', \
                time=0)
#collecting nodes in a set
nodes = set([Fr,FA,FB,FC,DA,DB,DC,F])
#Building up the net
for t in range(1,15):
    
    paramsfa = {'locvec': F, 'p': 0}
    FA = DeterNode('FA%s' %t, observe, paramsfa, continuousfa, space=spacefa, \
                    basename='FA', time=t)
                    
    paramsfb = {'locvec': F, 'p': 1}
    FB = DeterNode('FB%s' %t, observe, paramsfb, continuousfa, space=spacefa, \
                    basename='FB', time=t)
    
    paramsfc = {'locvec': F, 'p': 2}
    FC = DeterNode('FC%s' %t, observe, paramsfc, continuousfa, space=spacefa, \
                    basename='FC', time=t)
    
    DA = DecisionNode('DA%s' %t, 'A', actions, parents=[FA], basename='DA', time=t)
    DB = DecisionNode('DB%s' %t, 'B', actions, parents=[FB], basename='DB', time=t)
    DC = DecisionNode('DC%s' %t, 'C', actions, parents=[FC], basename='DC', time=t)
    
    paramsf = {'locvec': F, 'acta': DA, 'actb': DB, 'actc': DC}
    F = DeterNode('F%s' %t, updateloc, paramsf, continuousf, basename='F', \
                    time=t)
    nodes.update([FA,FB,FC,DA,DB,DC,F])#updating the node set
#rewards
def distrew(goaldist, oppdist):
    if oppdist>orangezone or goaldist<landzone: #no penalty assessed in landzone
        pen = 0
    elif oppdist<redzone: 
        pen = redrew
    else:
        pen = orangerew
    if goaldist<landzone:
        rew = landrew
    elif goaldist<termzone:
        rew = termrew
    else:
        rew = 0
    return rew+pen
#A's reward                    
def rewardA(F):
    loc = F[0]
    goaldist = norm(loc[0]-goal[0])
    dist = [norm(loc[0]-x) for x in loc] #list of distances from p
    dist[0] = 3000 #change from 0 to big number so argmin is an opponent
    oppdist = min(dist) 
    return distrew(goaldist, oppdist)
#B's reward    
def rewardB(F):
    loc = F[1]
    goaldist = norm(loc[1]-goal[1])
    dist = [norm(loc[1]-x) for x in loc] #list of distances from p
    dist[1] = 3000 #change from 0 to big number so argmin is an opponent
    oppdist = min(dist) 
    return distrew(goaldist, oppdist)
#C's reward
def rewardC(F):
    loc = F[2]
    goaldist = norm(loc[2]-goal[2])
    dist = [norm(loc[2]-x) for x in loc] #list of distances from p
    dist[2] = 3000 #change from 0 to big number so argmin is an opponent
    oppdist = min(dist) 
    return distrew(goaldist, oppdist)

r_funcs = {'A': rewardA, 'B': rewardB, 'C': rewardC}
    
G = iterSemiNFG(nodeset, r_funcs)
G.draw_graph()