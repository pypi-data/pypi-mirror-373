% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function loadLibraries(root_folder)
    block_libraries = dir(fullfile(root_folder, '**\*.slx'));
    for i=1:length(block_libraries)
        block_library = block_libraries(i);
        load_system(block_library.name);
    end


