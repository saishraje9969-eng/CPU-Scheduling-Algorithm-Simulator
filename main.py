"""OSLab desktop GUI: CPU Scheduling Algorithm Simulator."""

import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from scheduler import run_algorithm, compare_algorithms


BG = "#101827"
PANEL = "#172235"
PANEL_ALT = "#1D2B42"
TEXT = "#EAF0FA"
MUTED = "#A8B5C9"
ACCENT = "#70A5FF"
COLORS = ["#4C8DFF", "#20BFA9", "#A78BFA", "#F59E0B", "#F472B6", "#22C55E", "#FB7185", "#38BDF8"]


class OSLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OSLab | CPU Scheduling Simulator")
        self.root.geometry("1280x850")
        self.root.minsize(1000, 700)
        self.root.configure(bg=BG)

        self.processes = []
        self.last_result = None
        self.last_comparison = []

        self.algorithm_var = tk.StringVar(value="FCFS")
        self.quantum_var = tk.StringVar(value="2")
        self.pid_var = tk.StringVar(value="P1")
        self.arrival_var = tk.StringVar(value="0")
        self.burst_var = tk.StringVar(value="5")
        self.priority_var = tk.StringVar(value="1")
        self.status_var = tk.StringVar(value="Ready. Add processes or load sample data.")

        self._configure_styles()
        self._build_ui()
        self.load_sample()

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=29, borderwidth=0)
        style.configure("Treeview.Heading", background=PANEL_ALT, foreground=TEXT,
                        relief="flat", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#294B78")],
                  foreground=[("selected", "white")])
        style.configure("TCombobox", fieldbackground=PANEL_ALT, background=PANEL_ALT,
                        foreground=TEXT, arrowcolor=TEXT)
        style.configure("Horizontal.TProgressbar", troughcolor=PANEL_ALT,
                        background=ACCENT, bordercolor=PANEL_ALT)

    def _label(self, parent, text, size=10, color=TEXT, bold=False):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def _button(self, parent, text, command, primary=False):
        return tk.Button(
            parent, text=text, command=command,
            bg=ACCENT if primary else PANEL_ALT,
            fg="#0B1424" if primary else TEXT,
            activebackground="#8AB6FF" if primary else "#2B3D58",
            activeforeground="#0B1424" if primary else TEXT,
            relief="flat", bd=0, padx=13, pady=8,
            font=("Segoe UI", 9, "bold"), cursor="hand2"
        )

    def _entry(self, parent, variable, width=9):
        return tk.Entry(parent, textvariable=variable, width=width,
                        bg=PANEL_ALT, fg=TEXT, insertbackground=TEXT,
                        relief="flat", bd=0, font=("Segoe UI", 10))

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=22, pady=(18, 10))
        tk.Label(header, text="OSLab", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 24, "bold")).pack(side="left")
        tk.Label(header, text="CPU Scheduling Simulator", bg=BG, fg=TEXT,
                 font=("Segoe UI", 17, "bold")).pack(side="left", padx=(12, 0))
        tk.Label(header, text="OPERATING SYSTEMS PROJECT", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="right", pady=12)

        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=22, pady=(0, 10))

        input_panel = tk.Frame(top, bg=PANEL, padx=14, pady=12)
        input_panel.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._label(input_panel, "PROCESS INPUT", 10, ACCENT, True).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))

        labels = [("Process ID", self.pid_var, 8), ("Arrival", self.arrival_var, 7),
                  ("Burst", self.burst_var, 7), ("Priority", self.priority_var, 7)]
        for col, (label, var, width) in enumerate(labels):
            self._label(input_panel, label, 9, MUTED).grid(row=1, column=col*2, sticky="w", padx=(0, 6))
            self._entry(input_panel, var, width).grid(row=2, column=col*2, sticky="w", padx=(0, 12), pady=(4, 9))
        self._button(input_panel, "＋ Add Process", self.add_process, True).grid(row=2, column=8, padx=3)
        self._button(input_panel, "Remove Selected", self.remove_selected).grid(row=2, column=9, padx=3)
        self._button(input_panel, "Load Sample", self.load_sample).grid(row=2, column=10, padx=3)

        run_panel = tk.Frame(top, bg=PANEL, padx=14, pady=12)
        run_panel.pack(side="right", fill="y")
        self._label(run_panel, "SIMULATION SETTINGS", 10, ACCENT, True).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        self._label(run_panel, "Algorithm", 9, MUTED).grid(row=1, column=0, sticky="w")
        self.algorithm_combo = ttk.Combobox(run_panel, textvariable=self.algorithm_var,
            values=["FCFS", "SJF", "SRTF", "Priority", "Round Robin"],
            state="readonly", width=16)
        self.algorithm_combo.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 8))
        self._label(run_panel, "Time quantum (Round Robin)", 9, MUTED).grid(row=3, column=0, sticky="w")
        self._entry(run_panel, self.quantum_var, 7).grid(row=3, column=1, sticky="e", padx=(8, 0))
        self._button(run_panel, "▶ Run Simulation", self.run_simulation, True).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self._button(run_panel, "Compare All Algorithms", self.compare_all).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(7, 0))

        middle = tk.Frame(self.root, bg=BG)
        middle.pack(fill="both", expand=True, padx=22, pady=(0, 10))

        process_panel = tk.Frame(middle, bg=PANEL, padx=12, pady=12)
        process_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self._label(process_panel, "PROCESS QUEUE", 10, ACCENT, True).pack(anchor="w", pady=(0, 8))
        process_cols = ("pid", "arrival", "burst", "priority")
        self.process_tree = ttk.Treeview(process_panel, columns=process_cols, show="headings", height=8)
        for col, title, width in [
            ("pid", "Process", 100), ("arrival", "Arrival", 90),
            ("burst", "Burst", 90), ("priority", "Priority", 90)
        ]:
            self.process_tree.heading(col, text=title)
            self.process_tree.column(col, width=width, anchor="center")
        self.process_tree.pack(fill="both", expand=True)

        result_panel = tk.Frame(middle, bg=PANEL, padx=12, pady=12)
        result_panel.pack(side="right", fill="both", expand=True)
        self._label(result_panel, "PERFORMANCE METRICS", 10, ACCENT, True).pack(anchor="w", pady=(0, 8))
        metric_grid = tk.Frame(result_panel, bg=PANEL)
        metric_grid.pack(fill="x")
        self.metric_values = {}
        metric_defs = [
            ("avg_wait", "Avg. waiting", "—"),
            ("avg_tat", "Avg. turnaround", "—"),
            ("avg_resp", "Avg. response", "—"),
            ("cpu", "CPU utilization", "—"),
            ("throughput", "Throughput", "—"),
            ("total", "Elapsed time", "—"),
        ]
        for i, (key, label, initial) in enumerate(metric_defs):
            card = tk.Frame(metric_grid, bg=PANEL_ALT, padx=10, pady=9)
            card.grid(row=i//3, column=i%3, sticky="nsew", padx=4, pady=4)
            self._label(card, label, 8, MUTED).pack(anchor="w")
            value = tk.Label(card, text=initial, bg=PANEL_ALT, fg=TEXT,
                             font=("Segoe UI", 16, "bold"))
            value.pack(anchor="w", pady=(4, 0))
            self.metric_values[key] = value
        for c in range(3):
            metric_grid.grid_columnconfigure(c, weight=1)

        chart_panel = tk.Frame(self.root, bg=PANEL, padx=12, pady=10)
        chart_panel.pack(fill="both", expand=True, padx=22, pady=(0, 10))
        self._label(chart_panel, "CPU EXECUTION TIMELINE", 10, ACCENT, True).pack(anchor="w")
        self.figure = Figure(figsize=(10, 2.5), dpi=100, facecolor=PANEL)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(4, 0))
        self._draw_empty_chart()

        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill="both", padx=22, pady=(0, 12))
        self._label(bottom, "PROCESS RESULTS", 10, ACCENT, True).pack(anchor="w", pady=(0, 6))
        result_cols = ("pid", "arrival", "burst", "priority", "completion", "turnaround", "waiting", "response")
        self.result_tree = ttk.Treeview(bottom, columns=result_cols, show="headings", height=5)
        titles = {
            "pid": "Process", "arrival": "Arrival", "burst": "Burst", "priority": "Priority",
            "completion": "Completion", "turnaround": "Turnaround", "waiting": "Waiting", "response": "Response"
        }
        for col in result_cols:
            self.result_tree.heading(col, text=titles[col])
            self.result_tree.column(col, width=95, anchor="center")
        self.result_tree.pack(fill="x")
        action_bar = tk.Frame(bottom, bg=BG)
        action_bar.pack(fill="x", pady=(8, 0))
        self._button(action_bar, "Export Results to CSV", self.export_csv).pack(side="left")
        tk.Label(action_bar, textvariable=self.status_var, bg=BG, fg=MUTED,
                 font=("Segoe UI", 9)).pack(side="left", padx=12)

    def _draw_empty_chart(self):
        self.ax.clear()
        self.ax.set_facecolor(PANEL)
        self.ax.text(0.5, 0.5, "Run a simulation to view the Gantt chart",
                     color=MUTED, ha="center", va="center", transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_color(PANEL)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _refresh_processes(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        for p in self.processes:
            self.process_tree.insert("", "end", values=(p["pid"], p["arrival"], p["burst"], p["priority"]))

    def add_process(self):
        pid = self.pid_var.get().strip()
        if not pid:
            messagebox.showerror("Invalid input", "Process ID cannot be empty.")
            return
        try:
            arrival = int(self.arrival_var.get())
            burst = int(self.burst_var.get())
            priority = int(self.priority_var.get())
            if arrival < 0 or burst <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid input", "Arrival must be ≥ 0, burst must be > 0, and priority must be an integer.")
            return
        if any(p["pid"] == pid for p in self.processes):
            messagebox.showerror("Duplicate process", f"{pid} already exists.")
            return
        self.processes.append({"pid": pid, "arrival": arrival, "burst": burst, "priority": priority})
        self._refresh_processes()
        self.pid_var.set(f"P{len(self.processes)+1}")
        self.status_var.set(f"Added process {pid}.")

    def remove_selected(self):
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showinfo("Select a process", "Select a process in the process queue first.")
            return
        ids = {self.process_tree.item(item, "values")[0] for item in selected}
        self.processes = [p for p in self.processes if p["pid"] not in ids]
        self._refresh_processes()
        self.status_var.set("Selected process(es) removed.")

    def load_sample(self):
        self.processes = [
            {"pid": "P1", "arrival": 0, "burst": 5, "priority": 3},
            {"pid": "P2", "arrival": 0, "burst": 3, "priority": 1},
            {"pid": "P3", "arrival": 1, "burst": 8, "priority": 4},
            {"pid": "P4", "arrival": 2, "burst": 2, "priority": 2},
        ]
        self._refresh_processes()
        self.status_var.set("Sample data loaded. Choose an algorithm and run the simulation.")

    def _read_quantum(self):
        try:
            q = int(self.quantum_var.get())
            if q <= 0:
                raise ValueError
            return q
        except ValueError:
            raise ValueError("Time quantum must be a positive integer.")

    def run_simulation(self):
        if not self.processes:
            messagebox.showerror("No processes", "Add at least one process first.")
            return
        try:
            q = self._read_quantum()
            result = run_algorithm(self.algorithm_var.get(), self.processes, q)
        except ValueError as exc:
            messagebox.showerror("Cannot run simulation", str(exc))
            return
        self.last_result = result
        self.last_comparison = []
        self._show_result(result)
        self.status_var.set(f"Simulation complete: {result['algorithm']}.")

    def compare_all(self):
        if not self.processes:
            messagebox.showerror("No processes", "Add at least one process first.")
            return
        try:
            q = self._read_quantum()
            results = compare_algorithms(self.processes, q)
        except ValueError as exc:
            messagebox.showerror("Cannot compare", str(exc))
            return
        self.last_comparison = results
        self.last_result = results[0]
        self._show_result(results[0])
        self._show_comparison_dialog(results)
        self.status_var.set("Comparison complete. FCFS is displayed in the main chart.")

    def _show_result(self, result):
        metrics = result["metrics"]
        vals = {
            "avg_wait": f"{metrics['average_waiting']:.2f}",
            "avg_tat": f"{metrics['average_turnaround']:.2f}",
            "avg_resp": f"{metrics['average_response']:.2f}",
            "cpu": f"{metrics['cpu_utilization']:.1f}%",
            "throughput": f"{metrics['throughput']:.3f}/unit",
            "total": f"{metrics['total_time']}",
        }
        for key, value in vals.items():
            self.metric_values[key].configure(text=value)

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for r in result["processes"]:
            self.result_tree.insert("", "end", values=(
                r["pid"], r["arrival"], r["burst"], r["priority"],
                r["completion"], r["turnaround"], r["waiting"], r["response"]
            ))
        self._draw_gantt(result)

    def _draw_gantt(self, result):
        self.ax.clear()
        self.ax.set_facecolor(PANEL)
        segments = result["segments"]
        ids = list(dict.fromkeys(s["pid"] for s in segments if s["pid"] != "IDLE"))
        color_map = {pid: COLORS[i % len(COLORS)] for i, pid in enumerate(ids)}
        for seg in segments:
            start, end, pid = seg["start"], seg["end"], seg["pid"]
            color = "#46546A" if pid == "IDLE" else color_map[pid]
            self.ax.barh(0, end-start, left=start, height=0.48, color=color,
                         edgecolor=PANEL, linewidth=1.5)
            if end - start >= 1:
                self.ax.text((start+end)/2, 0, "Idle" if pid == "IDLE" else pid,
                             ha="center", va="center", color="white", fontsize=8, fontweight="bold")
            self.ax.text(start, -0.36, str(start), ha="center", va="top", color=MUTED, fontsize=8)
        if segments:
            self.ax.text(segments[-1]["end"], -0.36, str(segments[-1]["end"]),
                         ha="center", va="top", color=MUTED, fontsize=8)
            self.ax.set_xlim(min(s["start"] for s in segments), max(s["end"] for s in segments) + 0.2)
        self.ax.set_ylim(-0.55, 0.55)
        self.ax.set_yticks([])
        self.ax.set_xlabel("Time units", color=MUTED, labelpad=5)
        self.ax.tick_params(axis="x", colors=MUTED)
        self.ax.set_title(result["algorithm"], color=TEXT, loc="left", fontsize=10, pad=8)
        for spine in self.ax.spines.values():
            spine.set_color(PANEL)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _show_comparison_dialog(self, results):
        win = tk.Toplevel(self.root)
        win.title("Algorithm Comparison")
        win.configure(bg=BG)
        win.geometry("850x390")
        tk.Label(win, text="Algorithm Performance Comparison", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18, pady=(16, 8))
        columns = ("algorithm", "avg_wait", "avg_tat", "avg_resp", "cpu", "throughput")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=8)
        headings = {
            "algorithm": "Algorithm", "avg_wait": "Avg Waiting", "avg_tat": "Avg Turnaround",
            "avg_resp": "Avg Response", "cpu": "CPU Utilization", "throughput": "Throughput"
        }
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=130 if col == "algorithm" else 125, anchor="center")
        tree.pack(fill="both", expand=True, padx=18, pady=10)
        for r in results:
            m = r["metrics"]
            tree.insert("", "end", values=(
                r["algorithm"], f"{m['average_waiting']:.2f}",
                f"{m['average_turnaround']:.2f}", f"{m['average_response']:.2f}",
                f"{m['cpu_utilization']:.1f}%", f"{m['throughput']:.3f}"
            ))
        tk.Label(win, text="Metrics are calculated from the same process set and time quantum.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(0, 14))

    def export_csv(self):
        result = self.last_result
        if not result:
            messagebox.showinfo("No results", "Run a simulation before exporting.")
            return
        path = filedialog.asksaveasfilename(
            title="Save simulation results", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="oslab_results.csv"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["CPU Scheduling Simulator - OSLab"])
                writer.writerow(["Algorithm", result["algorithm"]])
                writer.writerow([])
                writer.writerow(["Process", "Arrival", "Burst", "Priority", "Completion",
                                 "Turnaround", "Waiting", "Response"])
                for r in result["processes"]:
                    writer.writerow([r["pid"], r["arrival"], r["burst"], r["priority"],
                                     r["completion"], r["turnaround"], r["waiting"], r["response"]])
                writer.writerow([])
                m = result["metrics"]
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Average waiting time", f"{m['average_waiting']:.3f}"])
                writer.writerow(["Average turnaround time", f"{m['average_turnaround']:.3f}"])
                writer.writerow(["Average response time", f"{m['average_response']:.3f}"])
                writer.writerow(["CPU utilization (%)", f"{m['cpu_utilization']:.3f}"])
                writer.writerow(["Throughput (processes per time unit)", f"{m['throughput']:.5f}"])
                writer.writerow([])
                writer.writerow(["Gantt segment", "Start", "End"])
                for s in result["segments"]:
                    writer.writerow([s["pid"], s["start"], s["end"]])
            messagebox.showinfo("Export complete", f"Results saved to:\n{path}")
            self.status_var.set("CSV report exported.")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))


def main():
    root = tk.Tk()
    OSLabApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
