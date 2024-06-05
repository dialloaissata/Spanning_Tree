/* -*- P4_16 -*- */

#ifndef PARSERS_T
#define PARSERS_T

#include <core.p4>
#include <v1model.p4>

#include "headers.p4"

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
    out headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            ETHERNET_TYPE_STP: parse_stp;
            ETHERNET_TYPE_CPU: parse_cpu;
            default: accept;
        }
    }

    state parse_cpu {
        packet.extract(hdr.cpu);
        transition accept;
    }

    state parse_stp {
        packet.extract(hdr.stp);
        transition accept;
    }
}

#endif
