"""
copy paste from psutil lib
"""

import os
import warnings
from collections import namedtuple

__all__ = [
    'virtual_memory',
    'process_memory_info',
    'process_memory_percent'
]

PROCFS_PATH = '/proc'
MEM_INFO = os.path.join(PROCFS_PATH, 'meminfo')
ZONE_INFO = os.path.join(PROCFS_PATH, 'zoneinfo')

PAGESIZE = os.sysconf('SC_PAGE_SIZE')

svmem = namedtuple('svmem', [
    'total', 'available', 'percent', 'used', 'free', 'active',
    'inactive', 'buffers', 'cached', 'shared', 'slab'])

pmem = namedtuple('pmem', 'rss vms shared text lib data dirty')


def usage_percent(used, total, round_=None):
    """Calculate percentage usage of 'used' against 'total'."""
    try:
        ret = (float(used) / total) * 100
    except ZeroDivisionError:
        return 0.0
    else:
        if round_ is not None:
            ret = round(ret, round_)
        return ret


def calculate_avail_vmem(mems):
    free = mems[b'MemFree:']
    fallback = free + mems.get(b"Cached:", 0)
    try:
        lru_active_file = mems[b'Active(file):']
        lru_inactive_file = mems[b'Inactive(file):']
        slab_reclaimable = mems[b'SReclaimable:']
    except KeyError:
        return fallback
    try:
        f = open(ZONE_INFO, 'rb')
    except IOError:
        return fallback  # kernel 2.6.13

    watermark_low = 0
    with f:
        for line in f:
            line = line.strip()
            if line.startswith(b'low'):
                watermark_low += int(line.split()[1])
    watermark_low *= PAGESIZE

    avail = free - watermark_low
    pagecache = lru_active_file + lru_inactive_file
    pagecache -= min(pagecache / 2, watermark_low)
    avail += pagecache
    avail += slab_reclaimable - min(slab_reclaimable / 2.0, watermark_low)
    return int(avail)


def virtual_memory():
    """Report virtual memory stats.
    This implementation matches "free" and "vmstat -s" cmdline
    utility values and procps-ng-3.3.12 source was used as a reference
    (2016-09-18):
    https://gitlab.com/procps-ng/procps/blob/
        24fd2605c51fccc375ab0287cec33aa767f06718/proc/sysinfo.c
    For reference, procps-ng-3.3.10 is the version available on Ubuntu
    16.04.

    Note about "available" memory: up until psutil 4.3 it was
    calculated as "avail = (free + buffers + cached)". Now
    "MemAvailable:" column (kernel 3.14) from /proc/meminfo is used as
    it's more accurate.
    That matches "available" column in newer versions of "free".
    """
    missing_fields = []
    mems = {}
    with open(MEM_INFO, 'rb') as f:
        for line in f:
            fields = line.split()
            mems[fields[0]] = int(fields[1]) * 1024

    # /proc doc states that the available fields in /proc/meminfo vary
    # by architecture and compile options, but these 3 values are also
    # returned by sysinfo(2); as such we assume they are always there.
    total = mems[b'MemTotal:']
    free = mems[b'MemFree:']
    try:
        buffers = mems[b'Buffers:']
    except KeyError:
        # https://github.com/giampaolo/psutil/issues/1010
        buffers = 0
        missing_fields.append('buffers')
    try:
        cached = mems[b"Cached:"]
    except KeyError:
        cached = 0
        missing_fields.append('cached')
    else:
        # "free" cmdline utility sums reclaimable to cached.
        # Older versions of procps used to add slab memory instead.
        # This got changed in:
        # https://gitlab.com/procps-ng/procps/commit/
        #     05d751c4f076a2f0118b914c5e51cfbb4762ad8e
        cached += mems.get(b"SReclaimable:", 0)  # since kernel 2.6.19

    try:
        shared = mems[b'Shmem:']  # since kernel 2.6.32
    except KeyError:
        try:
            shared = mems[b'MemShared:']  # kernels 2.4
        except KeyError:
            shared = 0
            missing_fields.append('shared')

    try:
        active = mems[b"Active:"]
    except KeyError:
        active = 0
        missing_fields.append('active')

    try:
        inactive = mems[b"Inactive:"]
    except KeyError:
        try:
            inactive = \
                mems[b"Inact_dirty:"] + \
                mems[b"Inact_clean:"] + \
                mems[b"Inact_laundry:"]
        except KeyError:
            inactive = 0
            missing_fields.append('inactive')

    try:
        slab = mems[b"Slab:"]
    except KeyError:
        slab = 0

    used = total - free - cached - buffers
    if used < 0:
        # May be symptomatic of running within a LCX container where such
        # values will be dramatically distorted over those of the host.
        used = total - free

    # - starting from 4.4.0 we match free's "available" column.
    #   Before 4.4.0 we calculated it as (free + buffers + cached)
    #   which matched htop.
    # - free and htop available memory differs as per:
    #   http://askubuntu.com/a/369589
    #   http://unix.stackexchange.com/a/65852/168884
    # - MemAvailable has been introduced in kernel 3.14
    try:
        avail = mems[b'MemAvailable:']
    except KeyError:
        avail = calculate_avail_vmem(mems)

    if avail < 0:
        avail = 0
        missing_fields.append('available')

    # If avail is greater than total or our calculation overflows,
    # that's symptomatic of running within a LCX container where such
    # values will be dramatically distorted over those of the host.
    # https://gitlab.com/procps-ng/procps/blob/
    #     24fd2605c51fccc375ab0287cec33aa767f06718/proc/sysinfo.c#L764
    if avail > total:
        avail = free

    percent = usage_percent((total - avail), total, round_=1)

    # Warn about missing metrics which are set to 0.
    if missing_fields:
        msg = "%s memory stats couldn't be determined and %s set to 0" % (
            ", ".join(missing_fields),
            "was" if len(missing_fields) == 1 else "were")
        warnings.warn(msg, RuntimeWarning)

    return svmem(total, avail, percent, used, free,
                 active, inactive, buffers, cached, shared, slab)


def process_memory_info(pid):
    with open(os.path.join(PROCFS_PATH, str(pid), 'statm'), 'rb') as f:
        vms, rss, shared, text, lib, data, dirty = \
            [int(x) * PAGESIZE for x in f.readline().split()[:7]]
    return pmem(rss, vms, shared, text, lib, data, dirty)


def process_memory_percent(pid, memtype="rss"):
    """
    Args:
        pid: process id
        memtype: rss vms shared text lib data dirty
    """
    metrics = process_memory_info(pid)
    value = getattr(metrics, memtype)
    total_phymem = virtual_memory().total
    return (value / float(total_phymem)) * 100
