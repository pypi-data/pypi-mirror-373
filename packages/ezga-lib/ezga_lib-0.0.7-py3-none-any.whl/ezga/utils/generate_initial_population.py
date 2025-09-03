from sage_lib.partition.Partition import Partition

def generate_initial_population(species_list, output_path:str='.'):
	partitions = Partition()
	partitions.build_all_crystals(species_list)
	for c in partitions.containers:
		c.AtomPositionManager.E = 0
		
	partitions.export_files(
            file_location=f"{output_path}",
            source='xyz',
            label='enumerate',
            verbose=True
        )

