% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function path = getPath(handle)
    path=[get_param(handle,'parent') '/' get_param(handle,'name')];
end
