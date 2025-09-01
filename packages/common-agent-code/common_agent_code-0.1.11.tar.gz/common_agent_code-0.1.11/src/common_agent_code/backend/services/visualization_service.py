import plotly.graph_objects as go

def gathered_context_visualization(query_string: str, contexts: list, distances: list) -> str:
    """
    Create a visualization of context relevance using Plotly.
    Returns HTML string of the visualization.
    """
    try:
        # Create relevance scores (inverse of distances)
        relevance_scores = [1 / (1 + d) for d in distances]
        
        # Create truncated context labels
        context_labels = [f"{ctx[:50]}..." for ctx in contexts]
        
        # Create Plotly figure
        fig = go.Figure(data=[
            go.Bar(
                x=relevance_scores,
                y=context_labels,
                orientation='h',
                marker_color='rgb(55, 83, 109)'
            )
        ])
        
        fig.update_layout(
            title=f'Context Relevance for Query: "{query_string}"',
            xaxis_title='Relevance Score',
            yaxis_title='Contexts',
            height=100 + (len(contexts) * 50),  # Dynamic height based on number of contexts
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Save visualization to HTML file with timestamp
        filename = f'Context_Visualizations/context_visualization_{query_string[:25]}.html'
        fig.write_html(filename)
        
        return f"Visualization saved as {filename}"
        
    except Exception as e:
        return f"Error creating visualization: {str(e)}"
