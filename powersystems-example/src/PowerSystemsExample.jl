module PowerSystemsExample

using PowerSimulations
using PowerSystems
using CSV
using Pkg.Artifacts
using Logging
using DataFrames
using Statistics
using UnicodePlots

const RTS_GMLC_MATPOWER_FILENAME = joinpath(artifact"matpower", "RTS_GMLC.m")
const ROOT = dirname(@__DIR__)

export load_solve_output
export load
export solve
export output
export compare_v_gen_load
export compare_from_to_loss


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

function compare_v_gen_load()
    powersystems = CSV.read(joinpath(@__DIR__, "../results/bus.csv"), DataFrame)
    matpower = CSV.read(joinpath(@__DIR__, "../../matpower-example/results/bus.csv"), DataFrame)

    matpower = coalesce.(matpower, 0) # convert missing values to 0

    powersystems.V = powersystems.Vm .* exp.(im .* powersystems.θ)
    matpower.V = matpower.v_mag .* exp.(im .* matpower.v_ang)
    powersystems.gen = powersystems.P_gen .+ (im .* powersystems.Q_gen)
    matpower.gen = matpower.p_gen .+ (im .* matpower.q_gen)
    powersystems.load = powersystems.P_load .+ (im .* powersystems.Q_load)
    matpower.load = matpower.p_load .+ (im .* matpower.q_load)
    @show std(powersystems.V - matpower.V)
    @show std(powersystems.gen - matpower.gen)
    @show std(powersystems.load - matpower.load)
    println()
    @show std(abs.(powersystems.V - matpower.V))
    @show std(abs.(powersystems.gen - matpower.gen))
    @show std(abs.(powersystems.load - matpower.load))
    println()
    display(boxplot(abs.(powersystems.V - matpower.V), xlabel = "Voltage"))
    display(boxplot(abs.(powersystems.gen - matpower.gen), xlabel = "Generation"))
    display(boxplot(abs.(powersystems.load - matpower.load), xlabel = "Load"))
end

function compare_from_to_loss()
    powersystems = CSV.read(joinpath(@__DIR__, "../results/flow.csv"), DataFrame)
    matpower = CSV.read(joinpath(@__DIR__, "../../matpower-example/results/flow.csv"), DataFrame)

    matpower = coalesce.(matpower, 0) # convert missing values to 0

    powersystems.from = powersystems.P_from_to .+ (im .* powersystems.Q_from_to)
    matpower.from = matpower.from_bus_inj_p .+ (im .* matpower.from_bus_inj_q)
    powersystems.to = powersystems.P_to_from .+ (im .* powersystems.Q_to_from)
    matpower.to = matpower.to_bus_inj_p .+ (im .* matpower.to_bus_inj_q)

    powersystems.loss = powersystems.P_losses .+ (im .* powersystems.Q_losses)
    matpower.loss = matpower.loss_p .+ (im .* matpower.loss_q)
    @show std(powersystems.from - matpower.from)
    @show std(powersystems.to - matpower.to)
    @show std(powersystems.loss - matpower.loss)
    println()
    @show std(abs.(powersystems.from - matpower.from))
    @show std(abs.(powersystems.to - matpower.to))
    @show std(abs.(powersystems.loss - matpower.loss))
    println()
    display(boxplot(abs.(powersystems.from - matpower.from), xlabel = "From"))
    display(boxplot(abs.(powersystems.to - matpower.to), xlabel = "To"))
    display(boxplot(abs.(powersystems.loss - matpower.loss), xlabel = "Loss"))
end

end # module
