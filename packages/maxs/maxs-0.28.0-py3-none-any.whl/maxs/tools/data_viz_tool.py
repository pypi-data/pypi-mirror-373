"""
Data Visualization Tool - Create charts, graphs, and visualizations from data.

Supports: matplotlib, plotly, seaborn with multiple chart types and export formats.
"""

import subprocess
import sys
from typing import Dict, Any, List, Optional, Union
from strands import tool
import tempfile
import json
import os


def install_package(package_name: str) -> bool:
    """Install a Python package if not available."""
    try:
        __import__(package_name.replace("-", "_"))
        return True
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )
            return True
        except subprocess.CalledProcessError:
            return False


@tool
def data_viz_tool(
    action: str = "create",
    chart_type: str = "bar",
    data: Optional[Union[Dict, List, str]] = None,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    title: str = "Data Visualization",
    x_label: str = "",
    y_label: str = "",
    backend: str = "matplotlib",
    width: int = 10,
    height: int = 6,
    color_scheme: str = "default",
    export_format: str = "png",
    output_path: Optional[str] = None,
    interactive: bool = False,
) -> Dict[str, Any]:
    """Data visualization tool for creating charts and graphs.

    Actions:
        - create: Create a new visualization
        - list_types: Show available chart types
        - examples: Show example usage

    Chart Types:
        - bar: Bar chart
        - line: Line plot
        - scatter: Scatter plot
        - pie: Pie chart
        - histogram: Histogram
        - box: Box plot
        - violin: Violin plot
        - heatmap: Heat map
        - area: Area chart
        - multi_line: Multiple line plot

    Backends:
        - matplotlib: Static plots (PNG, SVG, PDF)
        - plotly: Interactive plots (HTML, PNG)
        - seaborn: Statistical plots (PNG, SVG)

    Args:
        action: Action to perform
        chart_type: Type of chart to create
        data: Data to visualize (dict, list, or JSON string)
        x_column: Column name for X-axis
        y_column: Column name for Y-axis
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        backend: Visualization backend to use
        width: Chart width in inches
        height: Chart height in inches
        color_scheme: Color scheme (default, viridis, plasma, etc.)
        export_format: Export format (png, svg, pdf, html)
        output_path: Custom output file path
        interactive: Whether to create interactive chart

    Returns:
        Dict containing status and response content
    """

    # Install required packages
    packages_to_install = ["matplotlib", "pandas", "numpy"]

    if backend == "plotly" or interactive:
        packages_to_install.extend(["plotly", "kaleido"])
    if backend == "seaborn":
        packages_to_install.append("seaborn")

    for package in packages_to_install:
        if not install_package(package):
            return {
                "status": "error",
                "content": [{"text": f"❌ Failed to install {package}"}],
            }

    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import matplotlib

        matplotlib.use("Agg")  # Use non-interactive backend

        if backend == "plotly" or interactive:
            import plotly.graph_objects as go
            import plotly.express as px

        if backend == "seaborn":
            import seaborn as sns

            sns.set_style("whitegrid")

    except ImportError as e:
        return {"status": "error", "content": [{"text": f"❌ Import error: {e}"}]}

    if action == "list_types":
        chart_types = {
            "bar": "Bar chart - Compare categories",
            "line": "Line plot - Show trends over time",
            "scatter": "Scatter plot - Show relationships between variables",
            "pie": "Pie chart - Show proportions",
            "histogram": "Histogram - Show data distribution",
            "box": "Box plot - Show statistical summary",
            "violin": "Violin plot - Show distribution density",
            "heatmap": "Heat map - Show correlation matrix",
            "area": "Area chart - Filled line plot",
            "multi_line": "Multiple line plot - Compare multiple series",
        }

        chart_info = "📊 **Available Chart Types:**\n\n"
        for chart, desc in chart_types.items():
            chart_info += f"- **{chart}**: {desc}\n"

        return {"status": "success", "content": [{"text": chart_info}]}

    elif action == "examples":
        examples = """
📈 **Example Usage:**

**Simple Bar Chart:**
```python
data_viz_tool(
    chart_type="bar",
    data={"categories": ["A", "B", "C"], "values": [10, 25, 15]},
    x_column="categories",
    y_column="values",
    title="My Bar Chart"
)
```

**Line Plot with Time Series:**
```python
data_viz_tool(
    chart_type="line",
    data={"dates": ["2024-01", "2024-02", "2024-03"], "sales": [100, 150, 200]},
    x_column="dates",
    y_column="sales",
    title="Sales Over Time",
    backend="plotly",
    interactive=True
)
```

**Scatter Plot:**
```python
data_viz_tool(
    chart_type="scatter",
    data={"height": [170, 180, 175], "weight": [65, 80, 70]},
    x_column="height", 
    y_column="weight",
    title="Height vs Weight"
)
```
        """

        return {"status": "success", "content": [{"text": examples}]}

    elif action == "create":
        if not data:
            return {
                "status": "error",
                "content": [{"text": "❌ Data parameter required"}],
            }

        # Parse data
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "content": [{"text": "❌ Invalid JSON data format"}],
                }

        # Convert to DataFrame
        try:
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                return {
                    "status": "error",
                    "content": [{"text": "❌ Data must be dict or list"}],
                }
        except Exception as e:
            return {
                "status": "error",
                "content": [{"text": f"❌ Failed to create DataFrame: {e}"}],
            }

        # Generate output path
        if not output_path:
            output_dir = "./visualizations"
            os.makedirs(output_dir, exist_ok=True)
            output_path = (
                f"{output_dir}/{chart_type}_{hash(str(data)) % 10000}.{export_format}"
            )

        try:
            if backend == "plotly" or interactive:
                # Plotly backend
                fig = None

                if chart_type == "bar":
                    fig = px.bar(
                        df,
                        x=x_column,
                        y=y_column,
                        title=title,
                        color_discrete_sequence=px.colors.qualitative.Set1,
                    )

                elif chart_type == "line":
                    fig = px.line(df, x=x_column, y=y_column, title=title)

                elif chart_type == "scatter":
                    fig = px.scatter(df, x=x_column, y=y_column, title=title)

                elif chart_type == "pie":
                    fig = px.pie(df, names=x_column, values=y_column, title=title)

                elif chart_type == "histogram":
                    fig = px.histogram(df, x=x_column, title=title)

                elif chart_type == "box":
                    fig = px.box(df, y=y_column, title=title)

                elif chart_type == "area":
                    fig = px.area(df, x=x_column, y=y_column, title=title)

                elif chart_type == "multi_line":
                    # Assume multiple y columns for multi-line
                    y_columns = [col for col in df.columns if col != x_column]
                    fig = go.Figure()
                    for col in y_columns:
                        fig.add_trace(
                            go.Scatter(
                                x=df[x_column], y=df[col], name=col, mode="lines"
                            )
                        )
                    fig.update_layout(
                        title=title, xaxis_title=x_label, yaxis_title=y_label
                    )

                if fig:
                    # Update layout
                    fig.update_layout(
                        width=width * 100,
                        height=height * 100,
                        xaxis_title=x_label or x_column,
                        yaxis_title=y_label or y_column,
                    )

                    # Save figure
                    if export_format == "html":
                        fig.write_html(output_path)
                    else:
                        fig.write_image(output_path)

            else:
                # Matplotlib/Seaborn backend
                plt.figure(figsize=(width, height))

                if backend == "seaborn" and chart_type in ["box", "violin", "heatmap"]:
                    if chart_type == "box":
                        sns.boxplot(data=df, y=y_column)
                    elif chart_type == "violin":
                        sns.violinplot(data=df, y=y_column)
                    elif chart_type == "heatmap":
                        # Assume data is correlation matrix or similar
                        sns.heatmap(
                            (
                                df.corr()
                                if df.select_dtypes(include=[np.number]).shape[1] > 1
                                else df
                            ),
                            annot=True,
                            cmap=(
                                color_scheme if color_scheme != "default" else "viridis"
                            ),
                        )
                else:
                    # Matplotlib plots
                    if chart_type == "bar":
                        plt.bar(df[x_column], df[y_column])

                    elif chart_type == "line":
                        plt.plot(df[x_column], df[y_column], marker="o")

                    elif chart_type == "scatter":
                        plt.scatter(df[x_column], df[y_column])

                    elif chart_type == "pie":
                        plt.pie(df[y_column], labels=df[x_column], autopct="%1.1f%%")

                    elif chart_type == "histogram":
                        plt.hist(df[x_column], bins=20, alpha=0.7)

                    elif chart_type == "area":
                        plt.fill_between(df[x_column], df[y_column], alpha=0.5)
                        plt.plot(df[x_column], df[y_column])

                    elif chart_type == "multi_line":
                        y_columns = [col for col in df.columns if col != x_column]
                        for col in y_columns:
                            plt.plot(df[x_column], df[col], label=col, marker="o")
                        plt.legend()

                # Set labels and title
                plt.title(title, fontsize=16, fontweight="bold")
                if x_label or x_column:
                    plt.xlabel(x_label or x_column)
                if y_label or y_column:
                    plt.ylabel(y_label or y_column)

                # Apply color scheme
                if color_scheme != "default":
                    plt.set_cmap(color_scheme)

                plt.tight_layout()
                plt.savefig(output_path, dpi=300, bbox_inches="tight")
                plt.close()

            # Get file size
            file_size = os.path.getsize(output_path) / 1024  # KB

            return {
                "status": "success",
                "content": [
                    {
                        "text": f"✅ Created {chart_type} chart using {backend}\n"
                        f"📁 Saved to: {output_path}\n"
                        f"📊 Size: {file_size:.1f} KB\n"
                        f"🎨 Format: {export_format.upper()}"
                    }
                ],
            }

        except Exception as e:
            return {
                "status": "error",
                "content": [{"text": f"❌ Visualization error: {str(e)}"}],
            }

    else:
        return {
            "status": "error",
            "content": [{"text": f"❌ Unknown action: {action}"}],
        }
