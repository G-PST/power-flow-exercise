module PowerModelsExample

using PowerSystems
using PowerModels
using PowerModelsInterface
using CSV
using Pkg.Artifacts
using Logging
using DataFrames
using Statistics
using UnicodePlots
using Ipopt

const RTS_GMLC_MATPOWER_FILENAME = joinpath(artifact"matpower", "RTS_GMLC.m")
const ROOT = dirname(@__DIR__)

export solve
export output
export compare_v_gen_load
export compare_from_to_loss


function solve()
    data = PowerModels.parse_file(RTS_GMLC_MATPOWER_FILENAME)
    results = run_ac_pf(data, Ipopt.Optimizer)
    (results, data)
end

function output(results, data)
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
        p_gen_arr[i] = x
    end

    map(gen_n_arr) do b
        x = results["solution"]["gen"][string(b)]["qg"]
        b = data["gen"][string(b)]["gen_bus"]
        i = only(findall(x -> x==b, bus_n_arr))
        q_gen_arr[i] = x
    end

    load_n_arr = sort(parse.(Int, keys(data["load"])))

    p_load_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))
    q_load_arr = Vector{Union{Missing, Float64}}(missing, length(bus_n_arr))

    map(load_n_arr) do b
        x = data["load"][string(b)]["pd"]
        b = data["load"][string(b)]["load_bus"]
        i = only(findall(x -> x==b, bus_n_arr))
        p_load_arr[i] = x
    end

    map(load_n_arr) do b
        x = data["load"][string(b)]["qd"]
        b = data["load"][string(b)]["load_bus"]
        i = only(findall(x -> x==b, bus_n_arr))
        q_load_arr[i] = x
    end


    df = DataFrame([
        bus_n_arr,
        v_mag_arr,
        v_ang_arr,
        p_gen_arr,
        q_gen_arr,
        p_load_arr,
        q_load_arr,
        # λ_p_arr,
        # λ_q_arr,
    ], [:bus_n, :v_mag, :v_ang, :p_gen, :q_gen, :p_load, :q_load])

    CSV.write(joinpath(@__DIR__, "../results/bus.csv"), df)
    nothing
end



end # module
