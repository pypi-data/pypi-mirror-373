#!/usr/bin/env python3
"""
acad_sdk.cli
Minimal ask-based CLI for Acad AI Deployment API packaged for console_scripts.
"""
import os
import sys
import json
import pathlib
from typing import Optional

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.theme import Theme
from rich import box

from . import AcadClient, AcadError, WeatherClient, WeatherError

theme = Theme({
    "info": "cyan",
    "warn": "yellow",
    "error": "bold red",
    "title": "bold magenta",
})
console = Console(theme=theme)


def prompt(text: str, default: Optional[str] = None) -> str:
    return Prompt.ask(text, default=default) if default is not None else Prompt.ask(text)


def yes_no(text: str, default_yes: bool = True) -> bool:
    return Confirm.ask(text, default=default_yes)


def choose_action() -> str:
    actions = [
        ("pipeline", "Run AI → Compile → Deploy pipeline"),
        ("status", "Check job status"),
        ("logs", "Stream job logs"),
        ("artifacts", "Fetch artifacts"),
        ("erc20", "One-click ERC20 deploy"),
        ("weather", "Simple weather (current/forecast)"),
        ("helpers", "AI helpers: generate/fix/compile"),
        ("quit", "Exit"),
    ]
    console.print(Panel.fit("Select action", title="Menu", style="title", box=box.ROUNDED))
    for i, (_, label) in enumerate(actions, start=1):
        console.print(f"[info]{i}. {label}")
    while True:
        choice = Prompt.ask("Enter number")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(actions):
                return actions[idx][0]
        console.print("[warn]Invalid choice. Try again.")


def ensure_out_dir(path: str) -> pathlib.Path:
    p = pathlib.Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def do_pipeline(client: AcadClient):
    console.print(Panel.fit("AI Pipeline", style="title", box=box.DOUBLE))
    prompt_text = prompt("Enter prompt", "ERC721 with minting")
    network = prompt("Network", "basecamp")
    max_iters_s = prompt("Max iterations", "5")
    filename = prompt("Filename (optional)", "AIGenerated.sol")

    try:
        max_iters = int(max_iters_s) if max_iters_s else None
    except ValueError:
        max_iters = None

    job_id = client.start_pipeline(prompt_text, network, max_iters=max_iters, filename=filename or None)
    console.print(f"[info]Started job: [bold]{job_id}")

    if yes_no("Wait for completion and stream logs?", True):
        def on_update(job):
            prog = job.get("progress", 0)
            step = job.get("step", "...")
            console.print(f"[info][STATUS] {prog}% - {step}")
        job = client.wait_for_completion(job_id, interval_sec=2.0, timeout_sec=1800, on_update=on_update, stream_logs=True)
        console.print(Panel.fit("Final Result", style="title", box=box.ROUNDED))
        console.print_json(data=job)
        res = (job or {}).get("result", {})
        if res.get("address"):
            console.print(f"[info]Deployed at [bold]{res['address']}[/] on {res.get('network')}")
        if yes_no("Fetch artifacts now?", True):
            out_dir = prompt("Output directory", "./artifacts")
            out = ensure_out_dir(out_dir)
            combo = client.get_artifacts(job_id, include="all")
            (out / "artifacts.json").write_text(json.dumps(combo, indent=2))
            console.print(f"[info]Artifacts saved to {out}")


def do_status(client: AcadClient):
    console.print(Panel.fit("Job Status", style="title", box=box.ROUNDED))
    job_id = prompt("Job ID")
    job = client.get_job_status(job_id)
    console.print_json(data=job)


def do_logs(client: AcadClient):
    console.print(Panel.fit("Job Logs", style="title", box=box.ROUNDED))
    job_id = prompt("Job ID")
    since_s = prompt("Start cursor (number)", "0")
    follow = yes_no("Follow (stream)?", True)
    try:
        since = int(since_s)
    except ValueError:
        since = 0

    while True:
        logs, since = client.get_job_logs(job_id, since)
        for e in logs:
            lvl = e.get("level", "info").upper()
            msg = e.get("msg", "")
            console.print(f"[info][{lvl}] {msg}")
        if not follow:
            break


def do_artifacts(client: AcadClient):
    console.print(Panel.fit("Artifacts", style="title", box=box.ROUNDED))
    job_id = prompt("Job ID")
    include = prompt("Include (all|sources|abis|scripts)", "all")
    out_dir = prompt("Output directory (optional)", "")

    if include == "all":
        data = client.get_artifacts(job_id, include="all")
        if out_dir:
            out = ensure_out_dir(out_dir)
            (out / "artifacts.json").write_text(json.dumps(data, indent=2))
            print(f"Saved to {out}/artifacts.json")
        else:
            console.print_json(data=data)
    elif include == "sources":
        sources = client.get_sources(job_id)
        if out_dir:
            out = ensure_out_dir(out_dir)
            for s in sources:
                fname = s.get("filename", "unknown.sol")
                (out / fname).write_text(s.get("code", ""))
            print(f"Saved {len(sources)} sources to {out}")
        else:
            console.print_json(data=sources)
    elif include == "abis":
        abis = client.get_abis(job_id)
        if out_dir:
            out = ensure_out_dir(out_dir)
            for a in abis:
                name = a.get("fqName", "contract").replace(":", "_").replace("/", "_") + ".json"
                (out / name).write_text(json.dumps(a, indent=2))
            print(f"Saved {len(abis)} ABIs to {out}")
        else:
            console.print_json(data=abis)
    elif include == "scripts":
        scripts = client.get_scripts(job_id)
        if out_dir:
            out = ensure_out_dir(out_dir)
            for sc in scripts:
                name = sc.get("name", "script")
                lang = sc.get("language", "sh")
                ext = {
                    "bash": "sh",
                    "sh": "sh",
                    "js": "js",
                    "ts": "ts",
                }.get(lang, "txt")
                (out / f"{name}.{ext}").write_text(sc.get("code", ""))
            print(f"Saved {len(scripts)} scripts to {out}")
        else:
            console.print_json(data=scripts)
    else:
        console.print("[warn]Invalid include value.")


def do_erc20(client: AcadClient):
    console.print(Panel.fit("ERC20 Deploy", style="title", box=box.ROUNDED))
    name = prompt("Name", "Camp Token")
    symbol = prompt("Symbol", "CAMP")
    supply = prompt("Initial supply", "1000000")
    network = prompt("Network", "basecamp")
    owner = prompt("Owner (optional)", os.getenv("ACAD_DEFAULT_OWNER", "0xa58DCCb0F17279abD1d0D9069Aa8711Df4a4c58E")) or None

    result = client.deploy_erc20(name=name, symbol=symbol, initial_supply=supply, network=network, owner=owner)
    console.print_json(data=result)


def do_helpers(client: AcadClient):
    console.print(Panel.fit("Helpers: 1) generate  2) fix  3) compile", style="title", box=box.ROUNDED))
    choice = prompt("Pick 1/2/3", "1")
    if choice == "1":
        text = prompt("Prompt", "ERC20 with mint and burn")
        res = client.ai_generate(text)
        console.print_json(data=res)
    elif choice == "2":
        code_path = prompt("Path to code file", "./broken.sol")
        err_path = prompt("Path to errors file", "./errors.txt")
        code = pathlib.Path(code_path).read_text(encoding="utf-8")
        errs = pathlib.Path(err_path).read_text(encoding="utf-8")
        res = client.ai_fix(code, errs)
        console.print_json(data=res)
    elif choice == "3":
        code_path = prompt("Path to solidity file", "./MyToken.sol")
        filename = prompt("Filename", "MyToken.sol")
        code = pathlib.Path(code_path).read_text(encoding="utf-8")
        res = client.ai_compile(filename, code)
        console.print_json(data=res)
    else:
        console.print("[warn]Invalid choice.")


def do_weather():
    console.print(Panel.fit("Weather", style="title", box=box.ROUNDED))
    console.print("Type a city/place (e.g., 'New York') or coordinates as 'lat,lon' (e.g., '37.77,-122.42').", style="info")
    q = prompt("Location", "San Francisco")
    mode = prompt("Mode (current|forecast)", "current").lower()
    try:
        wc = WeatherClient()
        lat, lon, resolved = wc.resolve_location(q)
        if mode == "forecast":
            days_s = prompt("Days (1-7)", "3")
            try:
                days = max(1, min(7, int(days_s)))
            except ValueError:
                days = 3
            res = wc.daily_forecast(lat, lon, days=days)
        else:
            res = wc.current(lat, lon)
        console.print(f"[info]Resolved: {resolved} ({lat:.4f},{lon:.4f})")
        console.print_json(data=res)
    except WeatherError as e:
        console.print(f"[error][WEATHER ERROR] {e}")


def main():
    console.print(Panel.fit("Acad AI Deploy CLI", subtitle="minimal", style="title", box=box.HEAVY))
    base = prompt("Base URL", os.getenv("ACAD_BASE_URL", "https://acadcodegen-production.up.railway.app"))
    api_key = prompt("API Key (leave blank if none)", os.getenv("ACAD_API_KEY", "")) or None
    auth_header = prompt("Auth header name", os.getenv("ACAD_AUTH_HEADER", "X-API-Key"))

    client = AcadClient(base_url=base, api_key=api_key, auth_header_name=auth_header)

    while True:
        try:
            action = choose_action()
            if action == "pipeline":
                do_pipeline(client)
            elif action == "status":
                do_status(client)
            elif action == "logs":
                do_logs(client)
            elif action == "artifacts":
                do_artifacts(client)
            elif action == "erc20":
                do_erc20(client)
            elif action == "weather":
                do_weather()
            elif action == "helpers":
                do_helpers(client)
            elif action == "quit":
                console.print("[info]Goodbye.")
                break
        except AcadError as e:
            console.print(f"[error][ERROR] {e} (status={getattr(e, 'status', None)})")
            if getattr(e, 'details', None):
                try:
                    console.print_json(data=e.details)
                except Exception:
                    pass
        except KeyboardInterrupt:
            console.print("\n[warn]Interrupted.")
            break
        except Exception as e:
            console.print(f"[error][UNEXPECTED] {e}")


if __name__ == "__main__":
    sys.exit(main())
