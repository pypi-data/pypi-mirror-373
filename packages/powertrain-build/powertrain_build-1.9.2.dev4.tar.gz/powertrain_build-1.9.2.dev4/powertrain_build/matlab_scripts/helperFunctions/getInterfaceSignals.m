% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function interfaceSignals = getInterfaceSignals(rootFolder)
    activeInterfaceFiles = dir([rootFolder '/Projects/*/Config/ActiveInterfaces/*Output.csv']);
    disp('Reading active interface files');
    signalNameColumn = 2;
    signalMinColumn = 5;
    signalMaxColumn = 6;
    signalInitValueColumn = 9;
    signals = [];
    minimums = [];
    maximums = [];
    values = [];

    for fileIndex = 1:length(activeInterfaceFiles)
        interfaceFile = activeInterfaceFiles(fileIndex, :);
        filePath = fullfile(interfaceFile.folder, interfaceFile.name);
        disp(['Reading:' filePath])
        options = detectImportOptions(filePath);
        options.LineEnding = {'\r\n'};
        csvContent = readtable(filePath, options);
        signals = [signals; csvContent{:, signalNameColumn}];
        minimums = [minimums; csvContent{:, signalMinColumn}];
        maximums = [maximums; csvContent{:, signalMaxColumn}];
        values = [values; csvContent{:, signalInitValueColumn}];
        % Remove duplicate signals, hopefully, the initial values were the same...
        [signals, indices] = unique(signals, 'stable');
        minimums = minimums(indices);
        maximums = maximums(indices);
        values = values(indices);
    end

    replaceNaNs = isnan(values);
    values(replaceNaNs) = 0;
    interfaceSignals = horzcat(signals, num2cell(minimums), num2cell(maximums), num2cell(values));
end
