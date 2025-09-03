% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function jsonValue = getProperValue(tlPort, tlValue)
%GETPROPERVALUE Get a value fitting for a json file, given a TL property
%value.
    if strcmp(tlValue, 'IMPLICIT_ENUM')
        tlValue = getEnumName(tlPort);
    end

    if ischar(tlValue)
        jsonValue = tlValue;
    elseif isempty(tlValue)
        jsonValue = '-';
    else
        jsonValue = tlValue(1);
        if isnan(jsonValue)
            jsonValue = '-';
        end
    end
end
