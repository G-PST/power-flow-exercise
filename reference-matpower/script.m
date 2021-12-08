%  matlab /minimize /nosplash /nodesktop /r "filename='RTS-GMLC.m';script"

mpc = loadcase(filename); % loadcase in matpower
runpf(mpc, mpoption(), strrep(filename, '.m', '.log')); % runpf in matpower
