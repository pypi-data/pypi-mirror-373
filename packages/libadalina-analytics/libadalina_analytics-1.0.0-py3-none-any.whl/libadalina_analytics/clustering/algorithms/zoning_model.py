from clustering.models.adalina_zoning_data import AdalinaZoningData
from clustering.models.adalina_zoning_solution import AdalinaZoningSolution

import highspy
import numpy as np
import time
import logging
from sklearn.cluster import AgglomerativeClustering

hscb = highspy.cb

# model.callbacks
# highspy.highs.HighsCallback

"""
    sum_{(s,t) in E : s in S, t in T x_{st} >= x_{ij} 
    forall cut [S,T] : i in S, j in T
"""

# def lazy_SEC_constraint(callback_type : hscb.HighsCallbackType,
#                   message : str,
#                   data_out : hscb.HighsCallbackDataOut,
#                   data_in : hscb.HighsCallbackDataOut,
#                   user_callback_data : object) -> None:
#
#     if callback_type == hscb.HighsCallbackType.kCallbackMipSolution:
#         print("callback mip_solution")
#         print(data_out.mip_solution.to_array(len(user_callback_data.vardict)))
#
#         # print("obj. fun callback ", data_out.objective_function_value)
#         # print("obj. fun callback ", data_out.running_time)
#
#         assert isinstance(user_callback_data, AdalinaZoningModel)
#
#         # if not user_callback_data._build_solution():
#         #    if len(user_callback_data.solution.unconnected_clusters) > 0:
#
#                 # costruisci gomory-hu su G con i valori delle x
#                 # per ogni cluster disconnesso:
#                 # per ogni coppia di nodi
#
#         #        for cl in user_callback_data.solution.unconnected_clusters:
#         #            print(cl)
#
#         pass
#
#     # elif callback_type == hscb.kCallbackMipDefineLazyConstraints:
#     #    print("LAZY CONSTRAINT")

# VAR
# x_ij {1 if i in cluster with representative j, 0 otherwise}
# y_j {1 if j is representative of a cluster, 0 otherwise}

# Kmin <= sum{j in N} y_j <= Kmax
# sum{j in N} x_ij + y_i = 1 forall i in N
# x_{ij} <= sum{k in N : k in adj(i) and dist^-(k, j) <= dist^-(i,j) } forall (i,j) : i not in adj(j)
# x_{ik} + x_{jk} <= 1 + w_{ij} forall i,j,k in N^3 : i \not= j \not= k
# x_{ik} + w_{ik} <= 1 forall (i,k) in N^2 : i \not= k
# min \sum{(i,j) \in N^2 : i \not= j} c[i,j] * (x_{ij} + w_{ij})
# \sum_{i in N :  i\not=j } x_ij * c_i >= y_j * F_min forall j in N

class AdalinaZoningModel:

    def __init__(self, data : AdalinaZoningData,  log_fout = None):

        self.log_fout = log_fout
        self.data = data
        self.vardict = dict()
        self.model = highspy.Highs()
        inf = highspy.kHighsInf
        self.run_status = None
        self.solution = None
        self.best_feasible_sol = None

        xvar = []
        for (i,j) in data.E1:
            xvar.append(
                self._add_variable(0, 1,
                    data.get_cost_edge(i,j),
                    highspy.HighsVarType.kInteger,
               f"x_{i}_{j}")
            )

        # y[s] in {0,1}
        zvar = []
        firstnode = True
        for i in data.G.nodes:
            if firstnode:
                zvar.append(
                    self._add_variable(1,1, 0,
                                       highspy.HighsVarType.kInteger,
                                     f"z_{i}")
                                 )
                firstnode = False
            else:
                zvar.append(
                    self._add_variable(0,1, 0,
                                       highspy.HighsVarType.kInteger,
                                     f"z_{i}")
                                 )

        # x_{ij} + x_{jk} - x_{ik} \le 1  & \forall i, j, k \in V \colon (i,j), (j,k), (i,k) \in E'
        for i in data.G.nodes:
            for j in data.edges[i]:
                for k in data.edges[j]:
                    if k <= i:
                        continue

                    for el in range(3):
                        _varvalues = [1]*3
                        _varvalues[el] = -1
                        self.model.addRow(-inf, 1, 3,
                                          np.array([
                                              self._get_vardict_index(f'x_{i}_{j}'),
                                              self._get_vardict_index(f'x_{j}_{k}'),
                                              self._get_vardict_index(f'x_{i}_{k}')
                                          ]),
                                          np.array(_varvalues)
                                          )

        # \sum_{(i,j) \in E'} w_j x_{ij}  \ge \left(F^{\min} - w_i\right) z_i & \forall i \in V
        for i in data.G.nodes:
            _vars = [self._get_vardict_index(f'z_{i}')]
            _varvalues = [- self.data.Fmin + self.data.get_weight_node(i)]
            for j in data.edges[i]:
                _vars.append(self._get_vardict_index(f'x_{i}_{j}'))
                _varvalues.append(self.data.get_weight_node(j))

            self.model.addRow(0, +inf, len(_vars),
                              np.array(_vars),
                              np.array(_varvalues)
                              )

        # \sum_{j \in V \colon j <= i} x_{ji} \le |V| (1-z_i) & \forall i \in V
        for i in data.G.nodes:
            _vars = [self._get_vardict_index(f'z_{i}')]
            _varvalues = [self.data.V]
            for j in data.G.nodes:
                if j >=i:
                    continue

                _vars.append(self._get_vardict_index(f'x_{j}_{i}'))
                _varvalues.append(1)

            self.model.addRow(-inf, self.data.V,
                              len(_vars),
                              np.array(_vars),
                              np.array(_varvalues)
                              )

        # \sum_{j\in V \colon j <= i} x_{ji} + z_i \ge 1 & \forall i \in V
        for i in data.G.nodes:
            _vars = [self._get_vardict_index(f'z_{i}')]
            _varvalues = [1]
            for j in data.G.nodes:
                if j >=i:
                    continue

                _vars.append(self._get_vardict_index(f'x_{j}_{i}'))
                _varvalues.append(1)

            self.model.addRow(1, inf,
                              len(_vars),
                              np.array(_vars),
                              np.array(_varvalues)
                              )

        # K^{\min} \le \sum_{i\in V} z_i \le K^{\max}
        _vars = [self._get_vardict_index(f'z_{i}') for i in data.G.nodes]
        _varvalues = np.ones(self.data.V)
        self.model.addRow(self.data.Kmin, self.data.Kmax,
                          len(_vars),
                          np.array(_vars),
                          np.array(_varvalues)
                          )

        # self.model.setCallback(lazy_SEC_constraint, self)
        # self.model.startCallback(hscb.HighsCallbackType.kCallbackMipSolution)
        # self.model.startCallback(hscb.HighsCallbackType.kCallbackMipDefineLazyConstraints)


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

    def run(self, timelimit=60, label_sol = None):

        self.solution = None
        self.model.setOptionValue("time_limit",
            #highspy.HighsOptions.time_limit,
                                  timelimit/5)

        if label_sol is None:
            try:
                agglom_clust = AgglomerativeClustering(linkage='average',
                                                metric='precomputed',
                                                n_clusters=self.data.Kmax).fit(self.data.node_pairs_costs_df)

                label_sol = agglom_clust.labels_
            except:
                logging.debug("AgglomaritveClustering failed!", self.log_fout)
                pass

        if label_sol is not None:
            xwarmstart = []
            for el in np.unique(label_sol):
                areas = np.where(label_sol==el)[0]
                xwarmstart.append(self._get_vardict_index(f'z_{areas[0]}'))
                for i, _el in enumerate(areas):
                    for j in range(i+1, areas.shape[0]):
                        xwarmstart.append(self._get_vardict_index(f'x_{_el}_{areas[j]}'))

            xwarmstart = np.array(xwarmstart, dtype=int)
            self.model.setSolution(xwarmstart.shape[0], xwarmstart, np.ones(xwarmstart.shape[0]))

        start_time = time.time()

        while True:
            self.solution = None
            self.run_status = self.model.run()

            self.get_solution(run_model=False)

            if self.solution is None:
                break

            if time.time() - start_time > timelimit:
                break

            if not self.solution.is_feasible and len(self.solution.unconnected_clusters) > 0:
                # costruisci gomory-hu su G con i valori delle x
                # per ogni cluster disconnesso:
                # per ogni coppia di nodi

                xvarvaluedict = dict()
                allvars = self.model.getVariables()

                for e in self.data.G.edges:
                    xvarvaluedict[e] = self.model.variableValue(allvars[self._get_vardict_index(f'x_{e[0]}_{e[1]}')])

                self.data.gomory_hu(xvarvaluedict)

                for cl in self.solution.unconnected_clusters:
                    # for u, v in zip(cl, cl[1:]):
                    for i, u in enumerate(cl):
                        for j in range(i+1, len(cl)):
                            v = cl[j]

                            if (u, v) in self.data.G.edges:
                                continue

                            _, (S, T) = self.data.minimum_edge_weight_in_shortest_path(u, v)

                            # sum_{(s,t) in E : s in S, t in T x_{st} >= x_{ij}
                            #     forall cut [S,T] : i in S, j in T
                            _vars = []
                            _varvalues = [-1]

                            if u < v:
                                _vars.append(self._get_vardict_index(f'x_{u}_{v}'))
                            elif u > v:
                                _vars.append(self._get_vardict_index(f'x_{v}_{u}'))

                            for s in S:
                                for t in T:
                                    if (s,t) in self.data.G.edges:
                                        if s < t:
                                            _vars.append(self._get_vardict_index(f'x_{s}_{t}'))
                                        else:
                                            _vars.append(self._get_vardict_index(f'x_{t}_{s}'))
                                        _varvalues.append(1)

                            # print_log("adding new cut" )
                            self.model.addRow(0, +highspy.kHighsInf,
                                              len(_vars),
                                              np.array(_vars),
                                              np.array(_varvalues)
                                              )

                # self.model.writeModel("/home/marco/Desktop/prova.lp")
            else:
                break

        return self.run_status

    def _build_solution(self):
        self.solution = AdalinaZoningSolution(self.data)
        allvars = self.model.getVariables()

        _repr = []
        for varname, varindex in self.vardict.items():

            val = self.model.variableValue(allvars[varindex])
            if val < 1e-5:
                continue

            l = varname.split("_")

            if l[0].startswith('x'):
                self.solution.add_edge(int(l[1]), int(l[2]))
            elif l[0].startswith('z'):
                _repr.append(int(l[1]))

        for r in _repr:
            self.solution.add_repr(r)

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

            else:
                logging.debug("model solved but solution infeasible!")

            return self.solution

        elif self.run_status == highspy.HighsStatus.kError:

            logging.debug("no solution available. model ended with Error")
            return None

        if self.solution is None and run_model:

            self.run()
            return self.get_solution(run_model=False)

        logging.debug("no solution available. run model with function run()")
        return None
