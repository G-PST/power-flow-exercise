module PowerSystemsExample

using PowerSystems
using PowerModelsInterface
using CSV
using Pkg.Artifacts
using Logging
using DataFrames
using Statistics
using UnicodePlots

const MATPOWER_DIR = joinpath(dirname(dirname(@__DIR__)), "reference-matpower")
const RTS_GMLC_MATPOWER_FILENAME = joinpath(MATPOWER_DIR, "RTS_GMLC", "RTS_GMLC.m")
const PEGASE_MATPOWER_FILENAME = joinpath(MATPOWER_DIR, "case9241pegase", "case9241pegase.m")
const ROOT = dirname(@__DIR__)
const SEPARATOR = '─'

export load_solve_output
export load
export solve
export output
export compare_v_gen_load
export compare_v_gen_load_nodal
export compare_from_to_loss


function load(;fname = RTS_GMLC_MATPOWER_FILENAME)
    system = System(fname)
    return system
end

function solve(system; method = PowerSystems)
    if method == PowerModelsInterface
        pm_data = get_pm_data(system)
        results = gather_results(compute_ac_pf(pm_data), pm_data)
    else
        results = solve_powerflow(system)
    end
    return results
end

function output(results, fname)
    case = last(splitpath(dirname(fname)))
    out_path = mkpath(joinpath(ROOT, case, "results"))
    CSV.write(joinpath(out_path, "flow.csv"), results["flow_results"])
    CSV.write(joinpath(out_path, "bus.csv"), results["bus_results"])
    nothing
end

function load_solve_output(; disable_logging = true, fname = RTS_GMLC_MATPOWER_FILENAME)
    disable_logging && configure_logging(console_level = Logging.Error, file_level = Logging.Error)
    !disable_logging && println("Loading system...")
    system = load(fname = fname)
    !disable_logging && println("Solve system...")
    method = fname == RTS_GMLC_MATPOWER_FILENAME ? PowerSystems : PowerModelsInterface
    results = solve(system; method = method)
    !disable_logging && println("Writing results...")
    output(results, fname)
    !disable_logging && println("Done!")
    nothing
end

function compare_v_gen_load(;fname = RTS_GMLC_MATPOWER_FILENAME)
    case = last(splitpath(dirname(fname)))
    powersystems = CSV.read(joinpath(ROOT, case, "results", "bus.csv"), DataFrame)
    matpower = CSV.read(joinpath(dirname(fname), "results", "bus.csv"), DataFrame)

    matpower = coalesce.(matpower, 0) # convert missing values to 0

    powersystems.V = powersystems.Vm .* exp.(im .* powersystems.θ)
    matpower.V = matpower.v_mag .* exp.(im .* (deg2rad.(matpower.v_ang)))
    powersystems.gen = powersystems.P_gen .+ (im .* powersystems.Q_gen)
    matpower.gen = matpower.p_gen .+ (im .* matpower.q_gen)
    powersystems.load = powersystems.P_load .+ (im .* powersystems.Q_load)
    matpower.load = matpower.p_load .+ (im .* matpower.q_load)

    @show std(powersystems.V - matpower.V)
    @show std(real.(powersystems.V) - real.(matpower.V))
    @show std(imag.(powersystems.V) - imag.(matpower.V))
    @show std(powersystems.gen - matpower.gen)
    @show std(real.(powersystems.gen) - real.(matpower.gen))
    @show std(imag.(powersystems.gen) - imag.(matpower.gen))
    @show std(powersystems.load - matpower.load)
    @show std(real.(powersystems.load) - real.(matpower.load))
    @show std(imag.(powersystems.load) - imag.(matpower.load))
    println()
    @show std(abs.(powersystems.V - matpower.V))
    @show std(abs.(powersystems.gen - matpower.gen))
    @show std(abs.(powersystems.load - matpower.load))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.V - matpower.V), title = "Voltage", xlabel=""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.gen - matpower.gen), title = "Generation", xlabel=""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.load - matpower.load), title = "Load", xlabel=""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.V - matpower.V), title = "Voltage", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.gen - matpower.gen), title = "Generation", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.load - matpower.load), title = "Load", xlabel = ""))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
end


function compare_v_gen_load_nodal(;fname = RTS_GMLC_MATPOWER_FILENAME, size = 10)
    case = last(splitpath(dirname(fname)))
    powersystems = CSV.read(joinpath(ROOT, case, "results", "bus.csv"), DataFrame)
    matpower = CSV.read(joinpath(dirname(fname), "results", "bus.csv"), DataFrame)

    matpower = coalesce.(matpower, 0) # convert missing values to 0

    powersystems.V = powersystems.Vm .* exp.(im .* powersystems.θ)
    matpower.V = matpower.v_mag .* exp.(im .* (deg2rad.(matpower.v_ang)))
    powersystems.gen = powersystems.P_gen .+ (im .* powersystems.Q_gen)
    matpower.gen = matpower.p_gen .+ (im .* matpower.q_gen)
    powersystems.load = powersystems.P_load .+ (im .* powersystems.Q_load)
    matpower.load = matpower.p_load .+ (im .* matpower.q_load)

    function sort_vec(vec, len)
        perm = sortperm(abs.(vec), rev = true)
        return DataFrame(:id=> perm[1:len], :diff=>vec[perm[1:len]])
    end

    @show sort_vec(real.(powersystems.V) - real.(matpower.V), size)
    @show sort_vec(imag.(powersystems.V) - imag.(matpower.V), size)
    @show sort_vec(real.(powersystems.gen) - real.(matpower.gen), size)
    @show sort_vec(imag.(powersystems.gen) - imag.(matpower.gen), size)
    @show sort_vec(real.(powersystems.load) - real.(matpower.load), size)
    @show sort_vec(imag.(powersystems.load) - imag.(matpower.load), size)
    println()
    @show sort_vec(abs.(powersystems.V - matpower.V), size)
    @show sort_vec(abs.(powersystems.gen - matpower.gen), size)
    @show sort_vec(abs.(powersystems.load - matpower.load), size)
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.V - matpower.V), xlabel = "Voltage"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.gen - matpower.gen), xlabel = "Generation"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.load - matpower.load), xlabel = "Load"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.V - matpower.V), xlabel = "Voltage"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.gen - matpower.gen), xlabel = "Generation"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.load - matpower.load), xlabel = "Load"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
end

function compare_from_to_loss(;fname = RTS_GMLC_MATPOWER_FILENAME)
    case = last(splitpath(dirname(fname)))
    powersystems = CSV.read(joinpath(ROOT, case, "results", "flow.csv"), DataFrame)
    matpower = CSV.read(joinpath(dirname(fname), "results" ,"flow.csv"), DataFrame)

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
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.from - matpower.from), xlabel = "From"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.to - matpower.to), xlabel = "To"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(histogram(abs.(powersystems.loss - matpower.loss), xlabel = "Loss"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.from - matpower.from), xlabel = "From"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.to - matpower.to), xlabel = "To"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
    display(boxplot(abs.(powersystems.loss - matpower.loss), xlabel = "Loss"))
    println(repeat(SEPARATOR, displaysize(stdout)[2]))
end

function gather_results(results, data)
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

    flow_names = ["line_name","bus_from","bus_to","P_from_to","Q_from_to","P_to_from","Q_to_from","P_losses","Q_losses"]
    flow_res = DataFrame(Dict(zip(flow_names, [[] for n in flow_names])))
    return Dict("bus_results" => df, "flow_results" => flow_res)
end

end # module
