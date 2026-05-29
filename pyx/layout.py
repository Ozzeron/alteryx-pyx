# Pyx, a Python module for creating, reading, and editing Alteryx Designer workflows entirely in code
# Copyright (C) 2020  David T. Wilcox
# Fork: alteryx-pyx — extended for automotive data pipelines

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Layout utilities for Alteryx workflow tools.

Provides topological-sort-based layout algorithms that position tools
into readable top-to-bottom or left-to-right arrangements.
"""

from collections import defaultdict, deque
from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .workflow import Workflow

from .tool import ToolPosition


# Side/decoration tools that should be placed to the right of main flow
_SIDE_PLUGINS = {
    'AlteryxBasePluginsGui.BrowseV2.BrowseV2',
    'AlteryxGuiToolkit.TextBox.TextBox',
    'AlteryxGuiToolkit.ToolContainer.ToolContainer',
}


def _build_topo_order(workflow: 'Workflow') -> list:
    """
    Returns tool IDs in topological order (sources first).
    Uses Kahn's algorithm. Cycles are broken arbitrarily.
    """
    in_degree: Dict[int, int] = {tid: 0 for tid in workflow.tools}
    adjacency: Dict[int, list] = defaultdict(list)

    for conn in workflow.connections:
        src = conn.origin_tool_id
        dst = conn.destination_tool_id
        if src in workflow.tools and dst in workflow.tools:
            adjacency[src].append(dst)
            in_degree[dst] += 1

    queue = deque(tid for tid, deg in in_degree.items() if deg == 0)
    order = []

    while queue:
        tid = queue.popleft()
        order.append(tid)
        for neighbor in adjacency[tid]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Include any remaining nodes (cycle members)
    seen = set(order)
    for tid in workflow.tools:
        if tid not in seen:
            order.append(tid)

    return order


def layout_vertical(
    workflow: 'Workflow',
    x_start: int = 50,
    y_start: int = 50,
    v_gap: int = 160,
    h_gap: int = 180,
) -> Dict[int, Tuple[int, int]]:
    """
    Lay out workflow top-to-bottom using topological sort.
    Side tools (Browse, TextBox, Container) go to the right.

    Returns:
        dict mapping tool_id -> (x, y)
    """
    order = _build_topo_order(workflow)

    positions: Dict[int, Tuple[int, int]] = {}
    main_y = y_start
    side_x = x_start + h_gap * 2
    side_y = y_start

    for tid in order:
        tool = workflow.tools[tid]
        if tool.plugin in _SIDE_PLUGINS:
            positions[tid] = (side_x, side_y)
            side_y += v_gap
        else:
            positions[tid] = (x_start, main_y)
            main_y += v_gap

    return positions


def layout_horizontal(
    workflow: 'Workflow',
    x_start: int = 50,
    y_start: int = 50,
    h_gap: int = 240,
    v_gap: int = 120,
) -> Dict[int, Tuple[int, int]]:
    """
    Lay out workflow left-to-right using topological sort.
    Each node's x position corresponds to its depth in the DAG.

    Returns:
        dict mapping tool_id -> (x, y)
    """
    order = _build_topo_order(workflow)
    adjacency: Dict[int, list] = defaultdict(list)

    for conn in workflow.connections:
        src = conn.origin_tool_id
        dst = conn.destination_tool_id
        if src in workflow.tools and dst in workflow.tools:
            adjacency[src].append(dst)

    # Assign depth (longest path to each node)
    depth: Dict[int, int] = {tid: 0 for tid in workflow.tools}
    for tid in order:
        for neighbor in adjacency[tid]:
            depth[neighbor] = max(depth[neighbor], depth[tid] + 1)

    # Group by depth, assign y within each column
    from collections import defaultdict
    col_tools: Dict[int, list] = defaultdict(list)
    for tid in order:
        col_tools[depth[tid]].append(tid)

    positions: Dict[int, Tuple[int, int]] = {}
    for col, tids in col_tools.items():
        x = x_start + col * h_gap
        for row_idx, tid in enumerate(tids):
            y = y_start + row_idx * v_gap
            positions[tid] = (x, y)

    return positions


def apply_layout(workflow: 'Workflow', positions: Dict[int, Tuple[int, int]]) -> None:
    """
    Apply a position dict to the workflow tools in-place.

    Args:
        workflow: The workflow to update.
        positions: Mapping of tool_id -> (x, y) as returned by layout_vertical/horizontal.
    """
    for tid, (x, y) in positions.items():
        if tid in workflow.tools:
            workflow.tools[tid].position = ToolPosition(x=x, y=y)
