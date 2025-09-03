% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function tmpSrcBlock = getDefBlock(varargin)
%% Find the blocks where the input variables are defined
    if length(varargin) == 1
        startBlock = varargin{1};
        tmpSrcBlock = getSrcBlocks(startBlock);
        tmpPort = get(getSrcLines(startBlock),'srcporthandle');
    elseif length(varargin) == 2
        tmpSrcBlock = varargin{1};
        tmpPort = varargin{2};
    else
        error('Wrong number of input arguments')
    end

    while 1
        %% If the block is a inport, but not a TL-port
        if strcmp(get_param(tmpSrcBlock,'blocktype'),'Inport') && isempty(get_param(tmpSrcBlock,'MaskType'))
            tmp=get_param(get_param(tmpSrcBlock,'parent'),'linehandles');
            tmpPort=get_param(tmp.Inport(str2num(get_param(tmpSrcBlock,'port'))),'srcporthandle');
            tmpSrcBlock=get_param(tmp.Inport(str2num(get_param(tmpSrcBlock,'port'))),'srcblockhandle');

        %% If the block is a From-block
        elseif strcmp(get_param(tmpSrcBlock,'blocktype'),'From')
            goto=find_system(get_param(tmpSrcBlock,'parent'),'lookundermasks','on','searchdepth',1,'blocktype','Goto','GotoTag',get_param(tmpSrcBlock,'GotoTag'));
            tmp=get_param(goto{1},'linehandles');
            tmpPort=get_param(tmp.Inport,'srcporthandle');
            tmpSrcBlock=get_param(tmp.Inport,'srcblockhandle');

        %% If subsystem
        elseif strcmp(get_param(tmpSrcBlock,'blocktype'),'SubSystem')
            outport=find_system(tmpSrcBlock,'followlinks', 'on', 'lookundermasks','on','searchdepth',1,'blocktype','Outport','port', num2str(get(tmpPort,'PortNumber')));
            tmpPort=get_param(getSrcLines(outport),'srcporthandle');
            tmpSrcBlock=getSrcBlocks(outport);
        else
            break
        end
    end
end