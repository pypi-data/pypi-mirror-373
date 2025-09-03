"""Creates SDDP 12 stages Case21 example."""
import copy
import os

import psr.factory


def _get_case_path() -> str:
    return os.path.join(os.path.splitext(os.path.basename(__file__))[0], "")


def create_case21(legacy: bool = False) -> psr.factory.Study:
    # Create a study object and define its basic settings.
    blocks = 1
    model = "SDDP" if not legacy else "SDDP17"
    # A context defines the dimensions of the study and the meaning of
    # its stages. You can only share or copy data from one study to another
    # if they share the same context.
    context = psr.factory.get_new_context()
    context.set("Models", [model, ])  # Default model: Sddp
    context.set("Blocks", blocks)   # Default number of blocks: 3
    context.set("StageType", 2)     # Weekly: 1, Monthly: 2 (default)

    study = psr.factory.create_study(context)
    study.set("Description", "SDDP")
    study.set("InitialYear", 2016)
    study.set("InitialStage", 1)
    study.set("NumberOfStages", 12)
    study.set("NumberOfSeries", 1)

    # Study options
    study.set("Type", 2)
    study.set("InitialYearOfHydrology", 2016)
    study.set("NumberOfSystems", 1)
    study.set("AggregateInTheOperationPolicy", 1)
    study.set("DeficitSegment", [100.0, 0.0, 0.0, 0.0])
    study.set("DeficitCost", [1000.0, 0.0, 0.0, 0.0])
    study.set("UMON", "$")

    # Study duration
    study.set("FixedDurationOfBlocks(1)", 100.0)

    # By default, a study comes with one system.
    system = study.get("System")[0]
    system.code = 1
    system.id = "s1"
    system.name = "S1"
    # System's currency
    system.set("SystemCurrency", "$")
    # It's not required to add an existing object to the study.

    # Set study to run with this unique system
    study.set("CodesOfPowerSystems", [1, ])

    # Create a demand segment - it's required to add at least
    # inelastic segment to a demand object.
    segment = psr.factory.create("DemandSegment", context)
    # Set demand and cost data.
    segment.set_at("EnergyPerBlock(:)", "01/2016", 11.7)
    segment.set_at("EnergyPerBlock(:)", "02/2016", 10.8)
    segment.set_at("EnergyPerBlock(:)", "03/2016", 12.5)
    segment.set_at("EnergyPerBlock(:)", "04/2016", 13.7)
    segment.set_at("EnergyPerBlock(:)", "05/2016", 14.6)
    segment.set_at("EnergyPerBlock(:)", "06/2016", 14.8)
    segment.set_at("EnergyPerBlock(:)", "07/2016", 15.8)
    segment.set_at("EnergyPerBlock(:)", "08/2016", 16.2)
    segment.set_at("EnergyPerBlock(:)", "09/2016", 15.3)
    segment.set_at("EnergyPerBlock(:)", "10/2016", 14.5)
    segment.set_at("EnergyPerBlock(:)", "11/2016", 12.9)
    segment.set_at("EnergyPerBlock(:)", "12/2016", 12.5)

    segment.set_at("PricePerBlock(:)", "01/2016", 0.0)
    # Add segment to the study.
    study.add(segment)

    # Create a system demand.
    demand = psr.factory.create("Demand", context)
    demand.code = 1
    demand.name = "S1"
    # Associate it with the only system in the case.
    demand.set("RefSystem", system)
    # Add segment to the demand.
    demand.set("RefSegments", [segment, ])
    # Add demand to the study.
    study.add(demand)

    # Create all fuels - Thermal plants requires them.
    fuel1 = psr.factory.create("Fuel", context)
    fuel1.code = 1
    fuel1.name = "C1"
    fuel1.set("Unit", "MWh")
    fuel1.set("Price", 8.0)
    fuel1.set("RefSystem", system)
    study.add(fuel1)

    fuel2 = psr.factory.create("Fuel", context)
    fuel2.code = 2
    fuel2.name = "C2"
    fuel2.set("Unit", "MWh")
    fuel2.set("Price", 12.0)
    fuel2.set("RefSystem", system)
    study.add(fuel2)

    fuel3 = psr.factory.create("Fuel", context)
    fuel3.code = 3
    fuel3.name = "C3"
    fuel3.set("Unit", "MWh")
    fuel3.set("Price", 14.4)
    fuel3.set("RefSystem", system)
    study.add(fuel3)

    # Create all thermal plants.
    plant1 = psr.factory.create("ThermalPlant", context)
    plant1.code = 1
    plant1.name = "T1"
    # Set plant's properties
    plant1.set("MaximumGenerationCapacity", 12.0)
    plant1.set("InstalledCapacity", 12.0)
    plant1.set("ThermalType", 0)  # Standard operation mode.
    plant1.set("Type", 0)         # It's an existing plant.
    plant1.set("NumberOfGeneratingUnits", 1)
    plant1.set("NumberOfAlternativeFuels", 0)  # No alternative fuels
    plant1.set("CodeOfAlternativeFuels(:)", 0)
    plant1.set("O&MCost", 0.0)
    plant1.set("FuelTransportationCost", 0.0)
    plant1.set("SpecificConsumptionSegment(1)", 100.0)
    plant1.set("SpecificConsumptionSegment(2:3)", 0.0)
    plant1.set("SpecificConsumption(1:3,1)", 1.0)
    plant1.set("Co2EmissionCoefficient", 1.0)
    # It's required to associate a thermal plant to a fuel.
    plant1.set("RefFuels", [fuel1, ])
    plant1.set("RefSystem", system)
    # These references are optional and can be set as None.
    plant1.set("RefGasNode", None)
    study.add(plant1)

    plant2 = psr.factory.create("ThermalPlant", context)
    plant2.code = 2
    plant2.name = "T2"
    plant2.set("MaximumGenerationCapacity", 8.0)
    plant2.set("InstalledCapacity", 8.0)
    plant2.set("ThermalType", 0)
    plant2.set("Type", 0)
    plant2.set("NumberOfGeneratingUnits", 1)
    plant2.set("NumberOfAlternativeFuels", 0)
    plant2.set("CodeOfAlternativeFuels(:)", 0)
    plant2.set("O&MCost", 0.0)
    plant2.set("FuelTransportationCost", 0.0)
    plant2.set("SpecificConsumptionSegment(1)", 100.0)
    plant2.set("SpecificConsumptionSegment(2:3)", 0.0)
    plant2.set("SpecificConsumption(1:3,1)", 1.0)
    plant2.set("Co2EmissionCoefficient", 1.0)
    plant2.set("RefFuels", [fuel2, ])
    plant2.set("RefSystem", system)
    study.add(plant2)

    plant3 = plant2.clone()
    plant3.code = 3
    plant3.name = "T3"
    plant3.set("MaximumGenerationCapacity", 4.0)
    plant3.set("InstalledCapacity", 4.0)
    plant3.set("RefFuels", [fuel3, ])
    plant3.set("RefSystem", system)
    study.add(plant3)

    # Define gauging station for hydro plants inflows
    station1 = psr.factory.create("HydroStation", context)
    station1.code = 1
    station1.name = "Estacion 1"

    station2 = psr.factory.create("HydroStation", context)
    station2.code = 2
    station2.name = "Estacion 2"

    for year in (2014, 2015, 2016):
        station1.set_at("Inflow", f"01/{year}", 13.5)
        station1.set_at("Inflow", f"02/{year}", 40.7)
        station1.set_at("Inflow", f"03/{year}", 28.8)
        station1.set_at("Inflow", f"04/{year}", 25.6)
        station1.set_at("Inflow", f"05/{year}", 23.8)
        station1.set_at("Inflow", f"06/{year}", 27.8)
        station1.set_at("Inflow", f"07/{year}", 28.8)
        station1.set_at("Inflow", f"08/{year}", 18.8)
        station1.set_at("Inflow", f"09/{year}", 18.2)
        station1.set_at("Inflow", f"10/{year}", 29.6)
        station1.set_at("Inflow", f"11/{year}", 17.7)
        station1.set_at("Inflow", f"12/{year}", 26.3)

        for month in range(1, 12 + 1):
            station2.set_at("Vazao", f"{month:02d}/{year}", 0.0)

    study.add(station1)
    study.add(station2)

    # Define hydroplants
    hydro1 = psr.factory.create("HydroPlant", context)
    hydro1.code = 1
    hydro1.name = "H1"
    hydro1.set("Type", 0)
    hydro1.set("NumberOfUnits", 1)
    hydro1.set("InstalledCapacity", 5.5)
    hydro1.set("MaximumTurbinedOutflow", 55.0)
    hydro1.set("MeanProductionCoefficient", 0.1)
    hydro1.set("MinimumStorage", 0.0)
    hydro1.set("MaximumStorage", 50.0)
    hydro1.set("InitialCondition", 0.2)
    hydro1.set("RefSystem", system)
    hydro1.set("RefStation", station1)
    study.add(hydro1)

    hydro2 = hydro1.clone()
    hydro2.code = 2
    hydro2.name = "H2"
    hydro2.set("MaximumStorage", 0.0)
    hydro2.set("InitialCondition", 1.0)
    hydro2.set("RefSystem", system)
    hydro2.set("RefStation", station2)
    study.add(hydro2)

    # Connect hydro plants
    connection_spill = psr.factory.create("HydroPlantConnection", context)
    connection_spill.set("IsVertimento", 1)
    connection_spill.set("RefPlants", [hydro1, hydro2])
    study.add(connection_spill)

    connection_turb = psr.factory.create("HydroPlantConnection", context)
    connection_turb.set("IsTurbinamento", 1)
    connection_turb.set("RefPlants", [hydro1, hydro2])
    study.add(connection_turb)

    return study


if __name__ == "__main__":
    case_path = _get_case_path()
    os.makedirs(case_path, exist_ok=True)
    print("Creating example case... ", end="")
    study = create_case21(False)
    print(" OK.")
    print("Saving example case in \"{}\"... ".format(case_path), end="")
    study.save(case_path)
    print(" OK.")
