% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function res = struct2JSON(struct, outputFileName)
   % A function that a strcut and file name as arguments,
   % and outputs the matlab struct as a JSON file in UTF-8 encoding
   fp = fopen(outputFileName, 'w', 'n', 'UTF-8');
   if fp > 0
       res = recursiveStringGen('', struct, '', 1);
       fwrite(fp,res);
       fclose(fp);
   else
       disp(['could not open file ' outputFileName])
   end
end

function res = recursiveStringGen(elementName, element, str, indentLevel)
    %function that outputs a string with a json format from a struct
    %Note the NaN value is not according to JSON standard, but the
    %python importer seems to handle it anyway
    if isstruct(element)
        subElementNames = fields(element);
        subElemsLen = length(subElementNames);

        if subElemsLen == 0
            str = sprintf('%s{}', str);
        else
            str = sprintf('%s{\n', str);
            for idx=1:subElemsLen
                subElementName = subElementNames{idx};
                subElement = element.(subElementName);
                if isfield(subElement, 'unshortenedName')
                    % When element name length is > 63, it can't be stored as a struct key, instead the
                    % full name is stored as a subelement with the key 'unshortenedName'.
                    subElementName = subElement.('unshortenedName')
                    subElement = rmfield(subElement, 'unshortenedName')
                end
                if ismember(elementName, {'inports', 'outports'})
                    % TL_In-/Out-ports have a depth of 1, which TL_BusIn-/Out-ports have a depth of 2.
                    % Bus ports should be reduced to a depth of 1, where each member is
                    % field with the new name Bus.Member.
                    subElementFields = fields(subElement);
                    if ~ismember('name', subElementFields)
                        subElements = subElement;
                        for idy=1:length(subElementFields)
                            subElementNameNew = [subElementName '.' subElementFields{idy}];
                            subElement = subElements.(subElementFields{idy});
                            str = [str indent(['"' subElementNameNew '": '], indentLevel)];
                            str = recursiveStringGen(subElementNameNew, subElement, str, indentLevel + 1);
                            if idy ~= length(subElementFields)
                                str = sprintf('%s,\n', str);
                            end
                        end
                    else
                        str = [str indent(['"' subElementName '": '], indentLevel)];
                        str = recursiveStringGen(subElementName, subElement, str, indentLevel + 1);
                    end
                else
                    str = [str indent(['"' subElementName '": '], indentLevel)];
                    str = recursiveStringGen(subElementName, subElement, str, indentLevel + 1);
                end

                if idx ~= subElemsLen
                    str = sprintf('%s,\n', str);
                else
                    str = sprintf('%s}', str);
                end
            end
        end
        res = str;
        return
    elseif iscell(element)
        elemLen = length(element);
        if elemLen == 0
            str = sprintf('%s[]', str);
        else
           str = sprintf('%s[\n', str);
           for idx=1:elemLen
               str = [str indent('', indentLevel)];
               str = recursiveStringGen('', element{idx}, str, indentLevel + 1);
               if idx ~= elemLen
                   str = sprintf('%s,\n', str);
               else
                   str = sprintf('%s]', str);
               end
            end
        end
        res = str;
        return
    elseif ischar(element)
       % replace line feeds with spaces, and " with '
       % as this is not supported inn JSON
        elemTmp = strrep(element,'"','''');
        newline = sprintf('\n');
        elemTmp = strrep(elemTmp, newline, ' ');
        % replace single \ with \\, as a single \ is interpreted as escape
        elemTmp = regexprep(elemTmp, '(?<!\\)\\(?!\\)', '\\\\');
        str = [str '"' elemTmp '"'];
        res = str;
        return
    elseif isscalar(element)
        str = [str num2str(element)];
        res = str;
        return
    elseif isvector(element)
        tmp = regexprep(num2str(element(1,:)),'\s+',', ');
        str = [str '[' tmp ']'];
        res = str;
        return
    elseif ismatrix(element)
        if isempty(element)
            str = [str '""'];
        else
            str = [str 'Not Implemented'];
        end
        res = str;
        return
    end
end

function outStr = indent(str, indentLevel)
    %function that returns a string with 2 spaces per indent level
    tmp = '';
    for i=1:indentLevel
        tmp = [tmp '  '];
    end
    outStr = [tmp str];
end
