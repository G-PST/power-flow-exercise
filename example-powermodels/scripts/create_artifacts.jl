using Pkg
using Pkg.Artifacts

artifacts_toml = joinpath(dirname(@__DIR__), "Artifacts.toml")

label = "matpower"
filename = "RTS_GMLC.m"
url = "https://raw.githubusercontent.com/GridMod/RTS-GMLC/v0.2.1/RTS_Data/FormattedData/MATPOWER/RTS_GMLC.m"

data_hash = artifact_hash(label, artifacts_toml)

if data_hash == nothing || !artifact_exists(data_hash)
    matpower_file = download(url, @__DIR__() * "/" * filename)
    hash_artifact = create_artifact() do artifact_dir
        cp(matpower_file, joinpath(artifact_dir, filename))
    end
    matpower_file_hash = archive_artifact(hash_artifact, joinpath(matpower_file))
    bind_artifact!(artifacts_toml, label, hash_artifact,
                   download_info = [ (url, matpower_file_hash) ], lazy=true, force=true)
    rm(matpower_file)
end
