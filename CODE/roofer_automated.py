import os
import subprocess

# Base paths
base_dir = os.path.dirname(os.path.abspath(__file__))  # Base directory relative to the script location
data_folder = os.path.abspath(os.path.join(base_dir, "..", "DATA"))  # DATA folder parallel to the CODE folder
output_folder = os.path.join(data_folder, "output")  # Single output folder inside DATA
docker_image = "3dgi/roofer:develop"

# List of city names to look for
city_names = ["Turkey"]

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# Convert data_folder and output_folder to use forward slashes for Docker
docker_data_folder = data_folder.replace("\\", "/")
docker_output_folder = output_folder.replace("\\", "/")

# Iterate through city folders
for city in city_names:
    city_folder = os.path.join(data_folder, city)
    
    if not os.path.exists(city_folder):
        print(f"City folder '{city}' does not exist. Skipping...")
        continue

    # Find .laz, .gpkg, and .shp files in the city folder
    laz_files = [f for f in os.listdir(city_folder) if f.lower().endswith(".laz")]
    gpkg_files = [f for f in os.listdir(city_folder) if f.endswith(".gpkg") or f.endswith(".shp")]

    if not laz_files:
        print(f"No .laz files found in '{city_folder}'. Skipping...")
        continue

    if not gpkg_files:
        print(f"No .gpkg files found in '{city_folder}'. Skipping...")
        continue

    # Use the first .gpkg file found
    input_gpkg = f"/data/{city}/{gpkg_files[0]}"

    # Process each .laz file
    for laz_file in laz_files:
        input_laz = f"/data/{city}/{laz_file}"  # Docker-compatible path

        # Define output subfolder inside the single "output" folder
        laz_basename = os.path.splitext(laz_file)[0]
        output_path = f"/data/output/{city}_{laz_basename}"  # Docker-compatible path

        # Construct the Docker command
        command = [
            "docker", "run", "-it", "--rm",
            "-v", f"{docker_data_folder}:/data",  # Volume mapping
            docker_image,
            "roofer",  # Explicitly call roofer
            input_laz,
            input_gpkg,
            output_path
        ]

        # Print the command (optional, for debugging)
        print("Running command:", " ".join(command))

        # Execute the command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error processing {laz_file} in {city_folder}: {e}")

print("Processing complete.")
