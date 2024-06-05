/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "headers.p4"
#include "parsers.p4"

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    // Multicast the packet to a multicast groupe
    action set_mcast_grp(bit<16> group) {
        standard_metadata.mcast_grp = group;
    }

    // Drop a packet
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action handle_cpu_packet() {
        standard_metadata.egress_spec = (bit<9>) hdr.cpu.outPort;
        hdr.ethernet.etherType = hdr.cpu.etherType;
        hdr.cpu.setInvalid();
    }

    table handle_cpu {
        key = {
            standard_metadata.ingress_port : exact;
        }
        actions = {
            handle_cpu_packet;
            drop;
            NoAction;
        }
        default_action = NoAction;
    }

    // This table is used to dispatch the packets in the switch.
    // Setting the closed stp ports is done just by removing
    // the ports from all the multicast tables.
    table dispatch {
        key = {
            standard_metadata.ingress_port : exact;
        }
        actions = {
            set_mcast_grp;
            drop;
            NoAction;
        }
        default_action = NoAction;
    }

    // Forward the packet to a port
    action forward_to_cpu(bit<9> port) {
        hdr.cpu.setValid();
        hdr.cpu.outPort = (bit<16>) standard_metadata.ingress_port;
        hdr.cpu.etherType = hdr.ethernet.etherType;

        hdr.ethernet.etherType = ETHERNET_TYPE_CPU;
        standard_metadata.egress_spec = port;
        truncate((bit<32>) 40);
    }

    table send_to_control {
        key = {
            hdr.ethernet.etherType : exact;
        }
        actions = {
            forward_to_cpu;
            NoAction;
        }
        default_action = NoAction;
    }

    // Apply the table to the packet
    apply {
        switch (handle_cpu.apply().action_run) {
            NoAction: {
                switch (send_to_control.apply().action_run) {
                    NoAction: {
                        dispatch.apply();
                    }
                }
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply { }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.cpu);
        packet.emit(hdr.stp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
