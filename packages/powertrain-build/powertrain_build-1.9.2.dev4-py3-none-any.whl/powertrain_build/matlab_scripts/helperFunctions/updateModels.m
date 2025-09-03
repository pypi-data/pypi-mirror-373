% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function errorOccurred = updateModels(mode, rootFolder, modelList)
    bdclose('all')
    evalin('base', 'global Vc');
    global Vc;
    startdir = pwd;
    % Load nvmram lists
    nvmStructs = [rootFolder '/Projects/*/conf.local/nvm_structs.json'];
    NVMData = struct();
    for file=dir(nvmStructs)'
        disp(['Loading NVM data from ' file.folder]);
        tmp_nvm=loadjson(fullfile(file.folder, file.name));
        for block=tmp_nvm
            if ~isempty(block(1).signals)
                for var=block(1).signals
                    NVMData.(var(1).name) = var(1);
                end
            end
        end
    end

    tlmodels = false;
    for i=1:length(modelList)
        [modelFolder, modelName, ~] = fileparts(modelList{i});
        % Check if model is configured to use TargetLink or not.
        isTLModel = modelConfiguredForTL(rootFolder, modelFolder, modelName);
        % Save if any of the models was a TargetLink model
        tlmodels = tlmodels || isTLModel;
    end

    % Load par-files, add *Const manually if not already in the list
    % This is required since they can contain constants used by other models
    modelListPar = modelList;
    if all(cellfun(@isempty, regexp(modelList,'Models/Common/\w*Const/\w*Const.mdl','match'))) 
        commonConstModels = dir('Models/Common/*Const/*Const.mdl');
        for i=1:length(commonConstModels)
            modelName = [commonConstModels(i).folder '/' commonConstModels(i).name]
            modelListPar = [{strrep(modelName, rootFolder, "")}, modelListPar];
        end
    end

    for i=1:length(modelListPar)
        [modelFolder, modelName, ~] = fileparts(modelListPar{i});
    end

    for i=1:length(modelListPar)
        [modelFolder, modelName, ~] = fileparts(modelListPar{i});
        modelFolder = strip(convertStringsToChars(modelFolder), '\');
        par_f_path = strip(join([modelFolder '\' modelName '_par.m'],''), '\');
        if ~isfile(par_f_path)
            error('Invalid par file path: "%s"', par_f_path);
        end

        % Set all model sample times to 0.01
        clear tmp; % tmp is used by many par_files, and not always cleaned up
        run(par_f_path);
        tok = regexp(modelName, '([A-Z]\w*?)([A-Z]\w*?)([A-Z]\w*?){0,1}(?:__.*?){0,1}$','tokens');
        if ~isempty(tok{1}{3})
            Vc.(tok{1}{2}).(tok{1}{3}).ts = 0.01;
        else
            Vc.(tok{1}{2}).ts = 0.01;
        end
        disp(['Loaded: ' par_f_path])
        cd(startdir);
    end

    % Update the model and generate code
    errorOccurred = false;
    interfaceSignals = getInterfaceSignals(rootFolder);
    for i=1:length(modelList)
        cd(startdir);
        if ~isfile(modelList{i})
            error('Invalid model path: "%s"', modelList{i});
        end

        [modelFolder, modelName, ~] = fileparts(modelList{i});
        cd([rootFolder '/' modelFolder]);

        % Would like to avoid this duplication, but not sure how.
        ssp = strsplit(modelList{i}, '/');
        % SSP is desired in the path "Models/<SSP>/<MODEL>/<MDL.mdl>, hence end-2.
        ssp = ssp(end-2);
        ssp = ssp{1};
        disp(ssp)

        isTLModel = modelConfiguredForTL(rootFolder, modelFolder, modelName);

        fprintf('\nStart generation of unitCfg for model %s\n', modelName);
        try
            fprintf('\nrootFolder: %s, modelName: %s, ssp: %s\n', rootFolder, modelName, ssp);

            switch mode
                case 'update'
                    disp(['Updating: ' modelName]);
                    updateModel(rootFolder, modelName, ssp, NVMData, interfaceSignals);
                case 'codegen'
                    disp(['Generating: ' modelName]);
                    if isTLModel
                        if ~exist('dsdd_manage_project', 'file')
                            error('TargetLink not installed. Cannot generate code for models configured with TargetLink');
                        end
                        generateTLUnit(rootFolder, modelName, ssp);
                    else
                        generateECUnit(rootFolder, modelName, ssp)
                    end
                otherwise
                    fprintf('\n Unsupported mode: %s\n', mode);
                    errorOccurred = true;
                    break;
            end
        catch err
            fprintf('\nError: %s\n', err.getReport());
            errorOccurred = true;
        end

        fprintf('\nFinished generation of unitCfg for model %s\n', modelName);
        cd(startdir);
    end

    if tlmodels
        % Throw away any local changes to DD0
        dsdd('Close', 'save', 0);
    end

    % Add final success message if no errors occurred
    if ~errorOccurred
        fprintf('\n%s\n', 'Matlab task succeeded!');
    end
end
