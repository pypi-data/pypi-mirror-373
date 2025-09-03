% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function macro = getName(handle, macro)

    if nargin == 1
        macro = tl_get(handle, 'output.name');
    end
    tmp_system = get_param(handle, 'Parent');
    idx = strfind(tmp_system, '/');
    TLSystem = tmp_system(1:idx(1)-1);
    if ~isempty(strfind(macro,'$L'))
        %get_param(Handle,'masktype')
        if ismember(get_param(handle,'masktype'),{'TL_Outport', 'TL_BusOutport'})
            line=getSrcLines(handle);
            lineName=get(line,'name');
            if isempty(lineName)
                lineName=get(get(line,'SrcPortHandle'),'PropagatedSignals');
            end
            macro=strrep(macro,'$L',lineName);
        else
            macro=strrep(macro,'$L',get(getDstLines(handle),'name'));
        end
    end

    if ~isempty(strfind(macro,'$N'))
        macro=strrep(macro,'$N',TLSystem);
    end
    if ~isempty(strfind(macro,'$B'))
        macro=strrep(macro,'$B',get_param(handle,'name'));
    end
    if ~isempty(strfind(macro,'$S'))
        parent=get_param(handle,'Parent');
        backslash=strfind(parent,'/');
        macro=strrep(macro,'$S',parent(backslash(end)+1:end));
    end
end
