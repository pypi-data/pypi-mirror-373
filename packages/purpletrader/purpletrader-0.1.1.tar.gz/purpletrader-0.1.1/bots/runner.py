from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


def launch_process(cmd: List[str]) -> subprocess.Popen:
    print("Launching:", " ".join(cmd))
    return subprocess.Popen(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Spawn multiple bots from a YAML config")
    parser.add_argument("--base-url", required=True, help="Engine base URL, e.g. http://host:8080")
    parser.add_argument("--config", required=True, help="Path to YAML config with bots list")
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r") as f:
        cfg: Dict[str, Any] = yaml.safe_load(f)

    processes: List[subprocess.Popen] = []
    for bot in cfg.get("bots", []):
        kind = bot.get("kind")
        user_id = bot.get("user_id")
        symbols = bot.get("symbols", [])
        extra_args = bot.get("args", {})

        if kind == "market_maker":
            cmd = [
                sys.executable,
                "-m",
                "bots.market_maker",
                "--base-url",
                args.base_url,
                "--user-id",
                user_id,
            ]
            for s in symbols:
                cmd += ["--symbol", s]
            if "spread_bps" in extra_args:
                cmd += ["--spread-bps", str(extra_args["spread_bps"])]
            if "qty" in extra_args:
                cmd += ["--qty", str(extra_args["qty"])]
            if "tick_sec" in extra_args:
                cmd += ["--tick-sec", str(extra_args["tick_sec"])]
            if "jitter_bps" in extra_args:
                cmd += ["--jitter-bps", str(extra_args["jitter_bps"])]
            processes.append(launch_process(cmd))
        elif kind == "momentum":
            cmd = [
                sys.executable,
                "-m",
                "bots.momentum",
                "--base-url",
                args.base_url,
                "--user-id",
                user_id,
            ]
            for s in symbols:
                cmd += ["--symbol", s]
            if "lookback" in extra_args:
                cmd += ["--lookback", str(extra_args["lookback"])]
            if "threshold_bps" in extra_args:
                cmd += ["--threshold-bps", str(extra_args["threshold_bps"])]
            if "qty" in extra_args:
                cmd += ["--qty", str(extra_args["qty"])]
            if "tick_sec" in extra_args:
                cmd += ["--tick-sec", str(extra_args["tick_sec"])]
            processes.append(launch_process(cmd))
        elif kind == "random":
            cmd = [
                sys.executable,
                "-m",
                "bots.random_bot",
                "--base-url",
                args.base_url,
                "--user-id",
                user_id,
            ]
            for s in symbols:
                cmd += ["--symbol", s]
            if "qty_min" in extra_args:
                cmd += ["--qty-min", str(extra_args["qty_min"])]
            if "qty_max" in extra_args:
                cmd += ["--qty-max", str(extra_args["qty_max"])]
            if "tick_sec" in extra_args:
                cmd += ["--tick-sec", str(extra_args["tick_sec"])]
            if "market_prob" in extra_args:
                cmd += ["--market-prob", str(extra_args["market_prob"])]
            if "limit_bps_range" in extra_args:
                cmd += ["--limit-bps-range", str(extra_args["limit_bps_range"])]
            processes.append(launch_process(cmd))
        else:
            print(f"Unknown bot kind: {kind}")

    # Wait for all processes (will run indefinitely until interrupted)
    for p in processes:
        p.wait()


if __name__ == "__main__":
    main()


