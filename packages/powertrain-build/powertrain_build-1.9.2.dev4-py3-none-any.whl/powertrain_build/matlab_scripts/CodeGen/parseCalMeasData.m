% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function [ allVariables ] = parseCalMeasData( system )
% parseCalMeasData Parse calibration measurement data
%
% See also parseModelInfo

    allVariables=struct;
    evalin('base', [system '_par']);
    allVariables.local_vars=struct;
    allVariables.calib_consts=struct;

    tmp=sortSystemByClass(system);

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Measurable variables
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    blocksTmp=tmp.CVC_DISP;
    % find all TL_Outports (should not be included in measurement variables
    % as they should be included in the outports key
    outports = find_system(topLevelSystem(system), 'FindAll', 'on', ...
                           'LookUnderMasks', 'all', 'MaskType', 'TL_Outport');
    blocks = setdiff(blocksTmp, outports);
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'local_vars', 'output');
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Cal variables
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    blocks=tmp.CVC_CAL;
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'output');
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Prelookups
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    blocks=find_system(get_param(system,'handle'), 'lookundermasks', 'on', 'masktype', 'TL_IndexSearch');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'input');

    blocks=find_system(get_param(system,'handle'), 'lookundermasks', 'on', 'masktype', 'TL_PreLookup');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'input');
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Lookups
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    blocks=find_system(get_param(system,'handle'), 'lookundermasks', 'on', 'regexp', 'on', 'masktype', 'TL_Interpolation.*');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'table');
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Stateflow
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    stateflow=find_system(get_param(system, 'handle'), 'FindAll', 'on', ...
                          'lookundermasks', 'on', 'masktype', 'Stateflow');
    for i=1:length(stateflow)
        allVariables = Create_Struct_SFlow(system, allVariables, stateflow(i));
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % CustomCode blocks
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    customCode=find_system(get_param(system, 'handle'), 'FindAll', 'on', ...
                          'lookundermasks', 'on', 'masktype', 'TL_CustomCode');
    for i=1:length(customCode)
        allVariables = createStructCustCode(system, allVariables, customCode(i));
    end
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % TCM specific blocks
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Lookup1D
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    blocks = find_system(get_param(system, 'handle'), 'lookundermasks', 'on', ...
                         'masktype','TL_Lookup1D');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'input');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'table');
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % Lookup2D
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    blocks = find_system(get_param(system,'handle'),'lookundermasks','on','masktype','TL_Lookup2D');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'row');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'col');
    allVariables = Create_Standard_Struct(system, allVariables, blocks, 'calib_consts', 'table');
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
end

function allVariables = Create_Standard_Struct(systemIn, allVariables, ...
                                               blocks, structName, field)

    if ~isempty(blocks)
        TLFields={'type', 'unit', 'description', 'max', 'min', 'lsb', ...
                  'offset', 'class'};
        system = regexprep(systemIn,'(\w+?)(__.*){0,1}','$1');
        for block = blocks'
            class=tl_getfast(block, [field '.class']);
            if ~isempty(class) && ~strcmp(class, 'default')
                name=tl_getfast(block, [field '.name']);
                res = regexp(name, '(\$[SD])', 'match', 'once');
                if ~isempty(res)
                    o = sprintf('Warning %s in block <a href = "matlab:Hilite_This_System(''%s'')">%s</a>', ...
                            res, getPath(block), getName(block));
                    disp(o)
                    %hilite_system(block)
                else
                    variableName=Get_Full_Name(block, name, system);
                    if sum(isstrprop(variableName, 'wspace')) > 0
                        o = sprintf('Illegal characters in the name property in block <a href = "matlab:Hilite_This_System(''%s'')">%s</a>', ...
                                    getPath(block), getName(block));
                        disp(o)
                        error('aborting')
                    end
                    %VariableName = VariableName(isstrprop(VariableName, 'wspace') == 0);
                    if ~isempty(variableName)
                        for tlField = TLFields
                            tmp_tlField = tlField{1};
                            if ismember(get_param(block, 'masktype'), ...
                                        {'TL_RelationalOperator', 'TL_LogicalOperator'}) && ...
                                        ismember(tmp_tlField , {'max', 'min', 'lsb', 'offset'})
                                allVariables.(structName).(variableName).(tmp_tlField) = '-';
                            elseif ismember(get_param(block, 'masktype'), {'TL_BitwiseOperator'}) ...
                                   && ismember(tmp_tlField , {'max', 'min', 'lsb', 'offset', 'unit'})
                                allVariables.(structName).(variableName).(tmp_tlField) = '-';
                            else
                                Value=tl_getfast(block, [field '.' tmp_tlField]);
                                if iscell(Value)
                                    Value = Value{1};
                                end
                                if strcmp(Value, 'IMPLICIT_ENUM')
                                    Value = getEnumName(block);
                                end
                                allVariables.(structName).(variableName).(tmp_tlField) = checkValue(Value);
                            end
                        end
                        allVariables.(structName).(variableName).handle = getPath(block);
                        consumerBlks = getConsumerBlocks(block);
                        if isempty(consumerBlks)
                            allVariables.(structName).(variableName).configs = getCodeSwitches(block);
                        else
                            codeSwTmp = {};
                            for j=1:length(consumerBlks)
                                consBlk = consumerBlks(j);
                                codeSwTmp{j} = getCodeSwitches(consBlk);
                            end
                            allVariables.(structName).(variableName).configs = removeConfigDuplicates(codeSwTmp);
                        end
                        if ismember(get_param(block, 'masktype'), {'TL_IndexSearch', 'TL_Interpolation', 'TL_Lookup1D', 'TL_Lookup2D'}) ...
                           && ~strcmp(field,'output')
                            [inputValueRef, errorFlag, ~] = tl_get(block, [field '.value']);
                            if errorFlag > 0
                                inputValueRef = tl_getfast(block, [field '.value']);
                            end
                            InputValue=evalin('base', inputValueRef);
                            VarSize=size(InputValue);
                            allVariables.(structName).(variableName).width = VarSize;
                        elseif strcmp(get_param(block, 'masktype'), 'TL_Constant') && strcmp(field,'output')
                            ConstantValue=evalin('base', tl_getfast(block, [field '.value']));
                            VarSize=size(ConstantValue);
                            if VarSize(2) == 1
                                allVariables.(structName).(variableName).width = 1;
                            else
                                allVariables.(structName).(variableName).width = VarSize;
                            end
                        elseif strcmp(get_param(block, 'masktype'), 'TL_IndexSearch') && strcmp(field, 'output')
                            if tl_getfast(block, 'outputmode') == 2
                                VarSize = [1,2];
                            else
                                VarSize = 1;
                            end
                            allVariables.(structName).(variableName).width = VarSize;
                        else
                            allVariables.(structName).(variableName).width = 1;
                        end
                        allVariables.(structName).(variableName) = modifyEnumStructField(allVariables.(structName).(variableName));
                        if length(variableName) > 63
                            % Can't store the full name as a struct key as matlab only supports key lengths < 64
                            o = sprintf('Warning variable name %s is longer than 63 chars, consider shortening it.', variableName);
                            disp(o)
                            allVariables.(structName).(variableName).unshortenedName = variableName;
                        end
                    end
                end
            end
        end
    end
end

function allVariables = Create_Struct_SFlow(system, allVariables, sFlow)
    configs = getCodeSwitches(sFlow);
    % Handle stateflow outports
    tmp_SFObj = get_param(sFlow, 'Object');
    chartObj = tmp_SFObj.find('-isa', 'Stateflow.Chart');
    sfDataArr = chartObj.find('-isa', 'Stateflow.Data');
    idArr = arrayfun(@(x) x.Id, sfDataArr);
    sfHandles = tl_get_sfobjects(sFlow, {'SF Output', 'SF Local'});
    for i=1:length(sfHandles)
        SfHandle = sfHandles(i);
        idx = idArr == SfHandle;
        sfData = sfDataArr(idx);
        tlClass = tl_get(SfHandle, 'class');
        if checkClass(tlClass, sFlow, sfData)
            continue % do nothing, if NVM, default class, or name error. NVM is handled elsewhere
        end
        tlName = tl_get(SfHandle, 'name');
        res = regexp(tlName, '(\$[SDCB])', 'tokens');
        if isempty(res)
            allVariables = copyFields(system, allVariables, sFlow, SfHandle, configs, sfData.port);
        else
            err_msg = res{1}{1};
            if isnan(sfData.port)
                port = '';
            else
                port = [':' num2str(sfData.port)];
            end
            o = sprintf('Warning %s in <a href = "matlab:Hilite_This_System(''%s'')">%s - %s (%s%s)</a>', ...
                    err_msg, getPath(sFlow), get_param(sFlow, 'name'), sfData.name, sfData.scope, port);
            disp(o)
        end
    end
end

function allVariables = createStructCustCode(system, allVariables, custCodeBlk)
    custFields={'type', 'unit', 'description', 'max', 'min', 'lsb', ...
                'offset', 'class'};
    parTypes =   {'state', 'work', 'param', 'input', 'output'};
    structName = {'local_vars', 'local_vars', 'calib_consts', 'local_vars', 'local_vars'};
    numTypes = cellfun(@(x) tl_get(custCodeBlk, ['num' x 's']), parTypes, 'uni', false);
    for pti = 1:length(parTypes)
        pType = parTypes{pti};
        for idx=1:numTypes{pti}
            class = tl_get(custCodeBlk, [pType '(' num2str(idx) ').class']);
            if ~ismember(class, {'default', 'STATIC_LOCAL_MACRO'})
                name = tl_get(custCodeBlk, [pType '(' num2str(idx) ').name']);
                if ~ismember(pType, {'output'}) && ~isempty(regexp(name, '\$L', 'once'))
                    error('Can not use $L macro in non output parameters')
                end
                if ~isempty(regexp(name, '\$S', 'once'))
                    error('Can not use $S macro in name.')
                end
                varName = getSignalName(system, custCodeBlk, name, idx);
                for fldidx = 1:length(custFields)
                    fld = custFields{fldidx};
                    value = val2str(tl_get(custCodeBlk, [ pType '(' num2str(idx) ').' fld ]));
                    if strcmp(value, 'IMPLICIT_ENUM')
                        allVariables.(structName{pti}).(varName).(fld) = getEnumName(custCodeBlk);
                    else
                        allVariables.(structName{pti}).(varName).(fld) = value;
                    end
                end
                if strcmp(pType, 'param')
                    inputValue=evalin('base', tl_get(custCodeBlk, [pType '(' num2str(idx) ').value']));
                    varSize=size(inputValue);
                    allVariables.(structName{pti}).(varName).width = varSize;
                else
                    %TODO: Check width parameter?
                    allVariables.(structName{pti}).(varName).width = 1;
                end
                allVariables.(structName{pti}).(varName) = modifyEnumStructField(allVariables.(structName{pti}).(varName));
                allVariables.(structName{pti}).(varName).handle = getPath(custCodeBlk);
                allVariables.(structName{pti}).(varName).configs = getCodeSwitches(custCodeBlk);
            end
        end
    end
end

function allVariables = copyFields(system, allVariables, sFlow, sfHandle, configs, outPortNbr)

    sfFields={'type', 'unit', 'description', 'max', 'min', 'lsb', ...
              'offset', 'class'};

    variableName = getSfSignalName(system, sFlow, sfHandle, outPortNbr);
    allVariables.local_vars.(variableName).configs = configs;

    for j=1:length(sfFields)
        fieldName = sfFields{j};
        value = tl_get(sfHandle, fieldName);
        if strcmp(value, 'IMPLICIT_ENUM')
            value = getEnumName(sfHandle);
        end
        allVariables.local_vars.(variableName).(fieldName) = checkValue(value);
    end

    allVariables.local_vars.(variableName) = modifyEnumStructField(allVariables.local_vars.(variableName));
end

function value = val2str(val_in)
    if ~ischar(val_in)
        if isnan(val_in)
            value = '-';
        elseif isempty(val_in)
            value = '-';
        else
            value = num2str(val_in);
        end
    else
        value=val_in;
    end
end

function newStr = stripIllegalChar(value)
    % replace all non word characters with space
    newStr = regexprep(value, '(?![\w/]).', ' ');
end

function newVal = checkValue(value)
    if ischar(value)
        newVal=strtrim(value);
    elseif isnan(value)
        newVal='-';
    elseif length(value) > 1
        newVal = {};
        for i=1:length(value)
            newVal{i} = checkValue(value(i));
        end
    else
        newVal=value;
    end
end

function nok = checkClass(tlClass, sFlow, sfData)
    if regexp(tlClass, '(?:default|CVC_DISP_NVM)')
        nok = 1;
        return % do nothing, NVM is handled elsewhere
    end
    if isempty(strfind(tlClass, 'CVC_DISP'))
        if isnan(sfData.port)
            port = '';
        else
            port = [':' num2str(sfData.port)];
        end
        o = sprintf('Warning - <a href = "matlab:Hilite_This_System(''%s'')">unknown class %s in %s - %s (%s%s)</a>', ...
                    getPath(sFlow), tlClass, get_param(sFlow, 'name'), sfData.name, sfData.scope, port);
        disp(o)
        nok = 0;
        return
    end
    nok = 0;
end

function name = getSfSignalName(systemIn, block, sfHandle, outPortNbr)
% function to get the name of a in/out-port of a block.
    macro = tl_get(sfHandle, 'name');
    system = getTLModelName(systemIn);
    nameTmp = macro;
    res = regexp(macro, '\$O', 'tokens');
    if ~isempty(res)
		tmp_SFObj = get_param(block, 'Object');
		chartObj = tmp_SFObj.find('-isa', 'Stateflow.Chart');
		sfData = chartObj.find('-isa', 'Stateflow.Data');
		idArr = arrayfun(@(x) x.Id, sfData);
		idx = idArr == sfHandle;
		nameTmp = regexprep(nameTmp,'\$O', sfData(idx).name);
    end
    res = regexp(macro, '\$L', 'tokens');
    if ~isempty(res)
        slPortHandles = get_param(block, 'PortHandles');
        ph = slPortHandles.Outport(outPortNbr);
        signal = get_param(get_param(ph, 'line'), 'name');
        if isempty(signal)
            %TODO: Consider removing the turning on of the propagated
            % signals
            if strcmp(get_param(ph, 'ShowPropagatedSignals'), 'off')
                set_param(ph, 'ShowPropagatedSignals', 'on')
            end
            signal = get_param(ph, 'PropagatedSignals');
            if isempty(signal)
                error('signal') % fix warning
            end
        end
        nameTmp = regexprep(nameTmp,'\$L', signal);
    end
    nameTmp = regexprep(nameTmp,'\$B', get_param(block, 'Name'));
    nameTmp = regexprep(nameTmp,'\$N', system);
    name = regexprep(nameTmp,' ', '');
end

function name = getSignalName(systemIn, block, macro, outPortNbr)
% function to get the name of a in/out-port of a block.
    res = regexp(macro, '(\$L)', 'tokens');
    system = regexprep(systemIn,'(\w+?)(__.*){0,1}','$1');
    nameTmp = macro;
    if ~isempty(res)
        slPortHandles = get_param(block, 'PortHandles');
        ph = slPortHandles.Outport(outPortNbr);
        signal = get_param(get_param(ph, 'line'), 'name');
        if isempty(signal)
            %TODO: Consider removing the turning on of the propagated
            % signals
            if strcmp(get_param(ph, 'ShowPropagatedSignals'), 'off')
                set_param(ph, 'ShowPropagatedSignals', 'on')
            end
            signal = get_param(ph, 'PropagatedSignals');
            if isempty(signal)
                error('signal') % fix warning
            end
        end
        nameTmp = regexprep(nameTmp,'\$L', signal);
    end
    nameTmp = regexprep(nameTmp,'\$B', get_param(block, 'Name'));
    nameTmp = regexprep(nameTmp,'\$N', system);
    name = regexprep(nameTmp,' ', '');
end
