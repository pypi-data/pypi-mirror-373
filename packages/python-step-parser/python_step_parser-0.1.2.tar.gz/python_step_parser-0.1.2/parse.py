from parsers import parse_and_store_step

# --- Run it ---
if __name__ == "__main__":
    project_name = "GlassDoor_BanksideYards"
    parse_and_store_step(f'{project_name}.stp', f'{project_name}.db')  # Change to your STEP file
