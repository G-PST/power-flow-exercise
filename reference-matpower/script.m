% matlab -nodisplay -nosplash -nodesktop -r "filename='RTS_GMLC/RTS_GMLC.m';script"

addpath('~/matpower');
install_matpower(1, 0, 0);

tt = tic
fprintf("Load...")
lt = tic
mpc = loadcase(filename); % loadcase in matpower
load_time = toc(lt)
opt = mpoption();
opt.out.suppress_detail = 0;
[fPath, fName, fExt] = fileparts(filename);
log_file = fullfile(fPath, sprintf('%s.log', fName));
mat_file = fullfile(fPath, sprintf('%s.mat', fName));
savecase(mat_file, mpc);
fclose(fopen(log_file, 'w'));
fprintf("Solve...")
st = tic
res = runpf(mpc, opt, log_file); % runpf in matpower
solve_time = toc(st)
res.losses = get_losses(res);
result_mat = fullfile(fPath, 'results', sprintf('%s.mat', fName));
result_m = fullfile(fPath, 'results', sprintf('%s.m', fName));
fprintf("Output...")
savecase(result_mat, res);
savecase(result_m, res);
ot = tic
csvwrite(fullfile(fPath, 'results', 'resline.csv'), res.branch(res.branch(:,9)==0,:))
csvwrite(fullfile(fPath, 'results','restrafo.csv'), res.branch(res.branch(:,9)~=0,:))
csvwrite(fullfile(fPath, 'results','resbus.csv'), res.bus)
output_time = toc(ot)
total_time = toc(tt)

fprintf('Load: %s \n', load_time)
fprintf('Solve: %s \n', solve_time)
fprintf('Output: %s \n', output_time)
fprintf('Total: %s \n', total_time)
exit()
