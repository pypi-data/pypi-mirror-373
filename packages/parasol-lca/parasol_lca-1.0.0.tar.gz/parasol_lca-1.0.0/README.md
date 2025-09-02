<div align="center">

<h3>Parasol LCA</h3>

</div>

## Overview

Parasol LCA is a Life Cycle Assessment (LCA) parametrized model of crystalline silicon-based photovoltaic (PV) systems. It relies on the  parametrization of existing life cycle inventory (LCI) data to better account for the progress already accomplished by the PV industry.

It was developed by Romain BESSEAU in 2019 for his [PhD Thesis](https://pastel.hal.science/tel-02732972). The first publication of this model as a Jupyter Notebook and the results of the corresponding study can be found in the article by [Besseau et al. (2023)](https://doi.org/10.1002/pip.3695).

Its development is based on the [Brightway2](https://docs.brightway.dev/en/legacy/index.html) and [lca_algebraic](https://lca-algebraic.readthedocs.io/en/stable/) libraries.

This python package makes Parasol LCA available as a ready-to-use module.

## Installation

Parasol LCA has been deployed to the pypi index and can be installed using the following command:

```sh
pip install parasol-lca
```
The module adds all the dependencies required to run the parameterized model.

## How to use Parasol LCA

The parameterized LCA model enables the assessment of the life cycle environmental impacts of a crystalline silicon-based PV system defined according to 35 input parameters.

To use the parameterized model, you may use the following code. Note that the `input_parameters` are meant to be changed depending on the parameters of the PV system to be evaluated. If no parameters are added to `input_parameters`, the model will use the default values.

*NOTE: Parasol LCA is compatible with the background database Ecoinvent 3.7, and has also been tested with Ecoinvent 3.9. Results are, however, not the same for both database versions. The results shown in the Parasol LCA article were produced with Ecoinvent 3.7.*

```sh
import brightway2 as bw
import parasol_lca
import lca_algebraic as agb

bw.projects.set_current("parasol-project")

import bw2io
bw2io.ecoinvent.import_ecoinvent_release("3.7", "cutoff", "your_ecoinvent_username", "your_ecoinvent_password")
#choose the corresponding ecoinvent release

MYDB = "parasol"
agb.resetDb(MYDB)
agb.resetParams(MYDB)
agb.setForeground(MYDB)

parasol_lca.create({
    "target_database": MYDB,
    "version":"3.7",
    "biosphere":"ecoinvent-3.7-biosphere",
    "technosphere":"ecoinvent-3.7-cutoff"
})


# Select impact/activity
activity = agb.findActivity('[parasol] PV impact per kWh', db_name=MYDB, single=True)

# NOTE: LCA results can also be evaluated per kWp :
# activity = agb.findActivity('[parasol] PV impact per kWp', db_name=MYDB, single=True)

# Default parameters
input_parameters = dict(
    # Installation
     Normalised_annual_PV_production_kWh_per_kWp=1300,  # kWh/kWp
     Power_plant_capacity=100,  # kWp
     PV_module_efficiency=0.22,  #
     Bifaciale_modules=0, # 0 = False, 1 = True
     Aluminium_frame_surfacic_weight=1.5,  # kg/m²
     Power_plant_lifetime=30,  # years
     Electrical_installation_specific_weight=3,  # kg/kWp
     # Inverter
     Inverter_weight_per_kW=2,  # kg/kWp
     Inverter_lifetime=15,  # years
     # Manufacturing
     Manufacturing_electricity_mix="World",
     ## Options: 'FR', 'EU', 'US', 'CN', 'World', 'PV', 'Nuclear','Coal','CO2_content'
     Electricity_mix_CO2_content=0.5,  # fraction
     Manufacturing_efficiency_gains=0,  # fraction
     Kerf_loss=0.3,  # fraction
     Wafer_thickness=160,  # µm
     Silver_content=9.6,  # g/m²
     Silicon_production_electricity_intensity=30,  # kWh/kg
     Silicon_production_heat_intensity=185,  # MJ/kg
     Silicon_casting_electricity_intensity=15,  # kWh/kg
     SiC_recycled_share=0,  # fraction
     Diamond_wiring_cutting=1,  # 0 = False, 1 = True
     Glass_thickness=4,  # mm
     # Mounting system
     roof_vs_ground_ratio=1,  # Proportion of roof installations.
     # 1 = all rooftop. 0 = all ground.
     Mounting_system_weight_alu=1.5,  # kg/m²
     Mounting_system_weight_total=5,  # kg/m²
     Mounting_system_weight_wood=0,  # kg/m²
     Ground_coverage_ratio=0.4,  # fraction
     # Transport
     Transport_distance_lorry=1000,  # km
     Transport_distance_train=500,  # km
     Transport_distance_boat=5000,  # km
     # Recycling
     Recycling_rate=0.9,  # fraction
     Recycling_rate_Al=0.96,  # fraction
     Recycling_rate_Cu=0.75,  # fraction
     Recycling_rate_glass=0.9,  # fraction
     Electricity_consumption_for_recycling=50,  # kWh/t
     Heat_consumption_for_recycling=76,  # MJ/t
)

# Choose the LCIA methods from list(bw.methods) that you wish to evaluate
# In the original article, the LCIA methods used were ILCD 2018
# ILCD now recommends using the Environmental Footprint (EF) methods

# Example: 3 impact categories with ecoinvent 3.7
methods = [('EF2.0 midpoint', 'climate change', 'climate change total'),
	   ('EF2.0 midpoint', 'resources', 'minerals and metals'),
           ('EF2.0 midpoint', 'resources', 'land use')]

data = agb.compute_impacts(models = { activity: 1.0 }, methods=methods, **input_parameters)
#print data to show the LCA results
data.T
```
