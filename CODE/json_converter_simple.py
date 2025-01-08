import json
import os

def combine_jsonl_to_cityjson(input_folder, output_file):
    # Initialize the CityJSON structure
    cityjson = {
        "CityObjects": {},
        "metadata": {
            "geographicalExtent": [],
            "referenceSystem": "https://www.opengis.net/def/crs/EPSG/0/7415"
        },
        "transform": {
            "scale": [0.001, 0.001, 0.001],
            "translate": [85088.390625, 446394.250000, 46.170002]
        },
        "type": "CityJSON",
        "version": "2.0",
        "vertices": []
    }

    vertex_map = {}  # Map to avoid duplicate vertices

    # Iterate through all JSONL files in the specified folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.jsonl'):
            jsonl_file = os.path.join(input_folder, file_name)
            print(f"Processing file: {jsonl_file}")

            with open(jsonl_file, 'r') as infile:
                for line in infile:
                    feature = json.loads(line.strip())

                    if feature["type"] == "CityJSON":
                        cityjson["metadata"] = feature.get("metadata", cityjson["metadata"])
                        cityjson["transform"] = feature.get("transform", cityjson["transform"])

                    elif feature["type"] == "CityJSONFeature":
                        for obj_id, obj_data in feature["CityObjects"].items():
                            if obj_id not in cityjson["CityObjects"]:
                                cityjson["CityObjects"][obj_id] = obj_data
                            else:
                                # Merge geometries directly
                                cityjson["CityObjects"][obj_id]["geometry"].extend(obj_data.get("geometry", []))

                            # Process vertices
                            for geometry in obj_data.get("geometry", []):
                                for boundary in geometry.get("boundaries", []):
                                    update_boundaries_and_vertices(boundary, feature["vertices"], cityjson, vertex_map)

    # Write the combined CityJSON to the output file
    with open(output_file, 'w') as outfile:
        json.dump(cityjson, outfile, separators=(',', ':'), indent=4)
    print(f"CityJSON file saved as {output_file}")


def update_boundaries_and_vertices(boundary, source_vertices, cityjson, vertex_map):
    """
    Updates the boundaries and vertices for the CityJSON object without filtering.
    """
    if isinstance(boundary, list):
        for i in range(len(boundary)):
            if isinstance(boundary[i], int):
                # Map single vertex reference
                vertex = tuple(source_vertices[boundary[i]])
                if vertex not in vertex_map:
                    vertex_map[vertex] = len(cityjson["vertices"])
                    cityjson["vertices"].append(vertex)
                boundary[i] = vertex_map[vertex]
            elif isinstance(boundary[i], list):
                # Recursively process nested lists
                update_boundaries_and_vertices(boundary[i], source_vertices, cityjson, vertex_map)


# Example usage
if __name__ == "__main__":
     input_folder =  '../DATA/output/tiles'
     output_file = "../DATA/output/combined.json"
     combine_jsonl_to_cityjson(input_folder, output_file)
