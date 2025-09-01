#!/usr/bin/env python3
import highspy
import numpy as np
import logging
from ..models import AdalinaData, AdalinaModelType, AdalinaSolution

class AdalinaModelHighs:

    def __init__(self, data : AdalinaData,
                 modeltype : AdalinaModelType = AdalinaModelType.MINSUM_ALLCOST,
                 ub_unserved = None,
                 ub_sum_assigned_distance = None,
                 log_fout = None):

        self.usagevar = None
        self.constr_UB_rhomax = None
        self.model_status = None
        self.log_fout = log_fout

        assert isinstance(data, AdalinaData)
        assert isinstance(modeltype, AdalinaModelType)

        self.modeltype = modeltype

        self.solution = None
        self.run_status = None
        self.objective_value = None

        self.rhomaxvar = None
        self.data = data

        self.vardict = {}
        self.varindex = {}
        self.dict_rownames = {}
        self.count_deletedrows = 0
        self.model = highspy.Highs()
        inf = highspy.kHighsInf

        ###
        ### VARIABLES
        ###

        logging.debug("INIT VARIABLES")

        logging.debug("x")

        # x[s,a] in [0,1]
        self.xvar = []
        for s in self.data.S:
            _xvar = []

            if not self.data.get_shelter_usable(s):
                continue

            for a in self.data.A:

                if not data.get_is_reachable(s, a):
                    continue

                _xvar.append(
                    self._add_variable(0, 1,
                        self._set_xvar_objfun_coeff(s,a),
                        highspy.HighsVarType.kContinuous,
                   f"x_{s}_{a}")
                )
            self.xvar.append(_xvar)

        logging.debug("rho")

        # rho[s,s,r] in [0,1]
        self.rhovar = []
        for s in self.data.S:
            _rhovar = []
            for s1 in self.data.S:

                if not self.data.get_transport_possible(s, s1):
                    continue

                _rhovarS = []
                for r in self.data.R:
                    _rhovarS.append(
                        self._add_variable(0,1,
                                           self._set_rhovar_objfun_coeff(s,s1,r),
                                           highspy.HighsVarType.kContinuous,
                                           f"rho_{s}_{s1}_{r}"
                                           )
                    )
                _rhovar.append(_rhovarS)
            self.rhovar.append(_rhovar)

        logging.debug("y")

        # y[s] in {0,1}
        self.yvar = []
        for s in self.data.S:
            self.yvar.append(
                self._add_variable(0,1,
                                   self._set_yvar_objfun_coeff(s),
                                   # self.data.get_fixed_cost_shelter(s),
                                   highspy.HighsVarType.kInteger,
                                 f"y_{s}")
                             )

        logging.debug("w")

        # w[a] in [0,1]
        self.wvar = []
        for a in self.data.A:
            self.wvar.append(
                self._add_variable(0,1,
                                   self._set_wvar_objfun_coeff(a),
                                   #self.data.get_cost_notserved(a)*self.data.get_area_demand(a),
                                   highspy.HighsVarType.kContinuous,
                                   name=f"w_{a}")
            )

        logging.debug("z")

        # z[s,r] in R >= 0
        self.zvar = []
        for s in self.data.S:
            _zvar = []
            for r in self.data.R:
                _zvar.append(
                    self._add_variable(0, inf,
                                       self._set_zvar_objfun_coeff(s),
                                       # self.data.get_cost_exceed_cap(s),
                                       highspy.HighsVarType.kContinuous,
                                       f"z_{s}_{r}")
                )
            self.zvar.append(_zvar)

        ###
        ### CONSTRAINTS
        ###

        logging.debug("INIT CONSTRAINTS")

        logging.debug("demand cover")

        # forall a in A:  sum{s in S} r[s,a] x[s,a] + w[a] = 1
        # self.constr_cover = []
        for i, a in enumerate(self.data.A):

            _varlist = [self._get_vardict_index(f'x_{s}_{a}')
                            for s in self.data.S if self.data.get_is_reachable(s, a)]

            self._my_add_row(1.0,1.0,
                              len(_varlist)+1,
                              _varlist +
                                [ self._get_vardict_index(f'w_{a}') ],
                              np.array([1]*(len(_varlist)+1)),
                              name = f"res_usage_{i}"
                              )

        logging.debug("resource usage")

        # forall s in S, r in S: n[r] sum{a in A} d[a]x[s,a] - sum{s1 in S} rho[s1, s, r] * o[s1,r] - z[s,r] <= 0
        # self.constr_maxcap = []
        for i,s in enumerate(self.data.S):
            # self.constr_maxcap.append([])
            for j, r in enumerate(self.data.R):

                _vars = []
                _varvalues = []
                for a in self.data.A:

                    if not self.data.get_is_reachable(s, a):
                        continue

                    val = self.data.get_area_demand(a) * self.data.get_resource_need(r)
                    if val > 1e-5:
                        _vars.append(self._get_vardict_index(f'x_{s}_{a}'))
                        _varvalues.append(val)

                for s1 in self.data.S:
                    if self.data.get_transport_possible(s1, s) and self.data.get_shelter_usable(s):

                        _val = data.get_resource_available(s1, r)

                        if _val > 1e-5:
                            _varvalues.append(-data.get_resource_available(s1, r))
                            _vars.append(self._get_vardict_index(f'rho_{s1}_{s}_{r}'))

                self._my_add_row(-inf, 0,
                              len(_vars) + 1,
                              _vars +
                               [ self._get_vardict_index(f'z_{s}_{r}') ],
                              np.array(_varvalues + [-1]),
                            f"usage_res_f{i}_r{j}"
                   )

        logging.debug("not exceeding initial resources")

        # forall s in S, r in R: sum[s1 in S] rho[s,s1,r] <= 1
        for i, s in enumerate(self.data.S):
            for j, r in enumerate(self.data.R):
                _vars = []
                for s1 in self.data.S:
                    varname = f'rho_{s}_{s1}_{r}'
                    if not self._check_vardict_exists(varname):
                        continue
                    _vars.append(self._get_vardict_index(f'rho_{s}_{s1}_{r}'))

                if len(_vars) == 0:
                    continue

                self._my_add_row(-inf, 1,
                                      len(_vars),
                                      _vars,
                                      np.ones(len(_vars), dtype=int),
                                 f"max_usage_f{s}_r{r}"
                )


        logging.debug("link z and y")

        for i, s in enumerate(self.data.S):

            if self.data.get_shelter_usable(s):

                #self.constr_link_zy.append(
                for j, r in enumerate(self.data.R):
                    self._my_add_row(-inf, 0,
                                          2,
                                          np.array([self._get_vardict_index(f'z_{s}_{r}'),
                                           self._get_vardict_index(f'y_{s}')
                                             ]),
                                            np.array(
                                                [1,
                                                 -self.data.get_bigMdemand()
                                                 ]
                                            ),
                                     f"link_zy_f{i}_r{j}"
                                          )

        logging.debug("forbidden assignments")

        # forall s in S, a in A: x[s,a] <= r[a,s]
        # for s in self.data.S:
        #     for a in self.data.A:
        #         if not self.data.get_is_reachable(s, a):
        #             self._set_variable_to_value(f'x_{s}_{a}', 0)

        logging.debug("link rho y, forbidden relocation")

        # forall s, s1 in S, r in R:   rho[s,s1,r] - r[s,s1] bar y[s1] y[s1] <= 0
        #self.constr_no_transport_unreachable = []
        #self.constr_link_rhoy = []
        for i, s in enumerate(self.data.S):
            #self.constr_no_transport_unreachable.append([])
            #self.constr_link_rhoy.append([])
            for j, s1 in enumerate(self.data.S):

                if not self.data.get_transport_possible(s, s1) or not self.data.get_shelter_usable(s1):

                    #self.constr_no_transport_unreachable[i].append([
                    for r in self.data.R:
                        varname = f'rho_{s}_{s1}_{r}'
                        if self._check_vardict_exists(varname):

                            self._set_variable_to_value(varname, 0)

                else:
                    #self.constr_link_rhoy[i].append([
                    for w, r in enumerate(self.data.R):
                        varname = f'rho_{s}_{s1}_{r}'
                        if self._check_vardict_exists(varname):
                            self._my_add_row(-inf, 0,
                                              2,
                                              [self._get_vardict_index(f'rho_{s}_{s1}_{r}'),
                                               self._get_vardict_index(f'y_{s1}')
                                               ],
                                              np.array([1, -1]),
                                             f"link_rho_y_from{i}_to{j}_r{w}"
                                              )


        if ub_unserved is not None:
            self.set_constr_ub_sumunserved(ub_unserved)

        if ub_sum_assigned_distance is not None:
            self.data.ub_total_assignment_distance = ub_sum_assigned_distance
            self.set_constr_ub_sumdist()

        logging.debug("INIT OBJECTIVE")

        if self.modeltype == AdalinaModelType.MIN_EXTRARESOURCES:
            # forall a in A: w[a] = 0
            self._set_w_to_zero()

        if self.modeltype == AdalinaModelType.MINSUM_UNSERVED:

            # set to 0 obj. coefficient of all variables except w[a]
            # self._reset_all_objcoeff(["w_"])

            self._set_z_to_zero()

        if self.modeltype == AdalinaModelType.MINMAX_UNSERVED:

            self._set_z_to_zero()

            # set to 0 obj. coefficient of all variables
            # self._reset_all_objcoeff()

            # add max w variable, only variable in the objective
            self.Wmaxvar = self._add_variable(0, +inf, 1,
                               highspy.HighsVarType.kContinuous, "Wmax")

            # add constraint Wmax >= d[a]w[a] forall a in A
            for i,a in enumerate(self.data.A):
                self._my_add_row(0, inf, 2,
                                  [self._get_vardict_index('Wmax'),
                                   self._get_vardict_index(f'w_{a}')],
                                  np.array([1, -self.data.get_area_demand(a)]),
                                 f"val_wmax_a{i}"
                                 )

        if self.modeltype == AdalinaModelType.MINMAX_USAGEFAC:
            self._set_z_to_zero()
            self._set_w_to_zero()

            self.set_model_minmax_rho()

        ###
        ### OBJECTIVE FUNCTION
        ###

        self.model.setMinimize()

    def _set_variable_to_value(self, varname, lbvalue, ubvalue=None):
        vari = self._get_vardict_index(varname)

        if ubvalue is None:
            ubvalue = lbvalue
        self.model.changeColBounds(vari, lbvalue, ubvalue)

    def _my_add_row(self, lb, ub, numvar, variables, varvalues, name):

        assert isinstance(name, str)

        self.model.addRow(lb, ub, numvar, variables, varvalues)
        self.model.passRowName(len(self.dict_rownames), name)
        self.dict_rownames[len(self.dict_rownames)] = name

    def reset_solution(self):
        self.solution = None
        self.run_status = None
        self.objective_value = None

    def set_model_minsum_unserved(self):
        self._set_z_to_zero()
        self.modeltype = AdalinaModelType.MINSUM_UNSERVED

        for a in self.data.A:
            i = self._get_vardict_index(f"w_{a}")
            self.model.changeColCost(i, self._set_wvar_objfun_coeff(a))

    def set_model_minmax_rho(self):

        inf = highspy.kHighsInf

        # add rho max variable, the only variable in the objective
        self.rhomaxvar = self._add_variable(0, +inf, 1,
                                            highspy.HighsVarType.kContinuous, "rhomax")

        # add constraint Wmax >= (sum{s1 in S, r in R} rho[s1,s,r]*o0[s1,r]) / sum{r in R} o0[s, r]   forall s in S

        logging.debug("constraint rho max")
        # self.constr_rhomax = []
        for i, s in enumerate(self.data.S):

            if not self.data.get_shelter_usable(s):
                continue

            _vars = [self._get_vardict_index('rhomax')]

            _val = self.data.resources_available.xs(s, level=0)["maximum"].sum()
            if _val < 1e-5:
                continue

            _varvalues = [_val]

            for r in self.data.R:
                for s1 in self.data.S:

                    varname = f'rho_{s1}_{s}_{r}'
                    if not self._check_vardict_exists(varname):
                        continue

                    _val = self.data.get_resource_available(s1, r)

                    if _val < 1e-5:
                        continue

                    _vars.append(self._get_vardict_index(varname))
                    _varvalues.append(-self.data.get_resource_available(s1, r))

            self._my_add_row(0, inf,
                              len(_vars),
                              _vars,
                              np.array(_varvalues),
                              f"link_rhomax_fac_{i}"
                              )


    def set_constr_ub_sumunserved(self, ub_unserved):
        logging.debug("constraint upper bound on amount of unserved demand")
        self._my_add_row(-highspy.kHighsInf, ub_unserved,
                              self.data.A_size,
                              [self._get_vardict_index(f'w_{a}') for a in self.data.A],
                              np.array([self.data.get_area_demand(a) for a in self.data.A]),
                         "UB_sum_unserved"
                              )

    def set_constr_ub_sumdist(self):

        logging.debug("constraint upper bound on amount of total transportation distance")

        _vars = []
        _varvalues = []
        for s in self.data.S:
            for a in self.data.A:

                _val = self.data.get_cost_assign(s, a) * self.data.get_area_demand(a)

                if _val > 1e-5:
                    _vars.append(self._get_vardict_index(f'x_{s}_{a}'))
                    _varvalues.append(self.data.get_cost_assign(s, a) * self.data.get_area_demand(a))

        # self.constr_ub_sum_assigned_distance = \
        self._my_add_row(-highspy.kHighsInf, self.data.ub_total_assignment_distance,
                              len(_vars),
                              _vars,
                              np.array(_varvalues),
                         "UB_sum_assign_dist")

    def reset_wvar_costs(self):
        for a in self.data.A:
            i = self._get_vardict_index(f"w_{a}")
            self.model.changeColCost(i, 0)

    def modify_model_to_minsumdist(self):

        # self.reset_solution()

        self.modeltype = AdalinaModelType.MINDIST_ASSIGNMENTS

        for a in self.data.A:
            for s in self.data.S:
                j = self._get_vardict_index(f"x_{s}_{a}")
                self.model.changeColCost(j,
                         self.data.get_cost_assign(s, a) * self.data.get_area_demand(a)
                )

    def modify_model_to_maxdist_unserved(self):

        self.modeltype = AdalinaModelType.MAXSUM_DIST_UNSERVED

        for a in self.data.A:
            for s in self.data.S:

                _ub = 1

                if not self.data.get_is_reachable(s, a):
                    _ub = 0

                self._add_variable(0,_ub,
                                   self.data.get_area_demand(a) * self.data.get_cost_assign(s,a),
                                   highspy.HighsVarType.kContinuous, f"w2_{a}_{s}")

        # sum{s in S} w[a,s] = w[a]
        for i, a in enumerate(self.data.A):
            _vars = [self._get_vardict_index(f"w_{a}")]
            _varvalues = [-1]

            for s in self.data.S:
                _vars.append(self._get_vardict_index(f"w2_{a}_{s}"))
                _varvalues.append(1)

            self._my_add_row(0,0,
                             len(_vars),
                             _vars,
                             _varvalues,
                             f"link_wa_was_{i}")

        # self.model.maximize()

    def reset_x_val_cost(self):
        # set to 0 obj. fun. coefficient of variables x
        for a in self.data.A:
            for s in self.data.S:
                j = self._get_vardict_index(f"x_{s}_{a}")
                self.model.changeColCost(j,0)

    def modify_model_to_minmax_usage_shelter(self):

        self.modeltype = AdalinaModelType.MINMAX_USAGEFAC
        self.set_model_minmax_rho()

    def reset_rhomax_var_objfun_coeff(self):
        rhoindex = self._get_vardict_index("rhomax")
        self.model.changeColCost(rhoindex, 0)

    def set_constr_ub_maxusage(self, value):

        self.data.ub_max_usage = value
        self._set_variable_to_value("rhomax", value)

    def modify_model_to_minsum_usage_shelter(self):

        self.modeltype = AdalinaModelType.MINSUM_USAGEFAC

        logging.debug("constraint rho max")
        # self.constr_UB_rhomax = []

        self.usagevar = []

        for i, s in enumerate(self.data.S):

            if not self.data.get_shelter_usable(s):
                continue

            _total_res = self.data.resources_available.xs(s, level=0)["maximum"].sum()
            if _total_res < 1e-5:
                continue

            self.usagevar.append(self._add_variable(0, self.data.ub_max_usage, 1,
                                                highspy.HighsVarType.kContinuous,
                                                     f"usagevar_{s}")
                                  )

            _vars = [self._get_vardict_index(f"usagevar_{s}")]
            _varvalues = [-_total_res]

            for r in self.data.R:
                for s1 in self.data.S:

                    _val = self.data.get_resource_available(s1, r)

                    if _val < 1e-5:
                        continue

                    _varname = f'rho_{s1}_{s}_{r}'

                    if not self._check_vardict_exists(_varname):
                        continue

                    _index = self._get_vardict_index(_varname)

                    # * self.data.get_cost_resource_transport(s1, s, r))

                    _vars.append(_index)
                    _varvalues.append(self.data.get_resource_available(s1, r))


            self._my_add_row(-highspy.kHighsInf, 0,
                              len(_vars),
                              _vars,
                              np.array(_varvalues),
                             f"UB_usage_f{i}"
                              )

    def set_UB_minsum_usage(self):
        _vars = []
        _varvalues = []
        for s in self.data.S:

            if not self.data.get_shelter_usable(s):
                continue

            _total_res = self.data.resources_available.xs(s, level=0)["maximum"].sum()
            if _total_res < 1e-5:
                continue

            _i = self._get_vardict_index(f"usagevar_{s}")

            self.model.changeColCost(_i, 0)

            _vars.append(_i)
            _varvalues.append(1)

        self._my_add_row(-highspy.kHighsInf, self.data.ub_sum_usage,
                          len(_vars), _vars, np.array(_varvalues),
                         "UB_sum_usage")

    def modify_model_to_minsum_relocation_costs(self):

        self.modeltype = AdalinaModelType.MINSUM_RELOCATION

        for s in self.data.S:
            for s1 in self.data.S:
                if s == s1:
                    continue
                for r in self.data.R:

                    _varname = f"rho_{s}_{s1}_{r}"

                    if not self._check_vardict_exists(_varname):
                        continue

                    self.model.changeColCost(
                        self._get_vardict_index(_varname),
                        self._set_rhovar_objfun_coeff(s, s1, r)
                    )

    def _set_zvar_objfun_coeff(self, shelter):

        if self.modeltype == AdalinaModelType.MIN_EXTRARESOURCES:
            return 1

        if self.modeltype != AdalinaModelType.MINSUM_ALLCOST:
            return 0

        return self.data.get_cost_exceed_cap(shelter)

    def _set_wvar_objfun_coeff(self, area):

        if self.modeltype == AdalinaModelType.MINSUM_UNSERVED:
            return self.data.get_area_demand(area)

        if self.modeltype != AdalinaModelType.MINSUM_ALLCOST:
            return 0

        return self.data.get_cost_notserved(area) * self.data.get_area_demand(area)

    def _set_yvar_objfun_coeff(self, shelter):

        if self.modeltype != AdalinaModelType.MINSUM_ALLCOST:
            return 0

        return self.data.get_fixed_cost_shelter(shelter)

    def _set_xvar_objfun_coeff(self, shelter, area ):

        #if self.modeltype in [AdalinaModelType.MINDIST_ASSIGNMENTS, AdalinaModelType.MINSUM_ALLCOST] :
        return self.data.get_demcost_assign(shelter,area, self.modeltype)# *self.data.get_area_demand(area)

        # return 0

    def _set_rhovar_objfun_coeff(self, shelter_from, shelter_to, resources):

        return self.data.get_cost_resource_transport(shelter_from, shelter_to, resources, self.modeltype)

    def reset_all_objcoeff(self, noreset_prefix = None):
        # set to 0 obj. coefficient of all variables
        for i, var in enumerate(self.model.getVariables()):
            if noreset_prefix is not None and sum([var.name.startswith(el) for el in noreset_prefix]) > 0:
                continue
            self.model.changeColCost(i, 0)

    def _set_w_to_zero(self):
        # forall a in A: w[a] = 0
        for a in self.data.A:
            self._set_variable_to_value(f'w_{a}', 0)

    def _set_z_to_zero(self):
        # set to 0 variable z
        for s in self.data.S:
            for r in self.data.R:
                self._set_variable_to_value(f'z_{s}_{r}', 0)

    def set_rhovar_to_zero(self):

        self.set_rhovar_by_distance_threshold(-1)

    def set_rhovar_by_distance_threshold(self, threshold ):
        for s in self.data.S:
            for s1 in self.data.S:
                if s == s1:
                    continue
                for r in self.data.R:

                    _varname = f"rho_{s}_{s1}_{r}"

                    if not self._check_vardict_exists(_varname):
                        continue

                    _facility_distance = self.data.get_facilities_distance(s, s1)
                    if _facility_distance is None:
                        self._set_variable_to_value(_varname, 0)

                    elif _facility_distance > threshold:
                        self._set_variable_to_value(_varname, 0)
                    else:
                        self._set_variable_to_value(_varname, 0, 1)

    def _add_variable_dict_element(self, name):
        _index = len(self.vardict)
        self.vardict[name] = _index
        self.varindex[_index] = name

        return _index

    def _add_variable(self, lb, ub, obj, vartype, name):
        var = self.model.addVariable(lb, ub,
                                   obj = obj,
                                   type=vartype,
                                   name=name)

        self._add_variable_dict_element(name)

        return  var

    def _check_vardict_exists(self, name):
        return name in self.vardict

    def _get_vardict_index(self, name):
        return self.vardict[name]

    def run(self, timelimit=60):

        logging.debug(f"INIT RUN WITH TIME LIMIT {timelimit} SECONDS")

        self.model.setOptionValue("time_limit",
            #highspy.HighsOptions.time_limit,
                                  timelimit)

        self.run_status = self.model.run()

        if self.run_status == highspy.HighsStatus.kOk:

            self.model_status = self.model.getModelStatus()

            if self.check_model_feasible():
                self.get_solution()
                return True
            else:
                logging.debug("solution not available")
                logging.debug(self.model_status)
                return False
        else:
            return False

    def _build_solution(self):

        logging.debug("building solution")

        self.solution = AdalinaSolution(self.objective_value) # self.model.getObjectiveValue())

        # allvars = self.model.getVariables()

        allvarvalues = np.array(self.model.variableValues(self.model.getVariables()))

        for varindex in np.where(allvarvalues > 1e-5)[0]:
            val = allvarvalues[varindex]
            varname = self.varindex[varindex]

            l = varname.split("_")

            if l[0].startswith('x'):
                self.solution.add_xvarvalue(l[1], l[2], val)
            elif l[0].startswith('y'):
                self.solution.add_yvarvalue(l[1], val)
            elif l[0] == 'w':
                self.solution.add_wvarvalue(l[1], val)
            elif l[0] == 'w2':
                self.solution.add_w2varvalue(l[1], l[2], val)
            elif l[0].startswith('z'):
                self.solution.add_zvarvalue(l[1], l[2], val)
            elif l[0] == 'rho':
                self.solution.add_rhovalue(l[1],l[2],l[3], val)
            elif self.modeltype == AdalinaModelType.MINMAX_UNSERVED:
                self.solution.set_wmaxvalue(val)
            elif self.modeltype == AdalinaModelType.MINMAX_USAGEFAC:
                self.solution.set_rhomaxvalue(val)
            elif l[0] == "usagevar":
                self.solution.add_usagevarvalue(l[1], val)

        if self.modeltype == AdalinaModelType.MINMAX_UNSERVED and not self.solution.check_wmax_set():
            self.solution.set_wmaxvalue(0)
        if self.modeltype == AdalinaModelType.MINMAX_USAGEFAC and not self.solution.check_rhomax_set():
            self.solution.set_rhomaxvalue(0)

        logging.debug("check feasibility of solution")
        return self.solution.check_feasibility(self.data, self.modeltype)

    def check_model_feasible(self):

        if self.model_status is None:
            return False

        return self.model_status in [highspy.HighsModelStatus.kOptimal, highspy.HighsModelStatus.kIterationLimit,
                                     highspy.HighsModelStatus.kTimeLimit
                                     ]

    def get_solution(self, run_model=True):

        if self.solution is not None:
            return self.solution

        elif self.check_model_feasible():

            self.objective_value = self.model.getObjectiveValue()

            if self._build_solution():
                logging.debug("feasibility double check passed!")

                return self.solution

            else:
                logging.debug(f"INFEASIBILITIES WITH POST-PROCESSING CONTROL: {self.solution.infeasibility_log}")
            # print_log("model infeasible. no solution")
            return None

        if self.solution is None and run_model:

            if self.run() == highspy.HighsStatus.kOk:
                if self._build_solution():
                    logging.debug("feasibility double check passed!")
                elif self.solution is not None:
                    logging.debug(f"INFEASIBILITIES WITH POST-PROCESSING CONTROL: {self.solution.infeasibility_log}")

                return self.solution

            return None

        elif self.solution is not None:
            return self.solution

        logging.debug("no solution available. run model with function run()")
        return None

