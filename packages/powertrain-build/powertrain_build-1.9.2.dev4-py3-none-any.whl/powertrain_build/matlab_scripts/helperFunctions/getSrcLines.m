% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function srcLines = getSrcLines(block)

    tmp=get_param(block,'linehandles');

    if isfield(tmp,'Inport')
        srcLines=tmp.Inport;
    else
        srcLines=[];
    end
end
