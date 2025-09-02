from chem_mat_data import load_graph_dataset, pyg_data_list_from_graphs
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader

# Load the dataset of graphs
graphs: list[dict] = load_graph_dataset('clintox')
print(f'number of graphs: {len(graphs)}')

# Convert the graph dicts into PyG Data objects
data_list: list[Data] = pyg_data_list_from_graphs(graphs)
data_loader: DataLoader = DataLoader(data_list, batch_size=32, shuffle=True)

# Network training...

