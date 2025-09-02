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

from collections import defaultdict

def load_ecoinvent_biosphere(path, biosphere_name):
    """
    Load ecoinvent biosphere from file, and define it as biosphere database.
    Parameters:
    -----------
        path : path to the `MasterData/ElementaryExchanges.xml' provided by file such as `ecoinvent 3.9_cutoff_ecoSpold02.7z'
        biosphere_name : name of the database where data will be stored
    """
    import os
    import brightway2 as bw
    import bw2data
    from bw2io.importers import Ecospold2BiosphereImporter, SingleOutputEcospold2Importer
    if biosphere_name not in bw.databases:
        eb = Ecospold2BiosphereImporter(name=biosphere_name,
             #filepath=os.path.join(path, "MasterData", "ElementaryExchanges.xml"))
             filepath=path)
        eb.apply_strategies()
        if not eb.all_linked:
                raise ValueError(f"Can't ingest biosphere database {biosphere_name} - unlinked flows.")
        eb.write_database(overwrite=False)
    bw2data.preferences["biosphere_database"] = biosphere_name

def load_ecoinvent_lci(path : str, db_name : str, biosphere_name : str):
    """
    Load ecoinvent LCI in db_name
    Parameters:
    -----------
        path : path to the dataset directory, usually the `datasets' directory provided by file such as `ecoinvent 3.9_cutoff_ecoSpold02.7z'
        db_name: database name where LCI will be stored
        biosphere_name: the biosphere database name to use to link LCI, be carefull to use the biosphere that corespond to LCI
    """
    import os
    import brightway2 as bw
    import bw2data
    from bw2io.importers import Ecospold2BiosphereImporter, SingleOutputEcospold2Importer
    if db_name not in bw.databases:
        soup = SingleOutputEcospold2Importer(
            #dirpath=os.path.join(path, "datasets"),
            dirpath=path,
            db_name=db_name,
            biosphere_database_name=biosphere_name,
            signal=None)
        soup.apply_strategies()
        if not soup.all_linked:
            raise ValueError(f"Can't ingest inventory database {db_name} - unlinked flows.")
        soup.write_database()

def load_ecoinvent_lcia(path : str, biosphere_name : str, version : str):
    """
    Load LCIA methods from ecoinvent file
    Parameters:
    ----------
        path: path to the ecoinvent xlsx file, such as `LCIA Implementation 3.9.xlsx' usualy found in `ecoinvent 3.9_LCIA_implementation.7z'
        biosphere_name: biosphere database name to use as biosphere usualy biosphere3
        version: ecoinvent version string such as "3.9", "3.9.1"; used to apply correct fix/strategy to load the data
    """
    from ecoinvent_interface.string_distance import damerau_levenshtein
    import bw2data
    from bw2io.extractors import ExcelExtractor
    from bw2io.ecoinvent import (
        get_excel_sheet_names,
        header_dict,
        pick_a_unit_label_already,
        drop_unspecified
    )

    if biosphere_name is None:
        biosphere_name = bw2data.config.biosphere
    if biosphere_name not in bw2data.databases or not len(bw2data.Database(biosphere_name)):
        raise ValueError(f"Can't find populated biosphere flow database {biosphere_name}")

    #lcia_file = ei.get_excel_lcia_file_for_version(release=release, version=version)
    lcia_file = path

    sheet_names = get_excel_sheet_names(lcia_file)

    if "units" in sheet_names:
        units_sheetname = "units"
    elif "Indicators" in sheet_names:
        units_sheetname = "Indicators"
    else:
        raise ValueError(
            f"Can't find worksheet for impact category units in {sheet_names}"
        )

    if "CFs" not in sheet_names:
        raise ValueError(
            f"Can't find worksheet for characterization factors; expected `CFs`, found {sheet_names}"
        )

    data = dict(ExcelExtractor.extract(lcia_file))
    units = header_dict(data[units_sheetname])

    cfs = header_dict(data["CFs"])

    CF_COLUMN_LABELS = {
        "3.4": "cf 3.4",
        "3.5": "cf 3.5",
        "3.6": "cf 3.6",
    }
    cf_col_label = CF_COLUMN_LABELS.get(version, "cf")
    units_col_label = pick_a_unit_label_already(units[0])
    units_mapping = {
        (row["method"], row["category"], row["indicator"]): row[units_col_label]
        for row in units
    }

    biosphere_mapping = {}
    for flow in bw2data.Database(biosphere_name):
        biosphere_mapping[(flow["name"],) + tuple(flow["categories"])] = flow.key
        if flow["name"].startswith("[Deleted]"):
            biosphere_mapping[
                (flow["name"].replace("[Deleted]", ""),) + tuple(flow["categories"])
            ] = flow.key

    lcia_data_as_dict = defaultdict(list)

    unmatched = set()
    substituted = set()

    for row in cfs:
        impact_category = (row["method"], row["category"], row["indicator"])
        if row[cf_col_label] is None:
            continue
        try:
            lcia_data_as_dict[impact_category].append(
                (
                    biosphere_mapping[
                        drop_unspecified(
                            row["name"], row["compartment"], row["subcompartment"]
                        )
                    ],
                    float(row[cf_col_label]),
                )
            )
        except KeyError:
            # How is this possible? We are matching ecoinvent data against
            # ecoinvent data from the same release! And yet it moves...
            category = (
                (row["compartment"], row["subcompartment"])
                if row["subcompartment"].lower() != "unspecified"
                else (row["compartment"],)
            )
            same_context = {
                k[0]: v for k, v in biosphere_mapping.items() if k[1:] == category
            }
            candidates = sorted(
                [
                    (damerau_levenshtein(name, row["name"]), name)
                    for name in same_context
                ]
            )
            if (
                candidates[0][0] < 3
                and candidates[0][0] != candidates[1][0]
                and candidates[0][1][0].lower() == row["name"][0].lower()
            ):
                new_name = candidates[0][1]
                pair = (new_name, row["name"])
                if pair not in substituted:
                    print(f"Substituting {new_name} for {row['name']}")
                    substituted.add(pair)
                lcia_data_as_dict[impact_category].append(
                    (
                        same_context[new_name],
                        float(row[cf_col_label]),
                    )
                )
            else:
                if row["name"] not in unmatched:
                    print(
                        "Skipping unmatched flow {}:({}, {})".format(
                            row["name"], row["compartment"], row["subcompartment"]
                        )
                    )
                    unmatched.add(row["name"])

    for key in lcia_data_as_dict:
        method = bw2data.Method(key)
        method.register(
            unit=units_mapping.get(key, "Unknown"),
            filepath=str(lcia_file),
            ecoinvent_version=version,
            database=biosphere_name,
        )
        method.write(lcia_data_as_dict[key])
    pass

def load_ecoinvent_database(path, db_name, biosphere_name):
    import os
    import brightway2 as bw
    import bw2data
    from bw2io.importers import Ecospold2BiosphereImporter, SingleOutputEcospold2Importer
    if biosphere_name not in bw.databases:
        eb = Ecospold2BiosphereImporter(name=biosphere_name,
             filepath=os.path.join(path, "MasterData", "ElementaryExchanges.xml"))
        eb.apply_strategies()
        if not eb.all_linked:
                raise ValueError(f"Can't ingest biosphere database {biosphere_name} - unlinked flows.")
        eb.write_database(overwrite=False)
    bw2data.preferences["biosphere_database"] = biosphere_name

    if db_name not in bw.databases:
        soup = SingleOutputEcospold2Importer(
            dirpath=os.path.join(path, "datasets"),
            db_name=db_name,
            biosphere_database_name=biosphere_name,
            signal=None)
        soup.apply_strategies()
        if not soup.all_linked:
            raise ValueError(f"Can't ingest inventory database {db_name} - unlinked flows.")
        soup.write_database()


