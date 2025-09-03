#-----------------------------------------------------------------------
# Name:        didanalysis (diffindiff package)
# Purpose:     Analysis functions for difference-in-differences analyses
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     2.0.7
# Last update: 2025-09-02 18:33
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import pandas as pd
from statsmodels.formula.api import ols
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import diffindiff.didtools


class DiffModel:

    def __init__(
        self,
        did_modelresults,
        did_modelconfig,
        did_modeldata,
        did_modelpredictions,
        did_model_statistics,
        did_olsmodel
        ):

        self.data = [
            did_modelresults, 
            did_modelconfig, 
            did_modeldata, 
            did_modelpredictions, 
            did_model_statistics, 
            did_olsmodel
            ]    

    def treatment_statistics(
        self,
        treatment: str = None,
        after_treatment_col: str = None
        ):

        model_config = self.data[1]
        model_data = self.data[2]
               
        if treatment is not None:
            if treatment not in model_config["treatment_col"]:
                raise ValueError ("Treatment ", treatment, " not in model object.")
        else:
            treatment = model_config["treatment_col"][0]
            print("NOTE: No treatment was stated. Choosing treatment " + treatment + " for analysis.")

        if after_treatment_col is not None:
            if len(model_config["after_treatment_col"]) == 0:
                raise ValueError ("Model object does not include after-treatment period.")
            if after_treatment_col not in model_config["after_treatment_col"]:
                raise ValueError ("Treatment ", treatment, " not in model object.")

        unit_col = model_config["unit_col"]
        time_col = model_config["time_col"]

        treatment_timepoints = model_data.groupby(unit_col)[treatment].sum()
        treatment_timepoints = pd.DataFrame(treatment_timepoints)
        treatment_timepoints = treatment_timepoints.reset_index()

        study_period_start = pd.to_datetime(min(model_data[time_col]))
        study_period_start = study_period_start.date()
        study_period_end = pd.to_datetime(max(model_data[time_col]))
        study_period_end = study_period_end.date()
        study_period_N = model_data[time_col].nunique()
        
        if len(model_data[model_data[treatment] == 1]) > 0:
            treatment_period_start = pd.to_datetime(min(model_data[model_data[treatment] == 1][time_col]))
            treatment_period_end = pd.to_datetime(max(model_data[model_data[treatment] == 1][time_col]))
            treatment_period_N = model_data.loc[model_data[treatment] == 1, time_col].nunique()
        else:
            treatment_period_N = 0
            
        after_treatment_period_start = None
        after_treatment_period_end = None
        after_treatment_period_N = None
        if len(model_config["after_treatment_col"]) > 0 and after_treatment_col is not None:
            after_treatment_period_start = treatment_period_end+pd.Timedelta(days=1)
            after_treatment_period_start = pd.to_datetime(after_treatment_period_start)
            after_treatment_period_end = pd.to_datetime(study_period_end)
            after_treatment_period_N = model_data.loc[model_data[after_treatment_col] == 1, time_col].nunique()            
            after_treatment_period_start = after_treatment_period_start.strftime(model_config["date_format"])
            after_treatment_period_end = after_treatment_period_end.strftime(model_config["date_format"])
            
        study_period_start = study_period_start.strftime(model_config["date_format"])
        study_period_end = study_period_end.strftime(model_config["date_format"])
        if treatment_period_N > 0:
            treatment_period_start = treatment_period_start.strftime(model_config["date_format"])
            treatment_period_end = treatment_period_end.strftime(model_config["date_format"])
        else:
            treatment_period_start = None
            treatment_period_end = None
        period_study = [study_period_start, study_period_end, study_period_N]
        period_treatment = [treatment_period_start, treatment_period_end, treatment_period_N]
        period_after_treatment = [after_treatment_period_start, after_treatment_period_end, after_treatment_period_N]
        time_periods = [period_study, period_treatment, period_after_treatment]

        treatment_group = np.array(treatment_timepoints[treatment_timepoints[treatment] > 0][unit_col])
        control_group = np.array(treatment_timepoints[treatment_timepoints[treatment] == 0][unit_col])
        groups = [treatment_group, control_group]

        treatment_group_size = len(treatment_group)
        control_group_size = len(control_group)
        all_units = treatment_group_size+control_group_size
        treatment_group_share = treatment_group_size/all_units
        control_group_share = control_group_size/all_units
        group_sizes = [treatment_group_size, control_group_size, all_units, treatment_group_share, control_group_share]

        if treatment_period_N > 0:
            average_treatment_time = treatment_timepoints[treatment_timepoints[unit_col].isin(treatment_group)][treatment].mean()
        else:
            average_treatment_time = 0

        return [
            group_sizes,
            average_treatment_time, 
            groups, 
            treatment_timepoints, 
            time_periods
            ]
    
    def treatment_diagnostics(
        self
        ):
        
        model_config = self.data[1]
        treatment_diagnostics = model_config["treatment_diagnostics"]
        
        treatment_diagnostics_df = pd.DataFrame()
        treatment_diagnostics_rows = []
        no_control_conditions = []

        for key, value in treatment_diagnostics.items():

            if value["is_simultaneous"]:
                adoption_type = "Simultaneous"
            else:
                adoption_type = "Staggered"

            if value["is_notreatment"]:
                no_treatment = "YES"
            else:
                no_treatment = "NO"

            if value["is_parallel"]:
                is_parallel = "YES"
            else:
                is_parallel = "NO"

            treatment_group_size = len (value["treatment_group"])
            control_group_size = len (value["control_group"])

            treatment_diagnostics_rows.append({
                "Treatment": value["treatment"],
                "Type of adoption": adoption_type,
                "No-treatment control group": no_treatment,                
                "Parallel trends (pre)": is_parallel,
                "Format": value["treatment_format"],
                "Treatment group (N)": treatment_group_size,
                "Control group (N)": control_group_size
            })

            if no_treatment == "NO" and adoption_type == "Simultaneous":
                no_control_conditions.append(value["treatment"])

        treatment_diagnostics_df = pd.DataFrame(treatment_diagnostics_rows)            
        treatment_diagnostics_df = treatment_diagnostics_df.reset_index(drop=True)

        return [treatment_diagnostics_df, no_control_conditions]

    def treatment_effects(
        self,
        baseline_components = False,
        treatment_group_only = True
        ):

        def replace_prefix(s, prefix, replace):
            if s.startswith(prefix):
                return s.replace(prefix, replace, 1)
            return s
        
        model_results = self.data[0]

        model_config = self.data[1]
        treatment_diagnostics = model_config["treatment_diagnostics"]
        treatment_col = model_config["treatment_col"]
        
        treatment_effects_df = pd.DataFrame()        
        if "average_treatment_effects" in model_results:            
            average_treatment_effects = model_results["average_treatment_effects"]
            average_treatment_effects_rows = []
            for key, value in average_treatment_effects.items():
                average_treatment_effects_rows.append({
                    "": "Average treatment effect " + value["Coefficient"],
                    "Estimate": value["Estimate"],
                    "SE": value["SE"],
                    "t": value["t"],
                    "p": value["p"],
                    "CI lower": value["CI_lower"],
                    "CI upper": value["CI_upper"]
                })
            treatment_effects_df = pd.DataFrame(average_treatment_effects_rows)
            if len (average_treatment_effects) == 1:
                    treatment_effects_df.at[0, ""] = "Average treatment effect"
                      
            if "average_after_treatment_effects" in model_results:            
                average_after_treatment_effects = model_results["average_after_treatment_effects"]            
                average_after_treatment_effects_rows = []
                for key, value in average_after_treatment_effects.items():
                    average_after_treatment_effects_rows.append({
                        "": "Average after-treatment effect " + value["Coefficient"],
                        "Estimate": value["Estimate"],
                        "SE": value["SE"],
                        "t": value["t"],
                        "p": value["p"],
                        "CI lower": value["CI_lower"],
                        "CI upper": value["CI_upper"]
                    })
                average_after_treatment_effects = pd.DataFrame(average_after_treatment_effects_rows)
                if len (average_after_treatment_effects) == 1:
                    average_after_treatment_effects.at[0, ""] = "Average after-treatment effect"
                treatment_effects_df = pd.concat([treatment_effects_df, average_after_treatment_effects], ignore_index=True)

            if ("control_group_baseline" in model_results and not model_config["FE_unit"]) or ("control_group_baseline" in model_results and baseline_components):            
                control_group_baseline = model_results["control_group_baseline"]                
                Intercept = round(control_group_baseline["Estimate"], 3)
                Intercept_SE = round(control_group_baseline["SE"], 3)
                Intercept_t = round(control_group_baseline["t"], 3)
                Intercept_p = round(control_group_baseline["p"], 3)
                Intercept_CI_lower = round(control_group_baseline["CI_lower"], 3)
                Intercept_CI_upper = round(control_group_baseline["CI_upper"], 3)                
                control_group_baseline_row = pd.DataFrame([{
                    "": "Control group baseline",
                    "Estimate": Intercept,
                    "SE": Intercept_SE,
                    "t": Intercept_t,
                    "p": Intercept_p,
                    "CI lower": Intercept_CI_lower,
                    "CI upper": Intercept_CI_upper
                    }])
                treatment_effects_df = pd.concat([treatment_effects_df, control_group_baseline_row], ignore_index=True)
            
            if ("treatment_group_deviation" in model_results and not model_config["FE_unit"]) or ("treatment_group_deviation" in model_results and baseline_components):
                treatment_group_deviation = model_results["treatment_group_deviation"]            
                treatment_group_deviation_rows = []
                for key, value in treatment_group_deviation.items():
                    treatment_group_deviation_rows.append({
                        "": replace_prefix(value["Coefficient"], "TG_", "Treatment group deviation "),
                        "Estimate": value["Estimate"],
                        "SE": value["SE"],
                        "t": value["t"],
                        "p": value["p"],
                        "CI lower": value["CI_lower"],
                        "CI upper": value["CI_upper"]
                    })
                treatment_group_deviation = pd.DataFrame(treatment_group_deviation_rows)
                if len (treatment_group_deviation) == 1:
                    treatment_group_deviation.at[0, ""] = "Treatment group deviation"
                treatment_effects_df = pd.concat([treatment_effects_df, treatment_group_deviation], ignore_index=True)
                   
            if ("non_treatment_time_effect" in model_results and not model_config["FE_time"]) or ("non_treatment_time_effect" in model_results and baseline_components):
                non_treatment_time_effect = model_results["non_treatment_time_effect"]            
                non_treatment_time_effect_rows = []
                for key, value in non_treatment_time_effect.items():
                    non_treatment_time_effect_rows.append({
                        "": replace_prefix(value["Coefficient"], "TT_", "Non-treatment time effect "),
                        "Estimate": value["Estimate"],
                        "SE": value["SE"],
                        "t": value["t"],
                        "p": value["p"],
                        "CI lower": value["CI_lower"],
                        "CI upper": value["CI_upper"]
                    })
                non_treatment_time_effect = pd.DataFrame(non_treatment_time_effect_rows)
                if len (non_treatment_time_effect) == 1:
                    non_treatment_time_effect.at[0, ""] = "Non-treatment time effect"
                treatment_effects_df = pd.concat([treatment_effects_df, non_treatment_time_effect], ignore_index=True)

            if "after_treatment_time_effects" in model_results:          
                after_treatment_time_effects = model_results["after_treatment_time_effects"]            
                after_treatment_time_effects_rows = []
                for key, value in after_treatment_time_effects.items():
                    after_treatment_time_effects_rows.append({
                        "": "After-treatment time effect " + value["Coefficient"],
                        "Estimate": value["Estimate"],
                        "SE": value["SE"],
                        "t": value["t"],
                        "p": value["p"],
                        "CI lower": value["CI_lower"],
                        "CI upper": value["CI_upper"]
                    })
                after_treatment_time_effects = pd.DataFrame(after_treatment_time_effects_rows)
                if len (after_treatment_time_effects) == 1:
                    after_treatment_time_effects.at[0, ""] = "After-treatment time effect"
                treatment_effects_df = pd.concat([treatment_effects_df, after_treatment_time_effects], ignore_index=True)

        if "individual_treatment_effects" in model_results:

            individual_treatment_effects = model_results["individual_treatment_effects"]

            individual_treatment_effects_rows = []

            for key, value in individual_treatment_effects.items():
                individual_treatment_effects_rows.append({
                    "Individual treatment effects": value["Coefficient"],
                    "Estimate": value["Estimate"],
                    "SE": value["SE"],
                    "t": value["t"],
                    "p": value["p"],
                    "CI lower": value["CI_lower"],
                    "CI upper": value["CI_upper"]
                })
            treatment_effects_df = pd.DataFrame(individual_treatment_effects_rows)

            if treatment_group_only:
                
                treatment_effects_df["treatment"] = ""
                treatment_effects_df["treatment_group"] = ""

                for index, row in treatment_effects_df.iterrows():

                    treatment_string = row["Individual treatment effects"]

                    treatment = next((tr for tr in treatment_col if treatment_string.startswith(tr)), None)
                    row["treatment"] = treatment
                    
                    treatment_group = [entry["treatment_group"] for entry in treatment_diagnostics.values() if treatment in entry["treatment"]]
                    treatment_group = treatment_group[0]

                    if row["Individual treatment effects"].endswith(tuple(treatment_group)):
                        row["treatment_group"] = 1
                    else:
                        row["treatment_group"] = 0
                    
                    treatment_effects_df.at[index, "treatment_group"] = int(treatment_string.endswith(tuple(treatment_group)))
                
                treatment_effects_df = treatment_effects_df.loc[treatment_effects_df["treatment_group"] == 1]
                treatment_effects_df = treatment_effects_df[["Individual treatment effects", "Estimate", "SE", "t", "p", "CI lower", "CI upper"]]                

        if "group_treatment_effects" in model_results:

            group_treatment_effects = model_results["group_treatment_effects"]

            group_treatment_effects_rows = []

            for key, value in group_treatment_effects.items():
                group_treatment_effects_rows.append({
                    "Group treatment effects": value["Coefficient"],
                    "Estimate": value["Estimate"],
                    "SE": value["SE"],
                    "t": value["t"],
                    "p": value["p"],
                    "CI lower": value["CI_lower"],
                    "CI upper": value["CI_upper"]
                })
            treatment_effects_df = pd.DataFrame(group_treatment_effects_rows) 
        
        treatment_effects_df = treatment_effects_df.reset_index(drop=True)
        return treatment_effects_df    

    def covariates(
        self
        ):

        model_results = self.data[0]

        model_config = self.data[1]       
        
        if len(model_config["covariates"]) > 0:

            covariates_effects = model_results["covariates_effects"]                            

            covariates_effects_rows = []

            for key, value in covariates_effects.items():
                covariates_effects_rows.append({
                    "": value["Coefficient"],
                    "Estimate": value["Estimate"],
                    "SE": value["SE"],
                    "t": value["t"],
                    "p": value["p"],
                    "CI lower": value["CI_lower"],
                    "CI upper": value["CI_upper"]
                })
            covariates_effects_df = pd.DataFrame(covariates_effects_rows)

            covariates_effects_df = covariates_effects_df.reset_index(drop=True)
            return covariates_effects_df
        
        else:

            print ("Model does not include covariates.")
            return None
     
    def fixed_effects(
        self,
        units = True,
        time = True,
        group = True
        ):

        model_results = self.data[0]

        fixed_effects = [None, None, None]
        
        if model_results["fixed_effects"][0] is not None:
            
            fixed_effects_unit = model_results["fixed_effects"][0]["FE_unit"]                            

            fixed_effects_unit_rows = []

            for key, value in fixed_effects_unit.items():
                fixed_effects_unit_rows.append({
                    "Unit": value["Coefficient"],
                    "Estimate": value["Estimate"],
                    "SE": value["SE"],
                    "t": value["t"],
                    "p": value["p"],
                    "CI lower": value["CI_lower"],
                    "CI upper": value["CI_upper"]
                })
            fixed_effects_units_df = pd.DataFrame(fixed_effects_unit_rows)
            fixed_effects_units_df = fixed_effects_units_df.reset_index(drop=True)

            if units:
                fixed_effects[0] = fixed_effects_units_df
        
        else:
            fixed_effects_units_df = None
                        
        if model_results["fixed_effects"][1] is not None:
            
            fixed_effects_time = model_results["fixed_effects"][1]["FE_time"]                         
        
            fixed_effects_time_rows = []

            for key, value in fixed_effects_time.items():
                fixed_effects_time_rows.append({
                    "Time": value["Coefficient"],
                    "Estimate": value["Estimate"],
                    "SE": value["SE"],
                    "t": value["t"],
                    "p": value["p"],
                    "CI lower": value["CI_lower"],
                    "CI upper": value["CI_upper"]
                })
            fixed_effects_time_df = pd.DataFrame(fixed_effects_time_rows)
            fixed_effects_time_df = fixed_effects_time_df.reset_index(drop=True)

            if time:
                fixed_effects[1] = fixed_effects_time_df

        else:
            fixed_effects_time_df = None
            
        if model_results["fixed_effects"][2] is not None:
            
            fixed_effects_group = model_results["fixed_effects"][2]["FE_group"]
        
            fixed_effects_group_rows = []

            for key, value in fixed_effects_group.items():
                fixed_effects_group_rows.append({
                    "Group": value["Coefficient"],
                    "Estimate": value["Estimate"],
                    "SE": value["SE"],
                    "t": value["t"],
                    "p": value["p"],
                    "CI lower": value["CI_lower"],
                    "CI upper": value["CI_upper"]
                })
            fixed_effects_group_df = pd.DataFrame(fixed_effects_group_rows)
            fixed_effects_group_df = fixed_effects_group_df.reset_index(drop=True)

            if group:
                fixed_effects[2] = fixed_effects_group_df

        else:
            fixed_effects_group_df = None

        return fixed_effects
        
    def summary(
        self,
        show_baseline_components: bool = True,
        show_covariates: bool = False,
        show_treatment_group_only = True
        ):

        model_config = self.data[1]
        outcome_col_original = model_config["outcome_col"]   
        no_covariates = len(model_config["covariates"])

        data_diagnostics = model_config["data_diagnostics"]
        modeldata_isbalanced = data_diagnostics["is_balanced"]
        modeldata_ismissing = data_diagnostics["is_missing"]
        modeldata_dropmissing = data_diagnostics["drop_missing"]
        modeldata_missingreplacebyzero = data_diagnostics["missing_replace_by_zero"]

        model_data = self.data[2]

        model_statistics = self.data[4]

        treatment_effects_df = self.treatment_effects(
            baseline_components = show_baseline_components,
            treatment_group_only = show_treatment_group_only
            )
        
        treatment_effects_df["Estimate"] = treatment_effects_df["Estimate"].map(lambda x: f"{x:,.3f}")
        treatment_effects_df["SE"] = treatment_effects_df["SE"].map(lambda x: f"{x:,.3f}")
        treatment_effects_df["t"] = treatment_effects_df["t"].map(lambda x: f"{x:,.3f}")
        treatment_effects_df["p"] = treatment_effects_df["p"].map(lambda x: f"{x:,.3f}")
        treatment_effects_df["CI lower"] = treatment_effects_df["CI lower"].map(lambda x: f"{x:,.3f}")
        treatment_effects_df["CI upper"] = treatment_effects_df["CI upper"].map(lambda x: f"{x:,.3f}")

        total_width = (sum(treatment_effects_df.astype(str).map(len).max()) + len(treatment_effects_df.columns) * 2)       

        print("=" * total_width)
        print (model_config["analysis_description"])      
        print("-" * total_width)

        print(treatment_effects_df.to_string(index=False))            
        
        print("-" * total_width)

        if show_covariates and no_covariates > 0:            
            max_width_column1 = max(treatment_effects_df.iloc[:, 0].apply(len))
            covariates_effects_df = self.covariates()
            covariates_effects_df["Estimate"] = covariates_effects_df["Estimate"].map(lambda x: f"{x:,.3f}")
            covariates_effects_df["SE"] = covariates_effects_df["SE"].map(lambda x: f"{x:,.3f}")
            covariates_effects_df["t"] = covariates_effects_df["t"].map(lambda x: f"{x:,.3f}")
            covariates_effects_df["p"] = covariates_effects_df["p"].map(lambda x: f"{x:,.3f}")
            covariates_effects_df["CI lower"] = covariates_effects_df["CI lower"].map(lambda x: f"{x:,.3f}")
            covariates_effects_df["CI upper"] = covariates_effects_df["CI upper"].map(lambda x: f"{x:,.3f}")
            covariates_effects_df.iloc[:, 0] = covariates_effects_df.iloc[:, 0].apply(lambda x: f"{x:<{max_width_column1}}")
            print("Covariates") 
            print(covariates_effects_df.to_string(index=False))
        if not show_covariates or no_covariates == 0:
            if no_covariates > 0:
                print ("Covariates                 YES")
            else:
                print ("Covariates                 NO")

        print("Fixed effects")        
        if model_config["FE_unit"]:
            print (" Units                     YES")
        else:
            print (" Units                     NO")
        if model_config["FE_time"]:
            print (" Time points               YES")
        else:
            print (" Time points               NO")
        if model_config["group_by"] is not None:
            print (" Groups                    YES")
        else:
            print (" Groups                    NO")

        if model_config["ITT"]:
            print ("Individual time trends     YES")
        else:
            print ("Individual time trends     NO")
        if model_config["GTT"]:
            print ("Group-specific time trends YES")
        else:
            print ("Group-specific time trends NO")
            
        print("-" * total_width)
        print("Treatment diagnostics")
        treatment_diagnostics = self.treatment_diagnostics()
        treatment_diagnostics_df = treatment_diagnostics[0]
        no_control_conditions = treatment_diagnostics[1]       
        treatment_diagnostics_df_t = pd.DataFrame(
            treatment_diagnostics_df.values.T, 
            columns = treatment_diagnostics_df["Treatment"].values,
            index = treatment_diagnostics_df.columns)
        treatment_diagnostics_df_t = treatment_diagnostics_df_t.iloc[1:]
        print(treatment_diagnostics_df_t)
        if model_config["no_treatments"] > 1:
            untreated = diffindiff.didtools.untreated_units(
                data = model_data,
                unit_col = model_config["unit_col"],
                treatment_col = model_config["treatment_col"]
                )
            print ("Units with >=1 treatment(s): " + str(untreated[0]) + ", non-treated units: " + str(untreated[1]))
        if len(no_control_conditions) > 0:
            if len(no_control_conditions) == 1:
                print("NOTE: Treatment " + no_control_conditions[0], " has no control conditions")
            else:
                print("NOTE: Treatments " + ", ".join(no_control_conditions), "have no control conditions")  

        print("-" * total_width)
        print ("Input data diagnostics")
        if modeldata_isbalanced:
            print ("Balanced panel data        YES")
        else:
            print ("Balanced panel data        NO")
        if modeldata_ismissing and modeldata_dropmissing:
            print ("Missing values             YES (NA dropped)")
        elif modeldata_ismissing and modeldata_missingreplacebyzero:
            print ("Missing values             YES (NA replaced by zero)")
        else:
            print ("Missing values             NO")
        print ("Outcome variable           " + outcome_col_original + " (Mean=" + str(round(np.mean(model_data[outcome_col_original]), 2)) + " SD=" + str(round(np.std(model_data[outcome_col_original]), 2)) + ")")
        print ("Number of observations     " + str(len(model_data)))

        print ("---------------------------------------------------------------")
        print ("R-Squared                  " + str(round(model_statistics["rsquared"], 3)))
        print ("Adj. R-Squared             " + str(round(model_statistics["rsquared_adj"], 3)))
        print ("===============================================================")

        return self

    def plot_treatment_effects(
        self,
        colors = ["blue", "grey"],
        colors_by_signficance = ["red", "coral", "dimgray", "silver", "green", "palegreen"],
        x_label = "Estimates with confidence intervals",
        y_label = "Coefficient",
        plot_title = "DiD effects",
        plot_grid: bool = True,
        sort_by_coef: bool = False,
        sort_ascending: bool = True,
        plot_size: list = [7, 6],
        scale_plot: bool = True,
        show_central_tendency: bool = False,
        central_tendency: str = "mean"
        ):
                
        model_config = self.data[1]
        no_treatments = model_config["no_treatments"]
        confint_alpha = model_config["confint_alpha"]    
        
        treatment_effects = self.treatment_effects()

        if sort_by_coef:
            treatment_effects = treatment_effects.sort_values(
                by = treatment_effects.columns[1],
                ascending = not sort_ascending
                )
        
        plt.figure(figsize=(plot_size[0], plot_size[1]))
        
        point_estimates = treatment_effects["Estimate"].values
        p = treatment_effects["p"].values
        CI_lower = treatment_effects["CI lower"].values
        CI_upper = treatment_effects["CI upper"].values
        treatment_coefs = treatment_effects.iloc[:, 0]

        if colors_by_signficance is None or colors_by_signficance == []:
            colors_by_signficance = [colors[0], colors[1], colors[0], colors[1], colors[0], colors[1]]

        for i, row in treatment_effects.iterrows():
            
            if p[i] < confint_alpha and point_estimates[i] < 0:

                point_color = colors_by_signficance[0] 
                bar_color = colors_by_signficance[1]
            
            elif p[i] < confint_alpha and point_estimates[i] > 0:
                point_color = colors_by_signficance[4]
                bar_color = colors_by_signficance[5]
            
            else:
            
                point_color = colors_by_signficance[2] 
                bar_color = colors_by_signficance[3]
            
            plt.errorbar(
                x = point_estimates[i],
                y = treatment_coefs[i],
                xerr = [[point_estimates[i] - CI_lower[i]], [CI_upper[i] - point_estimates[i]]],
                fmt='o',
                color = point_color,
                ecolor = bar_color,
                elinewidth = 2,
                capsize = 4
            )

        if show_central_tendency:
            if central_tendency == "median":
                ITE_ct = np.median(treatment_effects["Estimate"])
            else:
                ITE_ct = np.mean(treatment_effects["Estimate"])
            plt.axvline(x = ITE_ct, color = "black")
        else:
            pass

        if scale_plot:
            maxval = treatment_effects.iloc[:, [1, 5, 6]].abs().max().max()
            maxval_plot = maxval*1.1
            plt.xlim(-maxval_plot, maxval_plot)
        
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel(y_label, fontsize=12)
        plt.title(plot_title, fontsize=14)
        if plot_grid:
            plt.grid(True)
        
        plt.show()

    def is_parallel(self):

        model_data = self.data[2]
        model_config = self.data[1]

        modeldata_isparallel = diffindiff.didtools.is_parallel(
            data = model_data,
            unit_col = model_config["unit_col"],
            time_col = model_config["time_col"],
            treatment_col = model_config["treatment_col"],
            outcome_col = model_config["outcome_col"],
            pre_post = model_config["pre_post"]
            )
        
        if modeldata_isparallel is not None:
            return modeldata_isparallel[1]
        else:
            return None
    
    def predictions(self):

        model_predictions = self.data[3]
        return model_predictions
    
    def counterfactual(
        self,
        treatment = None,
        after_treatment_col: str = None
        ):
        
        model_config = self.data[1]
        outcome_col = model_config["outcome_col"]

        model_data = self.data[2]
             
        if treatment is not None:
            if treatment not in model_config["treatment_col"]:
                raise ValueError ("Treatment ", treatment, " not in model object.")
        else:
            treatment = model_config["treatment_col"][0]
            print("NOTE: No treatment was stated. Choosing treatment " + treatment + " for analysis.")

        if after_treatment_col is not None:
            if len(model_config["after_treatment_col"]) == 0:
                raise ValueError ("Model object does not include after-treatment period.")
            if after_treatment_col not in model_config["after_treatment_col"]:
                raise ValueError ("After-treatment variable ", after_treatment_col, " not in model object.")
        else:
            after_treatment_col = []

        olsmodel = self.olsmodel()

        predictions = self.predictions()
        
        model_data = self.data[2]
        
        model_config = self.data[1]
 
        model_data_mod = model_data.copy()
        model_data_mod[treatment] = 0
        if after_treatment_col is not None:
            model_data_mod[after_treatment_col] = 0

        predictions_counterfac = olsmodel.predict(model_data_mod) 

        model_data_mod[outcome_col+"_pred"] = predictions
        model_data_mod[outcome_col+"_pred_counterfac"] = predictions_counterfac

        return model_data_mod

    def olsmodel(self):

        ols_model = self.data[5]
        return ols_model
    
    def prediction_intervals(
        self,
        confint_alpha = 0.05
        ):

        ols_model = self.data[5]

        prediction_intervals = ols_model.get_prediction()
        prediction_intervals = prediction_intervals.summary_frame(alpha = confint_alpha)

        return prediction_intervals
    
    def placebo(
        self,
        treatment: str = None,
        after_treatment_col: str = None,
        TG_col: str = None,
        TT_col: str = None,
        divide: float = 0.5,
        resample: float = 1.0,
        random_state = 71
        ):

        model_config = self.data[1]
        model_data = self.data[2]
             
        if treatment is not None:
            if treatment not in model_config["treatment_col"]:
                raise ValueError ("Treatment ", treatment, " not in model object.")
        else:
            treatment = model_config["treatment_col"][0]
            print("NOTE: No treatment was stated. Choosing treatment " + treatment + " for analysis.")

        if after_treatment_col is not None:
            if len(model_config["after_treatment_col"]) == 0:
                raise ValueError ("Model object does not include after-treatment period.")
            if after_treatment_col not in model_config["after_treatment_col"]:
                raise ValueError ("Treatment ", treatment, " not in model object.")
        else:
            after_treatment_col = []

        if divide <= 0 or divide > 1:
            raise ValueError("Parameter share must be > 0 and <= 1")
        if resample <= 0 or resample > 1:
            raise ValueError("Parameter resample must be > 0 and <= 1")
        
        treatment_statistics = self.treatment_statistics(treatment = treatment)
        
        TG_col_ = "TG_" + treatment
        TT_col_ = "TT_" + treatment
        TGxTT_ = "Placebo_" + treatment
        if TG_col is None and TG_col_ not in model_config["TG_col"]:
            raise ValueError("No treatment group identification variable for treatment " + treatment + ". Please state TG_col = [treatment_group_dummy].")
        if TT_col is None and TT_col_ not in model_config["TT_col"]:
            raise ValueError("No treatment time variable for treatment " + treatment + ". Please state TG_col = [treatment_time_dummy].")
        if TG_col is not None:
            TG_col_ = TG_col
        if TT_col is not None:
            TT_col_ = TT_col

        unit_col = model_config["unit_col"]
        time_col = model_config["time_col"]
        
        groups = treatment_statistics[2]
        control_group = groups[1]
        control_group_N = len(control_group)

        time_periods = treatment_statistics[4]
        treatment_period_start = time_periods[1][0]
        treatment_period_end = time_periods[1][1]
        treatment_period_start = pd.to_datetime(treatment_period_start)
        treatment_period_end = pd.to_datetime(treatment_period_end)

        model_data_c = model_data[model_data[unit_col].isin(control_group)].copy()
        model_data_c[time_col] = pd.to_datetime(model_data_c[time_col])
        model_data_c[unit_col] = model_data_c[unit_col].astype(str)

        units_random_sample = model_data_c[unit_col].sample(
            n = int(round(divide*control_group_N*resample, 0)), 
            random_state = random_state
            ).astype(str).tolist()

        model_data_c[TG_col_] = 0
        model_data_c.loc[(model_data_c[unit_col].isin(units_random_sample)), TG_col_] = 1
        model_data_c[TGxTT_] = model_data_c[TG_col_] * model_data_c[TT_col_]

        model_data_c_analysis = did_analysis(
            data = model_data_c,
            unit_col = unit_col,
            time_col = time_col,
            treatment_col = TGxTT_,
            outcome_col = model_config["outcome_col"],
            TG_col = TG_col_,
            TT_col = TT_col_,
            after_treatment_col = after_treatment_col,
            pre_post = model_config["pre_post"],
            log_outcome = model_config["log_outcome"],
            FE_unit = model_config["FE_unit"],
            FE_time = model_config["FE_time"],
            ITE = model_config["ITE"],
            GTE = model_config["GTE"],
            ITT = model_config["ITT"],
            GTT = model_config["GTT"],
            group_by = model_config["group_by"],
            covariates = model_config["covariates"], 
            confint_alpha = model_config["confint_alpha"],
            drop_missing = model_config["drop_missing"],
            placebo = True    
            )
            
        return model_data_c_analysis

    def plot_timeline(
        self,
        treatment: str = None,
        TG_col: str = None,
        x_label = "Time",
        y_label = "Analysis units",
        y_lim = None,
        plot_title = "Treatment time",
        plot_symbol = "o",
        treatment_group_only = True
        ):

        model_config = self.data[1]
        model_data = self.data[2]

        if treatment is not None:
            if treatment not in model_config["treatment_col"]:
                raise ValueError ("Treatment ", treatment, " not in model object.")
        else:
            treatment = model_config["treatment_col"][0]
            print("NOTE: No treatment was stated. Choosing treatment " + treatment + " for analysis.")
                
        if treatment_group_only:
            if TG_col is None:
                raise ValueError ("Set TG_col = [treament_group_col] to identify treatment group.") 

        modeldata_pivot = model_data.pivot_table (
            index = model_config["time_col"],
            columns = model_config["unit_col"],
            values = treatment
            )

        fig, ax = plt.subplots(figsize=(12, len(modeldata_pivot.columns) * 0.5))

        modeldata_pivot.index = pd.to_datetime(modeldata_pivot.index)

        for i, col in enumerate(modeldata_pivot.columns):
            time_points_treatment = modeldata_pivot.index[modeldata_pivot[col] == 1]
            values = [i] * len(time_points_treatment)
            ax.plot(time_points_treatment, values, plot_symbol, label=col)

        ax.set_xlabel(x_label)
        ax.set_yticks(range(len(modeldata_pivot.columns)))
        ax.set_yticklabels(modeldata_pivot.columns)
        ax.set_ylabel(y_label)
        ax.set_title(plot_title)
        ax.xaxis.set_major_formatter(DateFormatter(model_config["date_format"]))
        
        plt.xticks(rotation=90)
        plt.tight_layout()

        start_date = min(modeldata_pivot.index)
        end_date = max(modeldata_pivot.index)
        ax.set_xlim(start_date, end_date)
        
        if y_lim is not None:
            ax.set_ylim(y_lim)

        plt.show()

        return modeldata_pivot

    def plot(
        self,
        treatment = None,
        x_label: str = "Time",
        y_label: str = "Outcome",
        y_lim = None,
        plot_title: str = "Treatment group vs. control group",
        lines_col: list = ["blue", "green", "red", "orange"],
        lines_style: list = ["solid", "solid", "dashed", "dashed"],
        lines_labels: list = ["TG observed", "CG observed", "TG fit", "CG fit"],
        plot_legend: bool = True,
        plot_grid: bool = True,
        plot_observed: bool = False,
        plot_size_auto: bool = True,
        plot_size: list = [12, 6],
        pre_post_ticks: list = ["Pre", "Post"],
        pre_post_barplot = False,
        pre_post_bar_width = 0.5      
        ):

        model_config = self.data[1]
        TG_col = model_config["TG_col"]
        unit_col = model_config["unit_col"]
        treatment_diagnostics = model_config["treatment_diagnostics"]
        no_treatments = model_config["no_treatments"]
        outcome_col = model_config["outcome_col"]
        outcome_col_predicted = outcome_col+"_predicted"

        if TG_col is None and treatment is None:            
            if no_treatments == 1:
                raise ValueError ("Model object has no column for treatment group with respect to one treatment. Set parameter treatment = [your_treatment].")
            else:
                raise ValueError ("Model object has no column for treatment group with respect to ", str(no_treatments), " treatments. Choose one with parameter treatment.")

        if treatment is not None:
            treatment_included = any(
                entry.get("treatment") == treatment
                for entry in treatment_diagnostics.values()
                )            
            if not treatment_included:
                raise ValueError ("Treatment " + treatment + " not in model object")            
            for key, value in treatment_diagnostics.items():
                if value["treatment"] == treatment:                
                    treatment_group = value["treatment_group"]
                    break                        
        else:
            print("NOTE: No treatment was stated. Choosing treatment " + treatment_diagnostics[0]["treatment"] + " for plotting.")

            treatment_group = treatment_diagnostics[0]["treatment_group"]            
            treatment = treatment_diagnostics[0]["treatment"]

        model_data = self.data[2]
        model_data = model_data.reset_index()
        TG_col = "TG_"+treatment
        model_data[TG_col] = 0
        model_data.loc[model_data[unit_col].isin(treatment_group), TG_col] = 1

        model_predictions = self.data[3]
        model_predictions = pd.DataFrame(model_predictions)
        model_predictions = model_predictions.reset_index()
        model_predictions.rename(columns = {0: outcome_col_predicted}, inplace = True)
    
        model_data = pd.concat ([model_data, model_predictions], axis = 1)
        
        model_data_TG = model_data[model_data[TG_col] == 1]
        model_data_CG = model_data[model_data[TG_col] == 0]
    
        model_data_TG_mean = model_data_TG.groupby(model_config["time_col"])[outcome_col].mean()
        model_data_TG_mean = model_data_TG_mean.reset_index()
        model_data_CG_mean = model_data_CG.groupby(model_config["time_col"])[outcome_col].mean()
        model_data_CG_mean = model_data_CG_mean.reset_index()
    
        model_data_TG_mean_pred = model_data_TG.groupby(model_config["time_col"])[outcome_col_predicted].mean()
        model_data_TG_mean_pred = model_data_TG_mean_pred.reset_index()
        model_data_CG_mean_pred = model_data_CG.groupby(model_config["time_col"])[outcome_col_predicted].mean()
        model_data_CG_mean_pred = model_data_CG_mean_pred.reset_index()
    
        model_data_TG_CG = pd.concat ([
            model_data_TG_mean.reset_index(),
            model_data_CG_mean[outcome_col].reset_index(),
            model_data_TG_mean_pred[outcome_col_predicted].reset_index(),
            model_data_CG_mean_pred[outcome_col_predicted].reset_index()
            ],
            axis = 1)
    
        model_data_TG_CG.columns.values[1] = "t"
        model_data_TG_CG.columns.values[2] = outcome_col + "_observed_TG"
        model_data_TG_CG.columns.values[4] = outcome_col + "_observed_CG"
        model_data_TG_CG.columns.values[6] = outcome_col + "_expected_TG"
        model_data_TG_CG.columns.values[8] = outcome_col + "_expected_CG"
    
        if plot_size_auto:
            if model_config["pre_post"]:
                fig, ax = plt.subplots(figsize=(7, 6))
            else:
                fig, ax = plt.subplots(figsize=(12, 6))
        else:
            fig, ax = plt.subplots(figsize=(plot_size[0], plot_size[1]))       
    
        model_data_TG_CG["t"] = pd.to_datetime(model_data_TG_CG["t"])

        if not model_config["pre_post"]:
            pre_post_barplot = False

        if pre_post_barplot:

            x_pos_t1_TG = 0
            x_pos_t1_CG = x_pos_t1_TG + pre_post_bar_width  
            x_pos_t2_TG = 1.5  
            x_pos_t2_CG = x_pos_t2_TG + pre_post_bar_width  

            plt.bar(
                x = x_pos_t1_TG, 
                height = model_data_TG_CG[outcome_col + "_expected_TG"][0], 
                label = lines_labels[2], 
                color = lines_col[2], 
                width = pre_post_bar_width
                )   
            plt.bar(
                x = x_pos_t1_CG, 
                height = model_data_TG_CG[outcome_col + "_expected_CG"][0], 
                label = lines_labels[3], 
                color = lines_col[3], 
                width = pre_post_bar_width
                )            
            plt.bar(
                x = x_pos_t2_TG, 
                height = model_data_TG_CG[outcome_col + "_expected_TG"][1],                 
                color = lines_col[2], 
                width = pre_post_bar_width
                )            
            plt.bar(
                x = x_pos_t2_CG, 
                height = model_data_TG_CG[outcome_col + "_expected_CG"][1],                 
                color=lines_col[3], 
                width = pre_post_bar_width
                )

            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(plot_title)
            
        else:

            if plot_observed:
                plt.plot(
                    model_data_TG_CG["t"], 
                    model_data_TG_CG[outcome_col + "_observed_TG"], 
                    label = lines_labels[0], 
                    color=lines_col[0], 
                    linestyle=lines_style[0]
                    )
                plt.plot(
                    model_data_TG_CG["t"], 
                    model_data_TG_CG[outcome_col + "_observed_CG"], 
                    label = lines_labels[1], 
                    color=lines_col[1], 
                    linestyle=lines_style[1]
                    )
            
            plt.plot(
                model_data_TG_CG["t"], 
                model_data_TG_CG[outcome_col + "_expected_TG"], 
                label=lines_labels[2], 
                color=lines_col[2], 
                linestyle=lines_style[2]
                )
            plt.plot(
                model_data_TG_CG["t"], 
                model_data_TG_CG[outcome_col + "_expected_CG"], 
                label=lines_labels[3], 
                color=lines_col[3], 
                linestyle=lines_style[3]
                )

            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(plot_title)
            ax.xaxis.set_major_formatter(DateFormatter(model_config["date_format"]))

        if model_config["pre_post"]:
            if not pre_post_barplot:
                plt.xticks(
                    model_data_TG_CG["t"].unique(), 
                    labels = [pre_post_ticks[0], pre_post_ticks[1]]
                    )  
            else:
                plt.xticks(
                    [0.25, 1.75], 
                    labels = [pre_post_ticks[0], pre_post_ticks[1]]
                    )  
        else:
            plt.xticks(rotation=90)
        
        plt.tight_layout()

        if plot_legend:
            plt.legend()

        if plot_grid:
            if not model_config["pre_post"]:
                plt.grid(True)
            else:
                plt.grid(axis='y', linestyle='-', alpha=0.7)

        if y_lim is not None:
            ax.set_ylim(y_lim)
            
        plt.show()

        return model_data_TG_CG    

    def plot_counterfactual(
        self,
        treatment: str = None,
        after_treatment_col: str = None,
        x_label: str = "Time",
        y_label: str = "Outcome",
        y_lim = None,
        plot_title: str = "Treatment group Counterfactual",
        lines_col: list = ["blue", "green"],
        lines_style: list = ["solid", "dashed"],
        lines_labels: list = ["TG", "TG counterfactual"],
        plot_legend: bool = True,
        plot_grid: bool = True,
        plot_size: list = [12, 6]
        ):

        model_config = self.data[1]
        outcome_col = model_config["outcome_col"]
        outcome_col_pred = outcome_col+"_pred"
        outcome_col_pred_counterfac = outcome_col+"_pred_counterfac"
        TG_col = model_config["TG_col"]
        time_col = model_config["time_col"]
        unit_col = model_config["unit_col"]
        no_treatments = model_config["no_treatments"]
        treatment_diagnostics = model_config["treatment_diagnostics"]

        if TG_col is None and treatment is None:
            
            if no_treatments == 1:
                raise ValueError ("Model object has no column for treatment group with respect to one treatment. Set parameter treatment = [your_treatment].")
            else:
                raise ValueError ("Model object has no column for treatment group with respect to ", str(no_treatments), " treatments. Choose one with parameter treatment.")

        model_data_mod = self.counterfactual(
            treatment = treatment,
            after_treatment_col = after_treatment_col
            )

        if treatment is not None:

            treatment_included = any(
                entry.get("treatment") == treatment
                for entry in treatment_diagnostics.values()
                )
            
            if not treatment_included:
                raise ValueError ("Treatment " + treatment + " not in model object")
            
            for key, value in treatment_diagnostics.items():
                if value["treatment"] == treatment:
                    treatment_group = value["treatment_group"]
                    break
    
        else:
            print("NOTE: No treatment was stated. Choosing treatment " + treatment_diagnostics[0]["treatment"] + " for plotting.")

            treatment_group = treatment_diagnostics[0]["treatment_group"]

            treatment = treatment_diagnostics[0]["treatment"]

        treatment_group = [str(x) for x in treatment_group]

        TG_col = "TG_" + treatment
        
        model_data_mod[TG_col] = 0
        model_data_mod.loc[model_data_mod[unit_col].astype(str).isin(treatment_group), TG_col] = 1

        model_data_mod_TG = model_data_mod.loc[model_data_mod[TG_col] == 1]  

        model_data_TG_mean_pred = model_data_mod_TG.groupby(time_col)[outcome_col_pred].mean()
        model_data_TG_mean_pred = model_data_TG_mean_pred.reset_index()
        
        model_data_TG_mean_pred_counterfac = model_data_mod_TG.groupby(time_col)[outcome_col_pred_counterfac].mean()
        model_data_TG_mean_pred_counterfac = model_data_TG_mean_pred_counterfac.reset_index()
        model_data_TG_mean_pred_counterfac = model_data_TG_mean_pred_counterfac.drop(columns=[time_col])

        model_data_TG_mean = pd.concat ([
            model_data_TG_mean_pred.reset_index(),
            model_data_TG_mean_pred_counterfac.reset_index()
            ],
            axis = 1)
        model_data_TG_mean[time_col] = pd.to_datetime(model_data_TG_mean[time_col])

        fig, ax = plt.subplots(figsize=(plot_size[0], plot_size[1]))   
        
        plt.plot(
            model_data_TG_mean[time_col], 
            model_data_TG_mean[outcome_col_pred_counterfac], 
            label = lines_labels[1], 
            color = lines_col[1], 
            linestyle=lines_style[1]
            )
        plt.plot(
            model_data_TG_mean[time_col], 
            model_data_TG_mean[outcome_col_pred], 
            label = lines_labels[0], 
            color = lines_col[0], 
            linestyle = lines_style[0]
            )
        
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plot_title)
        ax.xaxis.set_major_formatter(DateFormatter(model_config["date_format"]))

        if plot_legend:
            plt.legend()

        if plot_grid:
            if not model_config["pre_post"]:
                plt.grid(True)
            else:
                plt.grid(axis='y', linestyle='-', alpha=0.7)
        
        plt.xticks(rotation=90)
        plt.tight_layout()
        
        if y_lim is not None:
            ax.set_ylim(y_lim)
            
        plt.show()

        return model_data_TG_mean

def did_analysis(
    data: pd.DataFrame,
    unit_col: str,
    time_col: str,
    treatment_col: list,
    outcome_col: str,
    TG_col: list = [],
    TT_col: list = [],
    after_treatment_col: list = [],
    ATT_col: list = [],
    pre_post: bool = False,
    log_outcome: bool = False,
    log_outcome_add = 0.01,
    FE_unit: bool = False,
    FE_time: bool = False,
    intercept: bool = True,
    ITE: bool = False,
    GTE: bool = False,
    ITT: bool = False,
    GTT: bool = False,
    group_by: str = None,
    covariates: list = [],
    group_benefit: list = [],
    placebo: bool = False,
    confint_alpha = 0.05,
    bonferroni: bool = False,
    freq = "D",
    date_format = "%Y-%m-%d",
    drop_missing: bool = True,
    missing_replace_by_zero: bool = False
    ):
    
    diffindiff.didtools.check_columns(
        df = data,
        columns = [unit_col, time_col, outcome_col]
        )
    
    if isinstance (treatment_col, str):
        if treatment_col == "":
            raise ValueError ("No treatment(s) in treatment_col stated.")
        treatment_col = [treatment_col]
    no_treatments = len(treatment_col)
    if no_treatments == 0:
        raise ValueError ("No treatment(s) in treatment_col stated.")    
    diffindiff.didtools.check_columns(
        df = data,
        columns = treatment_col
        )    
    
    cols_relevant = [
        unit_col,
        time_col,
        *treatment_col        
        ]
    
    treatment_diagnostics = {}    
    staggered_adoption = False
    for i, treatment in enumerate(treatment_col):    
        is_notreatment = diffindiff.didtools.is_notreatment(
            data = data,
            unit_col = unit_col,
            treatment_col = treatment
            )        
        is_parallel = diffindiff.didtools.is_parallel(
            data = data,
            unit_col = unit_col,
            time_col = time_col,
            treatment_col = treatment,
            outcome_col = outcome_col,
            pre_post = pre_post,
            alpha = confint_alpha
            )        
        is_simultaneous = diffindiff.didtools.is_simultaneous(
            data = data,
            unit_col = unit_col,
            time_col = time_col,
            treatment_col = treatment
            )        
        is_binary = diffindiff.didtools.is_binary(
            data = data,
            treatment_col = treatment
            )    
        treatment_diagnostics[i] = { 
            "treatment": treatment,
            "is_notreatment": is_notreatment[0],
            "treatment_group": is_notreatment[1],
            "control_group": is_notreatment[2],
            "is_parallel": is_parallel[0],
            "is_simultaneous": is_simultaneous,
            "is_binary": is_binary[0],
            "treatment_format": is_binary[1]            
            }        
    for key, value in treatment_diagnostics.items():
        if not value["is_simultaneous"]:
            staggered_adoption = True

    if no_treatments > 1:
        FE_unit = True
        intercept = False
        TG_col = []
        print ("NOTE: Quasi-experiment includes more than one treatment. Unit fixed effects are used instead of control group baseline and treatment group deviation.")
           
    if ITE:        
        FE_unit = True
        print ("NOTE: Model includes individual treatment effects. Unit fixed effects are included.")
        if GTE:
            GTE = False
            print ("NOTE: Both group and individual treatment effects were stated. Switching to individual treatment effects only.")
    if ITT:        
        FE_unit = True        
        TT_col = []
        print ("NOTE: Model includes individual time trends. Unit fixed effects are included. Treatment time variable is dropped.")
        if FE_time:
            FE_time = False
            print ("NOTE: Time fixed effects are dropped.")
        if GTT:
            GTT = False
            print ("NOTE: Both group and individual time trends were stated. Switching to individual time trends only.")
            
    if staggered_adoption:
        FE_unit = True
        FE_time = True        
        print ("NOTE: Quasi-experiment includes one or more staggered treatments. Two-way fixed effects model is used.")

    FE_group = False
    if group_by is not None and group_by != "":
        FE_group = True        
               
    if FE_unit:
        TG_col = []
    if FE_time:
        TT_col = []
    if FE_group:    
        TG_col = []        
        intercept = False
        print ("NOTE: Quasi-experiment includes group fixed effects. Control group baseline and treatment group deviation are dropped.")   
    
    if after_treatment_col is not None or (isinstance (after_treatment_col, list) and len(after_treatment_col) > 0):
        if isinstance (after_treatment_col, str):
            after_treatment_col = [after_treatment_col]
        after_treatment_col = [entry for entry in after_treatment_col if entry is not None]
        diffindiff.didtools.check_columns(
            df = data,
            columns = after_treatment_col
            )        
        cols_relevant = cols_relevant + after_treatment_col

    if ATT_col is not None or (isinstance (ATT_col, list) and len(ATT_col) > 0):
        if isinstance (ATT_col, str):
            ATT_col = [ATT_col]
        ATT_col = [entry for entry in ATT_col if entry is not None]
        diffindiff.didtools.check_columns(
            df = data,
            columns = ATT_col
            )        
        cols_relevant = cols_relevant + ATT_col

    if TG_col is not None or (isinstance (TG_col, list) and len(TG_col) > 0):
        if isinstance (TG_col, str):
            TG_col = [TG_col]
        TG_col = [entry for entry in TG_col if entry is not None]        
        diffindiff.didtools.check_columns(
            df = data,
            columns = TG_col
            )        
        cols_relevant = cols_relevant + TG_col        
    else:       
        FE_unit = True

    if TT_col is not None or (isinstance (TT_col, list) and len(TT_col) > 0):
        if isinstance (TT_col, str):
            TT_col = [TT_col]
        TT_col = [entry for entry in TT_col if entry is not None]
        diffindiff.didtools.check_columns(
            df = data,
            columns = TT_col
            )        
        cols_relevant = cols_relevant + TT_col        
    else:        
        FE_time = True

    if covariates is not None or (isinstance (covariates, list) and len(covariates) > 0):
        diffindiff.didtools.check_columns(
            df = data,
            columns = covariates
            )        
        cols_relevant = cols_relevant + covariates

    if group_by is not None and group_by != "":
        diffindiff.didtools.check_columns(
            df = data,
            columns = [group_by]
            )
        if group_by not in data.columns:
            cols_relevant = cols_relevant + [group_by]   
    
    cols_relevant = cols_relevant + [outcome_col]
    data = data[cols_relevant].copy()
    
    if "date_counter" not in data.columns:    
        data = diffindiff.didtools.date_counter(
            data,
            time_col,
            new_col = "date_counter"
            )

    modeldata_ismissing = diffindiff.didtools.is_missing(
        data, 
        drop_missing = drop_missing,
        missing_replace_by_zero = missing_replace_by_zero
        )    
    if modeldata_ismissing[0]:        
        print("NOTE: Variables contain NA values: " + ' ,'.join(modeldata_ismissing[1]), end = ". ")
        if drop_missing or missing_replace_by_zero:
            data = modeldata_ismissing[2]           
        if drop_missing:
            print ("Rows with missing values are skipped.")
        elif missing_replace_by_zero:
            print ("Missing values are replaced by 0.")
        else:
            print ("Missing values are not cleaned. Model may crash.")   
    
    other_cols_relevant = [col for col in cols_relevant if col not in [unit_col, time_col, outcome_col]]
    modeldata_isbalanced = diffindiff.didtools.is_balanced(
        data = data,
        unit_col = unit_col,
        time_col = time_col,
        outcome_col = outcome_col,
        other_cols = other_cols_relevant
        )
    
    data_diagnostics = {
        "is_balanced": modeldata_isbalanced, 
        "is_missing": modeldata_ismissing[0], 
        "drop_missing": drop_missing, 
        "missing_replace_by_zero": missing_replace_by_zero
        }
        
    if log_outcome:        
        if missing_replace_by_zero:
            data["log_"+f'{outcome_col}'] = np.log(data[outcome_col]+log_outcome_add)
        else:
            data["log_"+f'{outcome_col}'] = np.log(data[outcome_col])
        outcome_col = "log_"+f'{outcome_col}'

    did_formula = f'{outcome_col} ~ {" + ".join(treatment_col)}'
    
    if TG_col is not None and len(TG_col) > 0:
        did_formula = did_formula + f' + {" + ".join(TG_col)}'        
    if TT_col is not None and len(TT_col) > 0:
        did_formula = did_formula + f' + {" + ".join(TT_col)}'   

    if len(after_treatment_col) > 0:
        did_formula = did_formula + f' + {" + ".join(after_treatment_col)}'
    if len(ATT_col) > 0:
        did_formula = did_formula + f' + {" + ".join(ATT_col)}'
    
    if FE_unit:
        unit_col_todummies = diffindiff.didtools.to_dummies(
            data = data,
            col = unit_col,
            prefix = "UNIT",
            drop_first = intercept
            )        
        data = unit_col_todummies[0]
        did_formula = did_formula + f' + {unit_col_todummies[1]}'
        dummy_unit_vars = list(unit_col_todummies[2]["UNIT_"+unit_col].values)
        dummy_unit_original = list(unit_col_todummies[2][unit_col].values)

    if FE_time:
        time_col_todummies = diffindiff.didtools.to_dummies(   
            data = data,
            col = time_col,
            prefix = "TIME",
            drop_first = intercept
            )
        data = time_col_todummies[0]
        did_formula = did_formula + f' + {time_col_todummies[1]}'        
        dummy_time_vars = list(time_col_todummies[2]["TIME_"+time_col].values)
        dummy_time_original = list(time_col_todummies[2][time_col].values)   

    if GTE or GTT:    
        if group_by is None or group_by == "":
            print ("WARNING: Grouping variable is not defined. No group-specific analyses are carried out. Define a grouping variable using group_by.")
        else:            
            group_col_todummies = diffindiff.didtools.to_dummies(
                data = data,
                col = group_by,
                prefix = "GROUP",
                drop_first = False
                )
            data = group_col_todummies[0]
            GTE_columns_group = group_col_todummies[1]            
            dummy_group_original = list(group_col_todummies[2][group_by].values)
            dummy_group_vars = list(group_col_todummies[2]["GROUP_"+group_by].values)
            
    if GTT:        
        if group_by is not None and group_by != "":
            if "date_counter" not in data.columns:
                data = diffindiff.didtools.date_counter(
                    data,
                    time_col,
                    new_col="date_counter"
                    )
            group_x_time = pd.DataFrame()
            for col in dummy_group_vars:
                group_x_time[col] = data[col] * data["date_counter"]
                new_col_name = f"{col}_x_time"
                group_x_time = group_x_time.rename(columns={col: new_col_name})
            data = pd.concat([data, group_x_time], axis = 1)
            GTT_columns_groupxtime = ' + '.join(group_x_time.columns)
            did_formula = did_formula + f' + {GTE_columns_group} + {GTT_columns_groupxtime}'
    
    if ITT:        
        if "date_counter" not in data.columns:
            data = diffindiff.didtools.date_counter(
                data,
                time_col,
                new_col="date_counter"
                )        
        unit_x_time = pd.DataFrame()
        for col in dummy_unit_vars:
            unit_x_time[col] = data[col] * data["date_counter"]
            new_col_name = f"{col}_x_time"
            unit_x_time = unit_x_time.rename(columns={col: new_col_name})
        data = pd.concat([data, unit_x_time], axis = 1)
        ITT_columns_unitxtime = ' + '.join(unit_x_time.columns)
        did_formula = did_formula + f' + {ITT_columns_unitxtime}'
    
    if GTE:
        if group_by is None or group_by == "":
            pass
        else:
            group_x_treatment = pd.DataFrame()
            for col in dummy_group_vars:
                for treatment in treatment_col:
                    group_x_treatment[col] = data[col] * data[treatment]
                    new_col_name = f"{treatment}_{col}_x_time"
                    group_x_treatment = group_x_treatment.rename(columns={col: new_col_name})
            data = pd.concat([data, group_x_treatment], axis = 1)
            GTE_columns_groupxtreatment = ' + '.join(group_x_treatment.columns)
            did_formula = did_formula + f' + {GTE_columns_group} + {GTE_columns_groupxtreatment}'
    
    if ITE:
        unit_x_treatment = pd.DataFrame()
        for col in dummy_unit_vars:
            for treatment in treatment_col:
                unit_x_treatment[col] = data[col] * data[treatment]
                new_col_name = f"{treatment}_x_{col}"
                unit_x_treatment = unit_x_treatment.rename(columns={col: new_col_name})
        data = pd.concat([data, unit_x_treatment], axis = 1)
        ITE_columns_unitxtreatment = ' + '.join(unit_x_treatment.columns)
        did_formula = did_formula + f' + {ITE_columns_unitxtreatment}'

    if len(covariates) > 0:
        if group_by in covariates:
            covariates.remove(group_by)
        covariates_join = ' + '.join(covariates)
        did_formula = did_formula + f' +{covariates_join}'

    if len(group_benefit) > 0:        
        group_benefit = diffindiff.didtools.unique(group_benefit)
        if no_treatments == 1:       
            DDD = True
            if "TG_"+treatment_diagnostics[0]["treatment"] not in data.columns:                
                data["TG_"+treatment_diagnostics[0]["treatment"]] = 0
                data.loc[data[unit_col].isin(treatment_diagnostics[0]["treatment_group"]), "TG_"+treatment_diagnostics[0]["treatment"]] = 1
                TG_col = "TG_"+treatment_diagnostics[0]["treatment"]            
            data["group_benefit"] = 0
            data.loc[data[unit_col].astype(str).isin(group_benefit.astype(str)), "group_benefit"] = 1            
            data["TG_x_groupbenefit"] = data[TG_col] * data["group_benefit"]
            data["groupbenefit_x_treatment"] = data["group_benefit"] * data[treatment_diagnostics[0]["treatment"]]
            data["TG_x_groupbenefit_x_treatment"] = data[TG_col] * data["group_benefit"] * data[treatment_diagnostics[0]["treatment"]]
            did_formula = did_formula + f'+ group_benefit + TG_x_groupbenefit + groupbenefit_x_treatment + TG_x_groupbenefit_x_treatment'
        else:            
            print ("NOTE: Multiple treatments combined with triple difference (DDD) analysis are not yet supported. Switching to DiD.")            
            DDD = False
    else:
        group_benefit = []
        DDD = False
    
    did_formula = did_formula[:-1] if did_formula.endswith(" ") else did_formula
    did_formula = did_formula[:-1] if did_formula.endswith("+") else did_formula
    did_formula = did_formula[:-1] if did_formula.endswith(" ") else did_formula
    if not intercept:
        did_formula = did_formula + f' -1'    
    
    analysis_description = "Difference in Differences (DiD) Analysis"
    if DDD:
        analysis_description = "Difference in Difference in Differences (DDD) Analysis"
    if placebo:
        analysis_description = "Placebo Difference in Differences (DiD) Analysis"

    model_config = {
        "TG_col": TG_col,
        "TT_col": TT_col,
        "treatment_col": treatment_col,
        "unit_col": unit_col,
        "time_col": time_col,
        "outcome_col": outcome_col,
        "log_outcome": log_outcome,
        "freq": freq,
        "date_format": date_format,
        "after_treatment_col": after_treatment_col,
        "ATT_col": ATT_col,
        "pre_post": pre_post,
        "FE_unit": FE_unit,
        "FE_time": FE_time,
        "FE_group": FE_group,
        "intercept": intercept,
        "ITT": ITT,
        "GTT": GTT,
        "ITE": ITE,
        "GTE": GTE,
        "group_by": group_by,
        "covariates": covariates,
        "DDD": DDD,
        "group_benefit": group_benefit,
        "placebo": placebo,
        "confint_alpha": confint_alpha,
        "bonferroni": bonferroni,
        "drop_missing": drop_missing,
        "no_treatments": no_treatments,
        "treatment_diagnostics": treatment_diagnostics,
        "data_diagnostics": data_diagnostics,
        "did_formula": did_formula,
        "analysis_description": analysis_description
        }

    ols_model = ols(did_formula, data = data).fit()
    ols_coefficients = ols_model.params
    coef_standarderrors = ols_model.bse
    coef_t = ols_model.tvalues
    coef_p = ols_model.pvalues
    if bonferroni:
        confint_alpha = confint_alpha/no_treatments
    coef_conf_intervals = ols_model.conf_int(alpha = confint_alpha)
    
    model_results = {}

    if not ITE and not GTE:        
        ATE = {}        
        for i, treatment in enumerate(treatment_col):
            ATE[i] = {
                "Coefficient": treatment,
                "Estimate": ols_coefficients[treatment],
                "SE": float(coef_standarderrors[treatment]),
                "t": float(coef_t[treatment]),
                "p": float(coef_p[treatment]),
                "CI_lower": float(coef_conf_intervals.loc[treatment, 0]),
                "CI_upper": float(coef_conf_intervals.loc[treatment, 1]),
                }
        model_results = {"average_treatment_effects": ATE}
    
    if (any(col in ols_coefficients for col in TG_col)):
        TG = {}        
        for i, TG_ in enumerate(TG_col):
            TG[i] = {
                "Coefficient": TG_,
                "Estimate": ols_coefficients[TG_],
                "SE": float(coef_standarderrors[TG_]),
                "t": float(coef_t[TG_]),
                "p": float(coef_p[TG_]),
                "CI_lower": float(coef_conf_intervals.loc[TG_, 0]),
                "CI_upper": float(coef_conf_intervals.loc[TG_, 1]),
                }            
        model_results["treatment_group_deviation"] = TG

    if (any(col in ols_coefficients for col in TT_col)):
        TT = {}        
        for i, TT_ in enumerate(TT_col):
            TT[i] = {
                "Coefficient": TT_,
                "Estimate": ols_coefficients[TT_],
                "SE": float(coef_standarderrors[TT_]),
                "t": float(coef_t[TT_]),
                "p": float(coef_p[TT_]),
                "CI_lower": float(coef_conf_intervals.loc[TT_, 0]),
                "CI_upper": float(coef_conf_intervals.loc[TT_, 1]),
                }            
        model_results["non_treatment_time_effect"] = TT

    if "Intercept" in ols_coefficients:        
        Intercept = ols_coefficients["Intercept"]
        Intercept_SE = round(coef_standarderrors["Intercept"], 3)
        Intercept_t = round(coef_t["Intercept"], 3)
        Intercept_p = round(coef_p["Intercept"], 3)
        Intercept_CI_lower = coef_conf_intervals.loc["Intercept", 0]
        Intercept_CI_upper = coef_conf_intervals.loc["Intercept", 1]
        Intercept = {
            "Estimate": Intercept, 
            "SE": Intercept_SE, 
            "t": Intercept_t, 
            "p": Intercept_p,
            "CI_lower": Intercept_CI_lower,
            "CI_upper": Intercept_CI_upper,
            }
        model_results["control_group_baseline"] = Intercept

    if len(after_treatment_col) > 0:
        AATE = {}
        for i, after_treatment in enumerate(after_treatment_col):
            AATE[i] = {
                "Coefficient": after_treatment,
                "Estimate": ols_coefficients[after_treatment],
                "SE": float(coef_standarderrors[after_treatment]),
                "t": float(coef_t[after_treatment]),
                "p": float(coef_p[after_treatment]),
                "CI_lower": float(coef_conf_intervals.loc[after_treatment, 0]),
                "CI_upper": float(coef_conf_intervals.loc[after_treatment, 1]),
                }
        model_results["average_after_treatment_effects"] = AATE
    
    if (any(col in ols_coefficients for col in ATT_col)):
        ATT = {}        
        for i, ATT_ in enumerate(ATT_col):
            ATT[i] = {
                "Coefficient": ATT_,
                "Estimate": ols_coefficients[ATT_],
                "SE": float(coef_standarderrors[ATT_]),
                "t": float(coef_t[ATT_]),
                "p": float(coef_p[ATT_]),
                "CI_lower": float(coef_conf_intervals.loc[ATT_, 0]),
                "CI_upper": float(coef_conf_intervals.loc[ATT_, 1]),
                }            
        model_results["after_treatment_time_effects"] = ATT

    if DDD:

        ATET = ols_coefficients["TG_x_groupbenefit_x_treatment"]
        ATET_SE = round(coef_standarderrors["TG_x_groupbenefit_x_treatment"], 3)
        ATET_t = round(coef_t["TG_x_groupbenefit_x_treatment"], 3)
        ATET_p = round(coef_p["TG_x_groupbenefit_x_treatment"], 3)
        ATET_CI_lower = coef_conf_intervals.loc["TG_x_groupbenefit_x_treatment", 0]
        ATET_CI_upper = coef_conf_intervals.loc["TG_x_groupbenefit_x_treatment", 1]
        ATET = {
            "ATET": ATET, 
            "ATET_SE": ATET_SE, 
            "ATET_t": ATET_t, 
            "ATET_p": ATET_p,
            "ATET_CI_lower": ATET_CI_lower,
            "ATET_CI_upper": ATET_CI_upper
            }
        model_results["ATET"] = ATET

        BG = ols_coefficients["group_benefit"]
        BG_SE = round(coef_standarderrors["group_benefit"], 3)
        BG_t = round(coef_t["group_benefit"], 3)
        BG_p = round(coef_p["group_benefit"], 3)
        BG_CI_lower = coef_conf_intervals.loc["group_benefit", 0]
        BG_CI_upper = coef_conf_intervals.loc["group_benefit", 1]
        BG = {
            "BG": BG, 
            "BG_SE": BG_SE, 
            "BG_t": BG_t, 
            "BG_p": BG_p,
            "BG_CI_lower": BG_CI_lower,
            "BG_CI_upper": BG_CI_upper
            }
        model_results["BG"] = BG

        TBG = ols_coefficients["TG_x_groupbenefit"]
        TBG_SE = round(coef_standarderrors["TG_x_groupbenefit"], 3)
        TBG_t = round(coef_t["TG_x_groupbenefit"], 3)
        TBG_p = round(coef_p["TG_x_groupbenefit"], 3)
        TBG_CI_lower = coef_conf_intervals.loc["TG_x_groupbenefit", 0]
        TBG_CI_upper = coef_conf_intervals.loc["TG_x_groupbenefit", 1]
        TBG = {
            "TBG": TBG, 
            "TBG_SE": TBG_SE, 
            "TBG_t": TBG_t, 
            "TBG_p": TBG_p,
            "TBG_CI_lower": TBG_CI_lower,
            "TBG_CI_upper": TBG_CI_upper
            }
        model_results["TBG"] = TBG

        TTB = ols_coefficients["groupbenefit_x_treatment"]
        TTB_SE = round(coef_standarderrors["groupbenefit_x_treatment"], 3)
        TTB_t = round(coef_t["groupbenefit_x_treatment"], 3)
        TTB_p = round(coef_p["groupbenefit_x_treatment"], 3)
        TTB_CI_lower = coef_conf_intervals.loc["groupbenefit_x_treatment", 0]
        TTB_CI_upper = coef_conf_intervals.loc["groupbenefit_x_treatment", 1]
        TTB = {
            "TTB": TTB, 
            "TTB_SE": TTB_SE, 
            "TTB_t": TTB_t, 
            "TTB_p": TTB_p,
            "TTB_CI_lower": TTB_CI_lower,
            "TTB_CI_upper": TTB_CI_upper
            }
        model_results["TTB"] = TTB

    fixed_effects = [None, None, None]
    
    if FE_unit:        
        FE_unit_vars = list(unit_col_todummies[2]["UNIT_"+unit_col].values)        
        FE_unit_coef = {}        
        for i, unit_dummy in enumerate(FE_unit_vars):
            FE_unit_coef[i] = {
                "Coefficient": dummy_unit_original[i],
                "Estimate": ols_coefficients[unit_dummy],
                "SE": float(coef_standarderrors[unit_dummy]),
                "t": float(coef_t[unit_dummy]),
                "p": float(coef_p[unit_dummy]),
                "CI_lower": float(coef_conf_intervals.loc[unit_dummy, 0]),
                "CI_upper": float(coef_conf_intervals.loc[unit_dummy, 1]),
                "Coefficient_type": "Fixed effects for observational units"
                }
        fixed_effects[0] = {"FE_unit": FE_unit_coef}
        
    if FE_time:        
        FE_time_vars = list(time_col_todummies[2]["TIME_"+time_col].values)        
        FE_time_coef = {}        
        for i, time_dummy in enumerate(FE_time_vars):
            FE_time_coef[i] = {
                "Coefficient": dummy_time_original[i],
                "Estimate": ols_coefficients[time_dummy],
                "SE": float(coef_standarderrors[time_dummy]),
                "t": float(coef_t[time_dummy]),
                "p": float(coef_p[time_dummy]),
                "CI_lower": float(coef_conf_intervals.loc[time_dummy, 0]),
                "CI_upper": float(coef_conf_intervals.loc[time_dummy, 1]),
                "Coefficient_type": "Fixed effects for time points"
                }
        fixed_effects[1] = {"FE_time": FE_time_coef}
        
    if group_by is not None:        
        FE_group_vars = list(group_col_todummies[2]["GROUP_"+group_by].values)        
        FE_group_coef = {}        
        for i, group_dummy in enumerate(FE_group_vars):
            FE_group_coef[i] = {
                "Coefficient": dummy_group_original[i],
                "Estimate": ols_coefficients[group_dummy],
                "SE": float(coef_standarderrors[group_dummy]),
                "t": float(coef_t[group_dummy]),
                "p": float(coef_p[group_dummy]),
                "CI_lower": float(coef_conf_intervals.loc[group_dummy, 0]),
                "CI_upper": float(coef_conf_intervals.loc[group_dummy, 1]),
                "Coefficient_type": "Fixed effects for groups"
                }
        fixed_effects[2] = {"FE_group": FE_group_coef}

    model_results["fixed_effects"] = fixed_effects

    if ITT:

        ITT_vars = list(unit_x_time.columns)
        
        ITT_coef = {}

        for i, ITT_var in enumerate(ITT_vars):

            ITT_coef[i] = {
                "Coefficient": dummy_unit_original[i],
                "Estimate": ols_coefficients[ITT_var],
                "SE": float(coef_standarderrors[ITT_var]),
                "t": float(coef_t[ITT_var]),
                "p": float(coef_p[ITT_var]),
                "CI_lower": float(coef_conf_intervals.loc[ITT_var, 0]),
                "CI_upper": float(coef_conf_intervals.loc[ITT_var, 1]),
                }      
        
        model_results["individual_time_trends"] = ITT_coef

    if ITE:

        ITE_vars = list(unit_x_treatment.columns)
        
        ITE_coef = {}

        dummy_unit_current = dummy_unit_original*no_treatments

        treatment_current = []
        for treatment in treatment_col:
            treatment_single = [treatment]*len(dummy_unit_original)
            treatment_current = treatment_current + treatment_single

        for i, ITE_var in enumerate(ITE_vars):                

            ITE_coef[i] = {
                "Coefficient": treatment_current[i] + " " + dummy_unit_current[i],
                "Estimate": float(ols_coefficients[ITE_var]),
                "SE": float(coef_standarderrors[ITE_var]),
                "t": float(coef_t[ITE_var]),
                "p": float(coef_p[ITE_var]),
                "CI_lower": float(coef_conf_intervals.loc[ITE_var, 0]),
                "CI_upper": float(coef_conf_intervals.loc[ITE_var, 1]),
                }            
            
        model_results["individual_treatment_effects"] = ITE_coef

    if GTT:

        GTT_vars = list(group_x_time.columns)
        
        GTT_coef = {}

        for i, GTT_var in enumerate(GTT_vars):

            GTT_coef[i] = {
                "Coefficient": dummy_group_original[i],
                "Estimate": ols_coefficients[GTT_var],
                "SE": float(coef_standarderrors[GTT_var]),
                "t": float(coef_t[GTT_var]),
                "p": float(coef_p[GTT_var]),
                "CI_lower": float(coef_conf_intervals.loc[GTT_var, 0]),
                "CI_upper": float(coef_conf_intervals.loc[GTT_var, 1]),
                }      
        
        model_results["group_time_trends"] = GTT_coef

    if GTE:

        GTE_vars = list(group_x_treatment.columns)
        
        GTE_coef = {}

        dummy_group_current = dummy_group_original*no_treatments

        treatment_current = []
        for treatment in treatment_col:
            treatment_single = [treatment]*len(dummy_group_original)
            treatment_current = treatment_current + treatment_single
        
        for i, GTE_var in enumerate(GTE_vars):
            GTE_coef[i] = {
                "Coefficient": treatment_current[i] + " " + dummy_group_current[i],
                "Estimate": ols_coefficients[GTE_var],
                "SE": float(coef_standarderrors[GTE_var]),
                "t": float(coef_t[GTE_var]),
                "p": float(coef_p[GTE_var]),
                "CI_lower": float(coef_conf_intervals.loc[GTE_var, 0]),
                "CI_upper": float(coef_conf_intervals.loc[GTE_var, 1]),
                }      
        
        model_results["group_treatment_effects"] = GTE_coef

    if len(covariates) > 0:        
        if len(covariates) == 1 and covariates[0] == group_by:
            pass
        else:        
            covariates_effects = {}           
            for i, covariate in enumerate(covariates):
                covariates_effects[i] = {
                    "Coefficient": covariate,
                    "Estimate": ols_coefficients[covariate],
                    "SE": float(coef_standarderrors[covariate]),
                    "t": float(coef_t[covariate]),
                    "p": float(coef_p[covariate]),
                    "CI_lower": float(coef_conf_intervals.loc[covariate, 0]),
                    "CI_upper": float(coef_conf_intervals.loc[covariate, 1]),
                    }      
            model_results["covariates_effects"] = covariates_effects

    model_predictions = ols_model.predict()
    
    model_statistics = {
        "rsquared": ols_model.rsquared,
        "rsquared_adj": ols_model.rsquared_adj,
        }
    

    did_model_output = DiffModel(
        model_results,
        model_config,
        data,
        model_predictions,
        model_statistics,
        ols_model
        ) 

    return did_model_output