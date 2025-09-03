% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function TF = modelConfiguredForTL(rootFolder, modelFolder, modelName)
% Function that checks if model is configured for TargetLink
% rootFolder: The root folder of the project
% modelName: Name of model
% ssp: project name

    curr_dir = pwd;

    cd([rootFolder '/' modelFolder]);
    run(['./' modelName '_par.m']);
    load_system(modelName);

    TLDefineBlock = find_system(modelName, 'SearchDepth', 1, ...
        'Name', 'TargetLink Main Dialog');

    if isempty(TLDefineBlock)
        TF = false;
    else
        TF = true;
    end

    % Close system without saving
    close_system(modelName, 0)
    cd(curr_dir);
end
