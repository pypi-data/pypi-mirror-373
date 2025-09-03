% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function Data = Read_Units()
	% READ_UNITS Reads and return table in SPM_Units.xls sheet
	% This function reads using xlsxread 'basic' mode, which does not require
	% excel automation to run, i.e. it should never crash a server.

	% Turn off warning due to using xlsread in 'basic' mode
	wState = warning('off', 'MATLAB:xlsread:Mode');

	ex = [];
	try
	    [~, rawData] = xlsread('SPM_Units', 'Sheet1', '', 'basic');
	catch ex
	end

	% Restore warnings and re-raise possible errors
	warning(wState);
	if ~isempty(ex)
	    rethrow(ex);
	end

	% Find data columns
	[rHead, cAbbr] = find(strcmp(rawData, 'Abbreviation'), 1);
	[~,     cMean] = find(strcmp(rawData, 'Meaning'), 1);
	[~,     cUnit] = find(cellfun(@any, strfind(rawData, 'Unit')), 1); % contains 'Unit'

	% Find start of data: first value in abbreviation column
	rData = rHead + find(cellfun(@any, rawData(rHead+1:end,cAbbr)), 1);

	% Return data structure as cell array
	Data = strtrim(rawData(rData:end, [cAbbr, cMean, cUnit]));
end
