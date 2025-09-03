% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function out = removeConfigDuplicates(config)
    %Take a cell array with configs an return
    %a config cell array without duplicates

    confs = {};    
    lenConfig = length(config);
    j=1;
    for i=1:lenConfig
        if ~checkIfDefined(config{i},confs)
            confs{j} = config{i};
            j=j+1;
        end
    end
    out = confs;
end

function def = checkIfDefined(cellArr, inCellArrArr)
% Check if cell array is defined within an array of cell arrays
    def = 0;
    for i=1:length(inCellArrArr)
        lenCellArr = length(cellArr);
        if lenCellArr == length(inCellArrArr{i})
            if sum(strcmp(sort(cellArr),sort(inCellArrArr{i}))) == lenCellArr
                def = 1;
                return
            end
        end
    end
end