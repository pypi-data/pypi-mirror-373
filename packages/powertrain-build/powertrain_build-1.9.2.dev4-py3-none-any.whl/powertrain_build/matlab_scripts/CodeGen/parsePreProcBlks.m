% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function out = parsePreProcBlks(model)
    % parsePreProcBlks Find all preprocessor blocks in the model
    %
    % See also parseModelInfo
    preProcessorBlks = find_system(model, 'FindAll', 'on', 'RegExp', 'on', ...
                                   'LookUnderMasks', 'all', 'MaskType', 'TL_PreProcessorIf');
    blks = {};
    for sbh=preProcessorBlks'
        ports = get_param(sbh, 'PortHandles');
        l=get_param(ports.Inport, 'Line');
        blk = get_param(l, 'SrcBlockHandle');
        if strcmp(get_param(blk, 'blocktype'), 'Inport')
            tmp=get_param(get_param(blk,'parent'), 'linehandles');
            blk=get_param(tmp.Inport(str2num(get_param(blk, 'port'))), 'srcblockhandle');
        end
        if_exp = tl_get(sbh, 'ifexpression');
        blks = [strrep(if_exp,'u1',get_param(blk, 'const_name')); blks];
    end
    out = unique(blks);
end
