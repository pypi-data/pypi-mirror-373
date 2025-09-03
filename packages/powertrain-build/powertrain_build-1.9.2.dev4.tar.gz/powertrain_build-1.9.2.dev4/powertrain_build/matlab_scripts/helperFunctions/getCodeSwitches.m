% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function out = getCodeSwitches(handle, in)
    % recursivly find if there are any configuration switches affecting
    % the block "handle"
    if nargin == 1
        in = {};
    end
    parent = get_param(handle, 'Parent');
    if ~isempty(strfind(parent, '/'))
        ph = get_param(parent, 'PortHandles');
        if ~isempty(ph.Ifaction)
            l=get_param(ph.Ifaction,'Line');
            sbh=get_param(l,'SrcBlockHandle');
            sbp=get_param(l,'SrcPort');
            %hilite_system(sbh);
            mt=get_param(sbh,'MaskType');
            if strcmp(mt,'TL_PreProcessorIf')
                ports = get_param(sbh, 'PortHandles');
                l=get_param(ports.Inport, 'Line');
                blk = get_param(l, 'SrcBlockHandle');
                if strcmp(get_param(blk, 'BlockType'), 'Inport')
                    tmp=get_param(get_param(blk, 'Parent'), 'LineHandles');
                    blk=get_param(tmp.Inport(str2num(get_param(blk, 'Port'))), 'SrcBlockHandle');
                end
                if_exp = tl_get(sbh, 'ifexpression');
                if str2num(sbp)==2
                    if_exp = ['!(' if_exp ')'];
                end
                exp = strrep(if_exp,'u1',get_param(blk, 'const_name'));
                in = [in; exp];
            end
        elseif ~isempty(ph.Enable)
            l=get_param(ph.Enable,'Line');
            sbh=get_param(l,'SrcBlockHandle');
            mt=get_param(sbh,'MaskType');
            if strcmp(mt,'PreProcessorName')
                exp = get_param(sbh, 'const_name');
                in = [in; exp];
            end
        end
        in = getCodeSwitches(parent, in);
    end
    if length(in) > 0
        out = in;
    else
        out = {'all'};
    end
end
