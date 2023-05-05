import json
import urllib.request
import plotly.graph_objects as go
from voprov.models.model import VOProvDocument

#url = 'https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json'
#response = urllib.request.urlopen(url)
#data = json.loads(response.read())


def prov_to_plotly(bundle):
    """
    Convert a provenance bundle/document into a plotly object.

    :param bundle: The provenance bundle/document to be converted.
    :type bundle: :class: `ProvBundle`
    :returns: :class: `plotly.graph_objects`
    """

    if isinstance(bundle, VOProvDocument):
        data = json.loads(bundle.serialize())

        node = []
        color_node = []
        for e in data['entity']:
            node.append(e)
            color_node.append("lightgoldenrodyellow")
        for edes in data['entityDescription']:
            node.append(edes)
            color_node.append("orange")
        for a in data['agent']:
            node.append(a)
            color_node.append("yellow")
        for act in data['activity']:
            node.append(act)
            color_node.append("blue")
        for b_key, b_value in data['bundle'].items():
            if 'description' in b_key:
                for b_act in b_value['activityDescription']:
                    node.append(b_act)
                    color_node.append("orange")
            elif 'configuration' in b_key:
                if 'parameter' in b_value:
                    for b_param in b_value['parameter']:
                        node.append(b_param)
                        color_node.append("green")
                if 'configFile' in b_value:
                        for b_param in b_value['configFile']:
                            node.append(b_param)
                            color_node.append("green")

        source = []
        target = []
        color_links = []

        for att in data['wasAttributedTo'].values():
            source.append(node.index(att['prov:agent']))
            target.append(node.index(att['prov:entity']))
            color_links.append("lightgoldenrodyellow")
        for des in data['isDescribedBy'].values():
            source.append(node.index(des['voprov:descriptor']))
            target.append(node.index(des['voprov:described']))
            color_links.append("orange")
        for use in data['used'].values():
            source.append(node.index(use['prov:entity']))
            target.append(node.index(use['prov:activity']))
            color_links.append("red")
        for gen in data['wasGeneratedBy'].values():
            source.append(node.index(gen['prov:activity']))
            target.append(node.index(gen['prov:entity']))
            color_links.append("green")
        for conf in data['wasConfiguredBy'].values():
            source.append(node.index(conf['voprov:configurator']))
            target.append(node.index(conf['voprov:configured']))
            color_links.append("lightgreen")

        value = [1 for i in range(len(source))]

        fig = go.Figure(data=[go.Sankey(
            valueformat=".0f",

            # Define nodes
            node=dict(
              pad=15,
              thickness=15,
              line=dict(color="black", width=0.5),
              label=node,
              color=color_node
            ),
            # Add links
            link=dict(
                source=source,
                target=target,
                value=value,
                color=color_links
            )
        )])

        fig.update_layout(title_text="cellphone",
                          font_size=10)

        return fig
