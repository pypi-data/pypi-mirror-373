
from clustering.models.adalina_zoning_data import AdalinaZoningData
from clustering.models.adalina_zoning_solution import AdalinaZoningSolution

import highspy
import numpy as np
import time
import logging
# from sklearn.cluster import AgglomerativeClustering

# from itertools import permutations
# hscb = highspy.cb

# VAR
# x_ij {1 if i in cluster with representative j, 0 otherwise}
# y_j {1 if j is representative of a cluster, 0 otherwise}

# min \sum{(i,j) \in N^2 : i \not= j} c[i,j] * (x_{ij} + w_{ij})
# Kmin <= sum{j in N} y_j <= Kmax
# sum{j in N} x_ij + y_i = 1 forall i in N
# x_ij <= y_i forall i, j in N : i != j
# x_{ij} <= sum{k in N : k in adj(i) and dist^-(k, j) <= dist^-(i,j) } x_{kj} forall (i,j) : i not in adj(j)
# x_{ik} + x_{jk} <= 1 + w_{ij} forall i,j,k in N^3 : i \not= j \not= k
# x_ik + x_jk >= 2*w_ij
# x_{ik} + w_{ik} <= 1 forall (i,k) in N^2 : i \not= k
# \sum_{i in N :  i\not=j } x_ij * c_i >= y_j * F_min forall j in N

class AdalinaZoningModelSimple:

    def __init__(self, data : AdalinaZoningData,  log_fout = None):

        self.log_fout = log_fout
        self.data = data
        self.vardict = dict()
        self.model = highspy.Highs()
        inf = highspy.kHighsInf
        self.run_status = None
        self.solution = None
        self.best_feasible_sol = None
        self.warmstartsol = None

        # x_ij {1 if i in cluster with representative j, 0 otherwise}
        xvar = []
        for i in self.data.G.nodes:
            for j in self.data.G.nodes:
                if i == j:
                    continue
                xvar.append(
                    self._add_variable(0, 1,
                                       self.data.get_cost_edge(i, j),
                                       highspy.HighsVarType.kInteger,
                                       f"x_{i}_{j}")
                )

        wvar = []
        nnodes = list(self.data.G.nodes)
        for i, el in enumerate(nnodes):
            for j in range(i+1, len(nnodes)):
                el2 = nnodes[j]
                wvar.append(
                    self._add_variable(0, 1,
                                       self.data.get_cost_edge(el, el2),
                                       highspy.HighsVarType.kInteger,
                                       f"w_{i}_{j}")
                )

        # y[s] in {0,1}
        yvar = []
        for i in data.G.nodes:
            yvar.append(
                    self._add_variable(0,1, 0,
                                       highspy.HighsVarType.kInteger,
                                     f"y_{i}")
                                 )

        # K^{\min} <= \sum_{i\in V} z_i <= K^{\max}
        _vars = [self._get_vardict_index(f'y_{i}') for i in data.G.nodes]
        _varvalues = np.ones(self.data.V)
        self.model.addRow(self.data.Kmin, self.data.Kmax,
                          len(_vars),
                          np.array(_vars),
                          np.array(_varvalues)
                          )

        # x_ij <= y_j forall (i,j) in N^2 : i != j
        for i in data.G.nodes:
            for j in data.G.nodes:
                if i == j:
                    continue

                self.model.addRow(-inf,0,
                                  2,
                                  np.array(
                                      [self._get_vardict_index(f'x_{j}_{i}'),
                                       self._get_vardict_index(f'y_{i}')]
                                  ),
                                  np.array([1,-1])
                                  )

        # sum{j in N : i != j} x_ij + y_i = 1 forall i in N
        for i in data.G.nodes:
            _vars = ([self._get_vardict_index(f'x_{i}_{j}') for j in data.G.nodes if i != j] +
                     [self._get_vardict_index(f'y_{i}')])
            self.model.addRow(1, 1,
                              len(_vars),
                              np.array(_vars),
                              np.ones(len(_vars))
                              )

        # x_{ij} <= sum{k in N : k in adj(i) and dist^-(k, j) <= dist^-(i,j) } x_{kj} forall (i,j) : i not in adj(j)
        for i in self.data.G.nodes:
            for j in self.data.G.nodes:
                if i == j or j in self.data.G.neighbors(i):
                    continue

                _vars = [self._get_vardict_index(f'x_{i}_{j}')]
                _varvalues = [1]
                for k in self.data.G.neighbors(i):
                    if self.data.get_node_pair_geographic_distance(i, j) > self.data.get_node_pair_geographic_distance(k, j):
                        _vars.append(self._get_vardict_index(f'x_{k}_{j}'))
                        _varvalues.append(-1)

                self.model.addRow(-inf, 0,
                                  len(_vars),
                                  np.array(_vars),
                                  np.array(_varvalues)
                                  )

        # x_{ik} + x_{jk} <= 1 + w_{ij} forall i,j,k in N^3 : i \not= j \not= k
        # x_{ik} + x_{jk} >= 2*w_{ij} forall i,j,k in N^3 : i \not= j \not= k
        for i, n1 in enumerate(self.data.G.nodes):
            for j, n2 in enumerate(self.data.G.nodes):
                if i >= j:
                    continue

                if i > j:
                    _w = self._get_vardict_index(f'w_{j}_{i}')
                else:
                    _w = self._get_vardict_index(f'w_{i}_{j}')

                for k, n3 in enumerate(self.data.G.nodes):
                    if i == k or j == k:
                        continue

                    self.model.addRow(-inf, 1,
                                      3,
                                      np.array([_w,
                                                self._get_vardict_index(f'x_{n1}_{n3}'),
                                                self._get_vardict_index(f'x_{n2}_{n3}')]),
                                      np.array([-1, 1, 1])
                                      )

                    # self.model.addRow(0, +inf,
                    #                   3,
                    #                   np.array([_w,
                    #                             self._get_vardict_index(f'x_{n1}_{n3}'),
                    #                             self._get_vardict_index(f'x_{n2}_{n3}')]),
                    #                   np.array([-2, 1, 1])
                    #                   )

        # x_{ik} + w_{ik} <= 1 forall (i,k) in N^2 : i \not= k
        for i, n1 in enumerate(self.data.G.nodes):
            for k, n2 in enumerate(self.data.G.nodes):

                if i >= k:
                    continue

                if i > k:
                    _w = self._get_vardict_index(f'w_{k}_{i}')
                else:
                    _w = self._get_vardict_index(f'w_{i}_{k}')

                self.model.addRow(-inf, 1,
                                  3,
                                  np.array([_w,
                                            self._get_vardict_index(f'x_{n1}_{n2}'),
                                            self._get_vardict_index(f'x_{n2}_{n1}')]),
                                  np.array([1, 1, 1])
                                  )

        # \sum_{i in N :  i\not=j } x_ij * c_i >= y_j * F_min forall j in N
        for j in self.data.G.nodes:
            _vars = []
            _varvalues = []
            for i in self.data.G.nodes:
                if i == j:
                    continue
                _vars.append(self._get_vardict_index(f'x_{i}_{j}'))
                _varvalues.append(self.data.get_weight_node(i))

            self.model.addRow(0, inf,
                              len(_vars) + 1,
                              np.array(
                                  [self._get_vardict_index(f'y_{j}')] + _vars
                              ),
                              np.array([-self.data.Fmin] + _varvalues)
                              )


    def _add_variable_dict_element(self, name):
        self.vardict[name] = len(self.vardict)

    def _add_variable(self, lb, ub, obj, vartype, name):
        el = self.model.addVariable(lb, ub,
                                   obj = obj,
                                   type=vartype,
                                   name=name)
        self._add_variable_dict_element(name)

        return el

    def _get_vardict_index(self, name):
        return self.vardict[name]

    def run(self, timelimit=60, label_sol : list = None,
            init_sol : AdalinaZoningSolution = None):

        self.solution = None
        self.model.setOptionValue("time_limit",
                                  timelimit)
        self.warmstartsol = init_sol

        if label_sol is None and init_sol is None:
            heur_start = time.time()
            logging.debug("start constructive heuristic")
            constr_sol = AdalinaZoningSolution(self.data)
            if constr_sol.constructive():
                label_sol = constr_sol.labels_
                self.warmstartsol = constr_sol
            else:
                logging.debug("constructive heuristic FAILED")
            logging.debug(f"constructive heuristic ended in {time.time() - heur_start}")

        elif label_sol is None and init_sol is not None:
            label_sol = init_sol.labels_

        if label_sol is not None:
            xwarmstart = []
            for el in np.unique(label_sol):
                areas = np.where(label_sol==el)[0]
                xwarmstart.append(self._get_vardict_index(f'y_{areas[0]}'))
                for i, _el in enumerate(areas):
                    for j in range(i+1, areas.shape[0]):
                        xwarmstart.append(self._get_vardict_index(f'x_{_el}_{areas[j]}'))

            xwarmstart = np.array(xwarmstart, dtype=int)
            self.model.setSolution(xwarmstart.shape[0], xwarmstart, np.ones(xwarmstart.shape[0]))

        # start_time = time.time()

        self.solution = None
        self.run_status = self.model.run()

        self.get_solution(run_model=False)

        return self.run_status

    def _build_solution(self):
        self.solution = AdalinaZoningSolution(self.data)
        allvars = self.model.getVariables()

        _repr = []
        for varname, varindex in self.vardict.items():

            if not varname.startswith("y_"):
                continue

            val = self.model.variableValue(allvars[varindex])
            if val < 1e-5:
                continue

            l = varname.split("_")

            _repr.append(int(l[1]))

        for r in _repr:
            self.solution.add_repr(r, True)

        for varname, varindex in self.vardict.items():

            if not varname.startswith("x_"):
                continue

            val = self.model.variableValue(allvars[varindex])
            if val < 1e-5:
                continue

            l = varname.split("_")

            self.solution.add_belonging(int(l[1]), int(l[2]))

        for varname, varindex in self.vardict.items():

            if not varname.startswith("w_"):
                continue

            val = self.model.variableValue(allvars[varindex])
            if val < 1e-5:
                continue

            l = varname.split("_")

            if not self.solution.check_nodes_belong_same_cluster([int(l[1]), int(l[2])]):
                continue

            self.solution.add_edge(int(l[1]), int(l[2]))

        return self.solution.check_feasibility()

    def get_solution(self, run_model=True):

        if self.solution is not None:
            return self.solution

        info = self.model.getInfo()
        if (self.run_status == highspy.HighsStatus.kOk or
              (self.run_status == highspy.HighsStatus.kWarning and
               info.primal_solution_status == highspy.SolutionStatus.kSolutionStatusFeasible)):

            logging.debug(f"obj. fun. value {self.model.getObjectiveValue()}")

            if self._build_solution():
                logging.debug("solution feasible!")
                return self.solution
            else:
                logging.debug("model solved but solution infeasible!")

        elif self.run_status == highspy.HighsStatus.kError:

            logging.debug("model ended with Error")

        if self.solution is None and run_model:
            self.run()
            return self.get_solution(run_model=False)

        if self.solution is not None:
            return self.solution
        elif self.warmstartsol is not None:
            return self.warmstartsol
        else:
            logging.debug("no solution available. run model with function run()")
            return None
