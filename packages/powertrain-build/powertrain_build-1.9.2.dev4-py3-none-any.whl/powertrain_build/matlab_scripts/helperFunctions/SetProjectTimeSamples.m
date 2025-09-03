% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function IncludedFunctions = SetProjectTimeSamples(MaxRefreshRate, Models)
validModels = fieldnames(Models);
includedModels = {};
fields = fieldnames(MaxRefreshRate);
ts = struct;
for field = fields'
    if strcmp(field{1}, 'SampleTimes')
        continue
    else
        rasterName = field{1};
    end
    raster = MaxRefreshRate.(rasterName);
    for included_function = raster'
        if ismember(included_function, validModels)
            includedModels{end+1,1} = included_function{1};
            ts.(included_function{1}) = MaxRefreshRate.SampleTimes.(rasterName);
        end
    end
end
IncludedFunctions = struct();
for included_model = unique(includedModels)'
    IncludedFunctions.(included_model{1}) = struct;
    IncludedFunctions.(included_model{1}).ts = ts.(included_model{1});
end