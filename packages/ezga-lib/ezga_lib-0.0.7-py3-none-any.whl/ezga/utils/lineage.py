# lineage.py
from ..core.interfaces import ILineage

class LineageTracker(ILineage):
    def __init__(self):
        self._structure_id_counter = 0
        self.lineage = {}

    def assign_lineage_info(self, structure, generation: int, parents: list, operation: str, mutation_list: list=None):
        """
        Assigns lineage metadata to a structure.

        Parameters
        ----------
        structure : object
            The structure to which lineage info will be assigned.
        generation : int
            The current generation index.
        parents : list
            A list of parent structures.
        operation : str
            Genetic operation type, e.g., "mutation" or "crossover".
        """
        if not hasattr(structure.AtomPositionManager, 'metadata'):
              structure.AtomPositionManager.metadata = {}
        if not isinstance(structure.AtomPositionManager.metadata, dict):
            structure.AtomPositionManager.metadata = {}

        self._structure_id_counter += 1

        structure.AtomPositionManager.metadata['generation'] = generation
        structure.AtomPositionManager.metadata['parents'] = parents
        structure.AtomPositionManager.metadata['operation'] = operation
        structure.AtomPositionManager.metadata['id'] = self._structure_id_counter

        if mutation_list:
            structure.AtomPositionManager.metadata['mutation_list'] = mutation_list

        self.lineage[ self._structure_id_counter ] = {
                'structure':structure, 
                'generation':generation,
                'parents':parents, 
                'operation':operation,
                }

        return self._structure_id_counter

    def assign_lineage_info_par_partition(self, partition, generation: int, parents: list, operation: str, ):
        """
        """
        for container in partition.containers:
            self.assign_lineage_info(container, generation=generation, parents=parents, operation=operation)

        return self._structure_id_counter



