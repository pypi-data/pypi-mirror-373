% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function Outport = moveDefOutports(top_system)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Replace the top level TL-outports with simulink outports, and
%% define a new TL-outport in the innermost level outport
%% so that the port will be removed if it is within
%% preprocessor directive
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	%TODO: Check if only ports att the top system shall be considered
    tlOutports = find_system(top_system, 'FindAll', 'on', 'LookUnderMasks', 'all', ...
                            'SearchDepth', 1,'MaskType', 'TL_Outport');
    for i=1:length(tlOutports)
        moveDefOutport(tlOutports(i))
    end

end

function Outport = moveDefOutport(outport)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Unenhance the TL-outport, and
%% define a new TL-outport in the lowest level outport ->
%% that the port will be removed if the port is within
%% preprocessor directive
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %% remove outport and add terminator
    lowLevelOutport = getDefOutport(outport);
    if lowLevelOutport == -1
        return
    end
    srcBlkCodeSw = getCodeSwitches(lowLevelOutport);
    if ~strcmp(srcBlkCodeSw, 'all')
        ll_parent = get_param(lowLevelOutport, 'Parent');
        ll_name = get_param(lowLevelOutport, 'Name');
        ll_pn_str = get_param(lowLevelOutport, 'Port');
        ll_pn = str2double(ll_pn_str);
        llp_phs = get_param(ll_parent, 'PortHandles');
        llp_ph = llp_phs.Outport(ll_pn);
        ll_line = get_param(llp_ph, 'Line');
        ll_line_name = get_param(ll_line, 'Name');
        dst_phs = get_param(ll_line, 'DstPortHandle');

        % Replace inner simulink-port with new encapsulated TL-port from
        % Vcc_Lib
        new_blk_tmp = replace_block(ll_parent, 'SearchDepth' ,1, 'Name', ll_name, ...
                                      'Vcc_Lib/Signals and systems/EncapsulatedOut', 'noprompt');
        new_blk = new_blk_tmp{1};
        set_param(new_blk, 'LinkStatus', 'none');

        % Replace inner TL-port with original TL-port
        new_port_tmp = replace_block([new_blk '/EncapsulatedSubsystem'], 'SearchDepth' ,1, 'Name', 'Out', getPath(outport), 'noprompt');
        new_port = new_port_tmp{1};

        % Reconnect lines
        tmp_lines = find_system(new_blk, 'FindAll', 'on', 'Type', 'Line');
        for line = tmp_lines'
            line_parent = get_param(line, 'Parent');
            line_points = get_param(line, 'Points');
            delete_line(line);
            add_line(line_parent, line_points);
        end

        % Replace unconnected lines with ground block
        for tmp_dst = dst_phs'
            tmp_parent = get_param(ll_parent, 'Parent');
            tmp_lines = find_system(tmp_parent, 'FindAll', 'on', 'SearchDepth', 1, ...
                                   'Type', 'line', 'SrcPortHandle', -1);
            if ~isempty(tmp_lines)
                tmp_line_dsts = get_param(tmp_lines, 'DstPortHandle');
                delete_line(tmp_lines);
                for line_dst = tmp_line_dsts
                    tmp_pos = get_param(line_dst, 'Position');
                    tmp_pos = repmat(tmp_pos, 1, 2) + [-30 -10 -10 10];
                    h = add_block('simulink/Sources/Ground', [tmp_parent '/Ground'], ...
                                  'MakeNameUnique', 'on', 'Position', tmp_pos);
                    tmp_ph = get_param(h, 'PortHandles');
                    add_line(tmp_parent, tmp_ph.Outport(1), line_dst);
                end
            end
        end

        % Un-enhance old outer TL-port to simulink-port
        dummy = tl_unenhance_block(outport, struct('bSaveTLData',0));
    end
end
