#-----------------------------------------------------------------------
# Name:        tests_diffindiff (diffindiff package)
# Purpose:     Tests and examples for the diffindiff package
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     2.0.6
# Last update: 2025-06-04 07:52
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import pandas as pd
from diffindiff.didanalysis import DiffModel, did_analysis
from diffindiff.diddata import DiffGroups, create_groups, DiffTreatment, create_treatment, DiffData, merge_data, create_data


# Example 1: Effect of a curfew in German counties in the first
# wave of the COVID-19 pandemic (DiD pre-post analysis)

curfew_DE=pd.read_csv("data/curfew_DE.csv", sep=";", decimal=",")
# Dataset with daily and cumulative SARS-CoV-2 infections of German counties
# Data source: Wieland (2020) https://doi.org/10.18335/region.v7i2.324

curfew_groups=create_groups(
    treatment_group= 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group= 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"]
    )
# Creating treatment and control group
# "Bundesland" (=federal state): 9 = Bavaria, 10 = Saarland, 14 = Saxony

curfew_groups.summary()
# Groups summary

curfew_treatment_prepost=create_treatment(
    study_period=["2020-03-01", "2020-05-15"],
    treatment_period=["2020-03-21", "2020-05-05"],
    freq = "D",
    pre_post = True
    )
# Creating treatment
# Curfew from March 21, 2020, to May, 5, 2020

curfew_treatment_prepost.summary()
# Treatment summary

curfew_data_prepost_merge=merge_data(
    outcome_data=curfew_DE,
    unit_id_col="county",
    time_col="infection_date",
    outcome_col="infections_cum_per100000",
    DiffGroups=curfew_groups,
    DiffTreatment=curfew_treatment_prepost
    )

curfew_data_prepost_merge.summary()
# Summary of created data

curfew_data_prepost=create_data(
    outcome_data=curfew_DE,
    unit_id_col="county",
    time_col="infection_date",
    outcome_col="infections_cum_per100000",
    treatment_group= 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group= 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    study_period=["2020-03-01", "2020-05-15"],
    treatment_period=["2020-03-21", "2020-05-05"],
    freq="D",
    pre_post=True
    )
# Creating DiD treatement dataset by defining groups and
# treatment time at once

curfew_data_prepost.summary()
# Summary of created data

curfew_model_prepost=curfew_data_prepost.analysis()
# Model analysis of created data

curfew_model_prepost.summary()
# Model summary

print(curfew_model_prepost.treatment_effects())
# Show effects

curfew_model_prepost.plot(
    x_label="Timepoint",
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness pre-post - Groups over time",
    plot_observed=False,
    lines_col=[None,None,"blue","orange"],
    lines_labels=[None,None,"Treatment group","Control group"],
    lines_style=[None,None,"solid","solid"]
    )
# Plot DiD pre vs. post results
# with user-determined style

curfew_model_prepost.plot(
    x_label="Timepoint",
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness pre-post - Groups over time",
    lines_col=[None,None,"blue","orange"],
    lines_labels=[None,None,"Treatment group","Control group"],
    pre_post_barplot=True
    )
# Plot DiD pre vs. post results
# with user-determined style

curfew_model_prepost.plot_treatment_effects(
    x_label="Coefficients with 95% CI",
    plot_title="Curfew effectiveness pre-post - DiD effects"
    )
# plot effects

curfew_model_prepost.plot_treatment_effects(
    x_label="Coefficients with 95% CI",
    plot_title="Curfew effectiveness pre-post - DiD effects",
    scale_plot=False
    )
# plot effects

counties_DE=pd.read_csv("data/counties_DE.csv", sep=";", decimal=",", encoding='latin1')
# Dataset with German county data

curfew_data_prepost_withcov = curfew_data_prepost.add_covariates(
    additional_df=counties_DE, 
    unit_col="county",
    time_col=None, 
    variables=["comm_index", "TourPer1000"])

curfew_data_prepost_withcov.summary()
# Summary of created data

curfew_model_prepost_withcov = curfew_data_prepost_withcov.analysis()
# Model analysis of created data

curfew_model_prepost_withcov.summary()
# Model summary


# Example 2: DiD with a simultaneous intervention and multi-period panel
# data: German counties during the first Corona wave

curfew_data=create_data(
    outcome_data=curfew_DE,
    unit_id_col="county",
    time_col="infection_date",
    outcome_col="infections_cum_per100000",
    treatment_group= 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group= 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    treatment_name="Curfew",
    study_period=["2020-03-01", "2020-05-15"],
    treatment_period=["2020-03-21", "2020-05-05"],
    freq="D"
    )
# Creating DiD dataset by defining groups and treatment time at once
# Treatment curfew in three federal states: Bavaria (9), Saarland (10) and Saxony (14)

curfew_data.summary()
# Summary of created treatment data

curfew_model=curfew_data.analysis()
# Model analysis of created data

curfew_model.summary()
# Model summary

curfew_model.plot(
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness - Groups over time",
    plot_observed=True
    )
# Plot observed vs. predicted (means) separated by group (treatment and control)

curfew_model.plot_treatment_effects(
    x_label="Coefficients with 95% CI",
    plot_title="Curfew effectiveness - DiD effects"
    )
# plot effects

curfew_placebo = curfew_model.placebo(
    treatment="Curfew"
    )
# Placebo test with default parameters

curfew_placebo.summary()
# Summary of placebo test

# Two-way-fixed-effects model:

curfew_model_FE=curfew_data.analysis(
    FE_unit=True, 
    FE_time=True
    )
# Model analysis of created data with fixed effects for 
# units (FE_unit=True) and time (FE_time=True)

curfew_model_FE_summary = curfew_model_FE.summary()
# Model summary

print(curfew_model_FE.treatment_statistics())
# Print treatment statistics

curfew_model_FE.plot(
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness (Two-way FE model) - Groups over time",
    plot_observed=True
    )
# Plot of treatment and control group

fixed_effects = curfew_model_FE.fixed_effects()
# Fixed effects of CHBW_data_model_FE
print(fixed_effects)

# Model with after treatment period:

curfew_data_AT = create_data(
    outcome_data = curfew_DE,
    unit_id_col="county",
    time_col = "infection_date",
    outcome_col = "infections_cum_per100000",
    treatment_group = 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group = 
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    study_period = ["2020-03-01", "2020-05-15"],
    treatment_period = ["2020-03-21", "2020-05-05"],
    freq = "D",
    after_treatment_period = True
    )
# Creating DiD treatment dataset and including
# after-treatment period (after_treatment_period=True)

curfew_data_AT.summary()
# Summary of created data

curfew_model_AT = curfew_data_AT.analysis()
# Model analysis of created data with fixed effects for 
# units (FE_unit=True) and time (FE_time=True)

curfew_model_AT.summary()
# Model summary

curfew_model_AT.plot_treatment_effects()
# Model summary

curfew_model_AT.plot(    
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew effectiveness (Two-way FE model with after-treatment period) - Groups over time",
    plot_observed=True
)
# Plot observed vs. predicted (means) separated by group (treatment and control)


# Model with group-specific treatment effects:

curfew_data_withgroups = curfew_data.add_covariates(
    additional_df=counties_DE, 
    unit_col="county",
    time_col=None, 
    variables=["BL"])
# Adding federal state column as covariate

curfew_model_withgroups = curfew_data_withgroups.analysis(
    GTE=True,
    group_by="BL")
# Model analysis of created data

curfew_model_withgroups.summary()
# Model summary

curfew_model_withgroups.plot_treatment_effects()
# Plot of group-specific treatment effects

# Model with two treatments:

curfew_data_extended = curfew_data.add_treatment(
    treatment_name="Contact ban",
    treatment_period=["2020-03-23", "2020-05-04"],
    treatment_group=
        curfew_DE.loc[~curfew_DE["Bundesland"].isin([9,10,14])]["county"],
    control_group= 
        curfew_DE.loc[curfew_DE["Bundesland"].isin([9,10,14])]["county"]
    )
# Adding treatment contact ban in the remaining federal states

curfew_data_extended.summary()
# Summary of extended data

curfew_model_extended=curfew_data_extended.analysis()
# Model analysis of extended data

curfew_model_extended.summary()
# Model summary

curfew_model_extended.plot(
    y_label="Cumulative infections per 100,000",
    plot_title="Curfew and contact ban effectiveness - Groups over time",
    plot_observed=True
    )
# Plot observed vs. predicted (means) separated by group (treatment and control)


# Example 3: Nighttime curfew and other NPI in Hesse
# (Staggered adoption)

Corona_Hesse=pd.read_excel("data/Corona_Hesse.xlsx")
# Test data effective reproduction number and Corona NPI Hesse
# Data source: Wieland (2024) https://doi.org/10.1007/s10389-024-02218-x

Hesse_model1=did_analysis(
    data=Corona_Hesse,
    unit_col="REG_NAME",
    time_col="infection_date",
    treatment_col="Nighttime_curfew",    
    outcome_col="R7_rm",
    intercept=False
    )
# Model with staggered adoption (FE automatically)

Hesse_model1.summary(show_baseline_components=False)
# Model summary

Hesse_model1.plot(
    treatment="Nighttime_curfew",
    y_label="R_t (mean by group)",
    plot_title="Nighttime curfews in Hesse - Treatment group vs. control group",
    plot_observed=True
    )
# Plot of treatment vs. control group (observed and expected) over time

Hesse_model1.plot_counterfactual(
    treatment="Nighttime_curfew"
    )
# Plot of treatment group fit and counterfactual

Hesse_model1.plot_timeline(
    y_label="Hessian counties",
    plot_title="Nighttime curfews in Hesse - Treatment time",
    treatment_group_only=False
    )
# Plot timeline of intervention by region

Hesse_model2 = did_analysis(
    data = Corona_Hesse,
    unit_col = "REG_NAME",
    time_col = "infection_date",
    treatment_col = "Nighttime_curfew",
    outcome_col = "R7_rm",
    ITT = True
    )
# same model but including region-specific time trends (ITT=True)

Hesse_model2.summary()
# Model summary

Hesse_model2.plot(
    y_label = "R_t (mean by group)",
    plot_title = "Nighttime curfews in Hesse - Treatment group vs. control group",
    plot_observed=True,
    treatment = "Nighttime_curfew"
    )
# Plot of effects of Hesse_model2

Hesse_model3 = did_analysis(
    data = Corona_Hesse,
    unit_col = "REG_NAME",
    time_col = "infection_date",
    treatment_col = "Nighttime_curfew",
    outcome_col = "R7_rm",
    ITE = True
    )
# Model with individual treatment effects (ITE=True)

Hesse_model3.summary()

Hesse_model3.plot(
    plot_observed=True,
    treatment="Nighttime_curfew"
    )

Hesse_model3.plot_treatment_effects()
# Plot of treatment effects

Hesse_model4=did_analysis(
    data=Corona_Hesse,
    unit_col="REG_NAME",
    time_col="infection_date",
    treatment_col=["Nighttime_curfew", "School_holidays"],    
    outcome_col="R7_rm",
    ITE = True,
    covariates=["vacc_cum", "Alpha_share_ma"]
    )
# Model with two interventions (both staggered adoption)

Hesse_model4.summary()
# Model summary

Hesse_model4.plot_treatment_effects()

Hesse_model5=did_analysis(
    data=Corona_Hesse,
    unit_col="REG_NAME",
    time_col="infection_date",
    treatment_col=["Nighttime_curfew", "Mobility_restrictions", "Retail_closed", "CR_private_2"],
    covariates=["infections_cum", "R7_rm_lag10"],   
    outcome_col="R7_rm")
# Model with four interventions (two staggered, two without control conditions)

Hesse_model5.summary(show_covariates = True)
# Model summary