use crate::calculators::{CalcInput, Hamiltonian};
use crate::config::{Config, InitialState};
use crate::spin::SpinState;
use itertools::{iproduct, zip_eq};
use tracing::debug;

pub struct Grid<S: SpinState, R: rand::Rng> {
    pub spins: Vec<S>,
    pub size: usize,
    pub dim: [usize; 3],
    pub num_sublattices: usize,
    pub calc_inputs: Vec<CalcInput<S>>,
    pub rng: R,
    pub hamiltonian: Hamiltonian,
    pub group_index: Vec<Vec<usize>>,
}

impl<S: SpinState, R: rand::Rng> Grid<S, R> {
    pub fn new(config: &Config, mut rng: R) -> anyhow::Result<Self> {
        let dim = config.grid.dimensions;
        let num_sublattices = config.grid.sublattices;
        let mut spins = vec![];
        let total_sites = dim[0] * dim[1] * dim[2];
        let mut group_index = Vec::new();

        for sub_lattice_group in &config.output.group {
            let mut indexs = Vec::new();

            for sub_lattice in sub_lattice_group {
                for (x, y, z) in iproduct!(0..dim[0], 0..dim[1], 0..dim[2]) {
                    indexs.push(coord_to_index(
                        [x as isize, y as isize, z as isize],
                        *sub_lattice,
                        dim,
                    ))
                }
            }
            group_index.push(indexs);
        }

        let mut calc_inputs: Vec<CalcInput<S>> = vec![];
        for magnitude in &config.grid.spin_magnitudes {
            let new_spin = match config.simulation.initial_state {
                InitialState::Random => S::random(&mut rng, *magnitude),
                InitialState::X => S::along_x(*magnitude)?,
                InitialState::Y => S::along_y(*magnitude)?,
                InitialState::Z => S::along_z(*magnitude)?,
            };
            spins.extend(std::iter::repeat_n(new_spin, total_sites));
            calc_inputs.extend(std::iter::repeat_n(
                CalcInput {
                    magnitude: *magnitude,
                    ..Default::default()
                },
                total_sites,
            ));
        }

        let hamiltonian = Hamiltonian::new(config);

        for (sublattice, x, y, z) in iproduct!(0..num_sublattices, 0..dim[0], 0..dim[1], 0..dim[2])
        {
            let index = coord_to_index([x as isize, y as isize, z as isize], sublattice, dim);

            let calc_input = &mut calc_inputs[index];

            let mut exchange_neighbors = vec![];
            for exchange in &config.parsed_exchange {
                if exchange.from_sub == sublattice {
                    let offset_coord = [
                        exchange.offset[0] + x as isize,
                        exchange.offset[1] + y as isize,
                        exchange.offset[2] + z as isize,
                    ];

                    let offset_index_opt = safe_coord_to_index(
                        offset_coord,
                        exchange.to_sub,
                        dim,
                        num_sublattices,
                        config.grid.periodic_boundary,
                    );
                    if let Some(offset_index) = offset_index_opt {
                        exchange_neighbors
                            .push((&spins[offset_index] as *const S, exchange.strength));
                        calc_input.exchange_neighbor_index.push(offset_index);
                        calc_input.exchanges.push(exchange.strength);
                    }
                }
            }

            if !&config.parsed_anisotropy.is_empty() {
                calc_input.anisotropy = (
                    config.parsed_anisotropy[sublattice].strength,
                    config.parsed_anisotropy[sublattice].axis,
                );
                debug!("{:?}", calc_input.anisotropy);
            }
            calc_input.exchange_neighbors = Some(exchange_neighbors);
            calc_input.validate_exchange_neighbor()?;
        }

        Ok(Self {
            dim,
            num_sublattices,
            rng,
            size: total_sites * num_sublattices,
            spins,
            calc_inputs,
            hamiltonian,
            group_index,
        })
    }

    pub fn total_energy(&self) -> f64 {
        zip_eq(self.spins.iter(), self.calc_inputs.iter())
            .map(|(spin, calc_input)| spin.energy(calc_input, &self.hamiltonian, &self.spins))
            .sum::<f64>()
    }

    pub fn partial_spin_vector(&self, index: usize) -> S {
        self.group_index[index].iter().map(|i| self.spins[*i]).sum()
    }

    pub fn total_spin_vector(&self) -> S {
        self.spins.iter().copied().sum()
    }
    pub fn get_spin_by_coord(&self, sub: usize, x: isize, y: isize, z: isize) -> Option<&S> {
        self.spins.get(coord_to_index([x, y, z], sub, self.dim))
    }

    #[cfg(feature = "snapshots")]
    pub fn spins_to_array(&self) -> ndarray::Array4<S> {
        let mut result =
            ndarray::Array4::default([self.num_sublattices, self.dim[0], self.dim[1], self.dim[2]]);
        for (sub, x, y, z) in iproduct!(
            0..self.num_sublattices,
            0..self.dim[0],
            0..self.dim[1],
            0..self.dim[2]
        ) {
            if let Some(spin) = self.get_spin_by_coord(sub, x as isize, y as isize, z as isize) {
                result[[sub, x, y, z]] = *spin;
            } else {
                unreachable!(
                    "Internal error: invalid spin coordinate (sub={sub}, x={x}, y={y}, z={z})"
                );
            }
        }
        result
    }
}

fn coord_to_index(coord: [isize; 3], sublattice: usize, dim: [usize; 3]) -> usize {
    let [x, y, z] = coord;
    let (x, y, z) = (x as usize, y as usize, z as usize);
    sublattice * (dim[0] * dim[1] * dim[2]) + x * (dim[1] * dim[2]) + y * dim[2] + z
}

fn safe_coord_to_index(
    mut coord: [isize; 3],
    sublattice: usize,
    dim: [usize; 3],
    sublattices: usize,
    pbc: [bool; 3],
) -> Option<usize> {
    for i in 0..3 {
        if coord[i] < 0 || coord[i] >= dim[i] as isize {
            if pbc[i] {
                coord[i] = (coord[i] + dim[i] as isize) % dim[i] as isize;
            } else {
                return None;
            }
        }
    }

    if sublattice >= sublattices {
        return None;
    }

    Some(coord_to_index(coord, sublattice, dim))
}
