import numpy as np

# np.set_printoptions(precision=10, suppress=True)

def bohr_to_angstrom(value):
    factor = 0.52917720859
    return value * factor


def angstrom_to_bohr(value):
    factor = 0.52917720859
    return value / factor


def cartesian_vector_to_bravais_param(cart_vector):
    if np.size(cart_vector) != 9:
        print('Invalid vector')
        return None

    A, B, C = cart_vector[:]

    a = np.linalg.norm(A)
    b = np.linalg.norm(B)
    c = np.linalg.norm(C)
    alpha = np.rad2deg(np.arccos(np.dot(B, C) / (b * c)))
    beta = np.rad2deg(np.arccos(np.dot(A, C) / (a * c)))
    gamma = np.rad2deg(np.arccos(np.dot(A, B) / (a * b)))

    return a, b, c, alpha, beta, gamma


def cartesian_to_fractional_coords(cart_vector, cart_coord_position):
    # cartesian vector and atoms' coordinates must be in the same unit
    inv_vector = np.linalg.inv(cart_vector)
    return np.matmul(cart_coord_position, inv_vector)


def read_last_lattice_vectors(fname):
    with open(fname) as file:
        lines_of_interest = file.readlines()[-4:]

    number_of_runs, time_ps = map(np.float64, lines_of_interest[0].split())

    lattice_vector = []
    for line in lines_of_interest[1:]:
        vector = list(map(np.float64, line.split()))
        lattice_vector.append(vector)

    row_lattice_vector = np.transpose(lattice_vector)
    row_lattice_vector = bohr_to_angstrom(row_lattice_vector)

    return row_lattice_vector, number_of_runs, time_ps


def read_last_coord_positions(fname, n_atoms):
    str_coordinates = ['']
    with open(fname) as file:
        str_coordinates = file.readlines()[-n_atoms:]

    bohr_coordinates = []
    for coords in str_coordinates:
        bohr_coordinates.append(list(map(np.float64, coords.split())))

    bohr_coordinates = np.array(bohr_coordinates)

    return bohr_coordinates


def data_from_input_file(fname):
    prefix = ''
    outdir = ''
    n_atoms = 0
    atoms_names = []
    count = 0
    with open(fname) as file:
        for line in file.readlines():
            line_check = line.strip().split()

            if count > 0:
                atoms_names.append(line_check[0])
                count -= 1

            if 'ATOMIC_POSITIONS' in line_check:
                count = n_atoms
            else:
                if 'nat' in line_check:
                    n_atoms = int(line_check[-1])
                if 'outdir' in line_check:
                    outdir = line_check[-1]
                if 'prefix' in line_check:
                    prefix = line_check[-1]

        return n_atoms, atoms_names, prefix, outdir


def format_to_xyz(n_atoms, atoms_names, coordinates):
    lines = [str(n_atoms), '']

    for atom, coord in zip(atoms_names, coordinates):
        lines.append('{:>2}{:>20.14f}{:>20.14f}{:>20.14f}'.format(atom, coord[0], coord[1], coord[2]))

    return '\n'.join(lines)


def read_cpmd_data(main_dir, input_fname):
    n_atoms, atoms_names, prefix, outdir = data_from_input_file(main_dir + '/' + input_fname)

    outdir = outdir.replace("\'", '')
    prefix = prefix.replace("\'", '')

    # clean outdir name
    if outdir.find('.') == 0 or outdir.find('/') in [0, 1]:
        outdir = outdir.replace('.', '').replace('/', '', 1)

    outputs_path = main_dir + '/' + outdir + prefix

    cartesian_vector, number_of_runs, time_ps = read_last_lattice_vectors(outputs_path + '.cel')
    angstrom_coords = bohr_to_angstrom(read_last_coord_positions(outputs_path + '.pos', n_atoms))

    return n_atoms, atoms_names, cartesian_vector, angstrom_coords, number_of_runs, time_ps


def cpmd_to_xyz(main_dir, input_fname, xyz_fname=None):
    n_atoms, atoms_names, cartesian_vector, angstrom_coords, number_of_runs, time_ps = read_cpmd_data(main_dir,
                                                                                                      input_fname)
    data_text = format_to_xyz(n_atoms, atoms_names, angstrom_coords)

    if xyz_fname is None:
        rpoint = input_fname.rfind('.')
        xyz_fname = input_fname[:rpoint] + '.xyz'

    with open(xyz_fname, 'w') as file:
        file.write(data_text)


def generate_structure(main_dir, input_fname, write_data=False):
    from ase import Atoms
    from ase.io import write
    from ase.spacegroup import Spacegroup

    n_atoms, atoms_names, cartesian_vector, angstrom_coords, _, _ = read_cpmd_data(main_dir, input_fname)

    structure_ = Atoms(atoms_names, pbc=[1, 1, 1], info={'spacegroup': Spacegroup(173), 'unit_cell': 'conventional'},
                cell=cartesian_vector, positions=angstrom_coords)

    if write_data:
        structure_.write('structure.xyz')
        structure_.write('structure.cif')
        write('structure.png', structure_)

    return structure_


def visualize_structure(main_dir, input_file):
    from ase.visualize import view
    structure_ = generate_structure(main_dir, input_file)
    view(structure_)


def symmetrize_structure(main_dir, input_fname):
    print("Iniciando simetrização...")

    from pymatgen.symmetry.analyzer import PointGroupAnalyzer, SpacegroupAnalyzer
    from pymatgen.io.ase import AseAtomsAdaptor

    adapter = AseAtomsAdaptor()
    pymatgen_structure = adapter.get_structure(
        generate_structure(main_dir, input_fname)
    )

    sga = SpacegroupAnalyzer(pymatgen_structure)
    print(sga.get_symmetrized_structure())


def read_filename():
    from tkinter.filedialog import askopenfilename

    fname = askopenfilename()

    bar_file = fname.rfind('/')

    # return directory from cpmd files and input filename
    return fname[:bar_file], fname[bar_file+1:]


if __name__ == '__main__':
    cpmd_dir, in_file = read_filename()

    # visualize_structure(cpmd_dir, in_file)
    symmetrize_structure(cpmd_dir, in_file)
