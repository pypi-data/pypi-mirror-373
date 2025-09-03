% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function SrcLines = Get_SrcLines(Block)
    Tmp = get_param(Block, 'linehandles');
    
    if isfield(Tmp, 'Inport')
        SrcLines = Tmp.Inport;
    else
        SrcLines = [];
    end
end
