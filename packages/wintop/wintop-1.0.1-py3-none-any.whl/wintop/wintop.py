# -*- coding: utf-8 -*-
"""
WinTop--Windows System Monitor
"""

import psutil
import time
import os
import sys
from datetime import datetime

class WinTop:
    CLEAR_SCREEN = "\033[2J"
    CURSOR_HOME  = "\033[H"
    CURSOR_HIDE  = "\033[?25l"
    CURSOR_SHOW  = "\033[?25h"
    CLEAR_LINE   = "\033[K"
    
    def __init__(self, update_interval=1.5, process_limit=20):
        self.update_interval = update_interval
        self.process_limit = process_limit
        self.running = True
        self.move_cursor  = lambda r, c: f"\033[{r};{c}H"

        self.io_cache = {}
        self.last_process_count = 0
        self.screen_buffer = {}

    def format_bytes(self, b):
        if b == 0:
            return "   0B"
        for u in ['B', 'K', 'M', 'G', 'T']:
            if b < 1024.0:
                return f"{b:5.1f}{u}"
            b /= 1024.0
        return f"{b:5.1f}P"

    def format_rate(self, bps):
        if bps < 1024:
            return f"{int(bps):6.0f}B/s"
        elif bps < 1024 * 1024:
            return f"{bps/1024:6.1f}K/s"
        elif bps < 1024 * 1024 * 1024:
            return f"{bps/1024/1024:6.1f}M/s"
        else:
            return f"{bps/1024/1024/1024:6.1f}G/s"

    def get_system_info(self):
        sys_cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        
        total_disk_space, used_disk_space = 0, 0
        try:
            for part in psutil.disk_partitions(all=False):
                if 'removable' not in part.opts and 'cdrom' not in part.opts and part.fstype:
                    usage = psutil.disk_usage(part.mountpoint)
                    total_disk_space += usage.total
                    used_disk_space += usage.used
            disk_percent = (used_disk_space / total_disk_space * 100) if total_disk_space > 0 else 0
            disk = psutil._common.sdiskusage(
                total=total_disk_space, used=used_disk_space, free=total_disk_space - used_disk_space, percent=disk_percent
            )
        except (PermissionError, FileNotFoundError):
            disk = psutil.disk_usage('C:\\')

        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()

        return {
            'cpu': {'percent': sys_cpu, 'cores': psutil.cpu_count()},
            'memory': {'total': mem.total, 'used': mem.used, 'percent': mem.percent},
            'disk': disk, 'disk_io': disk_io, 'net_io': net_io
        }

    def get_processes_with_io(self, limit=20):
        procs_with_cpu = []
        pids_alive = set()
        for p in psutil.process_iter(['pid']):
            try:
                if p.info['pid'] == 0: continue
                cpu = p.cpu_percent(interval=None) or 0.0
                procs_with_cpu.append((cpu, p))
                pids_alive.add(p.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        pids_in_cache = set(self.io_cache.keys())
        pids_dead = pids_in_cache - pids_alive
        for pid in pids_dead:
            del self.io_cache[pid]
            
        procs_with_cpu.sort(key=lambda x: x[0], reverse=True)

        top_procs = procs_with_cpu[:limit]
        
        results = []
        now = time.time()
        for cpu, p in top_procs:
            try:
                pid = p.pid
                cpu_pct_global = cpu / psutil.cpu_count()
                
                with p.oneshot():
                    name = p.name() or 'Unknown'
                    mem_info = p.memory_info()
                    io = p.io_counters()

                mem_mb = mem_info.rss / 1024 / 1024
                dr, dw = io.read_bytes, io.write_bytes

                if pid in self.io_cache:
                    pt, pr, pw = self.io_cache[pid]
                    dt = now - pt
                    dr_rate = max(0, (dr - pr) / dt) if dt > 0 else 0
                    dw_rate = max(0, (dw - pw) / dt) if dt > 0 else 0
                else:
                    dr_rate = dw_rate = 0
                self.io_cache[pid] = (now, dr, dw)

                results.append({
                    'pid': pid, 'name': name, 'memory_mb': mem_mb, 'cpu': cpu_pct_global,
                    'disk_read_rate': dr_rate, 'disk_write_rate': dw_rate
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return results

    def update_line(self, ln, txt):
        cur = self.screen_buffer.get(ln, "")
        if cur != txt:
            sys.stdout.write(self.move_cursor(ln, 1) + txt + self.CLEAR_LINE)
            self.screen_buffer[ln] = txt

    def draw_header(self):
        lines = ["=" * 95,
                 "WinTop - Windows System Monitor".center(95),
                 "=" * 95, ""]
        for i, l in enumerate(lines, 1):
            self.update_line(i, l)

    def draw_system_info(self, info):
        now = time.time()
        disk_io = info['disk_io']
        if hasattr(self, '_last_disk'):
            dt = now - self._last_disk['t']
            dr_rate = max(0, (disk_io.read_bytes - self._last_disk['dr']) / dt) if dt else 0
            dw_rate = max(0, (disk_io.write_bytes - self._last_disk['dw']) / dt) if dt else 0
        else:
            dr_rate = dw_rate = 0
        self._last_disk = {'t': now, 'dr': disk_io.read_bytes, 'dw': disk_io.write_bytes}

        net_io = info['net_io']
        if hasattr(self, '_last_net'):
            dt = now - self._last_net['t']
            nr_rate = max(0, (net_io.bytes_recv - self._last_net['nr']) / dt) if dt else 0
            ns_rate = max(0, (net_io.bytes_sent - self._last_net['ns']) / dt) if dt else 0
        else:
            nr_rate = ns_rate = 0
        self._last_net = {'t': now, 'nr': net_io.bytes_recv, 'ns': net_io.bytes_sent}

        lines = [
            f"CPU: {info['cpu']['percent']:6.2f}% ({info['cpu']['cores']} cores)",
            f"MEM: {info['memory']['percent']:6.2f}% ({self.format_bytes(info['memory']['used'])} / {self.format_bytes(info['memory']['total'])})",
            f"DISK(Total): {info['disk'].percent:6.2f}% ({self.format_bytes(info['disk'].used)} / {self.format_bytes(info['disk'].total)})",
            f"DISK I/O: R:{self.format_rate(dr_rate)} | W:{self.format_rate(dw_rate)}",
            f"NET  I/O: R:{self.format_rate(nr_rate)} | W:{self.format_rate(ns_rate)}",
            "-" * 95
        ]
        start_line = 5
        for i, l in enumerate(lines): self.update_line(start_line + i, l)
        return start_line + len(lines)

    def draw_processes(self, procs, start_line):
        header = f"{'PID':>7} {'Process':<30} {'Mem(MB)':>15} {'CPU%':>6} {'Disk Read':>18} {'Disk Write':>12}"
        self.update_line(start_line, header)
        self.update_line(start_line + 1, "-" * 95)

        cur = start_line + 2
        for i, p in enumerate(procs):
            name = p['name'][:30] if len(p['name']) > 30 else p['name'] 
            line = (f"{p['pid']:>7} "
                    f"{name:<35} "
                    f"{p['memory_mb']:>9.1f} "
                    f"{p['cpu']:>6.1f} "
                    f"{self.format_rate(p['disk_read_rate']):>15} "
                    f"{self.format_rate(p['disk_write_rate']):>15}")
            self.update_line(cur + i, line)

        for i in range(len(procs), self.last_process_count): self.update_line(cur + i, "")
        self.last_process_count = len(procs)
        return cur + len(procs)

    def draw_footer(self, ln):
        self.update_line(ln, "-" * 95)
        self.update_line(ln + 1, f"Ctrl+C to Quit, Updated:{datetime.now().strftime('%H:%M:%S')}")

    def initialize_screen(self):
        sys.stdout.write(self.CLEAR_SCREEN + self.CURSOR_HOME + self.CURSOR_HIDE)
        sys.stdout.flush()
        self.screen_buffer.clear()

    def restore_screen(self):
        sys.stdout.write(self.CURSOR_SHOW + self.move_cursor(30, 1))
        sys.stdout.flush()

    def run(self):
        try:
            self.initialize_screen()
            psutil.cpu_percent(interval=None) 
            for p in psutil.process_iter():
                try: p.cpu_percent(interval=None)
                except psutil.Error: pass
            time.sleep(self.update_interval)

            while self.running:
                info = self.get_system_info()
                procs = self.get_processes_with_io(limit=self.process_limit)
                self.draw_header()
                sys_end = self.draw_system_info(info)
                proc_end = self.draw_processes(procs, sys_end + 1)
                self.draw_footer(proc_end)
                sys.stdout.flush()
                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            pass
        finally:
            self.restore_screen()

def main():
    try:
        import psutil
    except ImportError:
        print("Error:  'psutil' not found.")
        print("Use 'pip install psutil' to install psutil pls.")
        return
    
    if os.name == 'nt': os.system('')
        
    WinTop(update_interval=1.0, process_limit=20).run()

if __name__ == "__main__":
    main()