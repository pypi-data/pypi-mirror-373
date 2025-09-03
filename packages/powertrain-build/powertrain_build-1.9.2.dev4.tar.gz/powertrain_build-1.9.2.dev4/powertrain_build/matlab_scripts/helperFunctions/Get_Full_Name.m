% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% File name: Get_full_Name 
%% Author: Johan Backmark
%% Date: 2008/04/24
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Description: This tl_get takes in a Macro and returns the whole code
%% name
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


function Macro = Get_Full_Name(Handle,Macro,TLSystem)

if ~isempty(findstr(Macro,'$L'))
    %get_param(Handle,'masktype')
    if ismember(get_param(Handle,'masktype'),{'TL_Outport', 'TL_BusOutport'})
        Line=Get_SrcLines(Handle);
        LineName=get(Line,'name');
        if isempty(LineName)
            SrcPortHandle = get(Line,'SrcPortHandle');
            
            if SrcPortHandle ~= -1
                LineName=get(SrcPortHandle,'PropagatedSignals');
            else
                error(['Outport cannot follow source line "' get_param(Handle, 'Name') '" in model "' get_param(Handle, 'Parent') '"']);
            end
        end
        Macro=strrep(Macro,'$L',LineName);
    else
        Macro=strrep(Macro,'$L',get(getDstLines(Handle),'name'));
    end
end

if ~isempty(findstr(Macro,'$N'))
    Macro=strrep(Macro,'$N',TLSystem);
end
if ~isempty(findstr(Macro,'$B'))
    Macro=strrep(Macro,'$B',get_param(Handle,'name'));
end
if ~isempty(findstr(Macro,'$S'))
    Parent=get_param(Handle,'Parent');
    Backslash=strfind(Parent,'/');
    Macro=strrep(Macro,'$S',Parent(Backslash(end)+1:end));
end
