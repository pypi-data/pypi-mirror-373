% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function [res_blk, res_ports] = followLink(startBlock, startPort)
    % Follow the links until a block is found
    % or multiple paths are encountered
    if nargin == 1
        tmpDstBlock = getDstBlocks(startBlock);
        tmpPort = get(getDstLines(startBlock), 'DstPortHandle');
        if iscell(tmpPort)
            tmpPort = vertcat(tmpPort{:});
        end
    else
        tmpDstBlock = startBlock;
        tmpPort = startPort;
    end
    while 1
        %% Check for invalid handle
        if tmpDstBlock < 0
            disp(['Warning: Port not connected: ' ...
                  getPath(startBlock)])
            res_blk = -1;
            res_ports = -1;
            break;
        %% If multiple links were found
        elseif length(tmpDstBlock) > 1
            res_blk = tmpDstBlock;
            res_ports = tmpPort;
            break;
        %% If the block is a inport
        elseif strcmp(get_param(tmpDstBlock, 'blocktype'), 'Inport')
            tmp=get_param(get_param(tmpDstBlock,'parent'), 'linehandles');
            tmpPort=get_param(tmp.Inport(str2num(get_param(tmpDstBlock,'port'))), 'srcporthandle');
            tmpDstBlock=get_param(tmp.Inport(str2num(get_param(tmpDstBlock,'port'))), 'srcblockhandle');
        %% If the block is a outport
        elseif strcmp(get_param(tmpDstBlock, 'blocktype'), 'Outport')
            tmpParent=get_param(tmpDstBlock, 'parent');
            % If were about to exit a block with an action port. Stop!
            ph=get_param(tmpParent, 'PortHandles');
            if ~isempty(ph.Ifaction) || ~isempty(ph.Enable)
                res_blk = tmpDstBlock;
                res_ports = tmpPort;
                break;
            end
            tmp=get_param(tmpParent, 'linehandles');
            tmpOutport = tmp.Outport(str2num(get_param(tmpDstBlock, 'port')));
            if tmpOutport < 0
                % Not connected. Stop!
                res_blk = tmpDstBlock;
                res_ports = tmpPort;
                break;
            end
            tmpPort=get_param(tmpOutport, 'dstporthandle');
            tmpDstBlock=get_param(tmpOutport, 'dstblockhandle');
        %% If the block is a From-block
        elseif strcmp(get_param(tmpDstBlock, 'blocktype'), 'Goto')
            From=find_system(get_param(tmpDstBlock, 'parent'),'lookundermasks', ...
                             'on','searchdepth',1,'Findall','on', 'blocktype', ...
                             'From','GotoTag', get_param(tmpDstBlock,'GotoTag'));
            if length(From > 0)
                tmp=get_param(From, 'linehandles');
                tmpLen = length(tmp);
                %hanterar att det finns flera from block!!!
                if tmpLen > 1
                    tmpPort = [];
                    tmpDstBlock = [];
                    for i=1:tmpLen
                        tmpPort = [tmpPort; get_param(tmp{i}.Outport, 'dstporthandle')];
                        tmpDstBlock = [tmpDstBlock; get_param(tmp{i}.Outport, 'dstblockhandle')];
                    end
                else
                    tmpPort=get_param(tmp.Outport, 'dstporthandle');
                    tmpDstBlock=get_param(tmp.Outport, 'dstblockhandle');
                end
            else
                disp(['Warning: Goto-block, without from here:' ...
                      getPath(tmpDstBlock)])
                res_blk = -1;
                res_ports = -1;
                break;
            end
        %% If non masked subsystem
        elseif checkSubsystem(tmpDstBlock) && ~strcmp(get(tmpPort,'PortType'), 'enable')
            % kolla om subsystemet är maskat, eller om inporten är en enable port,
            % om så är fallet hantera som ett vanligt block
            inport=find_system(tmpDstBlock,'lookundermasks','on', ...
                                'searchdepth', 1, 'FindAll', 'on', ...
                                'blocktype','Inport', ...
                                'port', num2str(get(tmpPort,'PortNumber')));
            tmpPort=get_param(getDstLines(inport), 'dstporthandle');
            tmpDstBlock=getDstBlocks(inport);
        else
            res_blk = tmpDstBlock;
            res_ports = tmpPort;
            break;
        end
    end
end

function follow = checkSubsystem(block)
    % checkSubsystem returns a bool
    % true if followLink should continue inside the subsystem
    % false if followLink should not continue inside the subsystem
    follow = false;
    % If the block is not a SubSystem, stop.
    if strcmp(get_param(block,'blocktype'), 'SubSystem')
        if isempty(get_param(block,'MaskType'))
            % If the block is not masked, continue
            follow = true;
        else
            blockFields = fields(get(block));
            if ismember('FollowLinks', blockFields)
                % If the block is masked, but has FollowLinks property
                % 'on': continue
                 follow = strcmp(get_param(block,'FollowLinks'), 'on');
            end
        end
    end
end