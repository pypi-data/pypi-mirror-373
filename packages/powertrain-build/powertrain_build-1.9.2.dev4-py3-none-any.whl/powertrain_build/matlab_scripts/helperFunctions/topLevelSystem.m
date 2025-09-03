% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function topLevelSystem = topLevelSystem(model)
%Function which returns a string to the top level target link subsystem
%Takes one argument, which is the model names 
    tlFncs = find_system(model, 'FindAll', 'on', 'LookUnderMasks', 'all', ...
                         'Regexp' ,'on', 'MaskType', 'TL_Function');

    funcParents = get_param(tlFncs, 'Parent');
    if ~iscell(funcParents)
        funcParents = {funcParents};
    end
    lenFncs = cellfun(@(p)length(p), funcParents);
    if ~isempty(lenFncs)
        topLevelIdx = lenFncs == min(lenFncs(:));
        topLevelSystem = funcParents{topLevelIdx};
    else
        error('did not find any TL_Function blocks')
    end
end