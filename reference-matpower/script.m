% matlab -nodisplay -nosplash -nodesktop -r "filename='RTS_GMLC/RTS_GMLC.m';script"

mpc = loadcase(filename); % loadcase in matpower
opt = mpoption();
opt.out.suppress_detail = 0;
[fPath, fName, fExt] = fileparts(filename);
log_file = fullfile(fPath, sprintf('%s.log', fName));
mat_file = fullfile(fPath, sprintf('%s.mat', fName));
savecase(mat_file, mpc);
fclose(fopen(log_file, 'w'));
res = runpf(mpc, opt, log_file); % runpf in matpower
result_mat = fullfile(fPath, 'results', sprintf('%s.mat', fName));
result_m = fullfile(fPath, 'results', sprintf('%s.m', fName));
savecase(result_mat, res);
savecase(result_m, res);
csvwrite('resline.csv', res.branch(res.branch(:,9)==0,:))
csvwrite('restrafo.csv', res.branch(res.branch(:,9)~=0,:))
csvwrite('resbus.csv', res.bus)
exit()
