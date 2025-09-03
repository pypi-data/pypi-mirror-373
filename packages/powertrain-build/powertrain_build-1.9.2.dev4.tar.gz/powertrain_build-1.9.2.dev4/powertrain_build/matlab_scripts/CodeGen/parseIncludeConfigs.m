% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function includeConfigs = parseIncludeConfigs(model, cfgFolder)
    % parseIncludeConfigs Create include section for configs
    %
    % Look in the config folder for related configs.
    % This is used for models with handwritten c-code,
    % where the c-code handles nvm-signals, calibration, etc.
    %
    % See also parseModelInfo
    includeConfigs = {};
    if nargin<1
        return
    end

    json_files = dir([cfgFolder '/config_*.json']);
    for json_file=json_files'
        if strcmp(['config_' model '.json'], json_file.name)
            continue
        end
        include_start = length('config_') + 1;
        include_end = length('.json');
        includeConfigs{end+1} = json_file.name(include_start:end-include_end);
    end
