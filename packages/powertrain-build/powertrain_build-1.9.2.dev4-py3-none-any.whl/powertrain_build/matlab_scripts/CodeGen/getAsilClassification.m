% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function level = getAsilClassification(rootFolder, model)
% Function which defines the ASIL level given a model.
% Specific ASIL levels must be specified in a configuration file.
% rootFolder: The root folder of the project.
% model: Model name.

    % Struct which defines the ASIL level for dependability models.
    % These models will be converted to use TL ASIL classes, in order
    % to allocate them to the correct memory area.
    codeGenConfigPath = [rootFolder '/ConfigDocuments/matlab_script_config/CodeGen_config.json'];
    if isfile(codeGenConfigPath)
        CodeGenConfig = loadjson(codeGenConfigPath);
        depMdls = CodeGenConfig.dependability_model_asil_class;
    else
        warning('Found no config file: %s.', codeGenConfigPath)
        depMdls = struct();
    end

    model_wo_suffix = regexprep(model, '(\w+)__.*', '$1');
    if isfield(depMdls, model_wo_suffix)
        level = depMdls.(model_wo_suffix);
    else
        level = 'QM';
    end
end
