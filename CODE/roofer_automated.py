import os
import subprocess

# Base paths
base_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where the script is located
data_folder = os.path.abspath(os.path.join(base_dir, "..", "DATA"))  # DATA folder parallel to CODE folder
docker_image = "3dgi/roofer:develop"

# List of city names to process
city_names = ["TAVAS"]

# Convert data_folder to use forward slashes for Docker compatibility
docker_data_folder = data_folder.replace("\\", "/")

# Iterate through the specified city folders
for city in city_names:
    city_folder = os.path.join(data_folder, city)
    
    if not os.path.exists(city_folder):
        print(f"City folder '{city_folder}' does not exist. Skipping...")
        continue

    # Create the output directory inside the city folder
    output_folder = os.path.join(city_folder, "output")
    os.makedirs(output_folder, exist_ok=True)
    
    # Docker-compatible path for the city's output folder
    docker_output_folder = output_folder.replace("\\", "/")

    # Find .laz/.las and .gpkg/.shp files in the city folder
    laz_files = [f for f in os.listdir(city_folder) if f.lower().endswith((".laz", ".las"))]
    gpkg_files = [f for f in os.listdir(city_folder) if f.lower().endswith((".gpkg", ".shp"))]

    if not laz_files:
        print(f"No .laz or .las files found in '{city_folder}'. Skipping...")
        continue

    if not gpkg_files:
        print(f"No .gpkg or .shp files found in '{city_folder}'. Skipping...")
        continue

    # Use the first .gpkg or .shp file found
    input_gpkg = f"/data/{city}/{gpkg_files[0]}"

    # Process each .laz or .las file
    for laz_file in laz_files:
        input_laz = f"/data/{city}/{laz_file}"  # Docker-compatible path

        # Define output path inside the city's "output" folder (no extra city subfolder)
        laz_basename = os.path.splitext(laz_file)[0]
        output_path = f"/data/{city}/output/{laz_basename}"  # Correct Docker-compatible path

        # Construct the Docker command
        command = [
            "docker", "run", "-it", "--rm",
            "-v", f"{docker_data_folder}:/data",  # Volume mapping for Docker
            docker_image,
            "roofer",  # Call roofer explicitly
            input_laz,
            input_gpkg,
            output_path
        ]

        # Print the command (optional, for debugging)
        print("Running command:", " ".join(command))

        # Execute the Docker command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing '{laz_file}' in '{city_folder}': {e}")
        except Exception as e:
            print(f"Unexpected error while processing '{laz_file}' in '{city_folder}': {e}")

print("Processing complete.")
