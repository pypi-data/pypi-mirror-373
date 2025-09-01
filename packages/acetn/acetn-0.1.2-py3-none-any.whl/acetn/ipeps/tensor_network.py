import torch
from .site_tensor import SiteTensor

class TensorNetwork:
    """
    A class representing a tensor network, specifically for the iPEPS (infinite projected entangled pair states) method.

    This class handles the construction, initialization, and manipulation of a tensor network.
    It supports operations such as saving, loading, and setting up tensor networks, as well as managing the tensors.
    """
    _tensor_network = {}
    def __init__(self, tensor_network, config, dtype, device):
        """
        Initializes the TensorNetwork object.

        Args:
            tensor_network (TensorNetwork, optional): An existing tensor network to copy from. If None, a new network is created.
            config (dict): Configuration dictionary containing the dimensions, lattice size, and other parameters.
            dtype (torch.dtype): The data type for the tensors (e.g., torch.float32).
            device (torch.device): The device on which the tensors will be allocated (e.g., 'cpu' or 'cuda').
        """
        self.tn_config = config
        self.nx = config.nx
        self.ny = config.ny
        self.dims = config.dims

        self.dtype = dtype
        self.device = device

        self.setup_tensor_network(tensor_network)

    def __getitem__(self, site):
        """
        Retrieves the site tensor at the specified site.

        Args:
            site (tuple): The site at which the tensor is located, represented as a tuple (xi, yi).

        Returns:
            SiteTensor: The site tensor at the specified site.
        """
        site_tensor = self._tensor_network.get(site)
        if site_tensor is None:
            raise ValueError(f"Site tensor not defined at site {site}.")
        return site_tensor

    def __setitem__(self, site, site_tensor):
        """
        Sets the tensor at the specified site.

        Args:
            site (tuple): The site at which the tensor is located, represented as a tuple (xi, yi).
            site_tensor (SiteTensor): The tensor to be set at the specified site.
        """
        self._tensor_network[site] = site_tensor

    def copy_from(self, tensor_network):
        """
        Copies the tensor network from another instance.

        Args:
            tensor_network (TensorNetwork): Another instance of TensorNetwork to copy tensors from.
        """
        self.site_list = tensor_network.site_list.copy()
        self.bond_list = tensor_network.bond_list.copy()
        for site in self.site_list:
            self[site] = SiteTensor(self.dims, tensor_network[site], dtype=self.dtype, device=self.device)

    def copy(self):
        """
        Returns a deep copy of the current `TensorNetwork` instance.

        Returns:
            TensorNetwork: A new `TensorNetwork` with identical contents and metadata.
        """
        return TensorNetwork(tensor_network=self, config=self.tn_config, dtype=self.dtype, device=self.device)

    def to(self, dtype=None, device=None):
        """
        Sends the tensor network to a device and/or changes the data type.

        Args:
            dtype (torch.dtype, optional): The data type of the tensors.
            device (torch.device, optional): The device where the tensors are placed.

        Returns:
            TensorNetwork: The tensor network with updated device and/or dtype.
        """
        device = device or self.device
        dtype = dtype or self.dtype
        return TensorNetwork(tensor_network=self, config=self.tn_config, dtype=dtype, device=device)

    def save(self, filename='ipeps.pt'):
        """
        Saves the current tensor network to a file.

        Args:
            filename (str): The file name for the saved file.

        Saves the tensor network and its tensors to a PyTorch binary file.
        """
        tn_cpu = self.to(device="cpu")
        state_dict = {
            "tensor_network": tn_cpu,
            "tensors": tn_cpu._tensor_network,
        }
        torch.save(state_dict, filename)
        self.load(filename)

    def load(self, filename):
        """
        Loads the tensor network from a file.

        Args:
            filename (str): The name of the file to load the tensor network from.
        """
        state_dict = torch.load(filename, weights_only=False)
        tn_cpu = state_dict['tensors']
        for site, site_tensor in tn_cpu.items():
            self[site] = site_tensor.to(self.dtype, self.device)
        self.site_states_initialized = True

    def setup_tensor_network(self, tensor_network):
        """
        Initializes or copies the tensor network based on the input.

        If no tensor network is provided, it initializes a new one in a uniform polarized product state. Otherwise, it 
        copies from the provided network.

        Args:
            tensor_network (TensorNetwork, optional): Another tensor network to copy from. If None, a new network is created.
        """
        if tensor_network is None:
            uniform_site_state_map = lambda site: [1.,] + [0,]*(self.dims['phys']-1)
            self.initialize_site_tensors(uniform_site_state_map)
        else:
            self.copy_from(tensor_network)

    def initialize_site_tensors(self, site_state_map):
        """
        Initializes the tensors for the entire tensor network.

        This method creates tensors for all sites in the network and stores them in the `_tensor_network` dictionary.
        """
        self.bond_list = self.build_bond_list()
        self.site_list = self.build_site_list()
        for site in self.site_list:
            site_state = site_state_map(site)
            self[site] = SiteTensor(self.dims, site_state=site_state, dtype=self.dtype, device=self.device)
        self.site_states_initialized = True

    def build_bond_list(self):
        """
        Builds the list of bonds connecting sites in the tensor network.

        This method creates horizontal and vertical bonds between adjacent sites in the lattice.

        Returns:
            list: A list of bonds, where each bond is represented as a list of two sites and the bond direction.
        """
        bond_list = []
        # horizontal bonds
        for xi in range(self.nx):
            for yi in range(self.ny):
                site = (xi,yi)
                xj = (xi+1) % self.nx
                bond_site = (xj,yi)
                bond = [site, bond_site, 2]
                bond_list.append(bond)
        # vertical bonds
        for yi in range(self.ny):
            for xi in range(self.nx):
                site = (xi,yi)
                yj = (yi+1) % self.ny
                bond_site = (xi,yj)
                bond = [site, bond_site, 1]
                bond_list.append(bond)
        return bond_list

    def build_site_list(self):
        """
        Builds the list of all sites in the tensor network.

        This method creates a list of all (xi, yi) coordinates for the lattice sites.

        Returns:
            list: A list of all site coordinates in the tensor network.
        """
        site_list = []
        for xi in range(self.nx):
            for yi in range(self.ny):
                site = (xi,yi)
                site_list.append(site)
        return site_list
