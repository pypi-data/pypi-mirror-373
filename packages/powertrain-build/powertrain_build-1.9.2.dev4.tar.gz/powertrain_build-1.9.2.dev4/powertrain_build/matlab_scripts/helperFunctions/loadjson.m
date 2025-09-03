% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function A = loadjson(filename)
    A = jsondecode(fileread(filename));
end
