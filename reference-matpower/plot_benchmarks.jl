using CSV
using DataFrames
using UnicodePlots

function plot_benchmark(plt_data, case, step = "total")
    plt_data = plt_data[(plt_data.case .== case), names(plt_data) .!= "case"]
    if step == "total"
        plt_data = combine(groupby(plt_data,:package), "time (seconds)"=>sum, renamecols = false)
    else
        plt_data = plt_data[(plt_data.step .== step), names(plt_data) .!= "step"]
    end
    barplot(plt_data.package, plt_data[:,"time (seconds)"], title = step * " " * case)
end

data = CSV.read("../benchmark.csv", DataFrame)
for case in unique(data.case), step in  vcat(unique(data.step),"total")
    println("")
    show(plot_benchmark(data, case, step))
    println("")
end

