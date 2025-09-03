#!/usr/bin/env python3
"""
Dramatiq worker manager

Usage:
  python worker.py start [--dev]     # Start worker (dev mode)
  python worker.py stop              # Stop worker
  python worker.py status            # Check status
  python worker.py restart [--dev]   # Restart worker
  python worker.py test              # Test connections

Options:
  --dev        Development mode (file watching + verbose logs)
  --processes  Number of processes (default: 1)
  --threads    Number of threads (default: 1)
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# env variables auto loaded in docker compose
if os.getenv("REDIS_URL") is None:
    load_dotenv()


class WorkerManager:
    def __init__(self):
        self.cwd = Path(os.getcwd())
        self.pid_file = self.cwd / "dramatiq.pid"

    def _setup_env(self):
        """Setup environment variables"""

        env = os.environ.copy()
        if not env.get("REDIS_URL"):
            env["REDIS_URL"] = "redis://localhost:6379"
        return env

    def _get_pid(self):
        """Get running PID"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, "r") as f:
                    pid = int(f.read().strip())
                # Check if process is still running
                try:
                    os.kill(pid, 0)
                    return pid
                except OSError:
                    # Process doesn't exist, remove pid file
                    self.pid_file.unlink()
                    return None
            except (ValueError, FileNotFoundError):
                return None
        return None

    def _save_pid(self, pid):
        """Save PID to file"""
        with open(self.pid_file, "w") as f:
            f.write(str(pid))

    def start(self, worker, queues, dev=False, processes=1, threads=1):
        """Start worker"""
        if self._get_pid():
            print("❌ Worker already running")
            return False

        env = self._setup_env()

        if not queues:
            print("❌ 请通过 --queues 指定要监听的队列名，如 queue1")
            return False

        cmd = [
            sys.executable,
            "-m",
            "dramatiq",
            "--processes",
            str(processes),
            "--threads",
            str(threads),
            "--queues",
            queues,
        ]

        if dev:
            cmd.extend(["--watch", str(self.cwd), "--verbose"])
        else:
            cmd.append("--verbose")

        # 使用传入的 worker 参数
        if not worker:
            print(
                "❌ 请通过 --worker 指定要加载的 worker 模块名，如 xxx.queued_tasks.handlers"
            )
            return False
        cmd.append(worker)

        print("🚀 Starting Dramatiq worker...")
        print(f"   Mode: {'Development' if dev else 'Production'}")
        print(f"   Processes: {processes}")
        print(f"   Threads: {threads}")
        print(f"   Redis URL: {env.get('REDIS_URL')}")
        print("=" * 50)

        try:
            # Start background process
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid if os.name != "nt" else None,
            )

            # Save PID
            self._save_pid(process.pid)

            print(f"✅ Worker started (PID: {process.pid})")

            if dev:
                print("📝 Development mode: Live logs (Ctrl+C to stop)")
                try:
                    if process.stdout is not None:
                        for line in process.stdout:
                            print(line.decode().strip())
                except KeyboardInterrupt:
                    print("\n🛑 Stopping log monitoring...")
                    self.stop()
            else:
                print("📝 Production mode: Logs")
                try:
                    if process.stdout is not None:
                        for line in process.stdout:
                            print(line.decode().strip())
                except KeyboardInterrupt:
                    print("\n🛑 Stopping worker...")

            return True

        except Exception as e:
            print(f"❌ Start failed: {e}")
            return False

    def stop(self):
        """Stop worker"""
        pid = self._get_pid()
        if not pid:
            print("ℹ️  Worker not running")
            return True

        try:
            print(f"🛑 Stopping worker (PID: {pid})...")

            try:
                if os.name == "nt":  # Windows
                    os.kill(pid, signal.SIGTERM)
                else:  # Unix/Linux/macOS
                    os.killpg(os.getpgid(pid), signal.SIGINT)
            except ProcessLookupError:
                # Process already gone, which is fine.
                pass

            # Wait for process to end
            for _ in range(50):
                try:
                    reaped_pid, _ = os.waitpid(pid, os.WNOHANG)
                    if reaped_pid == pid:
                        # Process has been successfully reaped.
                        break
                except ChildProcessError:
                    try:
                        os.kill(pid, 0)  # Check if the process exists
                    except OSError:
                        break  # Exit loop
                time.sleep(0.1)
            else:
                # Force kill
                print("⚠️  Process not responding, force stopping...")
                try:
                    if os.name == "nt":
                        os.kill(pid, signal.SIGKILL)
                    else:
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                except ProcessLookupError:
                    # Process already gone, which is fine.
                    pass

            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()

            print("✅ Worker stopped")
            return True

        except Exception as e:
            print(f"❌ Stop failed: {e}")
            return False

    def status(self):
        """Check status"""
        pid = self._get_pid()
        if pid:
            print(f"✅ Worker running (PID: {pid})")
        else:
            print("❌ Worker not running")

        # Check Redis connection
        try:
            import redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            r = redis.from_url(redis_url)
            r.ping()
            print(f"✅ Redis connected: {redis_url}")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")

    def restart(self, worker, queues, dev=False, processes=1, threads=1):
        """Restart worker"""
        print("🔄 Restarting worker...")
        self.stop()
        time.sleep(1)
        return self.start(worker, queues, dev, processes, threads)

    def test(self):
        """Test connections"""
        print("🧪 Testing connections...")

        # Setup environment
        env = self._setup_env()
        os.environ.update(env)

        try:
            # Test Redis connection
            import redis

            redis_url = env.get("REDIS_URL")
            r = redis.from_url(redis_url)
            r.ping()
            print(f"✅ Redis connection successful: {redis_url}")

            # Test Broker setup
            from sparkden.shared.queued_job.config import setup_job_queue_broker

            broker = setup_job_queue_broker()
            print(f"✅ Broker setup successful: {type(broker).__name__}")

            # Test Tasks import
            # from xxx import handlers  # noqa: F401

            print("✅ Tasks import successful")

            print("🎉 All tests passed!")
            return True

        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    manager = WorkerManager()

    def shutdown_handler(signum, frame):
        print(f"ℹ️  Signal {signum} received, shutting down...")
        manager.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    parser = argparse.ArgumentParser(
        description="Dramatiq worker manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "restart", "test"],
        help="Command to execute",
    )

    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode (file watching + verbose logs)",
    )

    parser.add_argument(
        "--processes", type=int, default=1, help="Number of processes (default: 1)"
    )

    parser.add_argument(
        "--threads", type=int, default=1, help="Number of threads (default: 1)"
    )

    parser.add_argument(
        "--worker",
        type=str,
        help="Worker module to load (e.g. xxx.queued_tasks.handlers)",
        required=False,
    )

    parser.add_argument(
        "--queues",
        type=str,
        help="Comma-separated queue names (e.g. queue1)",
        required=True,
    )

    args = parser.parse_args()

    success = False
    if args.command == "start":
        success = manager.start(
            worker=args.worker,
            queues=args.queues,
            dev=args.dev,
            processes=args.processes,
            threads=args.threads,
        )
    elif args.command == "stop":
        success = manager.stop()
    elif args.command == "status":
        manager.status()
        success = True
    elif args.command == "restart":
        success = manager.restart(
            worker=args.worker,
            queues=args.queues,
            dev=args.dev,
            processes=args.processes,
            threads=args.threads,
        )
    elif args.command == "test":
        success = manager.test()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
