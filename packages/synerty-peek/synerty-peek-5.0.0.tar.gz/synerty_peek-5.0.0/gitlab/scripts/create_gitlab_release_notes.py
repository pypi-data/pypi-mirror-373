#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Set
from typing import Tuple
from typing import TypeVar
from urllib.parse import quote_plus

import aiohttp
from anthropic import AsyncAnthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class VersionItem(NamedTuple):
    """Base class for version-controlled items (epics and issues)"""

    id: int
    iid: int
    title: str
    is_epic: bool
    description: str
    labels: List[str]
    web_url: str
    comments: List[Dict]
    type: Optional[str]  # BUG, IMPROVEMENT, NEW FEATURE, TASK
    parent_ids: Set[int]  # IDs of parent epics/issues
    child_ids: Set[int]  # IDs of child issues/epics
    summary: Optional[str]


class ItemsAnalysis(NamedTuple):
    """Results of analyzing version items"""

    all_items: Dict[int, VersionItem]  # id -> item
    new_features: Set[int]  # ids of NEW FEATURE items
    improvements: Set[int]  # ids of IMPROVEMENT items
    bugs: Set[int]  # ids of BUG items
    tasks: Set[int]  # ids of TASK items
    skip_ids: Set[int]  # ids of items to skip (part of NEW FEATURES)


GitLabItemData = TypeVar("GitLabItemData", bound=Dict)


class ReleaseNotesGenerator:
    def __init__(
        self,
        version: str,
        gitlab_token: str,
        claude_token: str,
        gitlab_group: str,
        output_format: str = "md",
    ):
        self._comments_cache = {}
        self.version = version
        self.gitlab_token = gitlab_token
        self.claude_token = claude_token
        self.gitlab_group = gitlab_group.strip("/")
        self.output_format = output_format
        self.claude_client = AsyncAnthropic(api_key=claude_token)
        self.gitlab_base_url = self.extract_gitlab_base_url(gitlab_group)
        self.epic_base_url = None
        self.issue_base_url = None
        self.group_id = None
        self.project_ids = []

    async def initialize(self):
        """Initialize group and project IDs needed for API calls"""
        async with aiohttp.ClientSession() as session:
            headers = {"PRIVATE-TOKEN": self.gitlab_token}

            # Get group ID
            encoded_group = quote_plus(self.gitlab_group)
            group_url = f"{self.gitlab_base_url}/api/v4/groups/{encoded_group}"
            async with session.get(group_url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to fetch group info: {await response.text()}"
                    )
                group_data = await response.json()
                self.group_id = group_data["id"]
                self.epic_base_url = f"{self.gitlab_base_url}/api/v4/groups/{self.group_id}/epics"

            # Get project IDs
            projects_url = (
                f"{self.gitlab_base_url}/api/v4/groups/{self.group_id}/projects"
            )
            async with session.get(projects_url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to fetch projects: {await response.text()}"
                    )
                projects = await response.json()
                self.project_ids = [project["id"] for project in projects]
                if self.project_ids:
                    self.issue_base_url = f"{self.gitlab_base_url}/api/v4/projects/{self.project_ids[0]}/issues"

    def extract_gitlab_base_url(self, gitlab_group: str) -> str:
        """Extract GitLab base URL and group path from group URL."""
        if "://" not in gitlab_group:
            self.gitlab_group = gitlab_group
            return "https://gitlab.com"
        parts = gitlab_group.split("://")
        domain = parts[1].split("/")[0]
        self.gitlab_group = "/".join(parts[1].split("/")[1:])
        return f"{parts[0]}://{domain}"

    async def fetch_paginated_data(
        self,
        session: aiohttp.ClientSession,
        url: str,
        params: Dict,
        allow_404: bool = False,
    ) -> List[Dict]:
        """Fetch paginated data from GitLab API"""
        headers = {"PRIVATE-TOKEN": self.gitlab_token}
        all_data = []
        page = 1

        while True:
            params["page"] = page
            async with session.get(
                url, params=params, headers=headers
            ) as response:
                if response.status == 404 and allow_404:
                    return []
                if response.status != 200:
                    raise Exception(
                        f"Failed to fetch data: {await response.text()}"
                    )

                data = await response.json()
                if not data:
                    break

                all_data.extend(data)
                page += 1

        return all_data

    async def fetch_project_issues(
        self, session: aiohttp.ClientSession, project_id: int
    ) -> List[Dict]:
        """Fetch all issues for a specific project"""
        api_url = f"{self.gitlab_base_url}/api/v4/projects/{project_id}/issues"
        params = {
            "labels": f"version:{self.version}",
            "per_page": 100,
            "state": "all",
        }
        return await self.fetch_paginated_data(session, api_url, params)

    async def get_items_with_version(self, search_type: str) -> List[Dict]:
        """Fetch all items (epics/issues) with the specified version label."""
        if search_type not in ["epics", "issues", "all"]:
            raise ValueError("search_type must be 'epics', 'issues', or 'all'")

        await self.initialize()

        async with aiohttp.ClientSession() as session:
            all_items = []
            types_to_fetch = (
                ["epics", "issues"] if search_type == "all" else [search_type]
            )

            for item_type in types_to_fetch:
                if item_type == "epics":
                    params = {
                        "labels": f"version:{self.version}",
                        "per_page": 100,
                    }
                    epics = await self.fetch_paginated_data(
                        session, self.epic_base_url, params
                    )
                    for epic in epics:
                        epic["is_epic"] = True
                    all_items.extend(epics)
                else:
                    for project_id in self.project_ids:
                        issues = await self.fetch_project_issues(
                            session, project_id
                        )
                        for issue in issues:
                            issue["is_epic"] = False
                        all_items.extend(issues)

            epics_count = len([i for i in all_items if "epic_iid" not in i])
            issues_count = len([i for i in all_items if "epic_iid" in i])
            logger.info(
                f"Found {epics_count} epics and {issues_count} issues for version {self.version}"
            )
            return all_items

    async def get_comments(self, item: GitLabItemData) -> List[Dict]:
        """Fetch all comments for an epic or issue with caching."""
        cache_key = f"{item['id']}_{item.get('epic_iid', 'epic')}"

        if cache_key in self._comments_cache:
            return self._comments_cache[cache_key]

        if "epic_iid" in item:
            item_type = "issue"
            item_ref = f"{item['iid']}"
        else:
            item_type = "epic"
            item_ref = f"&{item['iid']}"

        logger.info(f"Loading {item_type} {item_ref} comments")

        async with aiohttp.ClientSession() as session:
            params = {"per_page": 100}
            if item_type == "issue":
                notes_url = f"{self.gitlab_base_url}/api/v4/projects/{item['project_id']}/issues/{item['iid']}/notes"
            else:
                notes_url = f"{self.gitlab_base_url}/api/v4/groups/{self.group_id}/epics/{item['iid']}/notes"

            comments = await self.fetch_paginated_data(
                session, notes_url, params, allow_404=(item_type == "epic")
            )
            self._comments_cache[cache_key] = comments
            return comments

    def determine_item_type(self, labels: List[str]) -> str:
        """Determine the type of an item based on its labels."""
        label_mapping = {
            "bug": "BUG",
            "enhancement": "IMPROVEMENT",
            "feature": "NEW FEATURE",
            "task": "TASK",
        }

        for label in labels:
            label_lower = label.lower()
            for key, value in label_mapping.items():
                if key in label_lower:
                    return value

        return "TASK"

    async def get_claude_summary(self, item: VersionItem) -> str:
        """Get a one-line summary from Claude for an epic or issue."""
        logger.info(f"Summarising issue {item.iid} - {item.title[:50]}...")
        comments_text = "\n".join(
            f"- {comment['body']}"
            for comment in item.comments
            if not comment.get("system", False)
        )

        format_ = {"md": "Markdown", "rst": "reStructuredText"}[
            self.output_format
        ]

        context = f"""Title: {item.title}
Description: {item.description}
IID: {item.iid}
IS Epic: {item.is_epic}

Comments:
{comments_text}

Please provide a one-line summary of this item. 
Focus on the end result/solution, not the journey. 
If this is a bug, include steps to reproduce only if they help users understand the fix.

Please prefix summary with
either "[peek&123] " for epics where 123 is the iid
or "[peek/peek#123] " for issues where 123 is the iid.

Please format you response as {format_}

"""

        response = await self.claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=400,
            temperature=0,
            system="You are a technical writer creating release notes for "
            "AttuneOps.io Automation. Be concise but clear.",
            messages=[{"role": "user", "content": context}],
        )

        return response.content[0].text.strip()

    def map_item_relationships(
        self, items: List[GitLabItemData]
    ) -> Tuple[Dict[int, Set[int]], Dict[int, int], List[int]]:
        """Map relationships between epics and issues"""
        epic_issue_map = {}  # epic_id -> set of issue_ids
        issue_epic_map = {}  # issue_id -> epic_id
        epics = []

        for item in items:
            item_id = item["id"]

            if "epic_iid" in item and item["epic_iid"]:
                epic_id = item["epic_iid"]
                issue_epic_map[item_id] = epic_id
                epic_issue_map.setdefault(epic_id, set()).add(item_id)
            elif "epic_iid" not in item:
                epics.append(item_id)

        return epic_issue_map, issue_epic_map, epics

    def categorize_items(
        self, all_items: Dict[int, VersionItem], epics: List[int]
    ) -> Tuple[Set[int], Set[int], Set[int], Set[int], Set[int]]:
        """Categorize items by type and identify items to skip"""
        new_features = {
            id for id, item in all_items.items() if item.type == "NEW FEATURE"
        }
        improvements = {
            id for id, item in all_items.items() if item.type == "IMPROVEMENT"
        }
        bugs = {id for id, item in all_items.items() if item.type == "BUG"}
        tasks = {id for id, item in all_items.items() if item.type == "TASK"}

        skip_ids = set()
        for epic_id in epics:
            epic = all_items[epic_id]
            if epic.type == "NEW FEATURE":
                skip_ids.update(epic.child_ids)

        return new_features, improvements, bugs, tasks, skip_ids

    async def analyze_relationships(
        self, items: List[GitLabItemData]
    ) -> ItemsAnalysis:
        """Analyze relationships between items and categorize them."""
        epic_issue_map, issue_epic_map, epics = self.map_item_relationships(
            items
        )

        all_items = {}
        for item_data in items:
            item_id = item_data["id"]
            comments = await self.get_comments(item_data)

            item = VersionItem(
                id=item_id,
                iid=item_data["iid"],
                title=item_data["title"],
                is_epic=item_data["is_epic"],
                description=item_data.get("description", ""),
                labels=item_data["labels"],
                web_url=item_data["web_url"],
                comments=comments,
                type=self.determine_item_type(item_data["labels"]),
                parent_ids=(
                    {issue_epic_map[item_id]}
                    if item_id in issue_epic_map
                    else set()
                ),
                child_ids=epic_issue_map.get(item_id, set()),
                summary=None,
            )
            all_items[item_id] = item

        new_features, improvements, bugs, tasks, skip_ids = (
            self.categorize_items(all_items, epics)
        )

        return ItemsAnalysis(
            all_items=all_items,
            new_features=new_features,
            improvements=improvements,
            bugs=bugs,
            tasks=tasks,
            skip_ids=skip_ids,
        )

    def format_item_list(
        self, items: Dict[int, VersionItem], item_ids: Set[int]
    ) -> str:
        """Format a list of items for release notes"""
        return chr(10).join(
            f"- iid={items[id_].iid}- {items[id_].summary}" for id_ in item_ids
        )

    async def process_items_for_notes(
        self, analysis: ItemsAnalysis
    ) -> Dict[int, VersionItem]:
        """Process items and generate summaries for release notes"""
        processed_items = {}
        for item_id, item in analysis.all_items.items():
            if item_id not in analysis.skip_ids or item.type == "NEW FEATURE":
                summary = await self.get_claude_summary(item)
                processed_items[item_id] = item._replace(summary=summary)
        return processed_items

    async def generate_release_notes(self) -> str:
        """Generate release notes by analyzing and processing items."""
        logger.info("Fetching GitLab items for release notes generation")
        items = await self.get_items_with_version("all")
        analysis = await self.analyze_relationships(items)
        processed_items = await self.process_items_for_notes(analysis)

        context = f"""Version: {self.version}

New Features:
{self.format_item_list(processed_items, analysis.new_features)}

Improvements (excluding those part of new features):
{self.format_item_list(processed_items, analysis.improvements - analysis.skip_ids)}

Bug Fixes (excluding those part of new features):
{self.format_item_list(processed_items, analysis.bugs - analysis.skip_ids)}

Tasks (excluding those part of new features):
{self.format_item_list(processed_items, analysis.tasks - analysis.skip_ids)}

Please create release notes in {'reStructuredText' if self.output_format == 'rst' else 'Markdown'} format following these rules:
1. Group by NEW FEATURE, BUG, IMPROVEMENT, and TASK
2. NEW FEATURES get their own sections with descriptions
3. Skip BUGS, TASKS, and IMPROVEMENTS that were part of implementing a NEW FEATURE (already handled in the data)
4. Include steps to reproduce for complex bugs where it helps users understand the fix
5. Use proper {'reST' if self.output_format == 'rst' else 'markdown'} formatting with headers and bullet points


Issues identified as TASKS should only be things that effect development
environments or build scripts
(e.g. no changes to how the delivered software operates)

Please prefix issue bullet points with
either "[peek&123] " for epics where 123 is the iid
or "[peek/peek#123] " for issues where 123 is the iid.

For new features, include a list of epic ids at the end of the section
EG: "Epics: peek&123 peek&456 where 123 is the iid"
If there are no epics, then list the issues
EG: "Issues: peek/peek#123 peek/peek#456 where 123 is the iid"

What is Peek?
Peek Enterprise Extensible Platform allows users access to
Operational Technology outside the control room.
"""

        response = await self.claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            temperature=0,
            system=f"You are a technical writer creating release notes"
            f" in {'reStructuredText' if self.output_format == 'rst' else 'Markdown'}"
            f" format for 'Peek'."
            f" Be professional and clear.",
            messages=[{"role": "user", "content": context}],
        )

        release_notes = response.content[0].text
        logger.info(
            f"Generated {len(release_notes.splitlines())} lines of release notes"
        )
        return release_notes


async def main():
    parser = argparse.ArgumentParser(
        description="Generate release notes from GitLab issues and epics"
    )
    parser.add_argument(
        "version", help="Version number to generate release notes for"
    )
    parser.add_argument(
        "gitlab_group",
        help="GitLab group URL or path (e.g., https://gitlab.com/group/project or group/project)",
    )
    parser.add_argument(
        "--format",
        choices=["md", "rst"],
        default="md",
        help="Output format (markdown or reStructuredText)",
    )
    parser.add_argument(
        "--gitlab-token",
        help="GitLab API token (falls back to GITLAB_TOKEN env var)",
    )
    parser.add_argument(
        "--claude-token",
        help="Claude API token (falls back to CLAUDE_TOKEN env var)",
    )
    args = parser.parse_args()

    gitlab_token = args.gitlab_token or os.getenv("GITLAB_TOKEN")
    claude_token = args.claude_token or os.getenv("CLAUDE_TOKEN")

    if not gitlab_token:
        logger.error(
            "GitLab token must be provided via --gitlab-token"
            " or GITLAB_TOKEN environment variable"
        )
        sys.exit(1)

    if not claude_token:
        logger.error(
            "Claude token must be provided via --claude-token"
            " or CLAUDE_TOKEN environment variable"
        )
        sys.exit(1)

    if not gitlab_token or not claude_token:
        logger.error(
            "GITLAB_TOKEN and CLAUDE_TOKEN environment variables are required"
        )
        sys.exit(1)

    try:
        generator = ReleaseNotesGenerator(
            f"v{args.version.strip('v')}",
            gitlab_token,
            claude_token,
            args.gitlab_group,
            args.format,
        )
        release_notes = await generator.generate_release_notes()
        print(release_notes)
        Path(f"release-notes.{args.format}").write_text(release_notes)

        logger.info("Release notes generated and saved to release-notes.md")
    except Exception as e:
        logger.error(f"Failed to generate release notes: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
