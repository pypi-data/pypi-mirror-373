% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function outStruct = modifyEnumStructField(inStruct)
    % MODIFYENUMSTRUCTFIELD Update a given struct with data based on type.
    %    If the given struct contains enumeration data, insert default value.
    %    If not, remove the default field if present.
    %
    %    NOTE: Used in parse*Ports/parseCalMeasData where "instruct" is
    %    created outside and then rewritten inside a for-loop.
    %    Only enum variables should have the default field.
    %
    %    See also parseInPorts, parseOutPorts, parseCalMeasData.
    tmpEnum = enumeration(inStruct.type);
    if ~isempty(tmpEnum)
        inStruct.default = char(tmpEnum.getDefaultValue());
    elseif isfield(inStruct, 'default')
        inStruct = rmfield(inStruct, 'default');
    end
    outStruct = inStruct;
end
