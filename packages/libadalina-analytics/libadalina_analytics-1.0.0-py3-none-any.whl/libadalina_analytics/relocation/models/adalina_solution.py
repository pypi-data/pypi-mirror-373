import json
import pandas as pd
import shapely

from libadalina_core.sedona_utils.coordinate_formats import EPSGFormats
from libadalina_analytics.utils import GeometryFormats
from .adalina_data import AdalinaData, EPSG_FORMAT_FOR_ALGORITHM
from .adalina_model_type import AdalinaModelType


class AdalinaSolution:

    def __init__(self, objfun_value=None):

        self.assignments = None
        self.all_relocations = None
        self.total_usage = None
        self.objfun_value = objfun_value

        self.xvarvalues = pd.DataFrame(columns=['shelter', 'area', 'value'])
        self.xvarvalues = self.xvarvalues.set_index(['shelter', 'area'])

        self.rhovalues = pd.DataFrame(columns=["shelter_from", "shelter_to", "resource", "value"])
        self.rhovalues = self.rhovalues.set_index(["shelter_from", "shelter_to", "resource"])

        self.yvarvalues = pd.DataFrame(columns=['shelter', 'value'])
        self.yvarvalues = self.yvarvalues.set_index(['shelter'])

        self.wvarvalues = pd.DataFrame(columns=['area', 'value'])
        self.wvarvalues = self.wvarvalues.set_index(['area'])

        self.zvarvalues = pd.DataFrame(columns=['shelter', 'resource', 'value'])
        self.zvarvalues = self.zvarvalues.set_index(['shelter', 'resource'])

        self.usagevarvalues = pd.DataFrame(columns=['shelter', 'value'])
        self.usagevarvalues = self.usagevarvalues.set_index(['shelter'])

        self.wmaxvalue = None
        self.rhomaxvalue = None
        self.w2varvalue = None

        self.feasible = False

        self.areas = pd.DataFrame(columns=['area', 'unserved', 'unserved_fract',
                                           'cost_transport', 'cost_unserved'])

        self.areas = self.areas.set_index(['area'])

        self.shelter = pd.DataFrame(columns=['shelter', 'isopen', 'cost_transport',
                                             'cost_open','cost_excess', 'fract_usage_kpi'])
        self.shelter = self.shelter.set_index(['shelter'])

        self.relocation = pd.DataFrame(columns = ['shelter', 'resource',
                                                  'need', 'exiting', 'entering', 'excess'])
        # self.relocation = self.relocation.set_index(['shelter', 'resource'])

        self.total_cost_unserved = 0
        self.total_cost_excess = 0
        self.total_cost_transport = 0
        self.total_cost_open = 0
        self.objfun_value_recomputed = 0
        self.total_cost_relocation = 0
        self.total_cost_unserved_w2 = 0

        self.infeasibility_log = []

        self.modeltype = None
        self.ub_unserved = None
        self.ub_assign_distance = None
        self.ub_max_usage = None

    def export_json(self, outfilename):

        serializable_dict = {
            "feasible" : self.feasible,
             "areas" : self.areas.to_dict(),
             "shelters" : self.shelter.to_dict(),
             # "relocation" : self.relocation.groupby(level=0).apply(
             #  lambda df: df.xs(df.name).to_dict()['value']).to_dict(),
             "cost_assignments" : float(self.total_cost_transport),
             "cost_open_facility": float(self.total_cost_open),
             "cost_excess_capacity": float(self.total_cost_excess),
             "cost_unserved": float(self.total_cost_unserved),
             "obj_fun_value" : float(self.objfun_value)
        }

        if self.modeltype is not None:

            assert isinstance(self.modeltype, AdalinaModelType)

            serializable_dict["modeltype"] = self.modeltype.get_label()

        if self.ub_unserved is not None:

            serializable_dict["UB_unserved"] = self.ub_unserved

        if self.ub_assign_distance is not None:
            serializable_dict["UB_assign_distance"] = self.ub_assign_distance

        if self.wmaxvalue is not None:
            serializable_dict["wmax"] = float(self.wmaxvalue)

        if self.rhomaxvalue is not None:
            serializable_dict["rhomax"] = float(self.rhomaxvalue)

        if self.xvarvalues.shape[0] > 0:
            serializable_dict["xvar"] = self.xvarvalues.groupby(level=0).apply(
                lambda df: df.xs(df.name).to_dict()['value']).to_dict()
        if self.yvarvalues.shape[0] > 0:
            serializable_dict["yvar"] = self.yvarvalues.to_dict()['value']
        if self.wvarvalues.shape[0] > 0:
            serializable_dict["wvar"] = self.wvarvalues.to_dict()['value']

        if self.zvarvalues.shape[0] > 0:
            serializable_dict["zvar"] = self.zvarvalues.groupby(level=0).apply(
                lambda df: df.xs(df.name).to_dict()['value']).to_dict()

        if self.rhovalues.shape[0] > 0:
            serializable_dict["rhovar"] = {}
            for sfrom in self.rhovalues.index.unique(0):
                rhofrom = self.rhovalues.xs(sfrom, level=0)
                serializable_dict["rhovar"][sfrom] = {}

                for sto in rhofrom.index.unique(0):
                    rhofromto = rhofrom.xs(sto, level=0)

                    serializable_dict["rhovar"][sfrom][sto] = rhofromto.to_dict()['value']

                # self.rhovalues.groupby(level=0).apply(
                # lambda df: df.xs(df.name).to_dict()['value']).to_dict()

        # Dump the serializable dictionary as a JSON file
        with open(outfilename+'.json', 'w') as fout:
            json.dump(serializable_dict, fout)

        self.assignments.to_csv(outfilename+"_assignments.csv", sep=";", index=None)
        self.all_relocations.to_csv(outfilename+"_relocations.csv", sep=";", index=None)

    def check_wmax_set(self):
        return self.wmaxvalue is not None

    def check_rhomax_set(self ):
        return self.rhomaxvalue is not None

    def set_wmaxvalue(self, value):
        self.wmaxvalue = value

    def set_rhomaxvalue(self, value):
        self.rhomaxvalue =  value

    def add_xvarvalue(self, shelter, area, value):
        self.xvarvalues.loc[(shelter, area), 'value'] = value

    def add_yvarvalue(self, shelter, value):
        self.yvarvalues.loc[shelter, 'value'] = value

    def add_wvarvalue(self, area, value):
        self.wvarvalues.loc[area, 'value'] = value

    def add_usagevarvalue(self, shelter, value):
        self.usagevarvalues.loc[shelter, 'value'] = value

    def add_zvarvalue(self, shelter, resource, value):
        self.zvarvalues.loc[ (shelter, resource), 'value'] = value

    def add_rhovalue(self, shelter_from, shelter_to, resource, value):
        self.rhovalues.loc[(shelter_from, shelter_to, resource), "value"] = value

    def add_w2varvalue(self, area, shelter, value):

        if self.w2varvalue is None:
            self.w2varvalue = pd.DataFrame(columns=['shelter', 'area', 'value'])
            self.w2varvalue = self.w2varvalue.set_index(['shelter', 'area'])
        self.w2varvalue.loc[(shelter, area), 'value'] = value

    def _set_infeasibility(self, logtext):
        self.feasible = False
        self.infeasibility_log.append(logtext)

    def check_feasibility(self, data, modeltype):

        assert isinstance(data, AdalinaData)
        assert isinstance(modeltype, AdalinaModelType)

        self.modeltype = modeltype

        self.assignments = self.xvarvalues.reset_index()

        for a in self.assignments.area.unique():
            self.assignments.loc[self.assignments.area == a, "value"] = self.assignments.loc[
                                                     self.assignments.area == a, "value"] * data.get_area_demand(a)

        self.all_relocations = self.rhovalues.reset_index()
        for s in self.all_relocations.shelter_from.unique():
            for r in self.all_relocations.loc[self.all_relocations.shelter_from == s].resource.unique():
                self.all_relocations.loc[(self.all_relocations.shelter_from == s) &
                                     (self.all_relocations.resource == r)
                                        , "value"] = \
                    self.all_relocations.loc[(self.all_relocations.shelter_from == s) &
                                         (self.all_relocations.resource == r)
                    , "value"]*data.get_resource_available(s, r)

        self.feasible = True

        for a in data.A:
            self.areas.loc[a] = 0.0
        for s in data.S:
            self.shelter.loc[s] = 0.0

            for r in data.R:
                self.relocation.loc[ self.relocation.shape[0], ["shelter", "resource"]] = [s,r]

        self.relocation = self.relocation.set_index(["shelter", "resource"])
        self.relocation[self.relocation.isna()] = 0

        self.shelter['isopen'] = self.shelter['isopen'].astype(bool)
        for s in self.yvarvalues.index:

            if not data.shelters.loc[s, 'usable']:
                self._set_infeasibility(f"shelter {s} opened but not usable")

            self.shelter.loc[s, 'isopen'] = True

        # sum[s] r[s,a]*x[s,a] + w[a] == 1 forall a
        for a in data.A:
            cover = 0

            _xvararea = self.xvarvalues[self.xvarvalues.index.isin([a], level=1)]

            for _, row in _xvararea.iterrows():

                s, _ = row.name

                val = row["value"]

                cover += val

                # x[s,a] <= r[a,s]
                if val > 1e-5 and not data.get_is_reachable(s, a):
                    self._set_infeasibility(f"assignment area {a} to shelter {s} while unreachable")

            if a in self.wvarvalues.index:

                val = self.wvarvalues.loc[a].iloc[0]
                cover +=  val

                self.areas.loc[a, 'unserved_fract'] += val

            if cover < 1 - 1e-5:
                self._set_infeasibility(f"area {a} not fully covered {cover}")

            self.areas.loc[a, 'unserved'] = self.areas.loc[a, 'unserved_fract']*data.get_area_demand(a)

        if modeltype in [AdalinaModelType.MINDIST_ASSIGNMENTS, AdalinaModelType.MINMAX_USAGEFAC] and \
            data.ub_total_unserved_demand is not None:
            demand_unserved = self.areas['unserved'].sum()

            self.ub_unserved = data.ub_total_unserved_demand

            if demand_unserved - data.ub_total_unserved_demand > 1e-5:
                self._set_infeasibility(f" total unserved demand {demand_unserved} exceeds UB {data.ub_total_unserved_demand}")

        # sum[a] d[a] * x[s,a] <= sum{s1 in S} rho[s1,s,r] + z[r, s] forall s in S, forall r
        for s in data.S:
            for r in data.R:

                need = 0
                entering = 0

                isopen = s in self.yvarvalues.index

                _xvarshelter = self.xvarvalues[self.xvarvalues.index.isin([s], level=0)]
                for _, row in _xvarshelter.iterrows():
                    _, area = row.name
                    need += data.get_area_demand(area) * row["value"] * data.get_resource_need(r)

                for s1 in data.S:
                    if (s1, s, r) in self.rhovalues.index:
                        val = self.rhovalues.loc[(s1, s, r), "value"]*data.get_resource_available(s1, r)
                        entering += val
                        self.relocation.loc[(s1,r), 'exiting'] += val

                        if not data.get_transport_possible(s, s1):
                            self._set_infeasibility(f"relocation between {s1} and {s} of {val} resources while not possible")

                if (s, r) in self.zvarvalues.index:
                    val = self.zvarvalues.loc[(s,r)].iloc[0]

                    # z[s] <= My[s]
                    if not open:
                        self._set_infeasibility(f"exceeding shelter {s} while not used")

                    # capacity += val
                    self.relocation.loc[(s,r), 'excess'] +=val

                if need > 1e-5 and not isopen:
                    self._set_infeasibility(f"using shelter {s} while not opened")

                self.relocation.loc[(s,r), 'need'] = need
                self.relocation.loc[(s, r), 'entering'] = entering

                excess = 0
                if (s,r) in self.zvarvalues.index:
                    excess = self.zvarvalues.loc[(s,r), "value"]
                self.relocation.loc[(s,r), 'excess'] = excess

                if need - entering - excess > 1e-2:
                    self._set_infeasibility(f"shelter {s} needs {need} of resource {r}, only having {entering+excess}")

        # objfun sum[a] c[a]d[a]w[a] + sum[a,s] c[s,a]*d[a]*x[s,a]  + sum[s] (co[s]y[s] + ce[s]z[s])

        # sum[a] c[a]d[a]w[a]
        for a in data.A:
            if a in self.wvarvalues.index:
                val = self.wvarvalues.loc[a].iloc[0]*data.get_demcost_notserved(a, modeltype) # data.get_area_demand(a)
                self.total_cost_unserved += val

                self.areas.loc[a, 'cost_unserved'] = val

        # sum[s] (co[s]y[s] + ce[s]z[r,s])
        for s in data.S:
            copen = data.get_fixed_cost_shelter(s, modeltype) # data.get_fixed_cost_shelter(s)
            if s in self.yvarvalues.index:
                self.shelter.loc[s, 'cost_open'] = copen

                self.total_cost_open += copen

                tot_res_used = self.relocation.xs(s, level=0).entering.sum()
                tot_res_init = sum([data.get_resource_available(s, r) for r in data.R])
                if tot_res_init > 1e-5:
                    self.shelter.loc[s, 'fract_usage_kpi'] = tot_res_used/tot_res_init

            for r in data.R:
                if (s,r) in self.zvarvalues.index:

                    val = self.zvarvalues.loc[(s,r), 'value']*data.get_cost_exceed_cap(s, modeltype) # data.get_cost_exceed_cap(s)

                    self.shelter.loc[s, 'cost_excess'] += val

                    self.relocation.loc[(s,r), 'excess'] = val

                    self.total_cost_excess += val

        for sfrom in data.S:
            for sto in data.S:
                if sfrom == sto:
                    continue
                for r in data.R:
                    if (sfrom, sto, r) in self.rhovalues.index:

                        rhoval = self.rhovalues.loc[(sfrom, sto, r), "value"]

                        self.total_cost_relocation += \
                            rhoval * \
                            data.get_cost_resource_transport(sfrom , sto, r, modeltype)

        # sum[a,s] c[s,a]*d[a]*x[s,a]
        for i, row in self.xvarvalues.iterrows():
            s, a = row.name
            val = row['value'] * data.get_cost_assign(s, a) * data.get_area_demand(a) #data.get_demcost_assign(s,a,modeltype) #

            self.total_cost_transport += val

            self.shelter.loc[s, 'cost_transport'] += val
            self.areas.loc[a, 'cost_transport'] += val

        if modeltype in [AdalinaModelType.MINMAX_USAGEFAC, AdalinaModelType.MINSUM_USAGEFAC] and data.ub_total_assignment_distance is not None:

            self.ub_assign_distance = data.ub_total_assignment_distance

            if self.total_cost_transport - data.ub_total_assignment_distance > 1e-5:
                self._set_infeasibility(f"total assignment cost {self.total_cost_transport} exceeds UB {data.ub_total_unserved_demand}")

        if modeltype == AdalinaModelType.MINSUM_USAGEFAC:

            self.total_usage = self.usagevarvalues.values.sum()

        if modeltype == AdalinaModelType.MAXSUM_DIST_UNSERVED:
            for i, row in self.w2varvalue.iterrows():
                s, a = row.name
                val = row['value'] * data.get_cost_assign(s, a) * data.get_area_demand(
                    a)  # data.get_demcost_assign(s,a,modeltype) #

                self.total_cost_unserved_w2 += val

        if modeltype == AdalinaModelType.MINSUM_UNSERVED:
            self.objfun_value_recomputed = self.total_cost_unserved
        elif modeltype == AdalinaModelType.MINMAX_UNSERVED:
            self.objfun_value_recomputed = self.wmaxvalue
        elif modeltype == AdalinaModelType.MINMAX_USAGEFAC:
            self.objfun_value_recomputed = self.rhomaxvalue
        elif modeltype == AdalinaModelType.MIN_EXTRARESOURCES:
            self.objfun_value_recomputed = self.total_cost_excess
        elif modeltype == AdalinaModelType.MINDIST_ASSIGNMENTS:
            self.objfun_value_recomputed = self.total_cost_transport
        elif modeltype == AdalinaModelType.MINSUM_USAGEFAC:
            self.objfun_value_recomputed = self.total_usage
        elif modeltype == AdalinaModelType.MINSUM_RELOCATION:
            self.objfun_value_recomputed = self.total_cost_relocation
        elif modeltype == AdalinaModelType.MAXSUM_DIST_UNSERVED:
            self.objfun_value_recomputed = self.total_cost_unserved_w2
        else:
            self.objfun_value_recomputed = self.total_cost_open  + self.total_cost_excess + self.total_cost_transport \
                                     + self.total_cost_unserved + self.total_cost_relocation

        if abs(self.objfun_value - self.objfun_value_recomputed) > 1e-2:
            self.infeasibility_log.append(f"objective function not matching recomputation: model {self.objfun_value} - recomputation {self.objfun_value_recomputed}")
            self.feasible = False

        return self.feasible


def get_solution_csv_AMELIA(sol: AdalinaSolution,
                            data : AdalinaData,
                            epsg: EPSGFormats = EPSGFormats.EPSG4326,
                            geometry_format: GeometryFormats = GeometryFormats.WKT
                            ):
    csv_out = pd.merge(data.areas.reset_index(), sol.areas.reset_index(), on = "area")

    if epsg != EPSG_FORMAT_FOR_ALGORITHM:
        csv_out = csv_out.to_crs(epsg=epsg.value)

    if geometry_format == GeometryFormats.WKT:
        return csv_out.to_wkt()
    elif geometry_format == GeometryFormats.GEOJSON:
        output_copy = pd.DataFrame(csv_out.select_dtypes(exclude='geometry'))
        for col in csv_out.columns[csv_out.dtypes == "geometry"]:
            output_copy[col] = csv_out[col].apply(shapely.to_geojson)
        return output_copy

    return csv_out
