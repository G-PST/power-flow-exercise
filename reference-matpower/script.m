% matlab -nodisplay -nosplash -nodesktop -r "filename='RTS_GMLC.m';script"

mpc = loadcase(filename); % loadcase in matpower
runpf(mpc, mpoption(), strrep(filename, '.m', '.log')); % runpf in matpower
exit()
