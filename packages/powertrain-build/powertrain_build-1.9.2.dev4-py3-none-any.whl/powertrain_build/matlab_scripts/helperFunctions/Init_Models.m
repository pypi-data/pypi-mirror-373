% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function [Models] = Init_Models(modelsFolder)
Models = struct;
SspFolders = dir(modelsFolder);
for SspEntry=SspFolders'
    SspName = SspEntry.name;
    if SspName(1) == '.'
        continue
    end
    if ~SspEntry.isdir
        continue
    end
    Models = FindSspModels([SspEntry.folder '/' SspEntry.name], Models, SspEntry.name);
end
end

function Models = FindSspModels(sspDirectory, Models, SspName)
SspDirContent = dir([sspDirectory '/Vc*']);
for ModelDir=SspDirContent'
    if ~ModelDir.isdir
        continue
    end
    ModelFiles = FindModelFiles(sspDirectory, ModelDir.name);
    if ~isempty(fieldnames(ModelFiles))
        Models.(ModelDir.name) = ModelFiles;
        Models.(ModelDir.name).Ssp = SspName;
    end
end
end

function ModelInfo = FindModelFiles(sspDirectory, modelName)
% Search for all available files in directoryName
% Add model path from release folder selected in ReleaseSwitch
ModelDirContent = dir([sspDirectory '/' modelName]);
ModelInfo = struct;
for ModelDirEntry = ModelDirContent'
    ModelFileName = ModelDirEntry.name;
    fullPath = [ModelDirEntry.folder filesep ModelDirEntry.name];
    if strcmp(ModelDirEntry.name, [modelName '.mdl'])
        % Model file found
        ModelInfo.modelFilePath = fullPath;
    elseif strcmp(ModelDirEntry.name, [modelName '_par.m'])
        % par file found
        ModelInfo.parFilePath = fullPath;
        % Do nothing, m file found
    elseif strcmp(ModelDirEntry.name, [modelName '_sgp.xml'])
        ModelInfo.sgpFilePath = fullPath;
    elseif ModelDirEntry.isdir
        % Model folder found
        if strcmp(ModelDirEntry.name, 'matlab_src')
            ModelInfo.matlabSrcPath = fullPath;
        elseif strcmp(ModelDirEntry.name, 'c_src')
            ModelInfo.cSrcFiles = FindCSourceFiles(fullPath);
        end
    end
end
% Add system name
if ~isempty(fieldnames(ModelInfo))
    ModelInfo.SystemName = Strip_Suffix(modelName);
    ModelInfo.FullModelName = modelName;
    % Getting the tl_subsystem for all models is too slow. Do it when
    % needed.
    % Stub for the time being
    ModelInfo.CurrentSystem = false;
end
end

function cSrcFiles = FindCSourceFiles(cSrcPath)
    cSrcFiles = {};
    cSrcDirFiles = dir(cSrcPath);
    for cSrcFile = cSrcDirFiles'
        if ~isempty(regexpi(cSrcFile.name, '\.(c|h|a2l)', 'match'))
            cSrcFiles{end+1} = [cSrcFile.folder '/' cSrcFile.name];
        end
    end
end
