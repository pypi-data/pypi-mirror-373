% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function dstBlocks = getDstBlocks(block)
%% Find the blocks where the input variables are defined

    dstBlocks=[];
    tmp=get_param(block,'linehandles');

    if isfield(tmp,'Outport')
        for i=1:length(tmp.Outport)
            if tmp.Outport(i)<0
                dstBlocks(i)=-1;
            else
                dstBlocks = [dstBlocks; get_param(tmp.Outport(i),'dstblockhandle')];
            end
        end
    end
end
