
from collections import defaultdict
import numpy as np
from .adalina_zoning_data import AdalinaZoningData
import time
import logging


class AdalinaZoningSolution:

    def __init__(self, data : AdalinaZoningData):
        self.data = data
        self.gdf_export = None

        self.labels = dict()
        self.weights = defaultdict(float)
        self.intraclust_distance = defaultdict(float)

        self.representatives = dict()
        self._K = -1

        self.cl_dict_set = None
        self.cl_dict_list = None
        self.infeasibilities = None
        self.is_feasible = False

        self.unconnected_clusters = []

        self.constr_heur_starttime = None

    def _check_timelim(self, timelimit):

        return time.time() - self.constr_heur_starttime <= timelimit

    def constructive(self, timelimit = 60, fout_log =  None):

        self.constr_heur_starttime = time.time()

        try:

            # get Kmax representative maximizing average distance?
            R = []
            WR = []
            n = self.data.node_pairs_costs_df.to_numpy()
            iv = n.max(axis=0)
            i = iv.argmax()
            j = n[i].argmax()

            i = int(i)
            R.append(i)
            WR.append(self.data.get_weight_node(i))
            j = int(j)
            R.append(j)
            WR.append(self.data.get_weight_node(j))

            while len(R) < self.data.Kmax and self._check_timelim(timelimit):
                v = n[:, R].mean(axis=1)

                m = None
                mi = None
                for i, el in enumerate(v):
                    if i in R:
                        continue
                    if m is None or el > m:
                        m = el
                        mi = i

                if mi is None:
                    break

                R.append(mi)
                WR.append(self.data.get_weight_node(mi))

            if not self._check_timelim(timelimit):
                return False

            R = np.array(R)
            WR = np.array(WR)
            R = R[np.argsort(WR)[::-1]]
            WR = np.sort(WR)[::-1]

            A = []
            k = 0
            N = list(self.data.G.nodes.keys())
            C = defaultdict(list)
            all_weights = dict()
            for n in N:
                if n in R:
                    continue
                all_weights[n]=self.data.get_weight_node(n)

            # self.data.Fmin = 3

            for j, r in enumerate(R):
                if len(C) >= self.data.Kmin or np.setdiff1d(N, R.tolist() + A).shape[0] == 0:
                    break

                wr = WR[j]
                C[r].append(r)

                if wr >= self.data.Fmin:
                    continue
                else:
                    i = 0
                    while i < len(C[r]) and self._check_timelim(timelimit):
                        r_el = C[r][i]
                        i += 1
                        #while wr < self.data.Fmin and np.setdiff1d(N, R.tolist() + A).shape[0] > 0:
                        wmax = []
                        wmaxi = []

                        for nk in self.data.G.neighbors(r_el): #, nw in all_weights.items():
                            if nk in A or nk in R:
                                continue
                            wmax.append(all_weights[nk])
                            wmaxi.append(nk)

                        if len(wmax) == 0:
                            continue

                        # wmax = np.array(wmax)
                        wmaxi = np.array(wmaxi)
                        wmaxi = wmaxi[np.argsort(wmax)[::-1]]
                        wmax = np.sort(wmax)[::-1]

                        for k, el in enumerate(wmax):
                            if wr + wmax[:(k+1)].sum() >= self.data.Fmin:
                                break

                        for l in range(k+1):
                            A.append(wmaxi[l])
                            C[r].append(wmaxi[l])
                            wr += wmax[l]

                        if wr >= self.data.Fmin:
                            break

                    if wr < self.data.Fmin:
                        for el in C[r]:
                            if el in A:
                                A.remove(el)
                            elif el in R:
                                i_el = np.where(R == el)[0][0]
                                R = np.concatenate((R[:i_el], R[(i_el+1):]))
                                # R.remove(el)
                        del(C[r])

            if len(C) < self.data.Kmin:
                return False

            if not self._check_timelim(timelimit):
                return False

            # aggiungi nodi mancanti ai cluster presenti, uno alla volta
            # aggiungendo per primo il nodo adiacente a un cluster con distanza minore
            # 1 - libera candidati rappresentanti non in C
            R = list(C.keys()) # np.setdiff1d(R, list(C.keys()))
            # 2 -
            while len(A) + len(R) < self.data.V and self._check_timelim(timelimit):

                dval = defaultdict(list)
                vval = defaultdict(list)
                for k, el in C.items():
                    vicini_esterni = {
                        v for u in el for v in self.data.G.neighbors(u)
                        if v not in el and v not in R and v not in A
                    }
                    for v in vicini_esterni:
                        val = self.data.node_pairs_costs_df.loc[v, el].sum()
                        dval[k].append(val)
                        vval[k].append(v)

                    if len(dval[k]) == 0:
                        continue

                    # dval[k] = np.array(dval[k])
                    vval[k] = np.array(vval[k])[np.argsort(dval[k])]
                    # dval[k] = np.sort(dval[k])

                    C[k].append(vval[k][0])
                    A.append(vval[k][0])

                # C[minvc].append(minvi)
                # A.append(minvi)

            if not self._check_timelim(timelimit):
                return False

            for k, el in C.items():
                for i, n in enumerate(el):
                    for j in range(i+1, len(el)):
                        n2 = el[j]
                        self.add_edge(n, n2)
                self.add_repr(k)

            return self.check_feasibility()

        except: # Exception as e:
            logging.error("constructive heuristic failed!")

        return False

    @property
    def labels_(self):
        _l = []
        for i, k in enumerate(self.data.G.nodes):
            _l.append(self.labels[k])
        return _l

    def get_K(self):
        return self._K + 1

    def add_belonging(self, i, k):

        if i in self.labels and self.labels[i] != k:
            raise ValueError("")

        self.labels[i] = k
        self.intraclust_distance[k] += self.data.get_cost_edge(i, k)

    def check_nodes_belong_same_cluster(self, nodes: list):

        nodes_k = [self.labels[n]  for n in nodes if n in self.labels]
        k = nodes_k[0]
        return all([el == k for el in nodes_k])

    def add_edge(self, i, j):

        k = -1
        if i in self.labels:
            k = self.labels[i]
        if j in self.labels:
            if k != -1 and k != self.labels[j]:
                raise ValueError(f"ERROR: nodi {i} e {j} già presenti in cluster diversi: {k}, {self.labels[j]}")

            k = self.labels[j]

        if k == -1:
            self._K += 1
            k = self._K

        self.labels[i] = k
        self.labels[j] = k
        self.intraclust_distance[k] += self.data.get_cost_edge(i,j)

    def add_repr(self, i, self_index=False):
        if i not in self.labels:
            self._K += 1
            i_index = self._K
            if self_index:
                i_index = i
            self.labels[i] = i_index

        self.representatives[i] = self.labels[i]

    def __repr__(self):
        top = f"{self.get_K()} cluster \n"

        if self.get_K() <= 0:
            return top

        if self.cl_dict_set is None:
            self.build_cluster_representations()

        top += "{ \n"
        for ck, cv in self.cl_dict_list.items():
            top += f" {ck} : ["
            top += ','.join([str(el) for el in list(cv)])
            top += '], \n'
        top += "}\n"

        if self.infeasibilities is not None and len(self.infeasibilities) > 0:
            top += "INFEASIBILITIES: \n"
            for el in self.infeasibilities:
                top += el + "\n"

        return top

    def to_json(self):

        # cl = self.get_clustering()

        j = dict()
        j['clusters'] = []

        for k, v in self.cl_dict_list.items():
            j['clusters'].append({
                'representative' : k,
                "nodes" : v,
                "distance" : self.intraclust_distance[k],
                "weight" : self.weights[k]
            }
        )

        return j

    # def get_clustering(self):
    #     cl = self.build_cluster_representations()
    #     ser_cl = None
    #     if cl is not None:
    #         ser_cl = dict()
    #         for k, v in self.cl_dict_set.items():
    #             ser_cl[k] = list(v)
    #
    #         self.data.gdf = self.data.gdf.add_clustering(ser_cl)
    #
    #     return ser_cl

    def build_cluster_representations(self):

        if self.cl_dict_set is not None:
            return # self.cl_dict_set

        self.cl_dict_set = dict()
        self.cl_dict_list = dict()

        for rk, rv in self.representatives.items():
            self.cl_dict_set[rv] = set()
            self.cl_dict_set[rv].add(rk)

        for lk, lv in self.labels.items():
            self.cl_dict_set[lv].add(lk)
            self.weights[lv] += self.data.get_weight_node(lk)

        for k, val in self.cl_dict_set.items():
            self.cl_dict_list[k] = list(val)

        self.gdf_export = self.data.add_clustering(self.labels)

        # return self.cl_dict_set

    def get_dataframe_to_export(self):
        return self.gdf_export

    def check_feasibility(self):

        self.build_cluster_representations()

        self.unconnected_clusters = []

        self.infeasibilities = []
        self.is_feasible = True

        missing_nodes = [ k for k in self.data.G.nodes if k not in self.labels ]
        if len(missing_nodes) > 0:
            self.is_feasible = False
            self.infeasibilities.append(
                f"nodi non assegnati a cluster : {missing_nodes}"
            )

        if self.get_K() < self.data.Kmin:
            self.infeasibilities.append(
                f"numero di cluster {self.get_K()} minore del lower bound {self.data.Kmin}"
            )
            self.is_feasible = False

        if self.get_K() > self.data.Kmax:
            self.infeasibilities.append(
                f"numero di cluster {self.get_K()} maggiore dell'upper bound {self.data.Kmax}"
            )
            self.is_feasible = False

        for ck, cv in self.cl_dict_set.items():
            if not self.data.check_nodes_subset_connected(list(cv)):
                self.infeasibilities.append(
                    f"cluster non connesso [" + ','.join([str(el) for el in list(cv)]) +  "]"
                )
                self.unconnected_clusters.append(list(cv))
                self.is_feasible = False

            peso_minimo = 0
            for el in cv:
                peso_minimo += self.data.get_weight_node(el)
            if peso_minimo < self.data.Fmin:
                self.infeasibilities.append(
                    f"cluster con peso totale {peso_minimo} minore del consentito {self.data.Fmin}"
                )
                self.is_feasible = False

        return self.is_feasible