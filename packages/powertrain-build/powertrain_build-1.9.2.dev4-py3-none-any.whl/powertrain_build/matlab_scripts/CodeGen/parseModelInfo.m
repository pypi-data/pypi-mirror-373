% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function [ output_args ] = parseModelInfo(rootFolder, model, cfgFolder)
    % parseModelInfo Extract unit-config data from model
    %
    % Parse the model and create a structure that can be used to create
    % a config file for the model.
    %
    % See also parseIncludeConfigs parseOutPorts parseInPorts parseCoreIdentifiers
    %          parseDIDs parseNVM parsePreProcBlks parseCalMeasData

    tic;
    load_system(model)
    % Trigger "update model" command.
    % This was added as a workaround for an inconsistent model.
    % TODO: Check if it is still needed.
    % set_param(model, 'SimulationCommand', 'Update');
    %
    root_subsystem = topLevelSystem(model);
    output_args = struct();

    % Version below should match the "config_version" of PyBuild, major must match.
    % If they don't match, this script (and more?) may require updates.
    output_args.version = '0.2.1';
    output_args.includes = parseIncludeConfigs(model, cfgFolder);
    output_args.integrity_level = getAsilClassification(rootFolder, model);
    output_args.outports = parseOutPorts(root_subsystem);
    output_args.inports = parseInPorts(root_subsystem);
    output_args.core = parseCoreIdentifiers(model);
    output_args.dids = parseDIDs(model);
    output_args.nvm = parseNVM(model);
    output_args.pre_procs = parsePreProcBlks(model);
    tmp=parseCalMeasData(model);
    output_args.local_vars = tmp.local_vars;
    output_args.calib_consts = tmp.calib_consts;
    toc
end
