% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function srcBlocks = getSrcBlocks(block)

    srcBlocks=[];
    tmp=get_param(block,'linehandles');

    if isfield(tmp,'Inport')
        srcBlocks=zeros(size(tmp.Inport));
        for i=1:length(tmp.Inport)
            if tmp.Inport(i)<0
                srcBlocks(i)=-1;
            else
                srcBlocks(i)=get_param(tmp.Inport(i),'srcblockhandle');
            end
        end
    end
end
