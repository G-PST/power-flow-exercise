using CSV
using DataFrames

const BUS_DATA = readlines(joinpath(@__DIR__, "bus-data.out"))

const BRANCH_DATA = readlines(joinpath(@__DIR__, "branch-data.out"))

function parse_bus()
    data = BUS_DATA
    data = map(line -> strip(line), data)
    data = filter(line -> !(startswith(line, "Total: ") || startswith(line, "=") || startswith(line, "-") || startswith(line, "|")), data)
    headers1 = popfirst!(data)
    headers2 = popfirst!(data)
    bus_n_arr = Union{Int64}[]
    v_mag_arr = Union{Float64, Missing}[]
    v_ang_arr = Union{Float64, Missing}[]
    p_gen_arr = Union{Float64, Missing}[]
    q_gen_arr = Union{Float64, Missing}[]
    p_load_arr = Union{Float64, Missing}[]
    q_load_arr = Union{Float64, Missing}[]
    # λ_p_arr = Union{Float64, Missing}[]
    # λ_q_arr = Union{Float64, Missing}[]
    for (i, line) in enumerate(data)
        bus_n, v_mag, v_ang, p_gen, q_gen, p_load, q_load = map(x -> x === nothing ? missing : x, tryparse.(Float64, split(line)))
        # bus_n, v_mag, v_ang, p_gen, q_gen, p_load, q_load, λ_p, λ_q = map(x -> x === nothing ? missing : x, tryparse.(Float64, split(line)))
        push!(bus_n_arr, Int(bus_n))
        push!(v_mag_arr, v_mag)
        push!(v_ang_arr, v_ang === missing ? 0 : v_ang)
        push!(p_gen_arr, p_gen)
        push!(q_gen_arr, q_gen)
        push!(p_load_arr, p_load)
        push!(q_load_arr, q_load)
        # push!(λ_p_arr, λ_p)
        # push!(λ_q_arr, λ_q)
    end
    DataFrame([
        bus_n_arr,
        v_mag_arr,
        v_ang_arr,
        p_gen_arr,
        q_gen_arr,
        p_load_arr,
        q_load_arr,
        # λ_p_arr,
        # λ_q_arr,
    ], [:bus_n, :v_mag, :v_ang, :p_gen, :q_gen, :p_load , :q_load])
end

function parse_branch()
    data = BRANCH_DATA
    data = map(line -> strip(line), data)
    data = filter(line -> !(startswith(line, "Total: ") || startswith(line, "=") || startswith(line, "-") || startswith(line, "|")), data)
    headers1 = popfirst!(data)
    headers2 = popfirst!(data)
    branch_n_arr = Union{Int64}[]
    from_bus_inj_p_arr = Union{Float64, Missing}[]
    from_bus_inj_q_arr = Union{Float64, Missing}[]
    to_bus_inj_p_arr = Union{Float64, Missing}[]
    to_bus_inj_q_arr = Union{Float64, Missing}[]
    loss_p_arr = Union{Float64, Missing}[]
    loss_q_arr = Union{Float64, Missing}[]
    for (i, line) in enumerate(data)
        branch_n, from_bus_inj_p, from_bus_inj_q, to_bus_inj_p, to_bus_inj_q, loss_p, loss_q, = map(x -> x === nothing ? missing : x, tryparse.(Float64, split(line)))
        push!(branch_n_arr, Int(branch_n))
        push!(from_bus_inj_p_arr, from_bus_inj_p)
        push!(from_bus_inj_q_arr, from_bus_inj_q)
        push!(to_bus_inj_p_arr, to_bus_inj_p)
        push!(to_bus_inj_q_arr, to_bus_inj_q)
        push!(loss_p_arr, loss_p)
        push!(loss_q_arr, loss_q)
    end
    DataFrame([
        branch_n_arr,
        from_bus_inj_p_arr,
        from_bus_inj_q_arr,
        to_bus_inj_p_arr,
        to_bus_inj_q_arr,
        loss_p_arr,
        loss_q_arr,
    ], [:branch_n, :from_bus_inj_p, :from_bus_inj_q, :to_bus_inj_p, :to_bus_inj_q, :loss_p , :loss_q])
end

function main()
    mkpath(joinpath(@__DIR__, "results"))
    CSV.write(joinpath(@__DIR__, "results/bus.csv"), parse_bus())
    CSV.write(joinpath(@__DIR__, "results/flow.csv"), parse_branch())
    println("Output written to ", joinpath(@__DIR__, "results/"))
end

main()
