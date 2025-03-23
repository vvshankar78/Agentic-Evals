import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader
import os
import warnings

import os, sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.load_config import load_config

def load_data(json_file):
    # Check if the file exists
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"File not found: {json_file}. Ensure the file exists and the path is correct.")
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Extract rows and metrics from the data
    rows = data.get('rows', [])
    metrics = data.get('metrics', {})
    return rows, metrics

def create_accuracy_metrics_chart(metrics):
    """Create bar chart for accuracy metrics"""
    # Suppress FutureWarning from pandas
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)

        metrics_df = pd.DataFrame({
            'Metric': [
                'Function Name Accuracy',
                'Plugin Name Accuracy',
                'Arguments Accuracy',
                'Overall Accuracy'
            ],
            'Value': [
                metrics['end_to_end_function_call.Function_name_accuracy'],
                metrics['end_to_end_function_call.Plugin_name_accuracy'],
                metrics['end_to_end_function_call.Arguments_accuracy'],
                metrics['end_to_end_function_call.Overall_accuracy']
            ]
        })

        fig = px.bar(metrics_df, 
                     x='Metric', 
                     y='Value',
                    #  title='Function Call Accuracy Metrics',
                     color='Metric',
                     text=metrics_df['Value'].apply(lambda x: f'{int(x*100)}%'))

        fig.update_layout(
            yaxis_title='Accuracy',
            yaxis_tickformat=',.0%',  # Format as whole number percentage
            yaxis_range=[0, 1],  # Set range from 0% to 100%
            showlegend=False
        )
        return fig.to_html(full_html=False)

def create_function_distribution_chart(df):
    """Create pie chart for function name distribution"""
    # Suppress FutureWarning from pandas
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)

        function_counts = df['inputs.predicted_function'].apply(
            lambda x: x[0]['function_name'] if x else None
        ).value_counts()

        fig = px.pie(values=function_counts.values,
                     names=function_counts.index,
                    #  title='Agent Type Distribution',
                     )
        return fig.to_html(full_html=False)

def create_plugin_distribution_chart(df):
    """Create pie chart for plugin name distribution."""
    # Suppress FutureWarning from pandas
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)

        plugin_counts = df['inputs.predicted_function'].apply(
            lambda x: x[0]['plugin_name'] if x else None
        ).value_counts()

        fig = px.pie(values=plugin_counts.values,
                     names=plugin_counts.index,
                     # title='Plugin Name Distribution',
                     )
        return fig.to_html(full_html=False)

def create_plugin_overall_accuracy_chart(data):
    """Create bar chart for overall accuracy by plugin name."""
    # Group data by plugin name and calculate overall accuracy
    plugin_metrics = {}
    for row in data:
        for func in row['inputs.expected_function']:
            plugin_name = func['plugin_name']
            if plugin_name not in plugin_metrics:
                plugin_metrics[plugin_name] = {
                    'total': 0,
                    'correct': 0
                }
            plugin_metrics[plugin_name]['total'] += 1
            plugin_metrics[plugin_name]['correct'] += int(row['outputs.end_to_end_function_call.Overall_accuracy'])

    # Calculate percentages and sort by accuracy
    plugin_data = [
        {
            'name': name,
            'accuracy': (metrics['correct'] / metrics['total'] * 100),
            'total': metrics['total']
        }
        for name, metrics in plugin_metrics.items()
    ]
    plugin_data.sort(key=lambda x: x['accuracy'], reverse=True)

    # Define colors based on accuracy
    def get_color(accuracy):
        if accuracy >= 80:
            return '#27ae60'  # Green for high accuracy
        elif accuracy >= 60:
            return '#f1c40f'  # Yellow for medium accuracy
        elif accuracy >= 40:
            return '#e67e22'  # Orange for low-medium accuracy
        else:
            return '#e74c3c'  # Red for low accuracy

    # Create the bar chart with color coding
    fig = go.Figure([
        go.Bar(
            x=[d['name'] for d in plugin_data],
            y=[d['accuracy'] for d in plugin_data],
            text=[f"{d['accuracy']:.0f}%<br>({d['total']} calls)" for d in plugin_data],
            textposition='auto',
            marker_color=[get_color(d['accuracy']) for d in plugin_data],
            hovertemplate="<b>%{x}</b><br>" +
                         "Accuracy: %{y:.1f}%<br>" +
                         "<extra></extra>"
        )
    ])

    # Update layout
    fig.update_layout(
        # title='Overall Accuracy by Plugin Name',
        xaxis_title='Plugin Name',
        yaxis=dict(
            title='Overall Accuracy (%)',
            range=[0, 100],
            tickformat=',.0%',
            showticklabels=False,  # Hide tick labels
            showgrid=False,  # Hide grid lines
            zeroline=False   # Hide zero line
        ),
        showlegend=False,
        bargap=0.3
    )

    return fig.to_html(full_html=False)

def create_plugin_accuracy_by_function_chart(data):
    """Create bar chart for plugin accuracy grouped by function name."""
    # Group data by function name and plugin name, and calculate accuracy
    plugin_metrics = {}
    for row in data:
        for func in row['inputs.expected_function']:
            function_name = func['function_name']
            plugin_name = func['plugin_name']
            key = (function_name, plugin_name)
            if key not in plugin_metrics:
                plugin_metrics[key] = {
                    'total': 0,
                    'correct': 0
                }
            plugin_metrics[key]['total'] += 1
            plugin_metrics[key]['correct'] += int(row['outputs.end_to_end_function_call.Plugin_name_accuracy'])

    # Prepare data for the chart
    plugin_data = [
        {
            'function': key[0],
            'plugin': key[1],
            'accuracy': (metrics['correct'] / metrics['total'] * 100) if metrics['total'] > 0 else 0,
            'total': metrics['total']
        }
        for key, metrics in plugin_metrics.items()
    ]

    # Create a bar chart for each function
    charts = {}
    for function_name in set(item['function'] for item in plugin_data):
        function_data = [item for item in plugin_data if item['function'] == function_name]
        function_data.sort(key=lambda x: x['accuracy'], reverse=True)

        fig = go.Figure([
            go.Bar(
                x=[d['accuracy'] for d in function_data],
                y=[d['plugin'] for d in function_data],
                orientation='h',
                text=[f"{d['accuracy']:.0f}%<br>({d['total']} calls)" for d in function_data],
                textposition='auto',
                marker_color='#2ecc71',
                hovertemplate="<b>%{y}</b><br>" +
                              "Accuracy: %{x:.1f}%<br>" +
                              "<extra></extra>"
            )
        ])

        # Update layout
        fig.update_layout(
            title=f"Plugin Accuracy for Function: {function_name}",
            xaxis_title='Accuracy (%)',
            yaxis_title='Plugin Name',
            xaxis=dict(range=[0, 100]),
            showlegend=False,
            bargap=0.3
        )

        charts[function_name] = fig.to_html(full_html=False)

    return charts

def generate_report(rows, metrics, template_path, output_path):
    """Generate HTML report using Jinja2 template"""
    # Ensure the template loader is configured to the correct directory
    template_dir = os.path.dirname(template_path)
    template_name = os.path.basename(template_path)

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    
    # Convert data to DataFrame for easier manipulation
    df = pd.DataFrame(rows)
    
    # Create charts
    plugin_dist_chart = create_plugin_distribution_chart(df)
    accuracy_chart = create_accuracy_metrics_chart(metrics)
    plugin_overall_accuracy_chart = create_plugin_overall_accuracy_chart(rows)  # Retain overall accuracy chart
    
    # Calculate additional statistics
    total_queries = len(df)
    successful_queries = df['outputs.end_to_end_function_call.Overall_accuracy'].sum()
    success_rate = (successful_queries / total_queries) * 100
    
    # Render template
    html_content = template.render(
        rows=rows,
        metrics=metrics,
        agent_overall_accuracy_chart=plugin_overall_accuracy_chart,
        accuracy_chart=accuracy_chart,
        function_dist_chart=plugin_dist_chart,
        total_queries=total_queries,
        successful_queries=int(successful_queries),
        success_rate=round(success_rate, 1)
    )
    
    # Save the report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    # # Create directories if they don't exist
    # os.makedirs('templates', exist_ok=True)
    # os.makedirs('output', exist_ok=True)


    config = load_config()
    report_config = config["report"]

    dataset_path = Path(__file__).resolve().parents[1]
    input_file = os.path.join(dataset_path, report_config["input_path"], report_config["input_file"])
    
    try:
        rows, metrics = load_data(input_file)
        print("Data loaded successfully.")
        # Generate report
        template_path = os.path.join(os.path.dirname(__file__), 'report_template.html')  # Ensure correct path
        output_path = os.path.join(os.path.dirname(__file__), 'output_report.html')
        generate_report(rows, metrics, template_path, output_path)
        print(f"Report generated successfully at {output_path}")
    except FileNotFoundError as e:
        print(e)

if __name__ == "__main__":
    main()