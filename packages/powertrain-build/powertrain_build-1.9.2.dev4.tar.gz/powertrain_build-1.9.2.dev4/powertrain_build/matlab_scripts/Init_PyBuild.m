% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function [Models, Projects, QuantityUnitList] = Init_PyBuild(interactiveMode)
% Default is interactiveMode
if ~exist('interactiveMode', 'var')
    interactiveMode = true;
end
disp('Starting Init_Pybuild')
Clear_Base();
Remove_Old_Paths();
a = mfilename('fullpath');
b = mfilename;
fileFolder = a(1:length(a)-length(b));
cd(fileFolder);
cd('..'); % To remove .. from the path to folders we can change directory first
Add_Paths(pwd);

% Find dd file and set it as the project file
addpath('ConfigDocuments');
dd_file = dir('ConfigDocuments\*.dd');
dsdd_manage_project('SetProjectFile', dd_file(1).name);

tl_pref('set', 'projectfileautosave', 'off');
% Init Pybuild
disp('Initializing powertrain-build')
Models = Init_Models('Models');
Projects = Init_Projects('Projects', Models);
QuantityUnitList = Read_Units();

% Start the GUI
if interactiveMode
    disp('Starting GUI')
    evalin('base', 'global Vc');
    PyBuild_Manager(Models, Projects, QuantityUnitList);
end

% declare global variables for dependency scripts
% used by powermill_cli to be remove later
global ModelsInfo
global ProjectInfo
ProjectInfo = Projects;
ModelsInfo = Models;

end

function Clear_Base()
%CLEAR_BASE Clear workspace, close systems, close figures, clear command.
clearvars -global all
clear all;
close all;
bdclose all;
end

function Remove_Old_Paths()
%REMOVE_OLD_PATHS() Remove old folder paths from Matlab path, which are used in this script
AllPaths = path;
LineBreaks = strfind(AllPaths,';');

for i = 1:length(LineBreaks)
    if i == 1
        CurrentPath = AllPaths(1:LineBreaks(1)-1);
    else
        CurrentPath = AllPaths(LineBreaks(i-1)+1:LineBreaks(i)-1);
    end
    if contains(CurrentPath, '\ConfigDocuments') ||...
            contains(CurrentPath, '\Documents') ||...
            contains(CurrentPath, '\matlab-scripts\') ||...
            contains(CurrentPath, '\pytools\') ||...
            contains(CurrentPath, '\Script\')
        rmpath(CurrentPath)
    end
end
end

function Add_Paths(RepoRootFolder)
% Add required folder paths
disp(['Adding paths from ' RepoRootFolder])
ConfigDocumentsFolder = [RepoRootFolder '\ConfigDocuments'];
DocumentsFolder = [RepoRootFolder '\Documents'];
ModelsFolder = [RepoRootFolder '\Models'];
MatlabScriptsFolder = [RepoRootFolder '\matlab-scripts'];
ScriptFolder = [RepoRootFolder '\Script'];
addpath(ConfigDocumentsFolder);
addpath(DocumentsFolder);
addpath(ModelsFolder);
addpath([ModelsFolder '/Common']);
addpath([ModelsFolder '/Common/VcEnumDefinitions']);
addpath(genpath(MatlabScriptsFolder));
addpath(genpath(ScriptFolder));
end
