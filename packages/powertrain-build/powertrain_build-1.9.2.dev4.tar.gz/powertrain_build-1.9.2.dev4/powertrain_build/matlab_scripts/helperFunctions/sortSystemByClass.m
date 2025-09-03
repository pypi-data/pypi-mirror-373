% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function classSortedBlocks = sortSystemByClass(system)    
    classes={'CVC_DISP'; 'CVC_CAL'};
    classSortedBlocks=struct;
    for i=1:length(classes)
        classSortedBlocks.(classes{i}) = [];
    end

    %TODO: this parsing is not that nice, as it will find combinations of class
    %suffixes, which does not exist.
    blksWithType = find_system(system, 'FindAll', 'on', 'lookundermasks', 'on', 'regexp', 'on', ...
        'masktype', 'TL(?!_PreProcessorIf|_MilHandler|_Enable|_SimFrame|_MainDialog|_Function|_StateflowLogger|_StateflowLoggingMain|_ToolSelector|_AddFile|_DummyTrigger|_DataStoreRead|_DataStoreWrite|_CustomCode|SAMPLES_BW_LOGICAL_OPERATOR|SAMPLES_ROUNDING_FUNCTION|SAMPLES_16BIT_DECODER|SAMPLES_16BIT_ENCODER).*', 'data', '.*?''output''\,.*?');
    classWithType= tl_get(blksWithType, 'output.class');
    if ~isempty(classWithType)
        for i=1:length(classes)
            class = classes{i};
            filter_tmp = regexp(classWithType,['(?:ASIL_[ABCD]/){0,1}' class '(?:_MERGEABLE|_BURAM)?' '(?:_ASIL_[ABCD]){0,1}' '$']);
            if ~isempty(filter_tmp)
                filter = cellfun(@(c)~isempty(c), filter_tmp);
                classSortedBlocks.(classes{i}) = blksWithType(filter);
            end
        end
    end
end
