#!/usr/bin/env python3
"""Backup verificável dos bancos SQLite operacionais e do PostgreSQL do BI.

Executar no host Linux, na raiz do projeto:
    python3 ferramentas/backup_bancos.py
"""
from __future__ import annotations

import argparse
import hashlib
from contextlib import closing
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "Banco Dados"
BACKUP_DIR = ROOT / "backups"
DEFAULT_PG_CONTAINER = "meu-postgres"


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"' ")
    return values


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def backup_sqlite(source: Path, destination: Path) -> dict:
    """Use SQLite's online backup API, safe while the app is running."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True, timeout=30)) as src:
        with closing(sqlite3.connect(destination, timeout=30)) as dst:
            src.backup(dst)
            result = dst.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                raise RuntimeError(f"integrity_check falhou para {source.name}: {result}")
    return {
        "name": destination.name,
        "size_bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "integrity_check": "ok",
    }


def backup_postgres(destination: Path, env: dict[str, str]) -> dict:
    container = os.environ.get("BACKUP_PG_CONTAINER", DEFAULT_PG_CONTAINER)
    user = env.get("PG_USER", "postgres")
    database = env.get("PG_DATABASE", "controle_bi")
    command = [
        "docker", "exec", container,
        "pg_dump", "-U", user, "-d", database, "--format=custom",
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as output:
        result = subprocess.run(command, stdout=output, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        destination.unlink(missing_ok=True)
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"pg_dump falhou (container={container}, banco={database}): {detail}")
    if destination.stat().st_size == 0:
        raise RuntimeError("pg_dump gerou um arquivo vazio.")
    return {
        "name": destination.name,
        "size_bytes": destination.stat().st_size,
        "sha256": sha256_file(destination),
        "format": "PostgreSQL custom dump",
        "database": database,
        "container": container,
    }
def prune_old_backups(retention_days: int) -> list[str]:
    """Remove apenas pastas de backup anteriores à retenção."""
    cutoff = datetime.now().timestamp() - retention_days * 86400
    removed = []
    if not BACKUP_DIR.exists():
        return removed
    for folder in BACKUP_DIR.iterdir():
        if not folder.is_dir():
            continue
        # Só remove pastas com manifesto de sucesso; preserva backups incompletos.
        manifest = folder / "manifest.json"
        if not manifest.exists() or manifest.stat().st_mtime >= cutoff:
            continue
        shutil.rmtree(folder)
        removed.append(folder.name)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Faz backup verificado dos bancos do Controle de Ativos TI.")
    parser.add_argument("--retention-days", type=int, default=14, help="Dias de retenção (padrão: 14).")
    args = parser.parse_args()
    if args.retention_days < 1:
        parser.error("--retention-days precisa ser pelo menos 1.")
    if not DATA_DIR.is_dir():
        print(f"ERRO: diretório de bancos não encontrado: {DATA_DIR}", file=sys.stderr)
        return 2

    sources = sorted(
        path for path in DATA_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".sqlite", ".sqlite3", ".db"}
    )
    if not sources:
        print(f"ERRO: nenhum banco SQLite encontrado em {DATA_DIR}", file=sys.stderr)
        return 2

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = BACKUP_DIR / timestamp
    target.mkdir(parents=True, exist_ok=False)
    manifest = {
        "created_at": datetime.now().astimezone().isoformat(),
        "project": ROOT.name,
        "sqlite": [],
        "postgres": None,
        "status": "incomplete",
    }
    print(f"Iniciando backup em: {target}")
    try:
        for source in sources:
            info = backup_sqlite(source, target / source.name)
            manifest["sqlite"].append(info)
            print(f"OK SQLite: {source.name} ({info['size_bytes']} bytes; integridade OK)")

        env = read_env_file(ROOT / ".env")
        pg_info = backup_postgres(target / "controle_bi.dump", env)
        manifest["postgres"] = pg_info
        print(f"OK PostgreSQL: {pg_info['database']} ({pg_info['size_bytes']} bytes)")

        manifest["status"] = "success"
        manifest["retention_days"] = args.retention_days
        (target / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        removed = prune_old_backups(args.retention_days)
        print(f"BACKUP_SUCCESS: {target}")
        print(f"Bancos SQLite: {len(manifest['sqlite'])}; PostgreSQL: OK")
        print(f"Backups antigos removidos: {len(removed)}")
        return 0
    except Exception as exc:
        manifest["error"] = str(exc)
        (target / "FAILED.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"BACKUP_FAILED: {exc}", file=sys.stderr)
        print(f"Os arquivos gerados foram preservados para inspeção: {target}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
