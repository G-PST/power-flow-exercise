module PowerModelsExample

using PowerModels
using CSV
using Pkg.Artifacts
using Logging
using DataFrames
using Statistics
using UnicodePlots
using Ipopt

const MATPOWER_DIR = joinpath(dirname(dirname(@__DIR__)), "reference-matpower")
const RTS_GMLC_MATPOWER_FILENAME = joinpath(MATPOWER_DIR, "RTS_GMLC", "RTS_GMLC.m")
const PEGASE_MATPOWER_FILENAME = joinpath(MATPOWER_DIR, "case9241pegase", "case9241pegase.m")
const ROOT = dirname(@__DIR__)
const SEPARATOR = '─'

export load_solve_output
export solve
export output
export compare_v_gen_load
export compare_from_to_loss

function load(;fname = RTS_GMLC_MATPOWER_FILENAME)
    data = PowerModels.parse_file(fname)
    return data
end

function solve(data)
    #results = run_pf(data, ACPPowerModel, Ipopt.Optimizer) #optimization
    results = compute_ac_pf(data) #simulation
    (results, data)
end

function output(results, data, fname)
    bus_n_arr = sort(parse.(Int, keys(results["solution"]["bus"])))

    v_mag_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))
    v_ang_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))

    map(bus_n_arr) do b
        x = results["solution"]["bus"][string(b)]["vm"]
        i = only(findall(x -> x==b, bus_n_arr))
        v_mag_arr[i] = x
    end

    map(bus_n_arr) do b
        x = results["solution"]["bus"][string(b)]["va"]
        i = only(findall(x -> x==b, bus_n_arr))
        v_ang_arr[i] = x
    end

    gen_n_arr = sort(parse.(Int, keys(results["solution"]["gen"])))

    p_gen_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))
    q_gen_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))

    map(gen_n_arr) do b
        x = results["solution"]["gen"][string(b)]["pg"]
        b = data["gen"][string(b)]["gen_bus"]
        i = only(findall(x -> x==b, bus_n_arr))
        p_gen_arr[i] === missing && (p_gen_arr[i] = 0)
        p_gen_arr[i] += x
    end

    map(gen_n_arr) do b
        x = results["solution"]["gen"][string(b)]["qg"]
        b = data["gen"][string(b)]["gen_bus"]
        i = only(findall(x -> x==b, bus_n_arr))
        q_gen_arr[i] === missing && (q_gen_arr[i] = 0)
        q_gen_arr[i] += x
    end

    load_n_arr = sort(parse.(Int, keys(data["load"])))

    p_load_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))
    q_load_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))

    map(load_n_arr) do b
        x = data["load"][string(b)]["pd"]
        b = data["load"][string(b)]["load_bus"]
        i = only(findall(x -> x==b, bus_n_arr))
        p_load_arr[i] === missing && (p_load_arr[i] = 0)
        p_load_arr[i] += x
    end

    map(load_n_arr) do b
        x = data["load"][string(b)]["qd"]
        b = data["load"][string(b)]["load_bus"]
        i = only(findall(x -> x==b, bus_n_arr))
        q_load_arr[i] === missing && (q_load_arr[i] = 0)
        q_load_arr[i] += x
    end

    df = DataFrame([
        bus_n_arr,
        v_mag_arr,
        v_ang_arr,
        p_gen_arr * data["baseMVA"],
        q_gen_arr * data["baseMVA"],
        p_load_arr * data["baseMVA"],
        q_load_arr * data["baseMVA"],
        # λ_p_arr,
        # λ_q_arr,
    ], [:bus_n, :v_mag, :v_ang, :p_gen, :q_gen, :p_load, :q_load])

    case = last(splitpath(dirname(fname)))
    out_path = mkpath(joinpath(ROOT, case, "results"))
    CSV.write(joinpath(out_path, "bus.csv"), df)
    nothing
end

function load_solve_output(; disable_logging = true, fname = RTS_GMLC_MATPOWER_FILENAME)
    disable_logging && PowerModels.Memento.config!("critical")
    !disable_logging && println("Loading system...")
    system = load(;fname = fname)
    !disable_logging && println("Solve system...")
    results, data = solve(system)
    !disable_logging && println("Writing results...")
    output(results, data, fname)
    !disable_logging && println("Done!")
    nothing
end

function compare_v_gen_load(;fname = RTS_GMLC_MATPOWER_FILENAME)
    case = last(splitpath(dirname(fname)))
    powermodels = CSV.read(joinpath(ROOT, case, "results", "bus.csv"), DataFrame)
    matpower = CSV.read(joinpath(dirname(fname), "results", "bus.csv"), DataFrame)

    matpower = coalesce.(matpower, 0) # convert missing values to 0
    powermodels = coalesce.(powermodels, 0) # convert missing values to 0

    powermodels.V = powermodels.v_mag .* exp.(im .* powermodels.v_ang)
    matpower.V = matpower.v_mag .* exp.(im .* (deg2rad.(matpower.v_ang)))
    powermodels.gen = powermodels.p_gen .+ (im .* powermodels.q_gen)
    matpower.gen = matpower.p_gen .+ (im .* matpower.q_gen)
    powermodels.load = powermodels.p_load .+ (im .* powermodels.q_load)
    matpower.load = matpower.p_load .+ (im .* matpower.q_load)

    @show std(powermodels.V - matpower.V)
    @show std(real.(powermodels.V) - real.(matpower.V))
    @show std(imag.(powermodels.V) - imag.(matpower.V))
    @show std(powermodels.gen - matpower.gen)
    @show std(real.(powermodels.gen) - real.(matpower.gen))
    @show std(imag.(powermodels.gen) - imag.(matpower.gen))
    @show std(powermodels.load - matpower.load)
    @show std(real.(powermodels.load) - real.(matpower.load))
    @show std(imag.(powermodels.load) - imag.(matpower.load))
    println()
    @show std(abs.(powermodels.V - matpower.V))
    @show std(abs.(powermodels.gen - matpower.gen))
    @show std(abs.(powermodels.load - matpower.load))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powermodels.V - matpower.V), title = "Voltage", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powermodels.gen - matpower.gen), title = "Generation", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powermodels.load - matpower.load), title = "Load", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powermodels.V - matpower.V), title = "Voltage", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powermodels.gen - matpower.gen), title = "Generation", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powermodels.load - matpower.load), title = "Load", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
end

end # module
