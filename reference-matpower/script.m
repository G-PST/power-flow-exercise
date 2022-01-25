% matlab -nodisplay -nosplash -nodesktop -r "filename='RTS_GMLC/RTS_GMLC.m';script"

mpc = loadcase(filename); % loadcase in matpower
opt = mpoption()
opt.out.suppress_detail = 0
log_file = strrep(filename, '.m', '.log')
mat_file = strrep(filename, '.m', '.mat')
savecase(mat_file, mpc)
fclose(fopen(log_file, 'w'));
res = runpf(mpc, opt, log_file); % runpf in matpower
exit()
