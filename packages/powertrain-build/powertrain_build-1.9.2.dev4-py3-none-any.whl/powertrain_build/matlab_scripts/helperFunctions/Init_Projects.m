% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function ProjectInfo = Init_Projects(projectsPath, Models, ProjectInfo, baseName)
% INIT_PROJECTS Initialize projects related information.
if nargin < 3
	ProjectInfo = struct;
end
if nargin < 4
	baseName = '';
end

configFilePath = 'ConfigDocuments/matlab_script_config/PyBuild_config.json';
if isfile(configFilePath)
    projectNameConfig = loadjson(configFilePath);
    gitNames = fieldnames(projectNameConfig.project_name_replacements);
    svnNames = cellfun(@(x)(projectNameConfig.project_name_replacements.(x)), gitNames, 'UniformOutput', 0);
else
    warning('Found no config file: %s.', configFilePath)
    gitNames = {};
    svnNames = {};
end

projectFolders = dir(projectsPath);
for ProjectItem = projectFolders'
    if ~ProjectItem.isdir
        continue
    end
    if strcmp(ProjectItem.name(1),'.')
        continue
    end
    if endsWith(ProjectItem.folder, {'CSP', 'ZC'}) && strcmp(ProjectItem.name, 'ConfigDocuments')
        % Added a ConfigDocuments folder here. Not a project
        continue
    end
    if ismember(ProjectItem.name, {'CSP', 'ZC'})
		ProjectInfo = Init_Projects([ProjectItem.folder '/' ProjectItem.name], Models, ProjectInfo, [ProjectItem.name '_']);
        continue
    end
    projectName = [baseName ProjectItem.name];
    ProjectInfo.(projectName).Name = projectName;
    ProjectInfo.(projectName).InterfaceName = replace(projectName, gitNames, svnNames);
    ProjectInfo.(projectName).RootFolder = fullfile([ProjectItem.folder '/' ProjectItem.name]);
    ProjectInfo.(projectName).OutputFolder = fullfile([ProjectInfo.(projectName).RootFolder '/output']);
    ProjectInfo.(projectName).ConfigFile = fullfile([ProjectInfo.(projectName).RootFolder '/ProjectCfg.json']);
    ProjectInfo.(projectName).ProjectConfig = loadjson(ProjectInfo.(projectName).ConfigFile);
    ProjectInfo.(projectName).RasterFile = fullfile([ProjectInfo.(projectName).RootFolder '/conf.local/rasters.json']);
    ProjectInfo.(projectName).MaxRefreshRate = loadjson(ProjectInfo.(projectName).RasterFile);
    ProjectInfo.(projectName).IncludedFunctions = SetProjectTimeSamples(ProjectInfo.(projectName).MaxRefreshRate, Models);
    % Below should not be needed in the long run
    ProjectInfo.(projectName).A2lFileName = Get_A2L_File_Name(ProjectInfo.(projectName).ConfigFile);  % Used for LabelSplit
    ProjectInfo.(projectName).NewCoreIF = true;  % All projectd have "the new Core I/F". Used in checkscripts
    ProjectInfo.(projectName).CMT_enabled = true;  % Used in checkscripts and labelsplit
    ProjectInfo.(projectName).CMT_required = true;  % Used in checkscripts and labelsplit
    ProjectInfo.(projectName).IncludeVccSpVersion = true;
    ProjectInfo.(projectName).UseNVMStruct = true;
    ProjectInfo.(projectName).UpdateNVMStruct = true;
end
end

function a2LFileName = Get_A2L_File_Name(ConfigFile)
%GETA2LFILENAME Get the correct A2L file name of a given project.
    ProjectConfig = loadjson(ConfigFile);
    fullName = ProjectConfig.ProjectInfo.a2LFileName;
    name_parts = strsplit(fullName, '.');
    a2LFileName = name_parts{1};
end
