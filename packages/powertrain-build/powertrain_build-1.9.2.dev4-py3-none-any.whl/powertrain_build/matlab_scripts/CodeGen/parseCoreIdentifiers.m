% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function apiData = parseCoreIdentifiers(model)
% parseCoreIdentifiers Find all Core Identifier blocks in model
% returns a structs with identifier information
%
% See also parseModelInfo

    apiData = struct();
    % Which types of identifier shall be search for
    id_names = {'Events', 'IUMPR', 'FIDs', 'Ranking', 'TstId','TstId','Ranking'};
    idFilenames = {'CoreIdNameDefinition_EventIDs.csv',
                          'CoreIdNameDefinition_IUMPR.csv',
                          'CoreIdNameDefinition_FunctionIDs.csv',
                          'CoreIdNameDefinition_Ranking.csv',
                          'CoreIdNameDefinition_Mode$06.csv',
                          'CoreIdNameDefinition_Mode$06.csv',
                          'CoreIdNameDefinition_Ranking.csv'};
    id_names2Filenames = containers.Map(id_names, idFilenames);
    % The name of the blocks using the above identifiers
    blk_names = {'^Dem_SetEvent.*', '^Dem_RepIUMPR.*', '^FiM_GetFunction.*', ...
        '^bdcore_RVLG_SetRV.*', '^bdsrv_S06_SetTestResult.*', ...
        '^(Vcc|Dem)_SetDTR', '^(Vcc|Vc)_SetRanking'};
    % Which port of the block is the identifier connected to
    blk_port_nbr = [1,1,1,1,1,1,1];
    %which block data shall be stored per block.
    info = {'description', 'type', 'unit', 'offset', 'lsb', 'min', 'max', 'class'};

    for blk_type_idx=1:length(id_names)
        % remove name search once all Core blocks are replaced with ones
        % with correct mask names!
        name_search = find_system(model, 'FindAll', 'on', 'RegExp', 'on', 'LookUnderMasks', 'all', 'blocktype', 'SubSystem', 'Name', blk_names{blk_type_idx});
        msk_search = find_system(model, 'FindAll', 'on', 'RegExp', 'on', 'LookUnderMasks', 'all', 'MaskType', blk_names{blk_type_idx});
        search = union(name_search, msk_search);
        if ~isfield(apiData, id_names{blk_type_idx})
            apiData.(id_names{blk_type_idx}) = struct();
        end
        for i=1:length(search)
            %Find source block for EventID
            ports = get_param(search(i), 'PortHandles');
            l_h = get(ports.Inport(blk_port_nbr(blk_type_idx)), 'line');
            blk_h = get_param(l_h,'SrcBlockHandle');
            block_name = get_blk_name(model, blk_h);
            if ~isempty(block_name)
                %TODO: g�r API_blk till en cell array av structar
                api_blk_tmp = [get_param(search(i), 'Parent') '/' get_param(search(i), 'Name')];
                tmpStruct.path = api_blk_tmp;
                tmpStruct.config = getCodeSwitches(api_blk_tmp);
                if isfield(apiData.(id_names{blk_type_idx}), block_name)
                    apiData.(id_names{blk_type_idx}).(block_name).API_blk = [apiData.(id_names{blk_type_idx}).(block_name).API_blk ...
                                                                             tmpStruct];
                else
                    %APIData.(id_names{blk_type_idx}).(block_name) = struct();
                    apiData.(id_names{blk_type_idx}).(block_name).API_blk{1} = tmpStruct;
                end
                %Get targetlink block data
                apiData.(id_names{blk_type_idx}).(block_name).blk_name = get(blk_h, 'name');
                apiData.(id_names{blk_type_idx}).(block_name).subsystem = get(blk_h, 'parent');
                apiData.(id_names{blk_type_idx}).(block_name).API_blk_type = get(search(i), 'MaskType');
                for idx=1:length(info)
                    if strcmp(info{idx}, 'description')
                        apiData.(id_names{blk_type_idx}).(block_name).(info{idx}) = getCsvDescription(block_name, id_names2Filenames(id_names{blk_type_idx}));
                    else
                        apiData.(id_names{blk_type_idx}).(block_name).(info{idx}) = chkNan(tl_get(blk_h, ['output.' info{idx}]));
                    end
                end
            else
                disp(['Warning: model ' model ' contains illegal identifier blocks']);
                if isfield(apiData.(id_names{blk_type_idx}), 'IllegalBlk')
                    apiData.(id_names{blk_type_idx}).IllegalBlk.API_blk = [apiData.(id_names{blk_type_idx}).IllegalBlk.API_blk...
                                                                            {[get_param(search(i), 'Parent') '/' get_param(search(i), 'Name')]}];
                else
                    apiData.(id_names{blk_type_idx}).IllegalBlk.API_blk = [get_param(search(i), 'Parent') '/' get_param(search(i), 'Name')];
                end
                apiData.(id_names{blk_type_idx}).IllegalBlk.API_blk_type = get(search(i), 'MaskType');
                apiData.(id_names{blk_type_idx}).IllegalBlk.description = ['Illegal block ID!: ' get_param(search(i), 'Parent') '/' get_param(search(i), 'Name')];
            end
        end
    end
end

function blk_name = get_blk_name(model, block_h)
    type = get_param(block_h,'MaskType');
    if ~isempty(strfind(type,'NamedConstant'))
        blk_name_tmp = get_param(block_h,'MaskValues');
        blk_name = blk_name_tmp{1};
    elseif ~isempty(strfind(type,'From'))
        blk_tag = get_param(block_h,'GotoTag');
        blk_to = find_system(model, 'FindAll', 'on', 'LookUnderMasks', 'all', 'BlockType', 'Goto', 'GotoTag', blk_tag);
        ports = get_param(blk_to, 'PortHandles');
        l_h = get(ports.Inport(1), 'line');
        blk_h = get_param(l_h,'SrcBlockHandle');
        blk_name = get_blk_name(model, blk_h);
    else
        o_name = tl_get(block_h,'output.name');
        if ~isempty(o_name )
            [tok mat] = regexp(model ,'(.+?)_Tmp$', 'tokens');
            if mat > 0
                model_tmp = tok{1};
            else
                model_tmp = model;
            end
            tmp_name = regexprep(o_name, '\$N', model_tmp);
            blk_name = regexprep(tmp_name, '\$B', get(block_h,'name'));
        else
            blk_name = '';
        end
    end
end

function res = chkNan(value)
% Function which replaces NaN or empty fields with '-'
    if ~ischar(value)
        if isnan(value)
            res = '-';
        elseif isempty(value)
            res = '-';
        else
            res = num2str(value);
        end
    else
        res = value;
    end
end

function description = getCsvDescription(blockName, filename)
    % getCsvDescription Get description parametres from CSV files.
    txt = readtable(filename);
    % Using table column names is unsafe as the first row can become the
    % column names. Eg. txt.Var1 can become txt.Models.
    % Using columns instead.
    blockNameColumn = 2;
    descriptionColumn = 3;
    description = txt{strcmp(txt{:, blockNameColumn}, blockName), descriptionColumn};
    if isempty(description)
        description = 'Description missing';
    end
end
