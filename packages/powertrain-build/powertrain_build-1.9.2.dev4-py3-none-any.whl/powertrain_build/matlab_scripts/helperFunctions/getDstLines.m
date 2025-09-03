% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function dstLines = getDstLines(Block)

    tmp=get_param(Block,'linehandles');

    if isfield(tmp,'Outport')
        dstLines=tmp.Outport;
    else
        dstLines=[];
    end
end
