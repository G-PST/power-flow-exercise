using CSV
using DataFrames
using MAT

#bus_n,v_mag,v_ang,p_gen,q_gen,p_load,q_load
function parse_bus(filename)
    results = matread(filename)
    bus = results["mpc"]["bus"]
    gen = results["mpc"]["gen"]

    bus_df = DataFrame(bus[:, [1, 8, 9, 3, 4]], [:bus_n, :v_mag, :v_ang, :p_load, :q_load])
    gen_df = combine(
        groupby(DataFrame(gen[:, [1, 2, 3]], [:bus_n, :p_gen, :q_gen]), :bus_n),
        [:p_gen, :q_gen] .=> sum,
        renamecols = false,
    )
    leftjoin!(bus_df, gen_df, on = :bus_n)
    return bus_df
end

#branch_n,from_bus_index,to_bus_index,from_bus_inj_p,from_bus_inj_q,to_bus_inj_p,to_bus_inj_q,loss_p,loss_q
function parse_branch(filename)
    results = matread(filename)
    branch = results["mpc"]["branch"]
    bus = results["mpc"]["bus"]

    branch_df = DataFrame(
        branch[:, [1, 2, 14, 15, 16, 17]],
        [
            :from_bus_index,
            :to_bus_index,
            :from_bus_inj_p,
            :from_bus_inj_q,
            :to_bus_inj_p,
            :to_bus_inj_q,
        ],
    )
    branch_df.branch_n = 1:nrow(branch_df)
    loss = []
    #loss = baseMVA * abs(V(e2i(branch(:, F_BUS))) ./ tap - V(e2i(branch(:, T_BUS)))) .^ 2 ./ (branch(:, BR_R) - 1j * branch(:, BR_X));
    for b in eachrow(branch)
        tap = b[9] == 0.0 ? 1.0 : b[9]
        from_bus = findfirst(bus[:, 1] .== b[1])
        to_bus = findfirst(bus[:, 1] .== b[2])
        from_v = complex(bus[from_bus, 8], deg2rad(bus[from_bus, 9])) / tap
        to_v = complex(bus[to_bus, 8], deg2rad(bus[to_bus, 9]))
        push!(loss, results["baseMVA"] * abs(from_v - to_v)^2 / complex(b[3], -b[4]))
    end
    branch_df.loss_p = real.(loss)
    branch_df.loss_q = imag.(loss)

    return branch_df
end

function main()
    length(ARGS) == 0 && error("Must provide .mat file to parse.")
    res_dir = mkpath(joinpath(dirname(ARGS[1]), "results"))
    CSV.write(joinpath(res_dir, "bus.csv"), parse_bus(ARGS[1]))
    CSV.write(joinpath(res_dir, "flow.csv"), parse_branch(ARGS[1]))
    println("Output written to ", res_dir)
end

main()
