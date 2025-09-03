% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function dstBlocks = getConsumerBlocks(startBlock, port)
%% Find the blocks where the Input port variable are consumed
%% Returns an array with blockids

    %Only use handles in this function
    if ischar(startBlock)
        startBlock = get_param(startBlock,'Handle');
    end
    dstBlocks = [];
    if nargin == 1
        %in = [];
        [dstBlks, dstPorts] = followLink(startBlock);
    else
        [dstBlks, dstPorts] = followLink(startBlock, port);
    end

    dstBlksLen = length(dstBlks);
    if dstBlksLen > 1
        for i=1:dstBlksLen
            res = getConsumerBlocks(dstBlks(i), dstPorts(i));
            dstBlocks = [dstBlocks res];
        end
    % only add a dst block if they exists.
    elseif dstBlks > 0
        dstBlocks = dstBlks;
    end
end
