import os
import subprocess

import whatthepatch

from ppatch.app import app, logger
from ppatch.config import settings
from ppatch.model import SHA, ApplyResult, File
from ppatch.utils.common import process_title
from ppatch.utils.parse import wtp_diff_to_diff
from ppatch.utils.resolve import apply_change


@app.command(name="trace")
def trace_command(
    filename: str, from_commit: str = "", flag_hunk_list: list[int] = None
) -> dict[str, ApplyResult]:
    flag_hunk_list = [] if flag_hunk_list is None else flag_hunk_list

    if not os.path.exists(filename):
        logger.error(f"Warning: {filename} not found!")
        return

    logger.info(f"tracing patch {filename} from {from_commit}")

    output: str = subprocess.run(
        [
            "git",
            "log",
            "--pretty=format:%H",
            "--",
            filename,
        ],
        capture_output=True,
    ).stdout.decode("utf-8", errors="ignore")

    sha_list = output.splitlines()

    return trace(sha_list, filename, [from_commit], [flag_hunk_list])


def trace(
    sha_list: list[SHA],
    filename: str,
    commits: list[SHA],
    flag_hunks_list: list[list[int]] = None,
    symbols: list[str] = None,
) -> dict[SHA, ApplyResult]:

    # 将 commits 按照 sha_list 的顺序排列
    commits = sorted(commits, key=lambda x: sha_list.index(x)) if commits else []

    assert len(commits) == len(flag_hunks_list)
    # 从 commits 中取出首个 sha
    from_commit = commits.pop(0)
    # 在 sha_list 中找到 from_commit 和 to_commit 的位置
    from_index = sha_list.index(from_commit) if from_commit else -1
    if from_index == -1:
        logger.error(f"from_commit {from_commit} not found")
        return

    # 注意此处需要多选一个，包含 from commit 的前一个，用于 checkout
    sha_list = sha_list[: from_index + 2]

    logger.debug(f"Get {len(sha_list)} commits for {filename}")

    # checkout 到 from_commit 的前一个 commit
    subprocess.run(
        ["git", "checkout", sha_list.pop(), "--", filename],
        capture_output=True,
    )

    origin_file = File(file_path=filename)
    new_line_list = []
    # 首先将 from_commit 以 flag=True 的方式 apply
    from_commit_sha = sha_list.pop()
    assert from_commit_sha == from_commit
    logger.debug(f"Apply patch {from_commit_sha} to {filename}")
    patch_path = os.path.join(
        settings.base_dir,
        settings.patch_store_dir,
        f"{from_commit_sha}-{process_title(filename)}.patch",
    )

    for diff in whatthepatch.parse_patch(
        open(patch_path, mode="r", encoding="utf-8").read()
    ):
        diff = wtp_diff_to_diff(diff)
        if diff.header.old_path == filename or diff.header.new_path == filename:
            try:
                apply_result = apply_change(
                    diff.hunks,
                    origin_file.line_list,
                    flag=True,
                    flag_hunk_list=flag_hunks_list.pop(),  # 取出首个 flag_hunk_list
                )
                # TODO: 检查失败数
                new_line_list = apply_result.new_line_list
            except Exception as e:
                logger.error(f"Failed to apply patch {from_commit_sha}")
                logger.error(f"Error: {e}")
                return
        else:
            logger.debug(f"Do not match with {filename}, skip")

    conflict_list: dict[SHA, ApplyResult] = {}

    # 注意这里需要反向
    sha_list.reverse()
    for sha in sha_list:
        patch_path = os.path.join(
            settings.base_dir,
            settings.patch_store_dir,
            f"{sha}-{process_title(filename)}.patch",
        )

        apply_result: ApplyResult = ApplyResult()
        with open(patch_path, mode="r", encoding="utf-8") as (f):
            diffes = whatthepatch.parse_patch(f.read())

            for diff in diffes:
                diff = wtp_diff_to_diff(diff)
                if diff.header.old_path == filename or diff.header.new_path == filename:
                    try:
                        flag_hunk_list = []
                        if sha in commits:
                            # 将 sha 对应的 flag_hunk_list 取出
                            flag_hunk_list = flag_hunks_list[commits.index(sha)]

                        apply_result = apply_change(
                            diff.hunks,
                            new_line_list,
                            trace=True,
                            flag=True,
                            fuzz=3,
                            symbols=symbols,
                            patch_path=patch_path,
                            extra_flag_hunks=flag_hunk_list,
                        )
                        new_line_list = apply_result.new_line_list

                        logger.debug(
                            f"Apply patch {sha} to {filename}: {len(new_line_list)}"
                        )
                        break  # 保证每个 patch 中每个文件仅有一个 diff（True？）
                    except Exception as e:
                        # # DEBUG
                        # raise e
                        logger.error(f"Failed to apply patch {sha}")
                        logger.error(f"Error: {e}")

                        return
                else:
                    logger.debug(f"Do not match with {filename}, skip")

        if len(apply_result.conflict_hunk_num_list) > 0:
            conflict_list[sha] = apply_result
            logger.info(f"Conflict found in {sha}")
            logger.debug(f"Conflict hunk list: {apply_result.conflict_hunk_num_list}")

    # 写入文件
    with open(filename, mode="w+", encoding="utf-8") as (f):
        for line in new_line_list:
            if line.status:
                f.write(line.content + "\n")

    with open(filename + ".ppatch", mode="a+", encoding="utf-8") as (f):
        for line in new_line_list:
            if line.status:
                f.write(f"{line.index + 1}: {line.content} {line.flag}\n")

    logger.info(f"Conflict count: {len(conflict_list)}")

    return conflict_list
