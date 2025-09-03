% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function DID = parseDIDs(model_in)
% parseDIDs find all DID blocks in model
% returns a cell array with structs with DID information
%
% See also parseModelInfo
    DIDs_h = find_system(model_in, 'FindAll', 'on', 'LookUnderMasks', 'all', 'MaskType', 'DID');
    DID = struct();
    if ~isempty(DIDs_h)
        model = getTLModelName(model_in);
        outp_h = find_system(model_in, 'findall', 'on', 'lookundermasks', 'on', 'MaskType', 'TL_Outport');
        for i=1:length(DIDs_h)
            ports = get(DIDs_h(i), 'PortHandles');
            configs = getCodeSwitches(DIDs_h(i));
            l_h = get(ports.Inport, 'line');
            %Check if the signal is a propagated name
            %and find the original signal if it is
            tmp_sig_name = get(l_h, 'name');
            if isempty(tmp_sig_name)
                sp_h = get(l_h, 'SrcPortHandle');
                tmp_sig_name = get(sp_h, 'PropagatedSignals');
                if isempty(tmp_sig_name)
                    disp(['No signal name for block <a href = "matlab:Hilite_This_System(''' Get_Path(DIDs_h(i))...
                                    ''')">' Get_Path(DIDs_h(i)) '</a>'])
                    continue
                end
                ln_h_tmp = find_system(model_in, 'findall', 'on', 'lookundermasks', 'on', ...
                                       'type','line','name', tmp_sig_name);
                %Get one of the lines, as all have the same source block
                if length(ln_h_tmp) > 1
                    ln_h = ln_h_tmp(1);
                else
                    ln_h = ln_h_tmp;
                end
            else
                ln_h = l_h;
            end
            %find if there is a TL-outport with the signal name and it is
            % not a deafult port - if so use that port as the definition for the DID.
            found_outp_h = 0;
            for j=1:length(outp_h)
                oph = get(outp_h(j), 'PortHandles');
                opl_h = get(oph.Inport, 'line');
                sig_outp_name = get(opl_h, 'name');
                if isempty(sig_outp_name)
                    opp_h = get(opl_h, 'SrcPortHandle');
                    sig_outp_name = get(opp_h, 'PropagatedSignals');
                end
                if strcmp(tmp_sig_name,sig_outp_name)
                    found_outp_h = outp_h(j);
                    break
                else
                    found_outp_h = 0;
                end
            end

            if found_outp_h ~= 0
                sig_name = sig_outp_name;
                blk_name = [get(found_outp_h,'Parent') '/' get(found_outp_h,'Name')];
                sig_disc = tl_get(found_outp_h, 'output.description');
                data_type = tl_get(found_outp_h, 'output.type');
                unit = tl_get(found_outp_h, 'output.unit');
                offset = tl_get(found_outp_h, 'output.offset');
                lsb = tl_get(found_outp_h, 'output.lsb');
                min_v = tl_get(found_outp_h, 'output.min');
                max_v = tl_get(found_outp_h, 'output.max');
                tlclass = tl_get(found_outp_h, 'output.class');
            else
                %find TL-output name and expand the macro to a signal name
                src_blk_h = get(ln_h,'SrcBlockHandle');
                if strcmp(get_param(src_blk_h, 'MaskType'), 'TL_DataStoreRead')
                    parent = get(src_blk_h, 'Parent');
                    ds_name = tl_get(src_blk_h, 'Datastorename');
                    data_str = sprintf('.*?''name'',''%s''', ds_name);
                    src_blk_h = find_system(parent, 'findall', 'on', 'lookundermasks', 'on', ...
                                            'RegExp', 'on', 'MaskType', 'TL_DataStoreMemory', ...
                                            'data', data_str);
                end
                tl_outp_name = tl_get(src_blk_h, 'output.name');
                if isempty(tl_outp_name) % the upstream block has no tl.outputs (e.g. ports replaced by constants by scripts)
                    continue
                end
                % ToDo: add a check that no $B or $S is in the TL-name!
                % Remove _Tmp suffix from the model name
                [tok mat] = regexp(model ,'(.+?)_Tmp$', 'tokens');
                if mat > 0
                    model_tmp = tok{1};
                else
                    model_tmp = model;
                end
                tmp_name = regexprep(tl_outp_name, '\$N', model_tmp);
                sig_name = regexprep(tmp_name, '\$L', get(ln_h,'name'));
                %Store DID info in a struct
                blk_name = [get(src_blk_h,'Parent') '/' get(src_blk_h,'Name')];
                data_type = tl_get(src_blk_h, 'output.type');
                sig_disc = tl_get(src_blk_h, 'output.description');
                unit = tl_get(src_blk_h, 'output.unit');
                offset = tl_get(src_blk_h, 'output.offset');
                lsb = tl_get(src_blk_h, 'output.lsb');
                min_v = tl_get(src_blk_h, 'output.min');
                max_v = tl_get(src_blk_h, 'output.max');
                tlclass = tl_get(src_blk_h, 'output.class');
            end
            if strcmp('default', tlclass)
                disp(['Block creating signal has default class <a href = "matlab:Hilite_This_System(''' Get_Path(DIDs_h(i))...
                ''')">' Get_Path(DIDs_h(i)) '</a>'])
            else
                tmpDID = struct();
                tmpDID.handle = blk_name;
                tmpDID.name = sig_name;
                tmpDID.configs = configs;
                tmpDID.description = sig_disc;
                tmpDID.type = data_type;
                tmpDID.unit = unit;
                tmpDID.offset = offset;
                tmpDID.lsb = lsb;
                tmpDID.min = chkNan(min_v);
                tmpDID.max = chkNan(max_v);
                tmpDID.class = tlclass;
                DID.(tmpDID.name) = tmpDID;
            end
        end
    end
end

function res = chkNan(value)
% Function which replaces NaN or empty fields with '-'
    if ~ischar(value)
        if isnan(value)
            res = '-';
        elseif isempty(value)
            res = '-';
        else
            res = num2str(value);
        end
    else
        res = value;
    end
end
