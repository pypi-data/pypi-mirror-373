"""
📊 Qualitative Reasoning - Visualization Engine Module
====================================================

This module provides comprehensive visualization and reporting capabilities for qualitative
reasoning systems, implementing presentation layer functions that make qualitative physics
results understandable to users through visual and textual output.

📚 Theoretical Foundation:
Forbus, K. D., & de Kleer, J. (1993). "Building Problem Solvers", MIT Press
de Kleer, J., & Brown, J. S. (1984). "A Qualitative Physics Based on Confluences"
Larkin, J. H., & Simon, H. A. (1987). "Why a Diagram is (Sometimes) Worth Ten Thousand Words"

🎯 Visualization Theory:
The visualization engine implements the presentation layer that transforms abstract
qualitative reasoning results into human-comprehensible formats. This bridges the gap
between symbolic AI reasoning and human understanding through multiple modalities:

1. **State Visualization**: Present current system state in human-readable format
2. **History Rendering**: Show temporal evolution of qualitative states
3. **Report Generation**: Create comprehensive analysis reports
4. **Export Functionality**: Output results in various formats (text, JSON, markdown)
5. **Visual Representations**: ASCII art diagrams and charts for system states
6. **Trend Display**: Show quantity evolution patterns over time

🔬 Presentation Theory:
Effective presentation of qualitative reasoning requires:
- **Multi-level Detail**: From high-level summaries to detailed breakdowns  
- **Temporal Context**: Show how states evolve over time
- **Causal Clarity**: Make cause-and-effect relationships visible
- **Pattern Recognition**: Highlight important behavioral patterns
- **Interactive Exploration**: Allow users to drill down into details

🌟 Key Visualization Capabilities:
- Rich system state visualization with trend indicators
- Historical state progression displays
- Comprehensive behavior summary reports
- Multi-format export capabilities (text, JSON, markdown, CSV)
- ASCII art system diagrams and charts
- Quantity relationship visualizations
- Process activation timelines
- Constraint violation reporting
- Causal chain visualization
- Statistical pattern displays

🎨 Visualization Features:
- Unicode symbols for trends and directions (↗ ↘ →)
- Color-coded state displays (when supported)
- Hierarchical information organization
- Tabular data presentations
- Graph-like relationship displays
- Timeline-based historical views
- Summary dashboards
- Interactive exploration prompts

🔧 Integration:
This mixin integrates with:
- Core types for accessing qualitative data structures
- Analysis engine for behavioral explanations
- Simulation engine for state history
- All other modules for comprehensive reporting

Author: Benedict Chen
Based on foundational work by Kenneth Forbus, Johan de Kleer, and Jill Larkin
"""

from typing import Dict, List, Tuple, Union, Optional, Any, Set
from dataclasses import dataclass, field
import json
import warnings
from datetime import datetime

# Import core types
try:
    from .core_types import (
        QualitativeValue, QualitativeDirection, QualitativeQuantity, 
        QualitativeState, QualitativeProcess
    )
except ImportError:
    # Fallback imports
    try:
        from core_types import (
            QualitativeValue, QualitativeDirection, QualitativeQuantity,
            QualitativeState, QualitativeProcess  
        )
    except ImportError:
        from qualitative_reasoning.qr_modules.core_types import (
            QualitativeValue, QualitativeDirection, QualitativeQuantity,
            QualitativeState, QualitativeProcess
        )


@dataclass
class VisualizationConfig:
    """Configuration for visualization output formatting and styling"""
    
    # Display settings
    show_unicode_symbols: bool = True
    show_trend_indicators: bool = True
    show_confidence_scores: bool = True
    show_timestamps: bool = True
    max_history_items: int = 10
    
    # Formatting settings
    indent_size: int = 2
    column_width: int = 15
    max_line_length: int = 80
    use_colors: bool = False  # Terminal colors (when supported)
    
    # Content settings
    include_metadata: bool = True
    include_relationships: bool = True
    include_constraints: bool = True
    include_explanations: bool = True
    detail_level: str = "medium"  # "basic", "medium", "detailed", "comprehensive"
    
    # Export settings
    export_format: str = "text"  # "text", "json", "markdown", "csv", "html"
    include_charts: bool = True
    include_diagrams: bool = True


@dataclass
class VisualizationReport:
    """Comprehensive visualization report containing multiple presentation formats"""
    
    title: str
    timestamp: str
    summary: str
    sections: Dict[str, str] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_section(self, name: str, content: str):
        """Add a section to the report"""
        self.sections[name] = content
        
    def add_data(self, key: str, value: Any):
        """Add structured data to the report"""
        self.data[key] = value
        
    def to_text(self) -> str:
        """Convert report to formatted text"""
        lines = [
            f"{'='*60}",
            f"{self.title}",
            f"{'='*60}",
            f"Generated: {self.timestamp}",
            "",
            f"Summary:",
            f"{self.summary}",
            ""
        ]
        
        for section_name, section_content in self.sections.items():
            lines.extend([
                f"{section_name}:",
                f"{'-'*len(section_name)}",
                section_content,
                ""
            ])
            
        return "\n".join(lines)
        
    def to_json(self) -> str:
        """Convert report to JSON format"""
        return json.dumps({
            "title": self.title,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "sections": self.sections,
            "data": self.data,
            "metadata": self.metadata
        }, indent=2)
        
    def to_markdown(self) -> str:
        """Convert report to Markdown format"""
        lines = [
            f"# {self.title}",
            "",
            f"**Generated:** {self.timestamp}",
            "",
            f"## Summary",
            "",
            self.summary,
            ""
        ]
        
        for section_name, section_content in self.sections.items():
            lines.extend([
                f"## {section_name}",
                "",
                section_content,
                ""
            ])
            
        return "\n".join(lines)


class VisualizationEngineMixin:
    """
    📊 Advanced Visualization Engine for Qualitative Reasoning Systems
    
    This mixin provides comprehensive visualization and reporting capabilities that
    transform abstract qualitative reasoning results into human-comprehensible
    presentations across multiple formats and detail levels.
    
    The visualization engine implements the presentation layer that bridges the gap
    between symbolic AI reasoning and human understanding through:
    - Rich textual displays with unicode symbols and formatting
    - Structured data exports in multiple formats
    - Interactive exploration capabilities
    - Temporal visualization of state evolution
    - Causal relationship displays
    - Statistical pattern presentations
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize visualization engine components"""
        super().__init__(*args, **kwargs)
        
        # Visualization configuration
        self._viz_config = VisualizationConfig()
        self._viz_cache = {}
        self._export_history = []
        
        # Symbol mappings for display
        self._trend_symbols = {
            "+" : "↗", "-": "↘", "0": "→", "?": "❓",
            "increasing": "↗", "decreasing": "↘", "steady": "→", "unknown": "❓"
        }
        
        self._magnitude_symbols = {
            "pos_inf": "∞+", "neg_inf": "∞-", "pos_large": "++", "neg_large": "--",
            "pos_small": "+", "neg_small": "-", "zero": "0", "increasing": "↗", "decreasing": "↘"
        }
        
        # Initialize color support (if available)
        self._color_support = self._detect_color_support()
        
    def visualize_system_state(self, include_history: bool = True, detail_level: str = None) -> VisualizationReport:
        """
        📊 Visualize current system state and optional history
        
        Creates a comprehensive visualization of the current qualitative state
        including quantities, processes, relationships, and temporal context.
        
        Args:
            include_history: Whether to include historical state information
            detail_level: Level of detail ("basic", "medium", "detailed", "comprehensive")
            
        Returns:
            VisualizationReport: Complete visualization report
            
        🎯 Visualization Components:
        1. **System Overview**: High-level system status and statistics
        2. **Current Quantities**: All quantities with magnitudes and trends
        3. **Active Processes**: Currently running processes and their influences
        4. **Relationships**: Derived relationships between quantities
        5. **History**: Temporal evolution of system state (if requested)
        6. **Constraints**: System constraints and any violations
        7. **Analysis Summary**: Key insights and patterns
        """
        
        detail_level = detail_level or self._viz_config.detail_level
        
        # Create visualization report
        report = VisualizationReport(
            title=f"System State: {getattr(self, 'domain_name', 'Qualitative Reasoning System')}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=self._generate_system_summary()
        )
        
        # Add core sections
        report.add_section("System Overview", self._visualize_system_overview())
        report.add_section("Current Quantities", self._visualize_quantities(detail_level))
        report.add_section("Active Processes", self._visualize_active_processes(detail_level))
        
        if self._viz_config.include_relationships:
            report.add_section("Relationships", self._visualize_relationships())
            
        if include_history and hasattr(self, 'state_history') and len(self.state_history) > 1:
            report.add_section("State History", self._visualize_state_history(detail_level))
            
        if self._viz_config.include_constraints:
            report.add_section("Constraints", self._visualize_constraints())
            
        if detail_level in ["detailed", "comprehensive"]:
            report.add_section("Analysis Summary", self._generate_analysis_summary())
            
        # Add structured data
        report.add_data("quantities", self._export_quantities_data())
        report.add_data("processes", self._export_processes_data())
        report.add_data("relationships", self._export_relationships_data())
        
        # Cache and display
        self._viz_cache['last_state_visualization'] = report
        
        # Print to console by default (original behavior)
        print(self._format_console_output(report))
        
        return report
        
    def _generate_system_summary(self) -> str:
        """Generate a high-level summary of the system state"""
        
        # Count quantities by state
        qty_count = len(self.quantities) if hasattr(self, 'quantities') else 0
        active_processes = len([p for p in self.processes.values() if p.active]) if hasattr(self, 'processes') else 0
        total_processes = len(self.processes) if hasattr(self, 'processes') else 0
        
        # Analyze quantity states
        changing_count = 0
        stable_count = 0
        
        if hasattr(self, 'quantities'):
            for qty in self.quantities.values():
                direction_value = getattr(qty.direction, 'value', str(qty.direction))
                if direction_value in ['0', 'steady', 'std']:
                    stable_count += 1
                else:
                    changing_count += 1
                    
        summary_lines = [
            f"System contains {qty_count} quantities ({changing_count} changing, {stable_count} stable)",
            f"Process activity: {active_processes}/{total_processes} active"
        ]
        
        if hasattr(self, 'state_history'):
            summary_lines.append(f"Historical states: {len(self.state_history)} recorded")
            
        return "\n".join(summary_lines)
        
    def _visualize_system_overview(self) -> str:
        """Create system overview visualization"""
        
        lines = []
        
        # System info
        domain_name = getattr(self, 'domain_name', 'Unknown System')
        lines.append(f"Domain: {domain_name}")
        lines.append("")
        
        # Statistics
        if hasattr(self, 'quantities'):
            lines.append(f"Quantities: {len(self.quantities)}")
        if hasattr(self, 'processes'):  
            active_count = len([p for p in self.processes.values() if p.active])
            lines.append(f"Processes: {active_count}/{len(self.processes)} active")
        if hasattr(self, 'constraints'):
            lines.append(f"Constraints: {len(self.constraints)}")
            
        # Current time
        if hasattr(self, 'current_state') and self.current_state:
            lines.append(f"Current Time: {self.current_state.time_point}")
            
        return "\n".join(lines)
        
    def _visualize_quantities(self, detail_level: str) -> str:
        """Visualize current quantities with their states"""
        
        if not hasattr(self, 'quantities') or not self.quantities:
            return "No quantities defined"
            
        lines = []
        
        for name, qty in self.quantities.items():
            # Get display values
            magnitude_val = getattr(qty.magnitude, 'value', str(qty.magnitude))
            direction_val = getattr(qty.direction, 'value', str(qty.direction))
            
            # Get symbols
            trend_symbol = self._trend_symbols.get(direction_val, direction_val)
            magnitude_display = self._magnitude_symbols.get(magnitude_val, magnitude_val)
            
            # Format basic display
            name_padded = f"{name:15}"
            magnitude_padded = f"{magnitude_display:15}"
            
            basic_line = f"  {name_padded} = {magnitude_padded} {trend_symbol}"
            
            if detail_level == "basic":
                lines.append(basic_line)
            else:
                # Add detailed information
                lines.append(basic_line)
                
                if detail_level in ["detailed", "comprehensive"]:
                    # Add landmark values if available
                    if hasattr(qty, 'landmark_values') and qty.landmark_values:
                        landmarks_str = ", ".join(map(str, qty.landmark_values))
                        lines.append(f"    Landmarks: [{landmarks_str}]")
                    
                    # Add units if available
                    if hasattr(qty, 'units') and qty.units:
                        lines.append(f"    Units: {qty.units}")
                        
                    # Add description if available
                    if hasattr(qty, 'description') and qty.description:
                        lines.append(f"    Description: {qty.description}")
                        
                    lines.append("")  # Spacing between quantities
                    
        return "\n".join(lines)
        
    def _visualize_active_processes(self, detail_level: str) -> str:
        """Visualize active processes and their influences"""
        
        if not hasattr(self, 'processes') or not self.processes:
            return "No processes defined"
            
        active_processes = [name for name, process in self.processes.items() if process.active]
        
        lines = []
        lines.append(f"Active Processes: {active_processes}")
        lines.append("")
        
        if detail_level != "basic":
            for name, process in self.processes.items():
                status = "ACTIVE" if process.active else "INACTIVE"
                status_indicator = "●" if process.active else "○"
                
                lines.append(f"  {status_indicator} {name}: {status}")
                
                if detail_level in ["detailed", "comprehensive"] or process.active:
                    # Show influences
                    if process.influences:
                        lines.append(f"    Influences: {', '.join(process.influences)}")
                    
                    # Show conditions
                    if process.preconditions:
                        lines.append(f"    Preconditions: {', '.join(process.preconditions)}")
                    if process.quantity_conditions:
                        lines.append(f"    Qty Conditions: {', '.join(process.quantity_conditions)}")
                        
                    lines.append("")
                    
        return "\n".join(lines)
        
    def _visualize_relationships(self) -> str:
        """Visualize derived relationships between quantities"""
        
        # Get relationships from analysis or current state
        relationships = {}
        
        if hasattr(self, 'current_state') and self.current_state and self.current_state.relationships:
            relationships = self.current_state.relationships
        elif hasattr(self, 'derive_relationships'):
            try:
                relationships = self.derive_relationships()
            except:
                relationships = {}
                
        if not relationships:
            return "No relationships derived"
            
        lines = []
        
        # Group relationships by type
        relationship_groups = {}
        for rel_name, rel_type in relationships.items():
            if rel_type not in relationship_groups:
                relationship_groups[rel_type] = []
            relationship_groups[rel_type].append(rel_name)
            
        for rel_type, rel_names in relationship_groups.items():
            lines.append(f"  {rel_type}: {len(rel_names)}")
            for rel_name in rel_names[:5]:  # Limit display
                lines.append(f"    - {rel_name}")
            if len(rel_names) > 5:
                lines.append(f"    ... and {len(rel_names) - 5} more")
            lines.append("")
            
        return "\n".join(lines)
        
    def _visualize_state_history(self, detail_level: str) -> str:
        """Visualize historical state progression"""
        
        if not hasattr(self, 'state_history') or len(self.state_history) <= 1:
            return "No historical states available"
            
        lines = []
        max_items = min(self._viz_config.max_history_items, len(self.state_history))
        
        lines.append(f"Showing last {max_items} states:")
        lines.append("")
        
        for i, state in enumerate(self.state_history[-max_items:]):
            lines.append(f"  {state.time_point}: {len(state.quantities)} quantities tracked")
            
            if detail_level in ["detailed", "comprehensive"]:
                # Show quantity changes from previous state
                if i > 0:
                    prev_state = self.state_history[-max_items + i - 1]
                    changes = self._detect_state_changes(prev_state, state)
                    if changes:
                        for change in changes[:3]:  # Limit changes shown
                            lines.append(f"    → {change}")
                            
        return "\n".join(lines)
        
    def _visualize_constraints(self) -> str:
        """Visualize system constraints and any violations"""
        
        if not hasattr(self, 'constraints') or not self.constraints:
            return "No constraints defined"
            
        lines = []
        violations = []
        satisfied = []
        
        for constraint in self.constraints:
            try:
                if hasattr(self, '_evaluate_constraint') and self._evaluate_constraint(constraint):
                    satisfied.append(constraint)
                else:
                    violations.append(constraint)
            except:
                violations.append(constraint + " (evaluation error)")
                
        lines.append(f"Constraint Status: {len(satisfied)} satisfied, {len(violations)} violated")
        lines.append("")
        
        if violations:
            lines.append("⚠️  Violations:")
            for violation in violations[:5]:  # Limit display
                lines.append(f"  - {violation}")
            if len(violations) > 5:
                lines.append(f"  ... and {len(violations) - 5} more")
            lines.append("")
            
        if satisfied and self._viz_config.detail_level in ["detailed", "comprehensive"]:
            lines.append("✓ Satisfied:")
            for constraint in satisfied[:3]:  # Limit display
                lines.append(f"  - {constraint}")
            if len(satisfied) > 3:
                lines.append(f"  ... and {len(satisfied) - 3} more")
                
        return "\n".join(lines)
        
    def _generate_analysis_summary(self) -> str:
        """Generate analytical summary of system behavior"""
        
        lines = []
        
        # Try to get behavior summary if analysis engine is available
        if hasattr(self, 'generate_behavior_summary'):
            try:
                summary = self.generate_behavior_summary()
                
                if 'system_health' in summary:
                    health = summary['system_health']
                    lines.append(f"System Health: {health.get('overall_health', 'unknown')}")
                    lines.append(f"Stability Score: {health.get('stability_score', 0.0):.2f}")
                    lines.append("")
                    
                if 'behavioral_patterns' in summary:
                    patterns = summary['behavioral_patterns']
                    lines.append("Behavioral Patterns:")
                    for pattern_name, pattern_value in patterns.items():
                        lines.append(f"  {pattern_name}: {pattern_value}")
                    lines.append("")
                    
            except Exception as e:
                lines.append(f"Analysis unavailable: {str(e)}")
                
        # Basic pattern analysis
        if hasattr(self, 'quantities'):
            changing = sum(1 for qty in self.quantities.values() 
                          if getattr(qty.direction, 'value', str(qty.direction)) not in ['0', 'steady', 'std'])
            total = len(self.quantities)
            
            if changing == 0:
                lines.append("System Pattern: Equilibrium (no changing quantities)")
            elif changing == total:
                lines.append("System Pattern: Fully Dynamic (all quantities changing)")
            else:
                lines.append(f"System Pattern: Partially Dynamic ({changing}/{total} changing)")
                
        return "\n".join(lines)
        
    def _detect_state_changes(self, prev_state: QualitativeState, curr_state: QualitativeState) -> List[str]:
        """Detect changes between two states"""
        
        changes = []
        
        # Check for quantity changes
        for qty_name in curr_state.quantities:
            if qty_name in prev_state.quantities:
                prev_qty = prev_state.quantities[qty_name]
                curr_qty = curr_state.quantities[qty_name]
                
                # Check magnitude changes
                if prev_qty.magnitude != curr_qty.magnitude:
                    prev_mag = getattr(prev_qty.magnitude, 'value', str(prev_qty.magnitude))
                    curr_mag = getattr(curr_qty.magnitude, 'value', str(curr_qty.magnitude))
                    changes.append(f"{qty_name} magnitude: {prev_mag} → {curr_mag}")
                    
                # Check direction changes
                if prev_qty.direction != curr_qty.direction:
                    prev_dir = getattr(prev_qty.direction, 'value', str(prev_qty.direction))
                    curr_dir = getattr(curr_qty.direction, 'value', str(curr_qty.direction))
                    changes.append(f"{qty_name} direction: {prev_dir} → {curr_dir}")
                    
        return changes
        
    def _format_console_output(self, report: VisualizationReport) -> str:
        """Format report for console output (original behavior)"""
        
        lines = []
        
        # Header
        lines.append(f"\n📊 System State: {getattr(self, 'domain_name', 'Qualitative Reasoning System')}")
        lines.append("=" * 50)
        lines.append("")
        
        # Current quantities
        lines.append("Quantities:")
        if hasattr(self, 'quantities'):
            for name, qty in self.quantities.items():
                magnitude_val = getattr(qty.magnitude, 'value', str(qty.magnitude))
                direction_val = getattr(qty.direction, 'value', str(qty.direction))
                trend_symbol = self._trend_symbols.get(direction_val, direction_val)
                lines.append(f"  {name:15} = {magnitude_val:15} {trend_symbol}")
                
        # Active processes
        lines.append("")
        if hasattr(self, 'processes'):
            active_processes = [name for name, process in self.processes.items() if process.active]
            lines.append(f"Active Processes: {active_processes}")
            
        # Relationships
        if hasattr(self, 'current_state') and self.current_state and self.current_state.relationships:
            lines.append("")
            lines.append("Derived Relationships:")
            for rel_name, rel_type in self.current_state.relationships.items():
                lines.append(f"  {rel_name}: {rel_type}")
                
        # History
        if hasattr(self, 'state_history') and len(self.state_history) > 1:
            lines.append("")
            lines.append(f"State History ({len(self.state_history)} states):")
            for i, state in enumerate(self.state_history[-5:]):  # Show last 5
                lines.append(f"  {state.time_point}: {len(state.quantities)} quantities tracked")
                
        return "\n".join(lines)
        
    def render_state_history(self, format_type: str = "timeline") -> str:
        """
        📈 Render historical state evolution in various formats
        
        Args:
            format_type: Type of rendering ("timeline", "table", "chart", "summary")
            
        Returns:
            Formatted string representation of state history
        """
        
        if not hasattr(self, 'state_history') or not self.state_history:
            return "No state history available"
            
        if format_type == "timeline":
            return self._render_timeline_history()
        elif format_type == "table":
            return self._render_tabular_history()
        elif format_type == "chart":
            return self._render_chart_history()
        elif format_type == "summary":
            return self._render_summary_history()
        else:
            return self._render_timeline_history()
            
    def _render_timeline_history(self) -> str:
        """Render history as a timeline"""
        
        lines = []
        lines.append("Timeline View:")
        lines.append("─" * 40)
        
        for i, state in enumerate(self.state_history):
            # Timeline marker
            marker = "●" if i == len(self.state_history) - 1 else "○"
            
            lines.append(f"{marker} {state.time_point}")
            
            # Show key changes
            if i > 0:
                changes = self._detect_state_changes(self.state_history[i-1], state)
                for change in changes[:2]:  # Limit changes shown
                    lines.append(f"  └─ {change}")
                    
            lines.append("")
            
        return "\n".join(lines)
        
    def _render_tabular_history(self) -> str:
        """Render history in tabular format"""
        
        if not hasattr(self, 'quantities') or not self.quantities:
            return "No quantities to display"
            
        lines = []
        
        # Header
        qty_names = list(self.quantities.keys())[:5]  # Limit columns
        header = f"{'Time':<12} " + " ".join(f"{name[:8]:>10}" for name in qty_names)
        lines.append(header)
        lines.append("─" * len(header))
        
        # Data rows
        for state in self.state_history[-10:]:  # Last 10 states
            row_parts = [f"{state.time_point:<12}"]
            
            for qty_name in qty_names:
                if qty_name in state.quantities:
                    qty = state.quantities[qty_name]
                    magnitude_val = getattr(qty.magnitude, 'value', str(qty.magnitude))
                    direction_val = getattr(qty.direction, 'value', str(qty.direction))
                    trend_symbol = self._trend_symbols.get(direction_val, direction_val)
                    cell_value = f"{magnitude_val[:6]:>8}{trend_symbol:>2}"
                else:
                    cell_value = f"{'─':>10}"
                row_parts.append(cell_value)
                
            lines.append(" ".join(row_parts))
            
        return "\n".join(lines)
        
    def _render_chart_history(self) -> str:
        """Render history as ASCII chart"""
        
        lines = []
        lines.append("ASCII Chart View:")
        lines.append("")
        
        # Simple bar chart of changing quantities over time
        if hasattr(self, 'quantities'):
            for qty_name in list(self.quantities.keys())[:3]:  # Limit to 3 quantities
                lines.append(f"{qty_name}:")
                
                chart_line = "  "
                for state in self.state_history[-20:]:  # Last 20 states
                    if qty_name in state.quantities:
                        qty = state.quantities[qty_name]
                        direction_val = getattr(qty.direction, 'value', str(qty.direction))
                        
                        if direction_val in ['+', 'increasing', 'inc']:
                            chart_line += "▲"
                        elif direction_val in ['-', 'decreasing', 'dec']:
                            chart_line += "▼"
                        else:
                            chart_line += "─"
                    else:
                        chart_line += "?"
                        
                lines.append(chart_line)
                lines.append("")
                
        return "\n".join(lines)
        
    def _render_summary_history(self) -> str:
        """Render concise history summary"""
        
        lines = []
        
        total_states = len(self.state_history)
        lines.append(f"History Summary: {total_states} states recorded")
        
        if total_states > 0:
            first_state = self.state_history[0]
            last_state = self.state_history[-1]
            lines.append(f"Period: {first_state.time_point} → {last_state.time_point}")
            
            # Count transitions
            major_transitions = 0
            for i in range(1, len(self.state_history)):
                changes = self._detect_state_changes(self.state_history[i-1], self.state_history[i])
                if len(changes) > 0:
                    major_transitions += 1
                    
            lines.append(f"Major Transitions: {major_transitions}")
            
        return "\n".join(lines)
        
    def generate_comprehensive_report(self, include_predictions: bool = False) -> VisualizationReport:
        """
        📋 Generate comprehensive system analysis report
        
        Args:
            include_predictions: Whether to include future state predictions
            
        Returns:
            VisualizationReport: Complete analysis report
        """
        
        report = VisualizationReport(
            title=f"Comprehensive Analysis: {getattr(self, 'domain_name', 'Qualitative System')}",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary="Complete qualitative reasoning system analysis and behavior report"
        )
        
        # Add all major sections
        report.add_section("Executive Summary", self._generate_executive_summary())
        report.add_section("System State", self._visualize_system_overview())
        report.add_section("Quantity Analysis", self._visualize_quantities("comprehensive"))
        report.add_section("Process Analysis", self._visualize_active_processes("comprehensive"))
        report.add_section("Relationship Analysis", self._visualize_relationships())
        report.add_section("Historical Evolution", self._visualize_state_history("comprehensive"))
        report.add_section("Constraint Status", self._visualize_constraints())
        report.add_section("Behavioral Patterns", self._generate_analysis_summary())
        
        # Add predictions if requested
        if include_predictions and hasattr(self, 'predict_future_states'):
            try:
                predictions = self.predict_future_states(3)
                if predictions:
                    report.add_section("Future Predictions", self._visualize_predictions(predictions))
            except Exception as e:
                report.add_section("Future Predictions", f"Prediction unavailable: {str(e)}")
                
        # Add metadata
        report.metadata = {
            "generation_time": datetime.now().isoformat(),
            "system_type": "qualitative_reasoning",
            "version": "1.0",
            "includes_predictions": include_predictions
        }
        
        return report
        
    def _generate_executive_summary(self) -> str:
        """Generate executive summary of system status"""
        
        lines = []
        
        # System health assessment
        if hasattr(self, 'quantities'):
            total_qty = len(self.quantities)
            changing_qty = sum(1 for qty in self.quantities.values() 
                             if getattr(qty.direction, 'value', str(qty.direction)) not in ['0', 'steady', 'std'])
            
            lines.append(f"System contains {total_qty} quantities, {changing_qty} are currently changing.")
            
        if hasattr(self, 'processes'):
            active_count = len([p for p in self.processes.values() if p.active])
            total_count = len(self.processes)
            activity_ratio = active_count / total_count if total_count > 0 else 0
            
            if activity_ratio > 0.7:
                activity_level = "high"
            elif activity_ratio > 0.3:
                activity_level = "moderate"
            else:
                activity_level = "low"
                
            lines.append(f"Process activity level: {activity_level} ({active_count}/{total_count} active).")
            
        # Constraint status
        if hasattr(self, 'constraints'):
            violations = 0
            for constraint in self.constraints:
                try:
                    if hasattr(self, '_evaluate_constraint') and not self._evaluate_constraint(constraint):
                        violations += 1
                except:
                    violations += 1
                    
            if violations == 0:
                lines.append("All system constraints are satisfied.")
            else:
                lines.append(f"Warning: {violations} constraint violations detected.")
                
        return "\n".join(lines)
        
    def _visualize_predictions(self, predictions: List) -> str:
        """Visualize future state predictions"""
        
        lines = []
        lines.append(f"Future State Predictions ({len(predictions)} steps):")
        lines.append("")
        
        for i, pred_state in enumerate(predictions, 1):
            lines.append(f"Step {i} ({pred_state.time_point}):")
            
            # Show key predicted changes
            for qty_name, qty in pred_state.quantities.items():
                magnitude_val = getattr(qty.magnitude, 'value', str(qty.magnitude))
                direction_val = getattr(qty.direction, 'value', str(qty.direction))
                trend_symbol = self._trend_symbols.get(direction_val, direction_val)
                lines.append(f"  {qty_name}: {magnitude_val} {trend_symbol}")
                
            lines.append("")
            
        return "\n".join(lines)
        
    def export_data(self, format_type: str = "json", filename: Optional[str] = None) -> str:
        """
        💾 Export system data in various formats
        
        Args:
            format_type: Export format ("json", "csv", "markdown", "text")
            filename: Optional filename to save to
            
        Returns:
            Exported data as string
        """
        
        if format_type == "json":
            return self._export_json(filename)
        elif format_type == "csv":
            return self._export_csv(filename)
        elif format_type == "markdown":
            return self._export_markdown(filename)
        elif format_type == "text":
            return self._export_text(filename)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
            
    def _export_json(self, filename: Optional[str] = None) -> str:
        """Export system state as JSON"""
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "domain_name": getattr(self, 'domain_name', 'Unknown'),
            "quantities": self._export_quantities_data(),
            "processes": self._export_processes_data(),
            "relationships": self._export_relationships_data(),
            "state_history": self._export_history_data()
        }
        
        json_str = json.dumps(data, indent=2)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(json_str)
                
        return json_str
        
    def _export_csv(self, filename: Optional[str] = None) -> str:
        """Export quantities as CSV"""
        
        lines = []
        
        # Header
        lines.append("quantity_name,magnitude,direction,active_processes")
        
        # Data rows
        if hasattr(self, 'quantities'):
            for name, qty in self.quantities.items():
                magnitude_val = getattr(qty.magnitude, 'value', str(qty.magnitude))
                direction_val = getattr(qty.direction, 'value', str(qty.direction))
                
                # Find processes affecting this quantity
                affecting_processes = []
                if hasattr(self, 'processes'):
                    for proc_name, process in self.processes.items():
                        if process.active and any(name in influence for influence in process.influences):
                            affecting_processes.append(proc_name)
                            
                processes_str = ";".join(affecting_processes)
                lines.append(f"{name},{magnitude_val},{direction_val},{processes_str}")
                
        csv_str = "\n".join(lines)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(csv_str)
                
        return csv_str
        
    def _export_markdown(self, filename: Optional[str] = None) -> str:
        """Export system state as Markdown"""
        
        report = self.visualize_system_state(include_history=True, detail_level="detailed")
        markdown_str = report.to_markdown()
        
        if filename:
            with open(filename, 'w') as f:
                f.write(markdown_str)
                
        return markdown_str
        
    def _export_text(self, filename: Optional[str] = None) -> str:
        """Export system state as formatted text"""
        
        report = self.visualize_system_state(include_history=True, detail_level="comprehensive")
        text_str = report.to_text()
        
        if filename:
            with open(filename, 'w') as f:
                f.write(text_str)
                
        return text_str
        
    def _export_quantities_data(self) -> Dict[str, Any]:
        """Export quantities as structured data"""
        
        if not hasattr(self, 'quantities'):
            return {}
            
        return {
            name: {
                "magnitude": getattr(qty.magnitude, 'value', str(qty.magnitude)),
                "direction": getattr(qty.direction, 'value', str(qty.direction)),
                "landmark_values": getattr(qty, 'landmark_values', []),
                "units": getattr(qty, 'units', None),
                "description": getattr(qty, 'description', None)
            }
            for name, qty in self.quantities.items()
        }
        
    def _export_processes_data(self) -> Dict[str, Any]:
        """Export processes as structured data"""
        
        if not hasattr(self, 'processes'):
            return {}
            
        return {
            name: {
                "active": process.active,
                "preconditions": process.preconditions,
                "quantity_conditions": process.quantity_conditions,
                "influences": process.influences,
                "description": getattr(process, 'description', None),
                "priority": getattr(process, 'priority', 0)
            }
            for name, process in self.processes.items()
        }
        
    def _export_relationships_data(self) -> Dict[str, str]:
        """Export relationships as structured data"""
        
        if hasattr(self, 'current_state') and self.current_state and self.current_state.relationships:
            return self.current_state.relationships.copy()
        elif hasattr(self, 'derive_relationships'):
            try:
                return self.derive_relationships()
            except:
                return {}
        else:
            return {}
            
    def _export_history_data(self) -> List[Dict[str, Any]]:
        """Export state history as structured data"""
        
        if not hasattr(self, 'state_history'):
            return []
            
        history_data = []
        for state in self.state_history:
            state_data = {
                "time_point": state.time_point,
                "quantities": {
                    name: {
                        "magnitude": getattr(qty.magnitude, 'value', str(qty.magnitude)),
                        "direction": getattr(qty.direction, 'value', str(qty.direction))
                    }
                    for name, qty in state.quantities.items()
                },
                "relationships": state.relationships.copy() if hasattr(state, 'relationships') else {}
            }
            history_data.append(state_data)
            
        return history_data
        
    def _detect_color_support(self) -> bool:
        """Detect if terminal supports colors"""
        try:
            import os
            return os.getenv('TERM') is not None
        except:
            return False
            
    def configure_visualization(self, **config_options):
        """
        🔧 Configure visualization engine parameters
        
        Args:
            **config_options: Configuration parameters to update
        """
        
        for option, value in config_options.items():
            if hasattr(self._viz_config, option):
                setattr(self._viz_config, option, value)
            else:
                print(f"Warning: Unknown visualization option '{option}'")
                
    def get_visualization_metrics(self) -> Dict[str, Any]:
        """
        📊 Get visualization engine metrics and statistics
        
        Returns:
            Dict containing visualization metrics
        """
        
        return {
            "config": {
                "detail_level": self._viz_config.detail_level,
                "export_format": self._viz_config.export_format,
                "max_history_items": self._viz_config.max_history_items
            },
            "cache_size": len(self._viz_cache),
            "export_history_count": len(self._export_history),
            "color_support": self._color_support,
            "symbol_mappings": len(self._trend_symbols) + len(self._magnitude_symbols)
        }