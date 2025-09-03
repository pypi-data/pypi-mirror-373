% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function result = Strip_Suffix(fileName)
    % Some file names have a version suffix, remove that first
    underscoreIndex = strfind(fileName, '__');
    if isempty(underscoreIndex)
        result = fileName;
    else
        if strcmp(version('-release'),'2011b')
            result = fileName(1:underscoreIndex-1);
        else
            result = extractBefore(fileName,underscoreIndex);
        end
    end
end
