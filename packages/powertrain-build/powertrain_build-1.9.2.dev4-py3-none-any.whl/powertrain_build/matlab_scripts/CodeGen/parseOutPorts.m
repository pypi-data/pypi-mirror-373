% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function outPorts = parseOutPorts(root_subsystem)
    % parseOutPorts Parse which block data shall be stored per block.
    %
    % See also parseModelInfo
    outPorts = struct();
    info = {'description', 'type', 'unit', 'offset', 'lsb', 'min', 'max', 'class', 'width'};

    normalOutPorts = parseTLOutports(root_subsystem, info);
    normalFields = fieldnames(normalOutPorts);
    for idx = 1:length(normalFields)
        outPorts.(normalFields{idx}) = normalOutPorts.(normalFields{idx});
    end

    busOutPorts = parseTLBusOutports(root_subsystem, info);
    busFields = fieldnames(busOutPorts);
    for idx = 1:length(busFields)
        outPorts.(busFields{idx}) = busOutPorts.(busFields{idx});
    end
end

function outports = parseTLOutports(root_subsystem, info)
    out_ports = find_system(root_subsystem, 'FindAll', 'on', 'LookUnderMasks', 'all', 'MaskType', 'TL_Outport');
    outports = struct();
    tmpOutport = struct();
    for i=1:length(out_ports)
        outp = out_ports(i);
        def_blk = getDefBlock(outp);
        tmpOutport.handle = getPath(outp);
        tmpOutport.name = getName(outp);
        tmpOutport.configs = getCodeSwitches(def_blk);
        for idx=1:length(info)
            tmpValue = tl_get(outp, ['output.' info{idx}]);
            tmpOutport.(info{idx}) = getProperValue(outp, tmpValue);
        end

        tmpOutport = modifyEnumStructField(tmpOutport);

        if strcmp(tmpOutport.name, fields(outports))
            printf('Warning: outport %s is already defined', tmpOutport.name);
            printf('         signal will not be added again to the output signal');
        else
            outports.(tmpOutport.name) = tmpOutport;
        end
    end
end

function busOutPorts = parseTLBusOutports(root_subsystem, info)
    foundBusOutPorts = find_system(root_subsystem, 'FindAll', 'on', 'LookUnderMasks', 'all', 'MaskType', 'TL_BusOutport');
    busOutPorts = struct();
    tmpOutport = struct();
    for idx=1:length(foundBusOutPorts)
        outp = foundBusOutPorts(idx);
        busCreator = getDefBlock(outp);
        defBlocks = getBusSrcBlocks(outp, busCreator);
        if ismember('BusCreator', get_param(defBlocks, 'BlockType'))
            faultyOutport = [get(outp, 'path') '/' get(outp, 'name')];
            error('Nestled bus creators are currently not supported, see %s.', faultyOutport)
        end
        config = getBusConfig(defBlocks);
        for idy = 1:tl_get(outp, 'numoutputs')
            tmpOutport.handle = getPath(outp);
            tmpOutport.name = tl_get(outp, ['output(' num2str(idy) ').signalname']);
            tmpOutport.configs = config;
            for idz=1:length(info)
                tmpValue = tl_get(outp, ['output(' num2str(idy) ').' info{idz}]);
                tmpOutport.(info{idz}) = getProperValue(outp, tmpValue);
            end
            % TODO Fix later, cannot set width in TL_BusOutport:s due to "matrix unified output".
            tmpOutport.width = 1;

            tmpOutport = modifyEnumStructField(tmpOutport);

            busParts = split(tmpOutport.name, '.');
            if ~ismember(busParts{1}, fields(busOutPorts))
                busOutPorts.(busParts{1}) = struct();
                busOutPorts.(busParts{1}).(busParts{2}) = tmpOutport;
            elseif ~ismember(busParts{2}, fields(busOutPorts.(busParts{1})))
                busOutPorts.(busParts{1}).(busParts{2}) = tmpOutport;
            else
                printf('Warning: outport %s is already defined', tmpOutport.name);
                printf('         signal will not be added again to the output signal');
            end
        end
    end
end

function defBlocks = getBusSrcBlocks(busOutPort, bus_creator)
    defBlocks = [];
    if ~strcmp(get_param(bus_creator, 'BlockType'), 'BusCreator')
        faultyOutport = [get(busOutPort, 'path') '/' get(busOutPort, 'name')];
        error('Source block of a TL_BusOutport must be a bus creator, see %s.', faultyOutport)
    end
    srcBlocks = getSrcBlocks(bus_creator);
    tmpSrcPorts = get(getSrcLines(bus_creator), 'SrcPortHandle');

    if iscell(tmpSrcPorts)
        srcPorts = cell2mat(tmpSrcPorts);
    else
        srcPorts = tmpSrcPorts;
    end

    for idx = 1:length(srcBlocks)
        defBlocks(end+1) = getDefBlock(srcBlocks(idx), srcPorts(idx));
    end
end

function busConfig = getBusConfig(defBlocks)
    busConfig = {'all'};
    for idx = 1:length(defBlocks)
        defConfig = getCodeSwitches(defBlocks(idx));
        isValidConfig = iscell(defConfig) && length(defConfig) == 1 && strcmp(defConfig{1}, 'all');
        if ~isValidConfig
            faultyBlockPath = [get(defBlocks(idx), 'path') '/' get(defBlocks(idx), 'name')];
            error('All members of a bus outport must be active, %s is not.', faultyBlockPath)
        end
    end
end
