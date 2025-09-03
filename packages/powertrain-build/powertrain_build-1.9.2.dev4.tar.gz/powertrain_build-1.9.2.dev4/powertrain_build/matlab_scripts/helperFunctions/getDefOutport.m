% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function outport = getDefOutport(startBlock)
%% Find the blocks where the lowest level outport for the defining block
    tmpSrcBlock=getSrcBlocks(startBlock);
    tmpPort=get_param(getSrcLines(startBlock), 'srcporthandle');
    outport = -1;
    while 1
        %% If multiple links were found
        tmpH=getDstBlockHandles(tmpSrcBlock, tmpPort);
        if length(tmpH) > 1
            break

        %% If the block is a inport, but not a TL-port
        elseif strcmp(get_param(tmpSrcBlock, 'blocktype'), 'Inport') && ...
            isempty(get_param(tmpSrcBlock,'MaskType'))
            tmp=get_param(get_param(tmpSrcBlock, 'parent'), 'linehandles');
            tmpPort=get_param(tmp.Inport(str2num(get_param(tmpSrcBlock, 'port'))), 'srcporthandle');
            tmpSrcBlock=get_param(tmp.Inport(str2num(get_param(tmpSrcBlock, 'port'))), 'srcblockhandle');

        %% If the block is a From-block
        elseif strcmp(get_param(tmpSrcBlock, 'blocktype'), 'From')
            goto=find_system(get_param(tmpSrcBlock,'parent'), 'lookundermasks', ...
                            'on','searchdepth',1,'blocktype','Goto','GotoTag', ...
                            get_param(tmpSrcBlock,'GotoTag'));
            tmp=get_param(goto{1},'linehandles');
            tmpPort=get_param(tmp.Inport,'srcporthandle');
            tmpSrcBlock=get_param(tmp.Inport,'srcblockhandle');

        %% If subsystem
        elseif strcmp(get_param(tmpSrcBlock,'blocktype'),'SubSystem')
            % Don't move outports inside library blocks
            if ~isempty(get_param(tmpSrcBlock, 'MaskType')) &&...
                    (strncmp(get_param(tmpSrcBlock, 'MaskType'), 'VCC_', 4) ||...
                    strncmp(get_param(tmpSrcBlock, 'MaskType'), 'TL_', 3))
                break
            end

            outport=find_system(tmpSrcBlock,'lookundermasks','on','searchdepth',1, ...
                                'blocktype','Outport','port', ...
                                num2str(get(tmpPort,'PortNumber')));
            tmpPort=get_param(getSrcLines(outport),'srcporthandle');
            tmpSrcBlock=getSrcBlocks(outport);
        else
            break
        end
    end
end

function dstBlocks = getDstBlockHandles(block, port)
    dstBlocks=[];
    tmp=get_param(block,'linehandles');
    tmpNum=get_param(port,'PortNumber');
    if isfield(tmp,'Outport')
        dstBlocks = get_param(tmp.Outport(tmpNum),'dstblockhandle');
    end
end
