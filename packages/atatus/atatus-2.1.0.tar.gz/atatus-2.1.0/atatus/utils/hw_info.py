import os
import sys
import subprocess


def _key_value_from_command(cmd, sep, successful_status=(0,)):
    d = {}
    for line in _command_by_line(cmd, successful_status=successful_status):
        l = [s.strip() for s in line.split(sep, 1)]
        if len(l) == 2:
            d[l[0]] = l[1]
    return d


def _command_by_line(cmd, successful_status=(0,)):
    ok, output = _getoutput(cmd, successful_status=successful_status)
    if not ok:
        return

    output = output.decode('ascii')

    for line in output.splitlines():
        yield line.strip()


def _getoutput(cmd, successful_status=(0,)):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        output, _ = p.communicate()
        status = p.returncode
    except EnvironmentError as e:
        return False, ''
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) in successful_status:
        return True, output
    return False, output


def darwin_hwinfo():
    hwinfo = {}
    hw = _key_value_from_command(['sysctl', 'hw'], sep=":")
    machdep_cpu = _key_value_from_command(['sysctl', 'machdep.cpu'], sep=":")
    cpu_count = 1
    cpu_freq = 0
    model_name = ""
    cpu_info = []
    mem_size = 0
    if hw:
        if 'hw.logicalcpu' in hw:
            cpu_count = int(hw['hw.logicalcpu'])
        if 'hw.cpufrequency' in hw:
            cpu_freq = hw['hw.cpufrequency']
        if 'hw.memsize' in hw:
            mem_size = int(hw['hw.memsize'])
    if machdep_cpu:
        if 'machdep.cpu.brand_string' in machdep_cpu:
            model_name = machdep_cpu['machdep.cpu.brand_string']
    for i in range(cpu_count):
        entry = {}
        entry["cores"] = 1
        entry["mhz"] = cpu_freq
        entry["model"] = model_name
        cpu_info.append(entry)

    hwinfo["cpu"] = cpu_info
    hwinfo["mem_size"] = mem_size
    return hwinfo


def linux_hwinfo():
    hwinfo = {}
    hwinfo["cpu"] = _linux_cpuinfo()
    hwinfo["mem_size"] = _linux_meminfo()
    bootid = _linux_bootid()
    if bootid:
        hwinfo["bootid"] = bootid
    return hwinfo


def _linux_bootid():
    try:
        fo = open('/proc/sys/kernel/random/boot_id')
    except EnvironmentError as e:
        return None
    else:
        bootid = fo.read().strip()
        fo.close()
        return bootid


def _linux_cpuinfo():
    try:
        fo = open('/proc/cpuinfo')
    except EnvironmentError as e:
        return [
            {
                "cores": "0",
                "mhz": 0,
                "model": "linux /proc/cpuinfo file not accessible"
            }
        ]
    else:
        info = [{}]
        for line in fo:
            name_value = [s.strip() for s in line.split(':', 1)]
            if len(name_value) != 2:
                continue
            name, value = name_value
            if not info or name in info[-1]:  # next processor
                info.append({})
            info[-1][name] = value
        fo.close()
        cpu_info = []
        for i in info:
            entry = {}
            entry["cores"] = 1
            if "cpu MHz" in i:
                entry["mhz"] = i["cpu MHz"]
            if "model name" in i:
                entry["model"] = i["model name"]
            cpu_info.append(entry)
        return cpu_info


def _linux_meminfo():
    try:
        fo = open('/proc/meminfo')
    except EnvironmentError as e:
        return -1
    else:
        info = [{}]
        for line in fo:
            name_value = [s.strip() for s in line.split(':', 1)]
            if len(name_value) != 2:
                continue
            name, value = name_value
            if not info or name in info[-1]:  # next processor
                info.append({})
            if value.endswith(' kB'):
                value = int(value[:-3])
                value = value * 1024  # to bytes
            info[-1][name] = value
        fo.close()
        mem_size = 0
        for i in info:
            if "MemTotal" in i:
                mem_size = i["MemTotal"]

        return mem_size


def default_hwinfo():
    hwinfo = {}
    hwinfo["cpu"] = [{
        "cores": "0",
        "mhz": 0,
        "model": sys.platform + " not supported"
    }]
    hwinfo["mem_size"] = 0
    return hwinfo
