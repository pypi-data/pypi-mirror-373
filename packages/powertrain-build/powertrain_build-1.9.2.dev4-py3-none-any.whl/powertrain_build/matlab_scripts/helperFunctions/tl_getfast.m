% Copyright 2024 Volvo Car Corporation
% Licensed under Apache 2.0.

function Ans = tl_get(Handles,Field)

if isempty(Handles)
    Ans=[];
    return;
end

if iscell(Handles)
    for i=1:length(Handles)
        HTemp(i,1)=get_param(Handles{i},'handle');
    end
    Handles=HTemp;
elseif ischar(Handles)
    Handles=get_param(Handles,'handle');
end

Dot=strfind(Field,'.');

if ~isempty(Dot)
    Before=Field(1:Dot-1);
    After=Field(Dot+1:end);
end



if length(Handles)==1
    Tmp = Read_Block_Data(Handles);
    if ~isempty(Dot)
        Ans=Tmp.(Before).(After);
    else
        Ans=Tmp.(Field);
    end
else
Ans={};
    for i=1:length(Handles)
        Tmp = Read_Block_Data(Handles(i));
        if ~isempty(Dot)
            Ans{i,1}=Tmp.(Before).(After);
        else
            Ans{i,1}=Tmp.(Field);
        end
    end
end


function Data = Read_Block_Data(Handle)


BlockType = get_param(Handle, 'MaskType');
DataStr = get_param(Handle, 'data');
Data = eval(DataStr, '[]');
if ~isempty(tl_manage_blockset('GetDataDescription',BlockType))
    Data = tl_supplement_data_struct(Data, BlockType);
end

switch get_param(Handle,'masktype')
    case 'TL_Constant'
        Data.output.value=get_param(Handle,'value');
    case 'TL_IndexSearch'
        Data.input.value=get_param(Handle,'bpData');
    case 'TL_Prelookup'
        Data.input.value=get_param(Handle,'BreakpointsData');
    case 'TL_Interpolation'
        Data.table.value=get_param(Handle,'table');
    case 'TL_Interpolation_n-D'
        Data.table.value=get_param(Handle,'Table');
end


if strcmp(BlockType,'TL_Rescaler')
    Data.output.value=tl_get(Handle,'output.value');
end



try
Data.output.width=str2double(get_param(Handle,'PortDimensions'));
catch
end







