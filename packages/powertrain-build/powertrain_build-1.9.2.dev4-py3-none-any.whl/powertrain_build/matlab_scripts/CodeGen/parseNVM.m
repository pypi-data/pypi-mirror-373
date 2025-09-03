% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function nvm = parseNVM(model)
    % parseNVM Parse all the NVM-ram blocks used in the model
    % and return a struct with which ram-cells there are, and in
    % which configurations they are present
    %
    % See also parseModelInfo

    %TODO: add looking for NVM class in stateflow!!

    outp_and_data_stores = find_system(model, 'FindAll', 'on', 'LookUnderMasks', 'all', ...
                                       'RegExp', 'On', 'MaskType', 'TL_DataStoreMemory|TL_Outport');
    unit_delays = find_system(model, 'FindAll', 'on', 'LookUnderMasks', 'all', ...
                              'RegExp', 'On', 'MaskType', 'TL_UnitDelay');

    nvm = struct();
    for i=1:length(outp_and_data_stores)
        dstore_h = outp_and_data_stores(i);
        class = tl_get(dstore_h,'output.class');
        name = tl_get(dstore_h,'output.name');
        if ~isempty(regexp(class, 'CVC_DISP_NVM(_P){0,1}', 'tokens'))
            nvm = getParams(dstore_h, class, name, nvm);
        end
    end
    for i=1:length(unit_delays)
        udel_h = unit_delays(i);
        class_tmp = tl_get(udel_h, 'output.class');
        state = tl_get(udel_h, 'state.class');
        if ~isempty(regexp(class_tmp, 'CVC_DISP_NVM(_P){0,1}', 'tokens'))
            class = class_tmp;
            name = tl_get(udel_h, 'output.name');
        elseif ~isempty(state) && ~isempty(regexp(state, 'CVC_DISP_NVM(_P){0,1}', 'tokens'))
            class = state;
            name = tl_get(udel_h, 'state.name');
        else
            class = '';
        end
        if ~isempty(class)
            nvm = getParams(udel_h, class, name, nvm);
        end
    end
end

function nvm = getParams(blk_handle, class, name, nvm)
    info = {'description', 'type', 'unit', 'offset', 'lsb', 'min', 'max', 'width'};
    tmpNvm = struct();
    tmpNvm.handle = getPath(blk_handle);
    tmpNvm.name = getName(blk_handle, name);
    config = getCodeSwitches(blk_handle);
    if ismember(tmpNvm.name, fields(nvm))
        % Merge new configs with old
        tmpConfigs = nvm.(tmpNvm.name).configs;
        tmpConfigs{end+1} = config;
        tmpNvm.configs = removeConfigDuplicates(tmpConfigs);
    else
        % Always require nvm configs to be formatted in or+and+expression syntax
        tmpNvm.configs = {config};
    end
    tmpNvm.class = class;
    for idx=1:length(info)
        tmpNvm.(info{idx}) = chkNan(tl_get(blk_handle, ['output.' info{idx}]));
    end
    % Overwrite potential old nvm block with new configs
    nvm.(tmpNvm.name) = tmpNvm;
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