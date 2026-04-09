import time
import os
import csv
from datetime import datetime

DATA_DIR = "data/collaudi"


def execute_steps(
    steps, smioo_manager, codice, matricola, measure_engine, log_row, step_offset=0
):
    idx = step_offset
    for step in steps:
        # Gestione repeat ricorsiva
        if step["action"] == "repeat":
            for i in range(step["count"]):
                execute_steps(
                    step["body"],
                    smioo_manager,
                    codice,
                    matricola,
                    measure_engine,
                    log_row,
                    step_offset=idx,
                )
            idx += 1
        elif step["action"] == "set_output":
            smioo_manager.write_output(step["channel"], step["value"])
            idx += 1
        elif step["action"] == "wait_input":
            t0 = time.time()
            timeout = step.get("timeout", 10)
            while time.time() - t0 < timeout:
                val = smioo_manager.read_input(step["channel"])
                if val == step["value"]:
                    break
                time.sleep(0.05)
            idx += 1
        elif step["action"] == "wait_time":
            time.sleep(step["seconds"])
            idx += 1
        elif step["action"] == "acquire_measure":
            measures = measure_engine.get_enabled_measurements()
            for m in measures:
                # ok = measure_engine.calculate_measurement(m)
                val_misura = m.current_value
                trasduttori = {}
                for ch in m.channels:
                    ch_info = measure_engine.sensor_manager.get_channel_by_label(ch)
                    trasduttori[ch] = ch_info.current_value if ch_info else None
                log_row(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "codice": codice,
                        "matricola": matricola,
                        "step": idx,
                        "measure": m.name,
                        **trasduttori,
                        "value": val_misura,
                    }
                )
            idx += 1
        # Se servono altri action, aggiungi qui...
        else:
            print(f"[WARNING] Azione non riconosciuta: {step['action']}")
            idx += 1


def execute_cycle(cycle, smioo_manager, codice, matricola, measure_engine):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_file = os.path.join(DATA_DIR, f"{codice}_{matricola}_{timestamp}.csv")
    log_fields = [
        "timestamp",
        "codice",
        "matricola",
        "step",
        "measure",
    ]

    def log_row(row):
        with open(data_file, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=log_fields + list(row.keys()))
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(row)

    steps = cycle["steps"]
    execute_steps(steps, smioo_manager, codice, matricola, measure_engine, log_row)
