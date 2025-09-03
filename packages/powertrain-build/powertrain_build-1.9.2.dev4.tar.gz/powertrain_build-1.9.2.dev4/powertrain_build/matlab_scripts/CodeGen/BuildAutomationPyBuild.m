% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Author: Henrik Wahlqvist
% Date: 31-01-2019
% Purpose: This is for automatically generating c-files from MATLAB models.
% This program can also be used as daily PyBuild code generation.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function BuildAutomationPyBuild(mode, exitOnFailure, modelList)
    try
        addpath(genpath([pwd '/Projects']));
        addpath(genpath([pwd '/matlab-scripts']));

        initFile = 'Init_PyBuild(false);';
        disp(['Running init file: ' initFile])
        evalin('base', initFile);

        %Update all models unless a list is provided:
        if ~exist('modelList', 'var')
            disp('Updating all models...');
            modelList = gatherAllModels();
        end

        updateModels(mode, pwd, modelList);
        disp('Done.');

    catch err
        disp(getReport(err))
        if exitOnFailure
            quit force;
        end
    end
    if exitOnFailure
        exit;
    end
    bdclose Vcc_Lib;
end

function models = gatherAllModels()
% Function for gathering all models in the repo.
    startdir = pwd;
    models = {};
    modelsFolder = [startdir '/Models/'];
    env_ssp = getenv('SSP');
    if isempty(env_ssp)
        disp('ALL models')
        ssps = dir([modelsFolder '*']);
    else
        ssp_dir = [modelsFolder env_ssp '*']
        disp(['All models in ' ssp_dir])
        ssps = dir(ssp_dir);
    end

    for i=1:length(ssps)
        if ~ssps(i).isdir
            continue;
        end
        ssp = ssps(i).name;
        currSspFolder = [modelsFolder ssp '/'];
        cd(currSspFolder)
        modelsInSsp = dir('Vc*');
        for j=1:length(modelsInSsp)
            % Make sure it is a directory
            if ~modelsInSsp(j).isdir
                continue;
            end
            model = modelsInSsp(j).name;
            % Make sure the directory contains an .mdl file
            if isfile([model '/' model '.mdl'])
                models = [models ['Models/' ssp '/' model '/' model '.mdl']];
            end
        end
        cd(startdir);
    end
end
