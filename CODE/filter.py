import os
import subprocess
import json

# Base folder containing the data
base_folder = "../DATA/Adana"

# Downsampling radius
downsampling_radius = 0.2

# Iterate through all subdirectories in the Adana folder
for root, dirs, files in os.walk(base_folder):
    for file in files:
        if file.endswith(".las"):
            # Input LAS file
            input_las = os.path.join(root, file)
            
            # Define output LAS file path
            output_las = os.path.join(root, os.path.splitext(file)[0] + "_decimated.las")
            
            # PDAL pipeline configuration
            pipeline = {
                "pipeline": [
                    {
                        "type": "readers.las",
                        "filename": input_las.replace("\\", "/")  # Ensure paths are Docker/PDAL compatible
                    },
                    {
                        "type": "filters.sample",
                        "radius": downsampling_radius
                    },
                    {
                        "type": "writers.las",
                        "filename": output_las.replace("\\", "/")  # Ensure paths are Docker/PDAL compatible
                    }
                ]
            }
            
            # Save pipeline to a temporary JSON file
            pipeline_path = os.path.join(root, "pipeline.json")
            with open(pipeline_path, "w") as pipeline_file:
                json.dump(pipeline, pipeline_file, indent=4)
            
            # Run the PDAL pipeline
            try:
                print(f"Processing {input_las}...")
                subprocess.run(["pdal", "pipeline", pipeline_path], check=True)
                print(f"Output written to {output_las}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {input_las}: {e}")
            finally:
                # Clean up the temporary pipeline file
                os.remove(pipeline_path)

print("Downsampling complete.")
