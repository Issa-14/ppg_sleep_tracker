import time
import collections
import serial

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# ---------- SETTINGS ----------
PORT = "COM3"
BAUD = 115200

IR_HZ = 50
WINDOW_SEC = 12
MAX_POINTS = IR_HZ * WINDOW_SEC

MA_SEC = 1.0
MA_N = max(10, int(MA_SEC * IR_HZ))

PLOT_FPS = 20

# ---------- PARSER ----------
def parse_line(line: str):
    # Expected:
    # IR,12345
    # BEAT,123456,72.3   (millis, bpm)
    parts = line.strip().split(",")
    if not parts:
        return None

    if parts[0] == "IR" and len(parts) >= 2:
        try:
            return ("IR", int(parts[1]))
        except:
            return None

    if parts[0] == "BEAT" and len(parts) >= 3:
        try:
            return ("BEAT", int(parts[1]), float(parts[2]))
        except:
            return None

    return None

# ---------- MAIN ----------
def main():
    print("RUNNING PPG + BEAT MARKER PLOT ✅")
    print(f"Opening serial {PORT} @ {BAUD}")

    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(1.5)
    ser.reset_input_buffer()

    # Buffers
    t_buf   = collections.deque(maxlen=MAX_POINTS)  # seconds
    ir_buf  = collections.deque(maxlen=MAX_POINTS)
    det_buf = collections.deque(maxlen=MAX_POINTS)

    # Beat / RR buffers (seconds)
    beat_t = collections.deque(maxlen=200)     # time of beats (s)
    rr_ms  = collections.deque(maxlen=200)     # RR intervals (ms)
    bpm_buf = collections.deque(maxlen=200)

    last_beat_ms = None
    latest_bpm = None

    # Plot setup (two rows)
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

    # Top: detrended waveform + beat markers
    line_det, = ax1.plot([], [], lw=1, label="Detrended IR")
    scat = ax1.scatter([], [], s=18, label="Beat")  # beat markers

    ax1.set_ylabel("IR detrended (IR - MA)")
    ax1.set_title("PPG detrended + beat markers")
    ax1.legend(loc="upper right", labelcolor="red")
    ax1.grid(True)

    # Bottom: RR intervals
    line_rr, = ax2.plot([], [], lw=1, label="RR interval")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("RR (ms)")
    ax2.grid(True)
    ax2.legend(loc="upper right", labelcolor="red")

    start = time.time()
    last_plot = 0.0

    def compute_ma(vals, n):
        n = min(len(vals), n)
        if n <= 0:
            return 0.0
        tail = list(vals)[-n:]
        return sum(tail) / n

    try:
        while True:
            raw = ser.readline().decode(errors="ignore")
            if raw:
                msg = parse_line(raw)
                if msg:
                    now_s = time.time() - start

                    if msg[0] == "IR":
                        ir = msg[1]
                        t_buf.append(now_s)
                        ir_buf.append(ir)

                        ma = compute_ma(ir_buf, MA_N)
                        det = ir - ma
                        det_buf.append(det)

                    elif msg[0] == "BEAT":
                        beat_ms, bpm = msg[1], msg[2]
                        print(f"BEAT received: t_ms={beat_ms} bpm={bpm}")
                        latest_bpm = bpm

                        # RR from ESP32 millis timestamps (more stable than PC time)
                        if last_beat_ms is not None:
                            rr = beat_ms - last_beat_ms
                            # sanity limits
                            if 200 <= rr <= 3000:
                                beat_t.append(now_s)
                                rr_ms.append(rr)
                                bpm_buf.append(bpm)
                                print(f"RR={rr} ms")

                        last_beat_ms = beat_ms

            # refresh plots
            now = time.time()
            if now - last_plot >= 1.0 / PLOT_FPS and len(det_buf) > 20:
                # Waveform
                line_det.set_data(t_buf, det_buf)

                # X axis = last WINDOW_SEC
                xmax = t_buf[-1]
                xmin = max(0, xmax - WINDOW_SEC)
                ax2.set_xlim(xmin, xmax)

                # Autoscale Y for waveform (last ~5s)
                recent_det = list(det_buf)[-IR_HZ*5:]
                lo, hi = min(recent_det), max(recent_det)
                pad = (hi - lo) * 0.25 + 30
                ax1.set_ylim(lo - pad, hi + pad)

                # Beat markers: plot at (beat_t, det_at_that_time approx)
                # We'll place markers at y=0 (good enough for timing),
                # since exact sample alignment is nontrivial without buffering indices.
                if len(beat_t) > 0:
                    xs = list(beat_t)
                    ys = [0.0] * len(xs)
                    scat.set_offsets(list(zip(xs, ys)))
                    scat.set_sizes([18] * len(xs))

                else:
                     scat.set_offsets([(0, 0)])   # dummy point
                     scat.set_sizes([0])

                # RR plot
                if len(rr_ms) > 1:
                    line_rr.set_data(beat_t, rr_ms)
                    ax2.set_ylim(400, 1500)
                    recent_rr = list(rr_ms)[-min(len(rr_ms), 20):]
                    rlo, rhi = min(recent_rr), max(recent_rr)
                    rpad = (rhi - rlo) * 0.2 + 10
                    ax2.set_ylim(rlo - rpad, rhi + rpad)

                title = "PPG detrended + beat markers"
                if latest_bpm is not None:
                    title += f" | BPM={latest_bpm:.1f}"
                ax1.set_title(title)

                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.001)
                last_plot = now

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
