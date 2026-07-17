# CIC-IoT-2023 Notes:
test case;
    #data info:
        File used: Merged44.csv 
        Rows loaded: 10000
        Num Columns: 40

    #Cleaning: // Ml models cannot train properly with empty/missing/corrupted entries.
        replaced infinity values with NaN
        removed NaN values
        used dropna() // pandas function used to remove missing/empty values from data set.

        -only row 86070 got cleaned rate=inf. it had a label of DNS_SPOOFING // we can see which line is which by nan_rows = df[df.isnull().any(axis=1)]
    

    #Important Columns 
        Label column: Label  //this is what were gonna make ML learn to predict
        Protocol feature: Protocol Type //
        Timing feature: IAT
        Traffic rate feature: Rate
        
    #Labels found 
        DDOS-ICMP_FLOOD            15256
        DDOS-UDP_FLOOD             11439
        DDOS-TCP_FLOOD              9473
        DDOS-PSHACK_FLOOD           8749
        DDOS-RSTFINFLOOD            8749
        DDOS-SYN_FLOOD              8625
        DDOS-SYNONYMOUSIP_FLOOD     7711
        DOS-UDP_FLOOD               7009
        DOS-TCP_FLOOD               5631
        DOS-SYN_FLOOD               4409
        BENIGN                      2323
        MIRAI-GREETH_FLOOD          2074
        MIRAI-UDPPLAIN              1954
        MIRAI-GREIP_FLOOD           1640
        DDOS-ICMP_FRAGMENTATION      948
        VULNERABILITYSCAN            788
        DDOS-ACK_FRAGMENTATION       647
        MITM-ARPSPOOFING             627
        DDOS-UDP_FRAGMENTATION       610
        DNS_SPOOFING                 369
        RECON-HOSTDISCOVERY          289
        RECON-OSSCAN                 197
        RECON-PORTSCAN               154
        DOS-HTTP_FLOOD               144
        DDOS-HTTP_FLOOD               62
        DDOS-SLOWLORIS                50
        DICTIONARYBRUTEFORCE          24
        COMMANDINJECTION              16
        BROWSERHIJACKING               7
        XSS                            7
        BACKDOOR_MALWARE               7
        RECON-PINGSWEEP                5
        SQLINJECTION                   4
        UPLOADING_ATTACK               3







# CIC-IDS-2017
test case:
    #data info:
        File used: ./TrafficLabelling /Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
        Rows loaded: 100000
        Num Columns: 85

    #Cleaning: // Ml models cannot train properly with empty/missing/corrupted entries.
        replaced infinity values with NaN
        removed NaN values
        #used dropna() // pandas function used to remove missing/empty values from data set.

        #-only row 86070 got cleaned rate=inf. it had a label of DNS_SPOOFING // we can see which line is which by nan_rows = df[df.isnull().any(axis=1)]
    

    #Important Columns 
        Label column: 
        Protocol feature: 
        Timing feature: 
        Traffic rate feature: 
        
    #Labels found:
        BENIGN          99982
        Infiltration       18

