% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function inPorts = parseInPorts(root_subsystem)
    % parseInPorts Parse which block data shall be stored per block.
    %
    % See also parseModelInfo

    % TODO: Some models have more tha one inport per variable. Should we
    % check for this?
    inPorts = struct();
    info = {'description', 'type', 'unit', 'offset', 'lsb', 'min', 'max', 'class', 'width'};

    normalInPorts = parseTLInPorts(root_subsystem, info);
    normalFields = fieldnames(normalInPorts);
    for idx = 1:length(normalFields)
        inPorts.(normalFields{idx}) = normalInPorts.(normalFields{idx});
    end

    busInPorts = parseTLBusInPorts(root_subsystem, info);
    busFields = fieldnames(busInPorts);
    for idx = 1:length(busFields)
        inPorts.(busFields{idx}) = busInPorts.(busFields{idx});
    end
end

function inPorts = parseTLInPorts(root_subsystem, info)
    in_ports = find_system(root_subsystem, 'FindAll', 'on',  'SearchDepth', 1, 'MaskType', 'TL_Inport');
    inPorts = struct();
    tmpInport = struct();
    for i=1:length(in_ports)
        inp = in_ports(i);
        consumerBlks = getConsumerBlocks(inp);
        codeSwTmp = {};
        for j=1:length(consumerBlks)
            consBlk = consumerBlks(j);
            codeSwTmp{j} = getCodeSwitches(consBlk);
        end
        %TODO: Do a better reduction of code switch logics right now only duplicates are removed.
        codeSw = removeConfigDuplicates(codeSwTmp);
        tmpInport.handle = getPath(inp);
        tmpInport.name = strtrim(getName(inp));
        tmpInport.configs = codeSw;
        for idx=1:length(info)
            tmpValue = tl_get(inp, ['output.' info{idx}]);
            tmpInport.(info{idx}) = getProperValue(inp, tmpValue);
        end

        tmpInport = modifyEnumStructField(tmpInport);

        if strcmp(tmpInport.name, fields(inPorts))
            printf('Warning: inport %s is already defined', tmpInport.name);
            printf('         signal will not be added again to the input signal');
        else
            inPorts.(tmpInport.name) = tmpInport;
        end
    end
end

function busInPorts = parseTLBusInPorts(root_subsystem, info)
    foundBusInPorts = find_system(root_subsystem, 'FindAll', 'on',  'SearchDepth', 1, 'MaskType', 'TL_BusInport');
    busInPorts = struct();
    tmpInport = struct();
    for idx=1:length(foundBusInPorts)
        inp = foundBusInPorts(idx);
        for idy = 1:tl_get(inp, 'numoutputs')
            tmpInport.handle = getPath(inp);
            tmpInport.name = tl_get(inp, ['output(' num2str(idy) ').signalname']);
            tmpInport.configs = getBusConfig(inp);
            for idz=1:length(info)
                tmpValue = tl_get(inp, ['output(' num2str(idy) ').' info{idz}]);
                tmpInport.(info{idz}) = getProperValue(inp, tmpValue);
            end
            % TODO Fix later, cannot set width in TL_BusInport:s due to "matrix unified output".
            tmpInport.width = 1;

            tmpInport = modifyEnumStructField(tmpInport);

            busParts = split(tmpInport.name, '.');
            if ~ismember(busParts{1}, fields(busInPorts))
                busInPorts.(busParts{1}) = struct();
                busInPorts.(busParts{1}).(busParts{2}) = tmpInport;
            elseif ~ismember(busParts{2}, fields(busInPorts.(busParts{1})))
                busInPorts.(busParts{1}).(busParts{2}) = tmpInport;
            else
                printf('Warning: inport %s is already defined', tmpInport.name);
                printf('         signal will not be added again to the input signal');
            end
        end
    end
end

function busConfig = getBusConfig(inp)
    consumerBlks = getConsumerBlocks(inp);
    codeSwTmp = {};
    for idx=1:length(consumerBlks)
        consBlk = consumerBlks(idx);
        codeSwTmp{idx} = getCodeSwitches(consBlk);
    end
    %TODO: Do a better reduction of code switch logics right now only duplicates are removed.
    busConfig = removeConfigDuplicates(codeSwTmp);
    isValidConfig = iscell(busConfig) && length(busConfig) == 1 && strcmp(busConfig{1}, 'all');
    if ~isValidConfig
        error('Code switching bus inports is currently not supported. All bus inport destinations must be active.')
    end
end
