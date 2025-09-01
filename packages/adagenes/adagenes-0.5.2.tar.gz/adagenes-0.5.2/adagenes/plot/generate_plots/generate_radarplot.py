import json, traceback
import plotly
import plotly.express as px
import plotly.graph_objects as go


def generate_radar_plot(
        dfs,
        names,
        plot_type,
        bgcolor="#ffffff",
        linecolor="#58b3e0",
        fillcolor="#58b3e0",
        width=850,
        height=500,
        fillcolors=["#0067aa","#770000", "#007901"],
        return_figure=False
    ):
    """

    :param df:
    :param plot_type:
    :return:
    """
    if plot_type == "pathogenicity-scores-radar":
        try:
            #fig = go.Figure(
            #    data=go.Scatterpolar(
            #        r=df["r"].tolist(),
            #        theta=df["theta"].tolist(),
            #        fill='toself',
            #        fillcolor=fillcolor,
            #        line_color=linecolor,
            #        opacity=0.6,
            #        line=dict(color="orange"),
            #        mode='lines+text',
            #        textposition='top center'
            #    )
            #)
            fig = go.Figure()
            for i,df in enumerate(dfs):
                fig.add_trace(go.Scatterpolar(
                        name=names[i],
                        r=df["r"].tolist(),
                        theta=df["theta"].tolist(),
                        fill='toself',
                        opacity=0.6,
                        mode='lines+text+markers',
                        textposition='top center',
                        marker=dict(size=6,
                                    color=fillcolors[i],
                                    line=dict(width=2,
                                              color=fillcolors[i]))
                    )
                )
            #fig.add_trace(
            #px.scatter_polar(df,r="r",theta="theta")
            #)
            #fig = px.line_polar(
            #    df, r="r", theta="theta", line_close=True
            #)

            #fig.update_layout(showlegend=False)
            #fig.update_coloraxes(showscale=False)

            fig.update_layout(
                width=width,
                height=height,
                polar=dict(
                    bgcolor="#ffffff",
                    radialaxis=dict(visible=True,
                                    gridcolor="#303030"
                                    ),
                    angularaxis= dict(
                        visible=True,
                        gridcolor="#303030"
                    )
                ),
                margin=dict(l=20, r=20, t=20, b=20, pad=0),
                #paper_bgcolor="#c2d7e9",
                paper_bgcolor="#ffffff",
                showlegend=True
            )
            #fig.show()
            if return_figure is True:
                return fig

            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON
        except:
            print("error generating treatment sunburst plot")
            print(traceback.format_exc())
            return "<html></html>"

    return {}

