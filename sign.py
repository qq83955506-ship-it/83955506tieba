#!/usr/bin/env python3
"""百度贴吧自动签到脚本（基于 aiotieba）

每天运行一次，自动给当前账号所有「已关注」的贴吧签到。
每次运行都会重新拉取关注列表，所以新关注的吧会自动纳入，无需手动维护名单。

BDUSS 读取优先级（任一即可）:
  1. 命令行参数:      py sign.py <你的BDUSS>
  2. 环境变量:        TIEBA_BDUSS=<你的BDUSS>
  3. 本地文件:        与本脚本同目录的 bduss.txt（内容就是 BDUSS 那一串）

可选环境变量:
  TIEBA_SIGN_INTERVAL  每次签到之间的间隔秒数，默认 0.5（太急容易触发风控）

用法示例:
  py sign.py
  py sign.py "xxxxxx你的BDUSSxxxxxx"
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import aiotieba as tb

# 输出编码处理：控制台保持系统原生编码（中文 Windows 的 GBK 可正常显示中文）；
# 管道/重定向（计划任务、CI、日志）统一成 UTF-8，避免中文乱码或 UnicodeEncodeError。
if not sys.stdout.isatty() and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


def load_bduss() -> str:
    """按优先级读取 BDUSS。"""
    # 1) 命令行参数
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    # 2) 环境变量（适合 GitHub Actions / 定时任务）
    env = os.environ.get("TIEBA_BDUSS", "").strip()
    if env:
        return env
    # 3) 本地 bduss.txt
    p = Path(__file__).with_name("bduss.txt")
    if p.exists():
        v = p.read_text(encoding="utf-8").strip()
        if v:
            return v
    raise SystemExit(
        "未找到 BDUSS。请用以下任一方式提供：\n"
        "  1) py sign.py <BDUSS>\n"
        "  2) 设置环境变量 TIEBA_BDUSS\n"
        "  3) 在本脚本同目录新建 bduss.txt 并写入 BDUSS"
    )


async def sign_all(client: tb.Client, interval: float) -> dict[str, int]:
    stats = {"total": 0, "ok": 0, "already": 0, "fail": 0}
    pn = 1
    while True:
        forums = await client.get_self_follow_forums()
        if forums.err is not None:
            raise forums.err

        for f in forums:
            stats["total"] += 1
            if f.is_signed:
                stats["already"] += 1
                continue

            resp = await client.sign_forum(f.fname)
            if resp:  # BoolResponse 为真 => err 为 None => 签到成功
                stats["ok"] += 1
                print(f"  [OK]   {f.fname}  (Lv.{f.level})")
            else:
                stats["fail"] += 1
                print(f"  [FAIL] {f.fname} : {resp.err}")

            if interval > 0:
                await asyncio.sleep(interval)

        if not forums.has_more:
            break
        pn += 1

    return stats


async def main() -> None:
    bduss = load_bduss()
    interval = float(os.environ.get("TIEBA_SIGN_INTERVAL", "0.5") or "0")
    # 默认连接超时只有 3 秒，对慢网络/跨地域访问太短，这里放宽
    timeout = tb.TimeoutConfig(http_connect=15.0, http_read=30.0, http_acquire_conn=10.0)

    print("正在登录并拉取关注贴吧列表……")
    async with tb.Client(bduss, timeout=timeout) as client:
        stats = await sign_all(client, interval)

        # 成长值签到（可选，失败不影响主流程）
        try:
            g = await client.sign_growth()
            print(f"成长值签到: {'成功' if g else '失败 ' + str(g.err)}")
        except Exception as e:  # noqa: BLE001
            print(f"成长值签到跳过: {e}")

    print("-" * 48)
    print(
        f"关注吧总数: {stats['total']} | "
        f"新签到成功: {stats['ok']} | "
        f"今日已签: {stats['already']} | "
        f"失败: {stats['fail']}"
    )
    # 个别吧签到失败（如被某吧务封禁）不算整体失败，避免定时任务天天报红；
    # 真正的错误（BDUSS 失效 / 拉取列表失败 / 断网）会在上面抛异常并导致非零退出。


if __name__ == "__main__":
    asyncio.run(main())
