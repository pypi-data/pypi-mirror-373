% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function res = generateTLUnit(RootFolder, model, SSP)
%Generates c and config files for a unit based on a TL-model
    %TODO: Why does this generate TLSim and sfunctions?
    commonFolder = [RootFolder '/Models/Common/pybuild_src'];
    % TODO: When we deploy pybuild we should replace Common/pybuild_src with Common
    % TODO: Write a matlab config reader to get these values
    baseFolder = [RootFolder '/Models/' SSP '/' model];
    srcFolder = [baseFolder '/pybuild_src'];
    srcFolderTmp = [srcFolder '/Tmp'];
    cfgFolder = [baseFolder '/pybuild_cfg'];
    tmpMdlFolder = [baseFolder '/tmpMdl'];

    %run par file again, just to be sure the set values are used
    global Vc;
    oldVc = Vc;
    par_f_path = [model '_par.m'];
    run(par_f_path);
    if ~isequal(oldVc, Vc)
        warning('Vc has been updated.')
    end

    %create folders if they are missing
    folders = {srcFolder srcFolderTmp cfgFolder tmpMdlFolder commonFolder};
    for i=1:length(folders)
        folder = folders{i};
        % isdir check needed, rmdir may fail due to permissions
        if ~isdir(folder)
            mkdir(folder);
        end
        fprintf('Created folder %s\n', folder);
    end

    % Add matlab_src and c_src folders to the path if they exist
    matlabSrcFldr = [baseFolder '/matlab_src'];
    if isdir(matlabSrcFldr)
        addpath(matlabSrcFldr)
    end
    cSrcFldr = [baseFolder '/c_src'];
    if isdir(cSrcFldr)
        addpath(cSrcFldr)
        fprintf('\nCopy c_src files to src folder\n');
        copyfile([cSrcFldr '/*.*'], srcFolder);
    end

    % Load libraries
%    block_libraries = dir(include_folder, '**\*.slx');
%    for i=1:length(block_libraries)
%        block_library = block_libraries(i);
%        load_system(block_library.name);
%    end


    %diary([baseFolder '/' model '.log']);
    fp= fopen([baseFolder '/' model '.log'], 'w');
    unitCfg = [cfgFolder '/config_' model '.json'];
    fprintf('\nStart generation of temporary unitCfg %s for model %s\n', unitCfg, model);
    info = parseModelInfo(RootFolder, model, cfgFolder);
    struct2JSON(info, unitCfg);
    fprintf('\nFinished generation of temporary unitCfg for model %s\n', model);

    % Do this in better way to control where the model is stored
    fprintf('\nStart temp model generation for model %s\n', model);
    load_system(model)
    tmpMdl = [model '_OPortMvd'];
    save_system(model, [tmpMdlFolder '/' tmpMdl '.mdl']);
    subsystem = regexprep(model, '([A-Za-z0-9]+)(__\w+){0,1}','$1');
    moveDefOutports([tmpMdl '/' subsystem '/Subsystem/' subsystem]);
    configSet = getActiveConfigSet(tmpMdl);
    % Set sample times to a constant, to avoid problems when the ts
    % variable for the model isn't set (happens as this script is run
    % over all models, not only the ones currently in the project)
    set_param(configSet, 'SolverType', 'Fixed-step');
    set_param(configSet, 'FixedStep', '0.01');
    fnc_g = find_system(tmpMdl, 'FindAll', 'on', 'LookUnderMasks', 'all', ...
                        'SearchDepth', '1', ...
                        'MaskType', 'Function-Call Generator');
    set_param(fnc_g, 'sample_time', '0.01');
    fprintf('\nFinished temp model generation for model %s\n', model);

    %Generate code
    currDir = pwd;
    cd(srcFolderTmp);
    MILSystem=find_system(get_param(tmpMdl, 'handle'), 'lookundermasks', 'on', 'tag', 'MIL Subsystem');
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%% TL has a name length limitation on define file names (10 chars).
    %%% Define special IDs for debug models such that their
    %%% tl_defines_-files get unique names and don't overwrite each other.
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    CurrentFunctionName = model;
    CodeGenConfigPath = [RootFolder '/ConfigDocuments/matlab_script_config/CodeGen_config.json'];
    if isfile(CodeGenConfigPath)
        CodeGenConfig = loadjson(CodeGenConfigPath);
        ProblemModels = CodeGenConfig.problem_models_id_map;
    else
        warning('Found no config file: %s.', CodeGenConfigPath)
        ProblemModels = struct();
    end

    if isfield(ProblemModels, CurrentFunctionName)
        ModelID = ProblemModels.(CurrentFunctionName);
        warning('There are multiple models with the same ID (character 3-12 of the model name)')
        ModelsString = join(fieldnames(ProblemModels), ', ');
        disp(['This is one of: ' ModelsString{1}])
    else
        ModelID = CurrentFunctionName(3:min(end,12));
    end
    set_tlsystemID(MILSystem, ModelID);

    % Default code generation settings
    tl_set(...
        tmpMdl, ...
        'codeopt.cleancode', 1, ...
        'codeopt.sections', 1, ...
        'codeopt.optimization', 1, ...
        'codeopt.sfbitfields', 1, ...
        'codeopt.globalbitfields', 0, ...
        'codeopt.optimizedbooltype', 1, ...
        'codeopt.functionsfor64bitops', 0, ...
        'codeopt.limidentlength', 1, ...
        'codeopt.noinitstozero', 0, ...
        'codeopt.sharefunctions', 1 ...
    );

    % Custom code generation settings
    CCodeStyleSheetPath = [RootFolder '/ConfigDocuments/TL4_3_settings/CodeConfig/cconfig.xml'];
    if exist(CCodeStyleSheetPath, 'file')
        fprintf('\nUsing custom C code style sheet %s\n', CCodeStyleSheetPath);
        tl_set(tmpMdl, 'codeopt.outputstylefile', CCodeStyleSheetPath);
    end

    fprintf('\nStart code generation of %s\n', tmpMdl);
    warning('off', 'all')
    ds_error_set('BatchMode', 'on');
    ds_error_display('PrintMessage','off');
    ds_error_set('DefaultExcludedMessages', [17291 17001 17218 20281 19611 15229 15365 19001 15550]);
    tl_generate_code('Model', tmpMdl, 'SimMode', 'none')
    warning('on', 'all')
    ds_error_set('BatchMode', 'off');
    % print to stdout so the errors are displayed in the diary
    msgs = ds_error_get('AllMessages');
    for i=1:length(msgs)
        msg = msgs(i);
        fprintf(fp, '%s(%d) = %s\n',msg.type,msg.number,msg.msg);
    end
    if tl_error_check
        close_system(tmpMdl, 1);
        close_system(model, 0);
        error('Errors detected');
    end


    fprintf('\nFinished code generation of %s\n', tmpMdl)
    % print all messages
    chdir(srcFolder);
    A2lStylesheetName = [RootFolder '/ConfigDocuments/a2l_export_nd.xsl'];
    Generate_A2L(tmpMdl, A2lStylesheetName, '');
    close_system(tmpMdl, 1);
    process_generated_code(commonFolder, srcFolderTmp, srcFolder, subsystem, tmpMdl, model)
    fprintf('\nStart updating unitCfg %s based on generated code', unitCfg);
    updateCodeSwConfig(RootFolder, [baseFolder '/' model '.mdl'])
    fprintf('\nFinished updating unitCfg %s based on generated code', unitCfg);
    fclose(fp);
    close_system(model, 0);
    chdir(currDir);
end

function process_generated_code(commonFolder, srcFolderTmp, srcFolder, subsystem, tmpMdl, model)
    force_movefile = 'f';
    force_rmdir = 's';
    subsystem = regexprep(model, '([A-Za-z0-9]+)(__\w+){0,1}','$1');
    generated_files = dir([srcFolderTmp '/TLProj/' subsystem '/*.*']);
    for generated_file = generated_files'
        file_path = [generated_file.folder '/' generated_file.name];
        if isdir(file_path)
            disp([file_path ' is a directory. Skipping.'])
        elseif isfile([commonFolder '/' generated_file.name])
            disp([file_path ' is a common file. Skipping.'])
        elseif strcmp(generated_file.name, 'a2lexport.log')
            disp([file_path ' is a log file. Skipping.'])
        else
            post_process_source_file(file_path)
            if is_common_name(generated_file)
                disp(['Moving from ' file_path ' to ' commonFolder])
                movefile(file_path, commonFolder, force_movefile);
            else
                disp(['Moving from ' file_path ' to ' srcFolder])
                movefile(file_path, srcFolder, force_movefile);
            end
        end
    end
    fprintf('\nMoved src code to %s\n', srcFolder);
    %TODO: remove the A2L-generation log & dd files
    rmdir(srcFolderTmp, force_rmdir);
    movefile([srcFolder '/' tmpMdl '.a2l'], [srcFolder '/' model '.a2l'], force_movefile);
end

function post_process_source_file(file_path)
    disp('Starting source file post-process')
    file_contents = fileread(file_path);
    post_process_functions = {@remove_unsupported_comments};
    for function_index = 1:length(post_process_functions)
        file_contents = post_process_functions{function_index}(file_contents);
    end
    disp(['Updating file contents of file: "' file_path '"'])
    write_file(file_path, file_contents)
end

function updated_file_content = remove_unsupported_comments(file_content)
    disp('Replacing C++ style comments "//" with C style comments "/**/" for Green Hills compatibility')
    file_lines = splitlines(file_content);
    expression = '//(.*)$';
    replace_with = '/*$1*/';
    updated_file_lines = regexprep(file_lines, expression, replace_with);
    updated_file_content = strjoin(updated_file_lines, newline);
end

function write_file(file_path, file_content)
    file_id = fopen(file_path, 'w');
    fprintf(file_id, '%s\n', file_content);
    fclose(file_id);
end

function common = is_common_name(generated_file)
    % common = is_common(generated_file)
    %
    % Check if the file should be located in the common folder
    common = false;
    % TODO: Find more common files and add to this function
    if strncmp(generated_file.name, 'Tab', 3)
        common = true;
    elseif strcmp(generated_file.name, 'tl_basetypes.h')
        common = true;
    elseif strcmp(generated_file.name, 'tl_types.h')
        common = true;
    end
end
