/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4  = 0x800;
const bit<16> TYPE_ARP  = 0x806;
const bit<16> TYPE_PROBE = 0x102;

#define MAX_HOPS 5
#define MAX_PORTS 16

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<11> switchID_t;
typedef bit<48> time_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header srcRoute_t {
    bit<1>    bos;
    bit<7>   port;
}

header int_data_t {
    switchID_t switch_id;   // 凑8的倍数
    bit<9> ingress_port;    
    bit<9> egress_port;     
    bit<48> hop_latency;    // 在这一跳耽误的时间
    bit<19> deq_qdepth;
    bit<32> deq_timedelta;
    bit<32>   byte_cnt;
    time_t    last_time;
    time_t    cur_time;
}


header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}


header arp_t {
    bit<16> arpHdr;     /* format of hardware address */
    bit<16> arpPro;     /* format of protocol address */
    bit<8>  arpHln;     /* length of hardware address */
    bit<8>  arpPln;     /* length of protocol address */
    bit<16> arpOp;      /* ARP/RARP operation */
    bit<48> arpSha;     /* sender hardware address */
    bit<32> arpSpa;     /* sender protocol address */
    bit<48> arpTha;     /* target hardware address */
    bit<32> arpTpa;     /* target protocol address */
}

struct metadata {
    switchID_t switch_id;
}


struct headers {
    ethernet_t              ethernet;
    arp_t                   arp;
    srcRoute_t[MAX_HOPS]    srcRoutes;
    int_data_t              intdata;
    ipv4_t                  ipv4;
}

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
            TYPE_IPV4: parse_ipv4;
            TYPE_ARP: parse_arp;
            TYPE_PROBE: parse_srcRouting;
            default: accept;
        }
    }

    state parse_arp {
        packet.extract(hdr.arp);
        transition accept;
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }

    state parse_srcRouting {
        packet.extract(hdr.srcRoutes.next);
        transition select(hdr.srcRoutes.last.bos) {
            1: accept;
            default: parse_srcRouting;
        }
    }
}

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

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, bit<7> port) {
        standard_metadata.egress_spec = (bit<9>)port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action srcRoute_nhop() {
        standard_metadata.egress_spec = (bit<9>)hdr.srcRoutes[0].port;
        hdr.srcRoutes.pop_front(1);
    }

    // 不在最后将类型改回ipv4，sniff 就看不到首部了，只能看到负载，导致只能用原始socket接收，有点麻烦。
    action srcRoute_finish() {
        hdr.ethernet.etherType = TYPE_IPV4;
    }

    action arpreply(bit<48>repmac) {
        standard_metadata.egress_spec = standard_metadata.ingress_port;
        standard_metadata.egress_port = standard_metadata.ingress_port;
        hdr.ethernet.srcAddr=repmac;
        hdr.ethernet.dstAddr=hdr.arp.arpSha;
        bit<32> tempip;
        tempip=hdr.arp.arpSpa;
        hdr.arp.arpSpa=hdr.arp.arpTpa;
        hdr.arp.arpTpa=tempip;
        hdr.arp.arpTha=hdr.arp.arpSha;
        hdr.arp.arpSha=repmac;
    }

    table doarp {
        actions = {
            arpreply;
            NoAction;
        }
        key = {
            hdr.arp.arpTha:exact;
            hdr.arp.arpTpa:exact;
        }
        default_action=NoAction();
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    apply{
        if(hdr.ipv4.isValid()){
            ipv4_lpm.apply();
        }else if(hdr.srcRoutes[0].isValid()){
            if(hdr.srcRoutes[0].bos == 1){
                // 不在最后将类型改回ipv4，sniff 就看不到首部了，只能看到负载，导致只能用原始socket接收，有点麻烦。
                srcRoute_finish();
            }
                srcRoute_nhop();
        }else if(hdr.arp.isValid()){
             doarp.apply();
        }else{
            drop();
        }
    }

}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   ********************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    // count the number of bytes seen since the last probe
    register<bit<32>>(MAX_PORTS) byte_cnt_reg;
    // remember the time of the last probe
    register<time_t>(MAX_PORTS) last_time_reg;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action setSwitchId(switchID_t switch_id){
        meta.switch_id = switch_id;
    }

    table switchId {
        actions = {
            setSwitchId;
            NoAction;
        }
        default_action=NoAction();
    }

    apply{
        switchId.apply();

        bit<32> byte_cnt;
        bit<32> new_byte_cnt;
        time_t last_time;
        time_t cur_time = standard_metadata.egress_global_timestamp;
        // increment byte cnt for this packet's port
        byte_cnt_reg.read(byte_cnt, (bit<32>)standard_metadata.egress_port);
        byte_cnt = byte_cnt + standard_metadata.packet_length;
        // reset the byte count when a probe packet passes through
        new_byte_cnt = (hdr.ethernet.etherType == TYPE_PROBE) ? 0 : byte_cnt;
        byte_cnt_reg.write((bit<32>)standard_metadata.egress_port, new_byte_cnt);

        if (hdr.ethernet.etherType == TYPE_PROBE) {
            hdr.intdata.setValid();
            hdr.intdata.switch_id = meta.switch_id;
            hdr.intdata.ingress_port = standard_metadata.ingress_port;
            hdr.intdata.egress_port = standard_metadata.egress_port;
            hdr.intdata.hop_latency = standard_metadata.egress_global_timestamp - standard_metadata.ingress_global_timestamp;
            hdr.intdata.deq_qdepth = standard_metadata.deq_qdepth;
            hdr.intdata.deq_timedelta = standard_metadata.deq_timedelta;
            hdr.intdata.byte_cnt = byte_cnt;
            // read / update the last_time_reg
            last_time_reg.read(last_time, (bit<32>)standard_metadata.egress_port);
            last_time_reg.write((bit<32>)standard_metadata.egress_port, cur_time);
            hdr.intdata.last_time = last_time;
            hdr.intdata.cur_time = cur_time;
        }
    }

}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   ***************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.arp);
        packet.emit(hdr.srcRoutes);
        packet.emit(hdr.intdata);
        packet.emit(hdr.ipv4);
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