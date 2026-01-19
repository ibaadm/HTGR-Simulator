from src.simulation import PlantModel


def main():
    print("--- Starting HTGR System Operation ---")

    sim = PlantModel(config_path="config")
    sim.run()

    print("--- Operation Complete ---")


if __name__ == "__main__":
    main()
