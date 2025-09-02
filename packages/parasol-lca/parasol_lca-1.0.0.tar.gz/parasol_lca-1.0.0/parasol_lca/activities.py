# coding=utf-8
#
# Copyright 2021-2022 Romain BESSEAU <romain.besseau@ec.europa.eu>
# Copyright 2022-2024 Alejandra CUE GONZALEZ <alejandra.cue_gonzalez@minesparis.psl.eu>
# Copyright 2022-2024 Benoît GSCHWIND <benoit.gschwind@minesparis.psl.eu>
# Copyright 2022-2024 MINES Paris
#
# This file is part of "parasol-lca" and you can used under the
# term of European Union Public Licence.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# European Union Public Licence for more details.
#
# Version: 22 April 2025
#
# Code authors: Romain BESSEAU, Benoît GSCHWIND, Alejandra CUE GONZALEZ
#

import lca_algebraic as agb
from lca_algebraic.base_utils import getActByCode
from . import parameters as p

import brightway2 as bw
from bw2data.utils import get_activity
from bw2data.query import Filter
from types import SimpleNamespace
from copy import copy


class Config:
    def __init__(self, target_database, version):
        """
        Create new config

        Parameters
        ----------
        target_database : str
            Name of the database to use to store parasol activities
        version : str
            Version string of ecoinvent database such as "3.7", "3.9" ...

        Returns
        -------
        config

        """
        self.prefix = "[parasol] "
        self.version = version
        self.target_database = target_database
        self.biosphere = f"ecoinvent-{version}-biosphere"
        self.technosphere = f"ecoinvent-{version}-cutoff"

    @staticmethod
    def from_dict(d : dict):
        """
        Create config from dictionnary

        Parameters
        ----------
        d : dict
        expected keys:
            - target_database = database to use to store new activities (string)
            - version = ecoinvent version used (string)
            - (optional) prefix = prefix for created activities (string)
            - (optional) biosphere = biosphere database name (string)
            - (optional) technosphere = technosphere database name (string)

        Returns
        -------
        config

        """
        conf = Config(d["target_database"], d["version"])
        conf.prefix = d.get("prefix", conf.prefix)
        conf.biosphere = d.get("biosphere", conf.biosphere)
        conf.technosphere = d.get("technosphere", conf.technosphere)
        return conf


def get_acurate_activities(db_name, filters : dict):
    return [get_activity(key) for key in bw.Database(db_name).query(*[Filter(k, "==", v) for k, v in filters.items()])]


def ensure_electricity(conf: Config):
    """Create the electricity dataset and related activities.
    Activities of the market and market group for electricity, medium voltage,
    are recovered from the ecoinvent database for France (FR), Europe (EU),
    United States (US), China (CN), and the global market (World).
    Activities related to the electricity production through photovoltaic (PV),
    nuclear (Nuclear), and coal (Coal) are also recovered.
    Finally, an activity with a fixed share of fossil to determine the
    CO2 content is defined (CO2_content)

    These activities are aggregated in a virtual "switch" activity,
    from which the desired electricity source for PV manufacuring can be chosen

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity

    """

    ACTIVITY_NAME = f'{conf.prefix}electricity'
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")
    # ## Electricity dataset

    # These variables save the technosphere activities related to the electricity markets for different regions, as well as general energy markets.

    ### Electricity mix
    elec_FR = agb.findActivity('market for electricity, medium voltage','FR', db_name=conf.technosphere)
    elec_EU = agb.findActivity('market group for electricity, medium voltage', 'ENTSO-E', db_name=conf.technosphere)
    elec_US = agb.findActivity('market group for electricity, medium voltage','US', db_name=conf.technosphere)
    elec_CN = agb.findActivity('market group for electricity, medium voltage','CN', db_name=conf.technosphere)
    elec_world = agb.findActivity('market group for electricity, medium voltage','GLO', db_name=conf.technosphere)
    elec_PV = agb.findActivity('electricity production, photovoltaic, 570kWp open ground installation, multi-Si','FR', db_name=conf.technosphere)
    elec_nuclear = agb.findActivity('electricity production, nuclear, pressure water reactor','FR', db_name=conf.technosphere)
    elec_coal = agb.findActivity('electricity production, hard coal','FR', db_name=conf.technosphere)

    # We declare a parameter to select the electricity mix to be used for the manufacturing of PV components.

    # ### Dataset with a fixed share of fossil to determine the CO2 content

    # A parameterized mix with only hydropower and coal power can also be used.
    # It is convenient as the carbon footprint of hydropower is very low and
    # the carbon footprint of coal power plant is close to 1 kgCO2eq/kWh.
    # If you want to consider an electricity dataset with a carbon footprint
    # of 300 gCO2eq/kWh, you can use this dataset with a ratio of 0.3 of coal power.

    act_kWh_hydro = agb.findActivity('electricity production, hydro, reservoir, alpine region','FR', db_name=conf.technosphere)
    act_kWh_charbon =  agb.findActivity('electricity production, hard coal','RoW', db_name=conf.technosphere)

    act = agb.newActivity(
        name=f'{conf.prefix}electricity for PV manufacturing CO2 content',
        db_name = conf.target_database,
        unit = "kWh",
        exchanges={
            act_kWh_charbon: p.Electricity_mix_CO2_content,
            act_kWh_hydro: 1-p.Electricity_mix_CO2_content
        }
    )
    act.setOutputAmount(1.0)

    # +
    act_kWh_CO2 = agb.findActivity(f'{conf.prefix}electricity for PV manufacturing CO2 content', db_name=conf.target_database)
    # -

    # The following is a virtual activity corresponding to switch beteween electricity mixes.
    # We assign those values to the Manufacturing_elrctricity_mix parameter.
    #
    # If necessary, more choices can be added.

    return agb.newSwitchAct(
        name=ACTIVITY_NAME,
        dbname = conf.target_database,
        paramDef = p.Manufacturing_electricity_mix,
        acts_dict = {
            'FR' : elec_FR,
            'EU' : elec_EU,
            'US' : elec_US,
            'CN' : elec_CN,
            'World' : elec_world,
            'PV' : elec_PV,
            'Nuclear' : elec_nuclear,
            'Coal' : elec_coal,
            'CO2_content' : act_kWh_CO2
        }
    )


def ensure_mounting(conf: Config):
    """Create the mounting system dataset and related activities.
    Paramaterizes the ecoinvent photovoltaic mounting system production
    activity by including the parameters related to the total weight of the
    mounting system, the amount of aluminum, and the amount of wood in kg.
    It also updates the type of steel used for the mounting system.

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity

    """
    ACTIVITY_NAME = f'{conf.prefix}PV mounting system'
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    # ## Aluminium dataset

    # The original dataset taken from ecoinvent
    alu_original = agb.findActivity('market for aluminium, wrought alloy', single=True, db_name=conf.technosphere)

    # ## Mounting system

    # First we identify the technosphere activities relevant to the mounting system: the ground-mounted system, the roof-mounted system, and the markets for scrap and steel metals, since they're the materials the mounting frame is usually made of.

    # Mounting system (Aluminium and stainless steel based)
    ground_system = agb.findActivity('photovoltaic mounting system production, for 570kWp open ground module', db_name=conf.technosphere)
    roof_system = agb.findActivity('photovoltaic mounting system production, for slanted-roof installation','RER', db_name=conf.technosphere)

    # Markets for scrap alumuinium
    scrap_alu = agb.findActivity('market for scrap aluminium','Europe without Switzerland', db_name=conf.technosphere)
    scrap_steel = agb.findActivity('market for scrap steel','Europe without Switzerland', db_name=conf.technosphere)

    # We add the activity related to wood to include wood as a potential material to be used in the mounting system.

    # NEW 3.9
    #wood_act = agb.findActivity('market for sawnwood, softwood, dried (u=10%), planed','RER')
    # OLD 3.7
    wood_act = agb.findActivity('market for sawnwood, softwood, dried (u=20%), planed','RER', db_name=conf.technosphere)

    # We copy this way to avoid accidental modifications of the original activity
    act2 = agb.copyActivity(
            activity = ground_system,
            code = ACTIVITY_NAME,
            db_name = conf.target_database)

    #Update the ground system activity (process) with exchanges that include the paramaters that we defined
    #Aluminum
    m_alu = p.mounting_system_weight_alu
    m_steel = p.mounting_system_weight_total - p.mounting_system_weight_alu - p.mounting_system_weight_wood
    m_wood = p.mounting_system_weight_wood / 420.0 #420 kg/m3

    #Alu
    act2.updateExchanges({"scrap aluminium*": None})
    act2.addExchanges({scrap_alu : m_alu})
    act2.updateExchanges({"aluminium*": m_alu})
    #Steel
    act2.updateExchanges({"scrap steel*": None})
    act2.addExchanges({scrap_steel : m_steel})
    act2.updateExchanges({"reinforcing steel*": m_steel - 0.25})#substract chromium steel
    act2.updateExchanges({"section bar rolling, steel*": m_steel})
    #Wood
    act2.addExchanges({wood_act:m_wood})

    #GCR
    act2.updateExchanges({"Transformation*": 1.0/p.ground_coverage_ratio * (1.0-p.roof_ratio)})
    act2.updateExchanges({"Occupation*": 1.0/p.ground_coverage_ratio * p.lifetime * (1.0-p.roof_ratio)})
    #Concrete
    act2.updateExchanges({'concrete*':0.000542 * (1.0-p.roof_ratio)})

    return act2


def ensure_electrical_installation(conf: Config):
    """Creates the electrical installation dataset and related activities.
    The electrical installation consists of cables, fuse box,
    lightning protection, etc. without the inverter.

    Parameters
    ----------
    conf: Config
        see. help(Config)
    """
    ACTIVITY_NAME = f'{conf.prefix}photovoltaics, electric installation per kg'
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    # ## Electrical installation

    electrical_installation_3kW = agb.findActivity(
        db_name=conf.technosphere,
        name='photovoltaics, electric installation for 3kWp module, at building',
        loc='RoW')

    # We define a new activity weighting the installations:

    return agb.newActivity(
        db_name = conf.target_database,
        name = ACTIVITY_NAME,
        unit = "kg", # Unit
        exchanges = { # We define exhanges as a dictionarry of 'activity : amount'
            electrical_installation_3kW : 1.0/32.592
        }
    )


def ensure_inverter(conf: Config):
    """Creates the inverter dataset and related activities.
    The representative flow of the inverter activity is the production of
    1 kg of inverter.

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity

    """
    ACTIVITY_NAME = f"{conf.prefix}Inverter production, P kW per kg"
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    # ## Inverter

    # From a 3 kVA inverter to a 570 kVA inverter, there is a significant
    # evolution in the share material used.
    # The inventory will be calculated based on the weight of the inverter
    # multiplied by the share of the different material involved interpolated
    # between the 3 KVA and 570 kVA inventories.

    # ### Parameterized function for inverter

    # Recycling activities
    scrap_alu = agb.findActivity("market for scrap aluminium", "Europe without Switzerland", db_name=conf.technosphere)
    scrap_steel = agb.findActivity("market for scrap steel", "Europe without Switzerland", db_name=conf.technosphere)
    scrap_coper = agb.findActivity("market for scrap copper", "Europe without Switzerland", db_name=conf.technosphere)
    scrap_electronic = agb.findActivity("market for electronics scrap", db_name=conf.technosphere)

    inverter_500kW = agb.findActivity('inverter production, 500kW', 'RER', db_name=conf.technosphere)
    inverter_2500W = agb.findActivity('inverter production, 2.5kW', 'RER', db_name=conf.technosphere)
    weigth_2500W = 18.5
    weigth_500kW = 3000.0

    inverter_2500W_with_recycling = agb.copyActivity(
        db_name  = conf.target_database,
        activity=inverter_2500W,
        code="{conf.prefix}inverter production with recycling, 2.5kW")

    # Add recycling
    amount_alu = inverter_2500W.getAmount('aluminium, cast alloy*')
    amount_copper = inverter_2500W.getAmount('copper, cathode*')
    amount_steel = inverter_2500W.getAmount('steel, low-alloyed, hot rolled*')
    amount_electronic = inverter_2500W.getAmount([
            'capacitor*',
            'diode*',
            'integrated circuit*',
            'printed wiring*',
            'resistor*',
            'transitor*'
        ], sum=True)

    inverter_2500W_with_recycling.addExchanges({
        scrap_alu : amount_alu * p.recycling_rate,
        scrap_coper : amount_copper * p.recycling_rate,
        scrap_electronic : amount_electronic * p.recycling_rate,
        scrap_steel : amount_steel * p.recycling_rate
    })

    inverter_500kW_with_recycling = agb.copyActivity(
        db_name  = conf.target_database,
        activity=inverter_500kW,
        code="{conf.prefix}inverter production with recycling, 500kW")

    # Add recycling
    amount_alu = inverter_500kW.getAmount('aluminium, cast alloy*')
    amount_copper = inverter_500kW.getAmount('copper, cathode*')
    amount_steel = inverter_500kW.getAmount('steel, low-alloyed, hot rolled*')
    amount_electronic = inverter_500kW.getAmount([
            'capacitor*',
            'diode*',
            'integrated circuit*',
            'printed wiring*',
            'resistor*',
            'transitor*'
        ], sum=True)

    inverter_500kW_with_recycling.addExchanges({
        scrap_alu : amount_alu * p.recycling_rate,
        scrap_coper : amount_copper * p.recycling_rate,
        scrap_electronic : amount_electronic * p.recycling_rate,
        scrap_steel : amount_steel * p.recycling_rate
    })

    inverter_2500W_per_kg = agb.newActivity(
        db_name = conf.target_database,
        name = f'{conf.prefix}inverter production, 2.5kW per kg',
        unit = "kg",
        exchanges = { inverter_2500W_with_recycling : 1.0/weigth_2500W }
    )

    inverter_500kW_per_kg = agb.newActivity(
        db_name = conf.target_database,
        name = f'{conf.prefix}inverter production, 500kW per kg',
        unit = "kg",
        exchanges = { inverter_500kW_with_recycling : 1.0/weigth_500kW }
    )

    # Generate a dataset for 1kG of inverter, based on the power
    return agb.interpolate_activities(
        db_name = conf.target_database,
        act_name = ACTIVITY_NAME,
        param=p.P_install,
        act_per_value={
            0.0: inverter_2500W_per_kg,
            2.5: inverter_2500W_per_kg,
            500.0: inverter_500kW_per_kg,
            1e30: inverter_500kW_per_kg
        }
    )


def ensure_metalisation(conf: Config):
    """Creates the metalisation dataset and related activities.
    Needed for the silicon dataset.

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity

    """
    ACTIVITY_NAME = f'{conf.prefix}metal paste, copper'
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    # ## Metalisation paste for electric contact

    # This section replaces all the silver used in the metallization paste
    #by copper. The amount is assessed proportionnaly to the metal conductivity.

    # Find root activities
    metal_paste = agb.findActivity("metallization paste production, back side", "RER", db_name=conf.technosphere)
    copper = agb.findActivity('market for copper, anode', "GLO", db_name=conf.technosphere)

    # Copy and update metal paste with copper
    metal_paste_copper = agb.copyActivity(
        db_name = conf.target_database,
        activity = metal_paste,
        code = ACTIVITY_NAME)

    metal_paste_copper.updateExchanges({
        'silver*' : dict(input = copper, name="copper")
    })

    return metal_paste_copper


def ensure_silicon(conf: Config):
    """Creates the silicon dataset and related activities.
    Updates the dataset with the findings of Besseau et al. (2023)

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity

    """
    ACTIVITY_NAME = f"{conf.prefix}Wafer adjusted"
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    elec_switch_act = ensure_electricity(conf)

    # ## Silicon production

    # ### New dataset for silicon production

    # #### For MG grade

    act = agb.findActivity('market for silicon, metallurgical grade', db_name=conf.technosphere)
    #agb.printAct(act) # Looked for it in ecoinvent

    silicon = agb.findActivity('silicon production, metallurgical grade', 'NO', db_name=conf.technosphere) #production in Europe, Norway
    silicon_adjusted = agb.copyActivity(
        db_name = conf.target_database,
        activity = silicon,
        code = f"{conf.prefix}MG - silicon production adjusted"
    )

    #Adjust the electricity mix
    silicon_adjusted.updateExchanges(updates = {
        'electricity, medium voltage*' : elec_switch_act
    })

    # #### For Solar Grade silicon

    silicon = agb.findActivity('silicon production, solar grade, modified Siemens process', 'RER', db_name=conf.technosphere) #production in Europe

    # We see a high share of hydro electricity absolutely not reprensentative of the current PV market with 65% manufacture with hydro electricity!

    act_MGSi = agb.findActivity(f"{conf.prefix}MG - silicon production adjusted", db_name=conf.target_database)

    # +
    silicon = agb.findActivity('silicon production, solar grade, modified Siemens process', 'RER', db_name=conf.technosphere)
    silicon_adjusted = agb.copyActivity(
        db_name = conf.target_database,
        activity = silicon,
        code = f"{conf.prefix}SoG - silicon production adjusted")
    # Link to the parameterized MG Si dataset
    silicon_adjusted.updateExchanges({
        "silicon, metallurgical grade*": act_MGSi
    })

    # Remove all electricity sources and replace them by the selected
    # electricity mix.
    silicon_adjusted.updateExchanges(updates={'electricity*': None})
    silicon_adjusted.addExchanges({elec_switch_act: p.silicon_elec_intensity})


    silicon_adjusted.updateExchanges({"heat*": p.silicon_heat_intensity})
    # -

    # #### Market for silicon solar grade

    act = agb.findActivity('market for silicon, solar grade', db_name=conf.technosphere)

    silicon = agb.findActivity(f'{conf.prefix}SoG - silicon production adjusted', db_name=conf.target_database)

    act_adjusted = agb.copyActivity(db_name = conf.target_database,
                                    activity = act,
                                    code = f"{conf.prefix}SoG - market for silicon adjusted")
    #link to the parameterized MG Si dataset
    act_adjusted.updateExchanges({"silicon*": None})
    act_adjusted.addExchanges({silicon: 1.0})

    # #### Silicon production Si casted

    act = agb.findActivity('silicon production, multi-Si, casted', 'RER', db_name=conf.technosphere)

    # Let's remove the use of silicon electronics grade, the share was significant when the world silicon production was relatively low, nowadays volume can be neglected compared to the level reached by the solar industry.

    silicon = agb.findActivity(f'{conf.prefix}SoG - market for silicon adjusted', db_name=conf.target_database)

    act_adjusted = agb.copyActivity(db_name = conf.target_database,
                                    activity = act,
                                    code = f"{conf.prefix}silicon production, Si, casted adjusted")
    #link to the parameterized MG Si dataset
    act_adjusted.updateExchanges({"silicon,*": None})
    act_adjusted.updateExchanges({"electricity, medium voltage*": elec_switch_act})
    act_adjusted.updateExchanges({"electricity, medium voltage*": p.silicon_casting_elec_intensity})
    act_adjusted.addExchanges({silicon: 1.0})

    # ####  Market for Si casted

    act = agb.findActivity('market for silicon, multi-Si, casted','RER', db_name=conf.technosphere)

    silicon = agb.findActivity(f'{conf.prefix}silicon production, Si, casted adjusted', db_name=conf.target_database)

    act_adjusted = agb.copyActivity(db_name = conf.target_database,
                                    activity = act,
                                    code = f"{conf.prefix}market for silicon, Si, casted adjusted")
    #link to the parameterized MG Si dataset
    act_adjusted.updateExchanges({"silicon*": None})
    act_adjusted.addExchanges({silicon:1})

    # ### Wafer manufacturing

    # #### Cutting process
    #
    # ##### SiC, Recycled

    silicon_carbide = agb.findActivity('silicon carbide production', 'RER', db_name=conf.technosphere)
    silicon_carbide_recycled = agb.copyActivity(db_name = conf.target_database,
                                                activity = silicon_carbide,
                                                code = f'{conf.prefix}silicon carbid adjusted',
                                                withExchanges = False)

    if conf.version == '3.10.1': lc='RoE' #Change to 'RoW' is the waste is not produced in Europe
    else: lc='GLO'

    silicon_carbide_recycled.addExchanges(exchanges = {
        agb.findActivity('market group for electricity, medium voltage', 'ENTSO-E', db_name=conf.technosphere) : 0.78571,
        agb.findActivity('market for transport, freight, lorry, unspecified', 'RER', db_name=conf.technosphere) : 0.2625,
        agb.findActivity('market for silicone factory', db_name=conf.technosphere) : 1e-11,
        agb.findActivity('Heat, waste', categories=['air'],db_name=conf.biosphere) : 2.8286,
        agb.findActivity('market for waste, from silicon wafer production, inorganic', loc=lc, db_name=conf.technosphere) : -0.042857,
        agb.findActivity('treatment of spent antifreezer liquid, hazardous waste incineration', 'CH', db_name=conf.technosphere) : -0.071429,
        agb.findActivity('market for pig iron', 'RER', db_name=conf.technosphere) : -0.13571,
    })

    # #### Diamond Wiring

    # ##### Tungstene

    # The Original code used this, which select the wrong activity, see below.
    #act_sulfuric_acid = agb.findActivity(db_name='ecoinvent3.7', name='sulfuric acid production', loc='RER', single=False)[0]

    # This activity is {name: 'sulfuric acid production', loc='RER', reference product: 'steam, in chemical industry'}
    # It the one used by Romain (2019) but it seems to be wrong, it should be replaced by the one below
    #act_sulfuric_acid = getActByCode(db_name=conf.technosphere, code='4c9bd1eb18a182413455faa532d6532b')
    # This activity is {name: 'sulfuric acid production', loc='RER', reference product: 'sulfuric acid'}
    # This is the one that should be used.
    #act_sulfuric_acid = getActByCode(db_name=conf.technosphere, code='168c76950bbe49d9e0e63ec7f36a7a26')

    # try if this activity is available, if not we are using ecoinvent >3.7
    try:
        # This activity is the wrong one but it is the one used by Romain 2019
        act_sulfuric_acid = getActByCode(db_name=conf.technosphere, code='4c9bd1eb18a182413455faa532d6532b')
        print("WARNING: Using wrong 'sulfuric acid production' activity for backward compliance")
    except:
        act_sulfuric_acid = None

    # This is the actual activity required by Romain 2019
    if act_sulfuric_acid is None:
        act_sulfuric_acid = get_acurate_activities(conf.technosphere, {
            "name":'sulfuric acid production',
            "location":'RER',
            "reference product": 'sulfuric acid'
        })

        if len(act_sulfuric_acid) != 1:
            raise Exception("No proper 'sulfuric acid production' activity found.")
        act_sulfuric_acid = act_sulfuric_acid[0]

    tungstene_carbide = agb.copyActivity(
        db_name = conf.target_database,
        activity = silicon_carbide,
        code = f"{conf.prefix}tungstene carbide",
        withExchanges = False)

    #Data from pg 113 of Isabella Bianco's thesis (2018)
    #later published in a scientific article:
        #https://doi.org/10.1016/j.jclepro.2019.03.309

    if conf.version in {'3.10.1', '3.10'}:
        H2='market for hydrogen, gaseous, medium pressure, merchant'
        lc='RER'
    else:
        H2 = 'market for hydrogen, liquid'
        lc = 'GLO'
    tungstene_carbide.addExchanges({
        agb.findActivity('market for sodium hydroxide, without water, in 50% solution state', loc=lc, db_name=conf.technosphere) : 1.49,
        agb.findActivity('aluminium sulfate production, powder', 'RER', db_name=conf.technosphere) : 0.071,
        agb.findActivity('sodium sulfide production', db_name=conf.technosphere) : 0.044,
        agb.findActivity('magnesium sulfate production', 'RER', db_name=conf.technosphere) : 0.027,
        agb.findActivity('market for ammonia, anhydrous, liquid', 'RER', db_name=conf.technosphere) : 0.106,
        agb.findActivity('market for soda ash, dense', db_name=conf.technosphere) : 1.21,
        act_sulfuric_acid : 1.24,
        agb.findActivity('market group for electricity, medium voltage', 'ENTSO-E', db_name=conf.technosphere) : 111.16,
        agb.findActivity('hydrogen sulfide production', 'RER', db_name=conf.technosphere) : 0.0076,
        agb.findActivity('market for nitrogen, liquid', 'RER', db_name=conf.technosphere) : 1.65,
        agb.findActivity(H2, 'RER', db_name=conf.technosphere) : 0.32,
        agb.findActivity('market for tap water', 'RoW', db_name=conf.technosphere) : 2.84,
        agb.findActivity('carbon black production', db_name=conf.technosphere) : 0.13,
        })
    # -

    # ##### Diamond powder

    diamond_powder_ori = agb.findActivity('sodium percarbonate production, powder', 'RER', db_name=conf.technosphere)
    diamond_powder = agb.copyActivity(db_name = conf.target_database,
                                      activity = diamond_powder_ori,
                                      code = f"{conf.prefix}Diamond powder",
                                      withExchanges = False)
    diamond_powder.addExchanges({
        agb.findActivity("market group for electricity, medium voltage", "GLO", db_name=conf.technosphere) : 840,
        agb.findActivity("graphite production", "RER", db_name=conf.technosphere) : 1,
        agb.findActivity("market for transport, freight, sea, container ship", db_name=conf.technosphere) : 170,
        agb.findActivity("transport, freight, lorry 16-32 metric ton, EURO4", "RER", db_name=conf.technosphere) : 0.53,
    })

    # ##### Sintered diamond bead

    # +
    sintered_diamond_ori = agb.findActivity("polymethyl methacrylate production, beads", "RER", db_name=conf.technosphere)

    sintered_diamond = agb.copyActivity(db_name = conf.target_database,
                                        activity = sintered_diamond_ori,
                                        code = f"{conf.prefix}sintered diamond bead, for quarrying",
                                        withExchanges=False)

    sintered_diamond.addExchanges({
        agb.findActivity("market group for electricity, medium voltage", "ENTSO-E", db_name=conf.technosphere) : 0.1,
        agb.findActivity("market for steel, unalloyed", "GLO", db_name=conf.technosphere) : 0.003,
        agb.findActivity("market for cobalt", db_name=conf.technosphere) : 7e-08,
        agb.findActivity("market for copper, anode", db_name=conf.technosphere) : 2.1e-07,
        agb.findActivity("market for pig iron", 'RER', db_name=conf.technosphere) : 3.5e-07,
        agb.findActivity("market for nickel, class 1", db_name=conf.technosphere) : 2.1e-08,
        tungstene_carbide : 3.5e-08,
        diamond_powder : 2e-05,
        agb.findActivity('polymethyl methacrylate production, beads', "RER", db_name=conf.technosphere) :  2e-05,
        agb.findActivity("market for cobalt", db_name=conf.technosphere) : 5e-05,
        agb.findActivity("market for silver", db_name=conf.technosphere) : 2.1e-04,
        agb.findActivity("market for nitrogen, liquid", "RER", db_name=conf.technosphere) : 0.0323,
        agb.findActivity(H2, "RER", db_name=conf.technosphere) : 9e-04
    })

    sintered_diamond.setOutputAmount(0.004)
    # -

    # ##### Sintered diamond wire

    try:
        # activity from =3.7
        polyurethane = agb.findActivity("polyurethane production, flexible foam", "RER", db_name=conf.technosphere)
    except:
        # activity from >3.7
        polyurethane = agb.findActivity("polyurethane production, flexible foam, MDI-based", "RER", db_name=conf.technosphere)

    # +
    act_ori = agb.findActivity('wire drawing, steel', 'RER', db_name=conf.technosphere)
    sintered_diamond_wire = agb.copyActivity(
        db_name = conf.target_database,
        activity = act_ori,
        code = f"{conf.prefix}sintered diamond wire, steel",
        withExchanges = False)

    sintered_diamond_wire.addExchanges({
        sintered_diamond : 0.0427,
        agb.findActivity("market group for electricity, medium voltage", "ENTSO-E", db_name=conf.technosphere) : 0.9,
        agb.findActivity("wire drawing, steel", "RER", db_name=conf.technosphere) : 0.095,
        polyurethane : 0.15,
        agb.findActivity("transport, freight, lorry 16-32 metric ton, EURO4", "RER", db_name=conf.technosphere) : 0.003,
        agb.findActivity("market for waste plastic, mixture", "RoW", db_name=conf.technosphere) : 0.045
    })

    # #### Wafer

    wafer = agb.findActivity("multi-Si wafer production", "RER", db_name=conf.technosphere)

    silicon_adjusted = agb.findActivity(f'{conf.prefix}market for silicon, Si, casted adjusted', db_name=conf.target_database)

    # Formulas

    # Integrate gain in kerf loss for diamond wiring
    kerf_loss_adapted = p.kerf_loss - 0.15 * p.diamond_wiring
    sili_casting_amount = p.wafer_thickness * 1e-6 * 2328 / (1 - kerf_loss_adapted)
    non_diamond_wiring = 1 - p.diamond_wiring

    # Copy Wafer
    wafer = agb.findActivity("multi-Si wafer production", "RER", db_name=conf.technosphere)
    wafer_adjusted = agb.copyActivity(
        db_name = conf.target_database,
        activity = wafer,
        code = ACTIVITY_NAME)

    # Update wafer
    teg_recycled_share = 0.0

    wafer_adjusted.updateExchanges({
        'silicon, multi-Si, casted*' : dict(
            input = silicon_adjusted,
            amount = sili_casting_amount,
            name='silicon production, adjusted'),
        #'tap water' : 0.006000 + diamond_wiring * 98.94,
        'silicon carbide*' : non_diamond_wiring * 2.02988 * (1.0 - p.sic_recycled_share),
        'triethylene glycol*' : non_diamond_wiring * 2.16548 * (1.0 - teg_recycled_share)
    })

    wafer_adjusted.addExchanges({
        # Diamond wiring (see also Tap water updated above)
        sintered_diamond_wire :  p.diamond_wiring * 0.0006075,
        # Non -diamond wiring
        silicon_carbide_recycled : non_diamond_wiring * 2.02988 * p.sic_recycled_share
        })

    #Adapts the amount of electricity to be used
    wafer_adjusted.updateExchanges({"electricity, medium voltage*": 8 * (1 - p.manufacturing_efficiency)})
    wafer_adjusted.updateExchanges({"heat, district or industrial, natural gas*": 3.6 * (1 - p.manufacturing_efficiency)})
    #Adapts the dataset to be used
    wafer_adjusted.updateExchanges({"electricity*": elec_switch_act})

    return wafer_adjusted


def ensure_pv_cell_manufacturing(conf: Config):
    """Create the PV cell manufacturing dataset and related activities.

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity

    """
    ACTIVITY_NAME = f'{conf.prefix}photovoltaic cell production, multi-Si wafer - adjusted'
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    wafer_adjusted = ensure_silicon(conf)
    elec_switch_act = ensure_electricity(conf)

    # ## PV cell manufacturing

    cell_init = agb.findActivity('photovoltaic cell production, multi-Si wafer', 'RER', db_name=conf.technosphere)

    # To adapt the amount of **Silver** used for the *metallic contact*:
    # - By default, for the front side : 7.4 g/m² Silver based paste corresponding to 6.2 g/m² of Ag (84% Silver)
    # - By default, for the back side : 4.9 g/m² Silver based paste corresponding to 3.3 g/m² of Ag (67% Silver)
    # - An additional 0.7 g of Ag is used is anyway considered for the panel.
    #
    # To add the **copper paste** used to *substitute the amount of Silver use*:
    # - The amount of copper is calculated considering the difference of conductivity between Ag and Cu
    # - Conductiviy of Ag = 6.3e7 S/m, Cu = 5.96e7 S/m at 20°C

    front_silver_amount = agb.Max(7.4e-3 * (p.silver_amount - 0.7)  / (6.2 + 3.3), 0)
    back_silver_amount = agb.Max(4.9e-3 * (p.silver_amount - 0.7)  / (6.2 + 3.3), 0)

    cell_adjusted = agb.copyActivity(db_name = conf.target_database,
                                     activity = cell_init,
                                     code = ACTIVITY_NAME)

    try:
        cell_adjusted.updateExchanges({
        'metallization paste, front side' : front_silver_amount,
        'metallization paste, back side': back_silver_amount,
        'multi-Si wafer' : dict(input=wafer_adjusted)
        })
    except: #premise
        cell_adjusted.updateExchanges({
            'market for metallization paste, front side' : front_silver_amount,
            'market for metallization paste, back side': back_silver_amount,
            'market for multi-Si wafer' : dict(input=wafer_adjusted)
        })

    #Adapt the quantity of electricity to use
    cell_adjusted.updateExchanges({'electricity, medium voltage*': 30.243 * (1 - p.manufacturing_efficiency)})
    #Adapt the dataset to use
    cell_adjusted.updateExchanges({'electricity, medium voltage*': elec_switch_act})

    return cell_adjusted


def ensure_pv_panel(conf: Config):
    """
    Create the PV panel manufacturing dataset and related activities.

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity
    """
    """
## PV panel
"""
    ACTIVITY_NAME = f'{conf.prefix}photovoltaic panel production, multi-Si wafer - adjusted'
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    elec_switch_act = ensure_electricity(conf)
    # Define Max with abs() for later vector processing in numpy (sympy.Max is badly transformed)
    front_silver_amount = agb.Max(7.4e-3 * (p.silver_amount - 0.7)  / (6.2 + 3.3), 0)
    new_front_silver_amount = 0.84 * front_silver_amount

    back_silver_amount = agb.Max(4.9e-3 * (p.silver_amount - 0.7)  / (6.2 + 3.3), 0)
    new_back_silver_amount = 0.67 * back_silver_amount
    copper_amount = agb.Max(1/0.67 * 6.3e7 / 5.96e7 * ( 9.6e-3 -(new_front_silver_amount + new_back_silver_amount)), 0)

    new_copper_amount = 0.67 * copper_amount
    # ## PV panel

    panel_init = agb.findActivity('photovoltaic panel production, multi-Si wafer', 'RER', db_name=conf.technosphere)

    cell_adjusted = ensure_pv_cell_manufacturing(conf)

    # +
    # Activities
    scrapGlass = agb.findActivity('market for waste glass sheet', 'Europe without Switzerland', db_name=conf.technosphere)
    scrapAlu = agb.findActivity('market for scrap aluminium*', 'Europe without Switzerland', db_name=conf.technosphere)
    scrapCopper = agb.findActivity('market for scrap copper*', 'Europe without Switzerland', db_name=conf.technosphere)
    heat_for_recycling = agb.findActivity('heat and power co-generation, biogas, gas engine',
                                         loc = 'RoW', unit = 'megajoule', db_name=conf.technosphere)

    # Base activity
    panel_init = agb.findActivity('photovoltaic panel production, multi-Si wafer', 'RER', db_name=conf.technosphere)

    # Amount to recycle
    try:
        amount_copper = new_copper_amount + panel_init.getAmount('copper, cathode')
        amount_glass = panel_init.getAmount('solar glass, low-iron')
    except:
        amount_copper = new_copper_amount + panel_init.getAmount('market for copper, cathode')
        amount_glass = panel_init.getAmount('market for solar glass, low-iron')

    # Copy / update activity
    panel_adjusted = agb.copyActivity(db_name = conf.target_database,
                                      activity = panel_init,
                                      code = ACTIVITY_NAME)

    # Adding recycling related dataset
    panel_adjusted.addExchanges({
        scrapAlu : p.m_aluminium_frame * p.Recycling_rate_Al,
        scrapCopper : amount_copper * p.Recycling_rate_Cu,
        scrapGlass : p.glass_thickness * 2.5 * 1.0 * (1.0 + p.bifaciale) * p.recycling_rate_glass,
        elec_switch_act : dict(name='elec for recycling', amount = p.electricity_recycling * (20e-3/1.6)),
        heat_for_recycling : p.heat_recycling * (20e-3/1.6) / 3.6,
    })

    # Update the exchanges
    panel_adjusted.updateExchanges({
        'aluminium alloy, AlMg3*' : p.m_aluminium_frame,
        'solar glass, low-iron*' : p.glass_thickness * 2.5 * 1.0 * (1.0 + p.bifaciale),
        'tempering, flat glass*' : p.glass_thickness * 2.5 * 1.0 * (1.0 + p.bifaciale),
        'ethylvinylacetate, foil*': 1.0017 * (1 + p.bifaciale),
        'glass fibre reinforced plastic, polyamide, injection moulded*':0.18781 * (1.0 - p.bifaciale),
        'polyethylene terephthalate, granulate, amorphous*':0.37297 * (1.0 - p.bifaciale),
        'polyvinylfluoride, film*':0.1104 * (1.0 - p.bifaciale),
        'photovoltaic cell, multi-Si wafer*' : cell_adjusted,
    })

    panel_adjusted.updateExchanges({'electricity, medium voltage*': elec_switch_act})

    return panel_adjusted


def ensure_pv_system(conf: Config):
    """Creates the PV system dataset and related activities.
    It is composed of the mounting system, electrical installation, inverter,
    PV panel, and transport-related activities.

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    Brightway activity
    """
    ACTIVITY_NAME = f"{conf.prefix}Full PV system"
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    mounting_system = ensure_mounting(conf)
    elec_install = ensure_electrical_installation(conf)
    inverter_per_kg = ensure_inverter(conf)
    panel_adjusted = ensure_pv_panel(conf)

    # ## PV system

    # Tech datasets
    diesel = agb.findActivity('market for diesel, burned in building machine', "GLO", db_name=conf.technosphere)

    # Transport datasets
    transport_car = agb.findActivity('transport, passenger car, large size, petrol, EURO 5', 'RER', db_name=conf.technosphere)
    transport_van = agb.findActivity('transport, freight, light commercial vehicle', 'Europe without Switzerland', db_name=conf.technosphere)
    transport_lorry = agb.findActivity('lorry, all sizes, EURO6*', 'RER', db_name=conf.technosphere)
    transport_train = agb.findActivity('transport, freight train, electricity', 'RoW', db_name=conf.technosphere)
    transport_sea = agb.findActivity('market for transport, freight, sea, container ship', db_name=conf.technosphere)
    # -

    is_ground_system = 1.0 - p.roof_ratio
    surface_module = 1.6 #Module surface in m²
    P_module = p.module_efficiency * surface_module * 1000
    surface  = p.P_install*1e3 / P_module * surface_module #total surface of the installation

    system_PV = agb.newActivity(db_name = conf.target_database,
                                name = ACTIVITY_NAME,
                                unit = "unit")

    inverter_weight = p.inverter_weight_per_kW * p.P_install
    elec_install_weight = p.electrical_installation_weight_per_kW * p.P_install

    # PV panel weigths 20kg/m²
    total_mass_tons = 1e-3 * ((surface / surface_module) * 20\
                    + elec_install_weight + inverter_weight * p.lifetime / p.inverter_lifetime)

    system_PV.addExchanges({
        mounting_system : surface, #m²

        # Adding diesel burned in machine for site preparation
        # 7673 MJ were accounted for the 570 kWp power plant
        diesel : is_ground_system * p.P_install/570.0 * 7673.0,

        # Number of equivalent unit of 3kW elec install
        elec_install : elec_install_weight,

        inverter_per_kg : inverter_weight * p.lifetime / p.inverter_lifetime,
        panel_adjusted : surface,

        #for engineers for feasability study (100 - 200 km)(includes installation, and dismantlement)
        transport_car : 300,

        #for maintenance
        transport_van : 1e-3 * (inverter_weight) * 100 * p.lifetime / p.inverter_lifetime, #100 km?

        #transport in ton-kilometer (freight in payload-distance)
        transport_lorry : total_mass_tons * p.d_lorry,
        transport_sea : total_mass_tons * p.d_sea,
        transport_train : total_mass_tons * p.d_train
    })

    return system_PV


def ensure_impact_model_per_kWp(conf: Config):
    """Create the impact model with a functional unit of having an installed
    capacity of 1 kWp

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    impact_per_kWp : Brightway2 / lca_algebraic activity with the impact model

    """
    ACTIVITY_NAME = f"{conf.prefix}PV impact per kWp installed"
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    # ## per kWp
    system_PV = ensure_pv_system(conf)

    # Impact model, per kWp
    impact_per_kWp = agb.newActivity(
        db_name = conf.target_database,
        name = ACTIVITY_NAME,
        unit = "unit per kWp",
        exchanges = {
            system_PV : 1.0 / p.P_install
        })

    return impact_per_kWp


def ensure_impact_model_per_kWh(conf : Config):
    """Create the impact model with a functional unit of the production of
    1 kWh of electricity

    Parameters
    ----------
    conf: Config
        see. help(Config)

    Returns
    -------
    impact_per_kWh : Brightway2 / lca_algebraic activity with the impact model

    """
    ACTIVITY_NAME = f"{conf.prefix}PV impact per kWh"
    act = agb.findActivity(ACTIVITY_NAME, db_name=conf.technosphere, single=False)
    if len(act) == 1:
        return act
    if len(act) > 1:
        raise Exception(f"Error: Unexpected multiples activities {ACTIVITY_NAME}")

    # ## per kWh
    impact_per_kWp = ensure_impact_model_per_kWp(conf)
    impact_per_kWh = agb.newActivity(
        db_name = conf.target_database,
        name = ACTIVITY_NAME,
        unit = "unit per kWh",
        exchanges = {impact_per_kWp : 1.0 / (p.lifetime * p.kWhperkWp)})

    return impact_per_kWh


def create(conf : Config):
    """Create the updated PV system dataset, related activities, and 2 impact
    models with PARASOL_LCA.

    Parameters
    ----------
    conf: dict
        expected keys:
            - target_database = database to use to store new activities (string)
            - version = ecoinvent version used (string)
            - (optional) prefix = prefix for created activities (string)
            - (optional) biosphere = biosphere database name (string)
            - (optional) technosphere = technosphere database name (string)

    """
    if isinstance(conf, dict):
        conf = Config.from_dict(conf)
    #ensure_metalisation(conf)
    ensure_impact_model_per_kWh(conf)

