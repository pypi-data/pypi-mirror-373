import logging

from ..models import AdalinaData, AdalinaModelType, AdalinaAlgorithmOptions, AdalinaSolution
from .adalina_model_highs import AdalinaModelHighs
import time

def run_model_asis(problem, options):

    assert isinstance(problem, AdalinaModelHighs)

    logging.debug(f"RUN MODEL type {problem.modeltype.get_label()}")

    if problem.run(timelimit=options.timelimit):
        logging.debug(f"solved with o.f. value {problem.objective_value}!")  # problem.model.getObjectiveValue()}

        # if options.outdir is not None:
        #
        #     if solfile_suffix != "" and not solfile_suffix.startswith("_"):
        #         solfile_suffix = "_" + solfile_suffix
        #
        #     problem.get_solution().export_json(options.outdir +
        #                                        options.fileprefix +
        #                                        "_" + problem.modeltype.get_label() + solfile_suffix + '_sol')

        return problem.get_solution()

    else:
        logging.warning("SOLUTION NOT AVAILABLE")

    return None

def run_hierarchy_with_distance_threshold(data : AdalinaData,
                                          options : AdalinaAlgorithmOptions,
                                          run_it : int = 1,
                                          threshold_distance_relocation : float = None,
                                          problem : AdalinaModelHighs = None):
    """

    :param data: AdalinaData object
    :param options: AdalinaAlgorithmOptions object
    :param run_it: integer, default to 1, for iterations of runs
    :param threshold_distance_relocation: float, default to None, override threshold of maximum relocation
    :param problem: AdalinaModelHighs object, default to None, for iterations of run
    :return: AdalinaModelHighs object (or None if no solution available), [AdalinaSolution] list of solutions available
    """

    all_solutions = []

    start_step1 = time.perf_counter()
    logging.debug(f"STEP {run_it}.1: MIN SUM UNSERVED DEMAND")

    options.change_model_type(AdalinaModelType.MINSUM_UNSERVED)
    if problem is None:
        problem = AdalinaModelHighs(data, options.modeltype)
    else:
        problem.reset_all_objcoeff()
        problem.reset_solution()
        problem.set_model_minsum_unserved()

    if threshold_distance_relocation is not None:
        if threshold_distance_relocation < 1e-5:
            # forbid relocation
            problem.set_rhovar_to_zero()
        elif threshold_distance_relocation > 1e-5:
            problem.set_rhovar_by_distance_threshold(threshold_distance_relocation)

    """

    1 - min sum domanda non servita
    2 - min sum distanza di assegnamento (con UB su 1)
        domanda non servita per zona è KPI di rischio della zona per l'evento catastrofico

    """

    sol_minsum_unserved = run_model_asis(problem, options)# , f"_step{run_it}")
    all_solutions.append(sol_minsum_unserved)

    end_step1 = time.perf_counter()
    logging.debug(f"END STEP {run_it}.1 IN {(end_step1-start_step1):.3f} secondi")

    if sol_minsum_unserved is None:
        logging.debug("ERR: NO SOLUTION FOR min sum unserved demand")
        return None, all_solutions

    assert isinstance(sol_minsum_unserved, AdalinaSolution)

    problem.data.ub_total_unserved_demand = sol_minsum_unserved.objfun_value

    # remove obj. fun. coefficient on variables w
    problem.reset_wvar_costs()
    # UB on objective 1
    problem.set_constr_ub_sumunserved(problem.data.ub_total_unserved_demand)

    if options.run_parametric_analysis:
        if sol_minsum_unserved.objfun_value < 1e-5:
            logging.debug("NO UNSERVED DEMAND END HIERARCHY")

            if run_it <= 1:
                return problem, all_solutions

        else:

            start_step2a = time.perf_counter()
            problem.reset_solution()
            # 2 - min sum assignment distance (with UB on objective 1)
            logging.debug(f"STEP {run_it}.2: MIN SUM UNASSIGNMENT DISTANCE")
            problem.modify_model_to_minsumdist()
            options.change_model_type(AdalinaModelType.MINDIST_ASSIGNMENTS)

            # problem.modify_model_to_maxdist_unserved()
            # options.change_model_type(AdalinaModelType.MAXSUM_DIST_UNSERVED)

            # problem.model.writeModel("/home/marco/Desktop/test_maxsumdistuns.lp")
            sol_min_sumdist_assign = run_model_asis(problem, options)# ,f"_step{run_it}")

            end_step2a = time.perf_counter()
            logging.debug(f"END STEP {run_it}.2 IN {(end_step2a - start_step2a):.3f} secondi")

            if sol_min_sumdist_assign is None:
                logging.debug("ERR: NO SOLUTION FOR min sum assignment distance")
                return problem, all_solutions

            assert isinstance(sol_min_sumdist_assign, AdalinaSolution)

            all_solutions.append(sol_min_sumdist_assign)
            # export_html(options, sol_min_sumdist_assign, data, filesuffix=f"step{run_it}")

            problem.reset_x_val_cost()

    if run_it <= 1 and options.run_parametric_analysis:

        return problem, all_solutions

    """

    B - permetti relocation
      - analisi parametrica sulla distanza soglia che permette relocation. per ogni soglia:
            1 - min sum domanda non servita
            2a - min sum distanza di assegnamento (con UB su 1)
                - come riassumere i risultati di tutta l'analisi parametrica in valori di KPI?
                    * distanza per arrivare a zero unserved
                    * distanza per soglie valueable di unserved percentuali?
            2b - min max utilizzo relativo facility (con UB su 1)
            3b - min sum distanza di assegnamento (con UB su 1 e 2b)
            4b - min sum distanza di relocation (con UB su 1, 2b, 3b e 4b)

    """

    """
    HIERARCHY STEP 2b - min max utilizzo relativo facility (con UB su 1)
    """
    # reset xvar val
    start_step2b = time.perf_counter()

    problem.reset_solution()
    logging.debug(f"STEP {run_it}.2b MIN MAX FACILITY USAGE")
    problem.modify_model_to_minmax_usage_shelter()
    options.change_model_type(AdalinaModelType.MINMAX_USAGEFAC)

    # problem.model.writeModel("/home/marco/Desktop/test_minmaxrho.lp")
    sol_minmaxusage = run_model_asis(problem, options)# , f"_step{run_it}")

    end_step2b = time.perf_counter()
    logging.debug(f"END STEP {run_it}.2b IN {(end_step2b - start_step2b):.3f} secondi")

    if sol_minmaxusage is None:
        logging.debug("ERR: NO SOLUTION FOR min max usage of facility")
        return problem, all_solutions

    all_solutions.append(sol_minmaxusage)

    problem.reset_solution()
    problem.reset_rhomax_var_objfun_coeff()
    problem.set_constr_ub_maxusage(sol_minmaxusage.objfun_value)

    """
    HIERARCHY STEP 3 MIN SUM ASSIGNMENT DISTANCE
    """
    start_step3 = time.perf_counter()

    logging.debug(f"STEP {run_it}.3 MIN SUM ASSIGNMENT DISTANCE")
    problem.modify_model_to_minsumdist()
    options.change_model_type(AdalinaModelType.MINDIST_ASSIGNMENTS)

    # problem.model.writeModel("/home/marco/Desktop/test_misumdist.lp")
    sol_minsumdist = run_model_asis(problem, options) #, f"_step{run_it}")

    end_step3 = time.perf_counter()
    logging.debug(f"END STEP {run_it}.3 IN {(end_step3 - start_step3):.3f} secondi")

    if sol_minsumdist is None:
        logging.debug("ERR: NO SOLUTION FOR min sum assignment distance")
        return problem, all_solutions

    all_solutions.append(sol_minsumdist)

    assert isinstance(sol_minsumdist, AdalinaSolution)

    problem.data.ub_total_assignment_distance = sol_minsumdist.objfun_value
    problem.reset_solution()
    problem.reset_x_val_cost()
    problem.set_constr_ub_sumdist()

    """
    HIERARCHY STEP 4 MIN SUM RELOCATION
    """
    start_step4 = time.perf_counter()

    logging.debug(f"STEP {run_it}.4 MIN SUM RELOCATION COST")
    problem.modify_model_to_minsum_relocation_costs()
    options.change_model_type(AdalinaModelType.MINSUM_RELOCATION)

    # problem.model.writeModel("/home/marco/Desktop/test_minsumrho.lp")
    sol_minsumrho = run_model_asis(problem, options)#, f"_step{run_it}")

    end_step4 = time.perf_counter()
    logging.debug(f"END STEP {run_it}.4 IN {(end_step4 - start_step4):.3f} secondi")

    if sol_minsumrho is None:
        logging.debug("ERR: NO SOLUTION FOR min sum relocation costs")
        return problem, all_solutions

    all_solutions.append(sol_minsumrho)
    # export_html(options, sol_minsumrho, data, filesuffix=f"step{run_it}")

    return problem, all_solutions

