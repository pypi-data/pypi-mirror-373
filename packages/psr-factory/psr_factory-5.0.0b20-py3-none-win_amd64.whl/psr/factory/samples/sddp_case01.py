"""Creates SDDP 1 stage Case01 example."""
import copy
import os

import psr.factory


def _get_case_path() -> str:
    return os.path.join(os.path.splitext(os.path.basename(__file__))[0], "")


def create_case01(legacy: bool = False) -> psr.factory.Study:
    blocks = 1
    model = "SDDP" if not legacy else "SDDP17"
    # Create a study object and define its basic settings.
    study = psr.factory.create_study({
        "Models": [model, ], # Default model: SDDP
        "Blocks": blocks, # Default number of blocks: 1
        "StageType": 2,   # Weekly: 1 (default), Monthly: 2
    })
    study.from_dict({
        "Description": "Caso ejemplo - DT - 1 etapa - 1 bloque",
        "InitialYear": 2013,
        "InitialStage": 1,
        "NumberOfStages": 1,
        "NumberOfSeries": 1,
    })

    # Study options
    study.from_dict({
        "Type": 2,
        "InitialYearOfHydrology": 1996,
        "NumberOfSystems": 1,
        "AggregateInTheOperationPolicy": 0,
        "UMON": "$",
        "LoadSheddingInBuses": 0,
        "MonitoringOfCircuitLimits": 0,
        "HourlyRepresentation": 0,
        "MaximumNumberOfIterations": 10,
        "MinimumOutflowPenaltyHm3": 5000.0,
        "DeficitSegment": [100.0, 0.0, 0.0, 0.0],
        "DeficitCost": [500.0, 0.0, 0.0, 0.0],
        "FutureCostStage": 4,
        "FutureCostYear": 1998,
    })

    # Study duration
    study.set("FixedDurationOfBlocks(1)", 100.0)

    # By default, a study comes with one system.
    system = study.get("System")[0]
    system.code = 1
    system.id = "s1"
    system.name = "System 1"
    # System's currency
    system.set("SystemCurrency", "$")
    # It's not required to add an existing object to the study.

    # Set study to run with this unique system
    study.set("CodesOfPowerSystems", [1, ])

    # Create a demand segment - it's required to add at least
    # an inelastic segment to a demand object.
    segment = psr.factory.create("DemandSegment", study.context)
    # Set demand and cost data.
    segment.set_at("EnergyPerBlock(:)", "01/2013", 8.928)
    # Add segment to the study.
    study.add(segment)

    # Create a system demand.
    demand = psr.factory.create("Demand", study.context)
    demand.code = 1
    demand.name = "System 1"
    # Associate it with the only system in the case.
    demand.set("RefSystem", system)
    # Associate the demand with its segments.
    demand.set("RefSegments", [segment, ])
    # Add demand to the study.
    study.add(demand)

    # Create all fuels - Thermal plants requires then.
    fuel1 = psr.factory.create("Fuel", study.context)
    fuel1.code = 1
    fuel1.name = "Fuel 1"
    fuel1.from_dict({
        "Unit": "UC",
        "UE": "MWh",
        "Price": 0.8,
        "EmissionFactor": 0.0,
        "RefSystem": system,
    })
    study.add(fuel1)

    fuel2 = psr.factory.create("Fuel", study.context)
    fuel2.code = 2
    fuel2.name = "Fuel 2"
    fuel2.from_dict({
        "Unit": "UC",
        "UE": "MWh",
        "Price": 1.2,
        "EmissionFactor": 0.0,
        "RefSystem": system,
    })
    study.add(fuel2)

    # Create all thermal plants.
    plant1 = study.create("ThermalPlant")
    plant1.code = 1
    plant1.name = "Thermal 1"
    # Set plant's properties
    t_params = {
        "MaximumGenerationCapacity": 10.0,
        "InstalledCapacity": 10.0,
        "ThermalType": 0,
        "Type": 0,
        "NumberOfGeneratingUnits": 1,
        "NumberOfAlternativeFuels": 0,
        "CodeOfAlternativeFuels(:)": 0,
        "O&MCost": 0.0,
        "FuelTransportationCost": 0.0,
        "SpecificConsumptionSegment(1)": 100.0,
        "SpecificConsumptionSegment(2:3)": 0.0,
        "SpecificConsumption(1:3,1)": 10.0,
        "RefFuels": [fuel1, ],
        "RefSystem": system,
    }
    plant1.from_dict(t_params)
    study.add(plant1)

    # Use Python copy's module copy function to create
    # a copy of an object.
    plant2 = copy.copy(plant1)
    plant2.code = 2
    plant2.name = "Thermal 2"
    plant2.set("MaximumGenerationCapacity", 5.0)
    plant2.set("InstalledCapacity", 5.0)
    plant2.set("SpecificConsumption(1:3,1)", 15.0)
    plant2.set("RefFuels", [fuel1, ])
    plant2.set("RefSystem", system)
    study.add(plant2)

    plant3 = plant2.clone()
    plant3.code = 3
    plant3.name = "Thermal 3"
    plant3.from_dict({
        "MaximumGenerationCapacity": 20.0,
        "InstalledCapacity": 20.0,
        "SpecificConsumption(1:3,1)": 12.5,
        "RefFuels": [fuel2, ],
        "RefSystem": system,
    })
    study.add(plant3)

    return study


if __name__ == "__main__":
    case_path = _get_case_path()
    os.makedirs(case_path, exist_ok=True)
    print("Creating example case... ", end="")
    study = create_case01(False)
    print(" OK.")
    print("Saving example case in \"{}\"... ".format(case_path), end="")
    study.save(case_path)
    print(" OK.")
