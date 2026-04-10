from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

import yaml

from subagent_bench.models import Task


class TaskLoader:
    def __init__(self, tasks_dir: Path):
        self.tasks_dir = tasks_dir

    def load_all(self) -> List[Task]:
        tasks: List[Task] = []
        for task_file in sorted(self.tasks_dir.glob("task_*.md")):
            task = self.load_task(task_file)
            tasks.append(task)
        return tasks

    def load_task(self, task_file: Path) -> Task:
        content = task_file.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if not match:
            raise ValueError(f"Missing YAML frontmatter in {task_file}")

        metadata = yaml.safe_load(match.group(1)) or {}
        sections = self._parse_sections(match.group(2))

        return Task(
            task_id=metadata.get("id", ""),
            name=metadata.get("name", ""),
            category=metadata.get("category", ""),
            benchmark_target=metadata.get("benchmark_target", "C6a"),
            task_type=metadata.get("task_type", ""),
            dimensions=metadata.get("dimensions", []),
            grading_type=metadata.get("grading_type", "automated"),
            timeout_seconds=int(metadata.get("timeout_seconds", 120)),
            workspace_files=metadata.get("workspace_files", []),
            prompt=sections.get("Prompt", "").strip(),
            expected_behavior=sections.get("Expected Behavior", "").strip(),
            grading_criteria=self._extract_checklist(sections.get("Grading Criteria", "")),
            automated_checks=sections.get("Automated Checks"),
            llm_judge_rubric=sections.get("LLM Judge Rubric"),
            automated_weights=metadata.get("automated_weights"),
            grading_weights=metadata.get("grading_weights"),
            file_path=task_file,
            frontmatter=metadata,
        )

    def _parse_sections(self, body: str) -> Dict[str, str]:
        sections: Dict[str, str] = {}
        current_name = None
        current_lines: List[str] = []

        for line in body.splitlines():
            header = re.match(r"^##\s+(.+)$", line)
            if header:
                if current_name:
                    sections[current_name] = "\n".join(current_lines).strip()
                current_name = header.group(1).strip()
                current_lines = []
                continue
            if current_name:
                current_lines.append(line)

        if current_name:
            sections[current_name] = "\n".join(current_lines).strip()
        return sections

    def _extract_checklist(self, body: str) -> List[str]:
        criteria: List[str] = []
        for line in body.splitlines():
            match = re.match(r"^-\s+\[[ x]\]\s+(.+)$", line.strip())
            if match:
                criteria.append(match.group(1))
        return criteria
