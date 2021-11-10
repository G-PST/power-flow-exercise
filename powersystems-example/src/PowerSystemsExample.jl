module PowerSystemsExample

using PowerSimulations
using PowerSystems
using CSV
using Pkg.Artifacts
using Logging

const RTS_GMLC_MATPOWER_FILENAME = joinpath(artifact"matpower", "RTS_GMLC.m")
const ROOT = dirname(@__DIR__)

export load_solve_output
export load
export solve
export output


function load()
    System(RTS_GMLC_MATPOWER_FILENAME)
end

function solve(system)
    results = PowerSystems.solve_powerflow(system)
end

function output(results)
    mkpath(joinpath(ROOT, "results"))
    CSV.write(joinpath(ROOT, "results/flow.csv"), results["flow_results"])
    CSV.write(joinpath(ROOT, "results/bus.csv"), results["bus_results"])
    nothing
end

function load_solve_output(; disable_logging = true)
    disable_logging && configure_logging(console_level = Logging.Error, file_level = Logging.Error)
    !disable_logging && println("Loading system...")
    system = load()
    !disable_logging && println("Solve system...")
    results = solve(system)
    !disable_logging && println("Writing results...")
    output(results)
    !disable_logging && println("Done!")
    nothing
end

end # module
