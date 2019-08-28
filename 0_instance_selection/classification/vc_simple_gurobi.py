#!/usr/bin/env python3
#
# Copyright 2019
# M. Ayaz Dzulfikar, University of Indonesia, Indonesia
# Johannes K. Fichte, TU Dresden, Germany
# Markus Hecher, TU Wien, Austria
#
# vc_simple_gurobi is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# vc_simple_gurobi is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.  You should have received a
# copy of the GNU General Public License along with
# vc_simple_gurobi.  If not, see <http://www.gnu.org/licenses/>.
#

from gurobipy import *
import os
import sys
import time

def calc(x):
    i = 0
    y = 1
    while y <= x:
        y *= 10
        i += 1
    return i

def optimize(vertices, edges, cover_size):
    m = Model()
    m.setParam('OutputFlag', False)
    m.setParam("Threads", 1)
    m.setParam("TimeLimit", 3 * 60 * 60)
    m.setParam("MIPGap", 1.0 / (len(vertices)+1))
    vertexVars = {}

    sys.stderr.write("writing constraints..")
    for v in vertices:
        vertexVars[v] = m.addVar(vtype=GRB.BINARY,obj=1.0, name="x%d" % v)

    m.update()

    for edge in edges:
        u = edge[0]
        v = edge[1]
        xu = vertexVars[u]
        xv = vertexVars[v]
        m.addConstr(xu + xv >= 1, name="e%d-%d" % (u, v))

    sys.stderr.write("finish writing constraints\n")
    m.update()
    m.optimize()

    sys.stderr.write("Set MIP gap: {0:.16f}\n".format(1.0 / (len(vertices)+1)))
    sys.stderr.write("Final MIP gap value: {0:.16f}\n".format(m.MIPGap))
    sys.stderr.write("finished optimizing\n")

    cover = set()

    for v in vertices:
        if vertexVars[v].X > 0.5:
            cover.add(v)

    for edge in edges:
        u = edge[0]
        v = edge[1]
        assert(u in cover or v in cover)

    return cover

def read_input(filename):
    vertex = -1
    edge = -1
    vertices = None
    edges = []
    cover_size = -1

    with open(filename, "r") as f:
        for line in f.readlines():
            tokens = line.split()
            if tokens[0] == "p":
                vertex = int(tokens[2])
                edge = int(tokens[3])
                vertices = range(1, vertex+1)
            elif "vc size" in line:
                cover_size = int(tokens[4])
            elif tokens[0] != "c":
                u = int(tokens[0])
                v = int(tokens[1])

                edges.append([u, v])

    sys.stderr.write(str(len(vertices)) + " " + str(len(edges)) + " " + str(cover_size) + "\n")
    return vertices, edges, cover_size

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write('Missing filename...\nRun \'vc_simple_gurobi.py mygraph.gr\'\n\n  Exiting...\n\n')
        exit(1)
    filename = sys.argv[1]

    sys.stderr.write("#" * 20 + "\n")
    sys.stderr.write("doing " + filename + "\n")

    vertices, edges, cover_size = read_input(filename)

    start_time = time.time()
    cover = optimize(vertices, edges, cover_size)

    sys.stderr.write("finished in %s seconds\n" % (time.time() - start_time))
    sys.stderr.write("expected size " + str(cover_size) +  " got " + str(len(cover)) + "\n")
    if len(cover) <= cover_size:
        sys.stderr.write("c s SATISFIABLE\n")
        print("c s SATISFIABLE")
    else:
        sys.stderr.write("c s UNSATISFIABLE\n")
        print("c s UNSATISFIABLE")
    print("s vc {} {}".format(len(vertices), len(cover)))
    for v in cover:
        print("{}".format(v))

    sys.stderr.write("#" * 20 + "\n")
