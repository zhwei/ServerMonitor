/proc/meminfo 输出详解
=======================

$ cat /proc/meminfo

    MemTotal: 24675128 kB
    MemFree: 1017340 kB
    Buffers: 172424 kB
    Cached: 9777444 kB
    SwapCached: 572784 kB
    Active: 16491440 kB
    Inactive: 6170608 kB
    HighTotal: 0 kB
    HighFree: 0 kB
    LowTotal: 24675128 kB
    LowFree: 1017340 kB
    SwapTotal: 34996216 kB
    SwapFree: 32120548 kB
    Dirty: 276 kB
    Writeback: 0 kB
    AnonPages: 12699740 kB
    Mapped: 50432 kB
    Slab: 898396 kB
    PageTables: 39956 kB
    NFS_Unstable: 0 kB
    Bounce: 0 kB
    CommitLimit: 47333780 kB
    Committed_AS: 19160488 kB
    VmallocTotal: 34359738367 kB
    VmallocUsed: 280808 kB
    VmallocChunk: 34359457531 kB


    MemTotal: 所有可用RAM大小（即物理内存减去一些预留位和内核的二进制代码大小）
    MemFree: LowFree与HighFree的总和，被系统留着未使用的内存
    Buffers: 用来给文件做缓冲大小
    Cached: 被高速缓冲存储器（cache memory）用的内存的大小（等于 diskcache minus SwapCache ）.
    SwapCached:被高速缓冲存储器（cache memory）用的交换空间的大小，已经被交换出来的内存，但仍然被存放在swapfile中。用来在需要的时候很快的被替换而不需要再次打开I/O端口。
    Active: 在活跃使用中的缓冲或高速缓冲存储器页面文件的大小，除非非常必要否则不会被移作他用.
    Inactive: 在不经常使用中的缓冲或高速缓冲存储器页面文件的大小，可能被用于其他途径.
    HighTotal:暂无解释
    HighFree: 该区域不是直接映射到内核空间。内核必须使用不同的手法使用该段内存。
    LowTotal:暂无解释
    LowFree: 低位可以达到高位内存一样的作用，而且它还能够被内核用来记录一些自己的数据结构。
    SwapTotal: 交换空间的总大小
    SwapFree: 未被使用交换空间的大小
    Dirty: 等待被写回到磁盘的内存大小。
    Writeback: 正在被写回到磁盘的内存大小。
    AnonPages：未映射页的内存大小
    Mapped: 设备和文件等映射的大小。
    Slab: 内核数据结构缓存的大小，可以减少申请和释放内存带来的消耗。
    SReclaimable:可收回Slab的大小
    SUnreclaim：不可收回Slab的大小（SUnreclaim+SReclaimable＝Slab）
    PageTables：管理内存分页页面的索引表的大小。
    NFS_Unstable:不稳定页表的大小
    VmallocTotal: 可以vmalloc虚拟内存大小
    VmallocUsed: 已经被使用的虚拟内存大小。