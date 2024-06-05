/* -*- P4_16 -*- */

#ifndef HEADERS_T
#define HEADERS_T

#include <core.p4>
#include <v1model.p4>

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

const bit<16> ETHERNET_TYPE_STP = 0x8042;
const bit<16> ETHERNET_TYPE_CPU = 0x8043;

typedef bit<48> macAddr_t;
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16> etherType;
}

struct stpIdentifier_t {
    bit<16> priority;
    macAddr_t address;
}

header stp_t {
    stpIdentifier_t rootID;
    bit<32> rootCost;
    stpIdentifier_t bridgeID;
    bit<16> portID;
}

struct metadata {
}

header cpu_t {
    bit<16> outPort;
    bit<16> etherType;
}

struct headers {
    ethernet_t ethernet;
    cpu_t cpu;
    stp_t stp;
}

#endif