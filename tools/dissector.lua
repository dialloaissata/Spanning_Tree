local custom_bpdu = Proto("custombpdu", "Custom BPDU")

-- Function to dissect the customstp protocol
function custom_bpdu.dissector(buffer, pinfo, tree)
    -- Set protocol name in the UI
    pinfo.cols.protocol = "Custom BPDU"
    pinfo.cols.info =
        string.format("%d", buffer(0, 2):uint()) ..
        "." .. tostring(buffer(2, 6):ether()) .. "-" .. string.format("%d", buffer(8, 4):uint())

    -- Parse BPDU
    local subtree = tree:add(custom_bpdu, buffer(0, 22), "Custom BPDU " .. 
        string.format("%d", buffer(0, 2):uint()) ..
        "." .. tostring(buffer(2, 6):ether()) .. "-" .. string.format("%d", buffer(8, 4):uint()))

    local root_id = subtree:add(buffer(0, 8),
        "Root ID, Priority: " .. string.format("%d", buffer(0, 2):uint()) ..
        ", Addr: " .. tostring(buffer(2, 6):ether()))
    root_id:add(buffer(0, 2), "Root priority: " .. string.format("%d", buffer(0, 2):uint()))
    root_id:add(buffer(2, 6), "Root address: " .. tostring(buffer(2, 6):ether()))

    subtree:add(buffer(8, 4), "Cost: " .. string.format("%d", buffer(8, 4):uint()))

    local bridge_id = subtree:add(buffer(12, 8),
        "Bridge ID, Priority: " ..
        string.format("%d", buffer(12, 2):uint()) .. ", Addr: " .. tostring(buffer(14, 6):ether()))
    bridge_id:add(buffer(12, 2), "Bridge priority: " .. string.format("%d", buffer(12, 2):uint()))
    bridge_id:add(buffer(14, 6), "Bridge address: " .. tostring(buffer(14, 6):ether()))

    subtree:add(buffer(20, 2), "Port ID: " .. string.format("%d", buffer(20, 2):uint()))

end

local cpu_comm = Proto("cpucomm", "CPU Communication")

function cpu_comm.dissector(buffer, pinfo, tree)
    pinfo.cols.protocol = "CPU Communication"
    -- Parse CPU Communication
    local subtree = tree:add(cpu_comm, buffer(0, 4), "CPU Communication")
    subtree:add(buffer(0, 2), "Port: 0x" .. string.format("%02x", buffer(0, 2):uint()))
    subtree:add(buffer(2, 2), "Type: 0x" .. string.format("%02x", buffer(2, 2):uint()))

    -- Get dissector base on type
    local ethertype_table = DissectorTable.get("ethertype")
    local sub_dissector = ethertype_table:get_dissector(buffer(2, 2):uint())

    if (sub_dissector ~= nil) then
        sub_dissector(buffer(4):tvb(), pinfo, tree)
    else
        local data = tree:add(cpu_comm, buffer(4), string.format("Data (%d bytes)", buffer(4):len()))
        data:add(buffer(4), "Data: " .. buffer(4):bytes():tohex())
        data:add(string.format("[Length: %d]", buffer(4):len()))
    end
end

-- Add protocols in DissectorTable
local ethertype_table = DissectorTable.get("ethertype")
ethertype_table:add(0x8042, custom_bpdu)
ethertype_table:add(0x8043, cpu_comm)
