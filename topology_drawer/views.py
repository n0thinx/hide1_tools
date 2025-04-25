import json
import uuid
import xml.etree.ElementTree as ET
from django.http import HttpResponse
from django.shortcuts import render

def generate_drawio(data):
    root = ET.Element("mxfile")
    diagram = ET.SubElement(root, "diagram", {"name": "CDP Network"})
    model = ET.SubElement(diagram, "mxGraphModel", {
        "dx": "2954", "dy": "1627", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1", "pageWidth": "850",
        "pageHeight": "1100", "math": "0", "shadow": "0"
    })
    root_element = ET.SubElement(model, "root")
    ET.SubElement(root_element, "mxCell", {"id": "0"})
    ET.SubElement(root_element, "mxCell", {"id": "1", "parent": "0"})

    node_map = {}
    x, y = 100, 100
    x_spacing, y_spacing = 250, 120

    def create_object_node(label, mgmt_ip, platform, obj_id, x, y, capabilities=None, software_version=None):
        shape = "shape=mxgraph.cisco19.rect;verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;fillColor=#FAFAFA;strokeColor=#005073;prIcon=l2_switch;"
        if capabilities == "Router Switch IGMP" and "L3" in software_version:
            shape = shape.replace("l2_switch", "l3_switch")
        elif capabilities == "Router Switch IGMP":
            shape = "shape=mxgraph.cisco19.rect;verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;fillColor=#FAFAFA;strokeColor=#005073;prIcon=router;"

        obj = ET.SubElement(root_element, "object", {
            "id": obj_id, "label": label, "management_ip": mgmt_ip, "platform": platform
        })
        cell = ET.SubElement(obj, "mxCell", {
            "style": shape, "vertex": "1", "parent": "1"
        })
        ET.SubElement(cell, "mxGeometry", {
            "x": str(x), "y": str(y), "width": "50", "height": "50", "as": "geometry"
        })

    def create_edge(source_id, target_id, label, index, offset=0):
        edge = ET.SubElement(root_element, "mxCell", {
            "id": f"edge-{index}", "value": label,
            "style": "endArrow=none;startFill=0;entryX=0.25;entryY=0;exitX=0.25;exitY=1;",
            "edge": "1", "parent": "1", "source": source_id, "target": target_id
        })
        geom = ET.SubElement(edge, "mxGeometry", {"relative": "1", "as": "geometry"})
        geom.set("y", str(offset))
        ET.SubElement(geom, "Array", {"as": "points"})

    def shorten(name):
        return name.replace("GigabitEthernet", "GE") if name else ""

    edge_counter = 0
    for hostname, details in data.items():
        src_label = hostname.replace(".txt", "")
        capabilities = details.get("capabilities", "")
        software_version = details.get("software_version", "")
        platform = details.get("platform", "Unknown")
        if src_label not in node_map:
            node_id = f"node-{uuid.uuid4()}"
            node_map[src_label] = {"id": node_id, "x": x, "y": y, "edges": []}
            create_object_node(src_label, "", platform, node_id, x, y, capabilities, software_version)
            y += y_spacing

        for neighbor in details["data"].get("show cdp neighbors detail", []):
            dest_label = neighbor["destination_host"].split(".")[0]
            mgmt_ip = neighbor.get("management_ip", "")
            local_port = shorten(neighbor.get("local_port", ""))
            remote_port = shorten(neighbor.get("remote_port", ""))
            label = f"{local_port} - {remote_port}"

            if dest_label not in node_map:
                node_id = f"node-{uuid.uuid4()}"
                platform = neighbor.get("platform", "Unknown")
                node_map[dest_label] = {"id": node_id, "x": x + x_spacing, "y": y, "edges": []}
                create_object_node(dest_label, mgmt_ip, platform, node_id, x + x_spacing, y, neighbor.get("capabilities", ""), neighbor.get("software_version", ""))
                y += y_spacing

            reverse_edge_exists = any(e["target"] == node_map[src_label]["id"] for e in node_map[dest_label]["edges"])
            if not reverse_edge_exists:
                existing_edges = sum(1 for e in node_map[src_label]["edges"] if e["target"] == node_map[dest_label]["id"])
                offset = existing_edges * 20
                create_edge(node_map[src_label]["id"], node_map[dest_label]["id"], label, edge_counter, offset)
                edge_counter += 1
                node_map[src_label]["edges"].append({"target": node_map[dest_label]["id"], "label": label})

    return ET.ElementTree(root)

def upload_json_view(request):
    if request.method == "POST" and request.FILES.get("json_file"):
        json_file = request.FILES["json_file"]
        data = json.load(json_file)
        tree = generate_drawio(data)

        response = HttpResponse(content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename="network_custom.drawio"'
        tree.write(response, encoding="utf-8", xml_declaration=True)
        return response

    return render(request, "upload.html")
