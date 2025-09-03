try:
    import re
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing re: {str(e)}\n")
    del sys

class PDB:
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        pass
        
    def read_pdb(self, filename, save:bool=True, verbose:bool=False) -> dict:
        pdb_data = {
            "atoms": [],
            "hetatms": [],
            "ter": [],
            "helices": [],
            "sheets": [],
            "ssbonds": [],
        }

        helix_type = { 
                    1 :'Right-handed alpha (default)',
                    2 :'Right-handed omega',
                    3 :'Right-handed pi',
                    4 :'Right-handed gamma',
                    5 :'Right-handed 3/10',
                    6 :'Left-handed alpha',
                    7 :'Left-handed omega',
                    8 :'Left-handed gamma',
                    9 :' 2/7 ribbon/helix',
                    10:'Polyproline',
                    }
        
        with open(filename, 'r') as file:
            for line in file:
                record_type = line[0:6].strip()
                
                if record_type == "ATOM" or record_type == "HETATM":
                    atom_data = {
                        "record_type": record_type,
                        "atom_serial_number": int(line[6:11].strip()),
                        "atom_name": line[12:16].strip(),
                        "alt_loc": line[16].strip(),
                        "residue_name": line[17:20].strip(),
                        "chain_id": line[21].strip(),
                        "residue_seq_number": int(line[22:26].strip()),
                        "insertion_code": line[26].strip(),
                        "x": float(line[30:38].strip()),
                        "y": float(line[38:46].strip()),
                        "z": float(line[46:54].strip()),
                        "occupancy": float(line[54:60].strip()) if line[54:60].strip() else None,
                        "temp_factor": float(line[60:66].strip()) if line[60:66].strip() else None,
                        "element": line[76:78].strip(),
                        "charge": line[78:80].strip(),
                    }
                    pdb_data["atoms" if record_type == "ATOM" else "hetatms"].append(atom_data)
                
                elif record_type == "TER":
                    ter_data = {
                        "serial_number": int(line[6:11].strip()),
                        "residue_name": line[17:20].strip(),
                        "chain_id": line[21].strip(),
                        "residue_seq_number": int(line[22:26].strip()),
                        "insertion_code": line[26].strip(),
                    }
                    pdb_data["ter"].append(ter_data)
                
                elif record_type == "HELIX":
                    helix_data = {
                        "helix_serial_number": int(line[7:10].strip()),
                        "helix_identifier": line[11:14].strip(),
                        "initial_residue_name": line[15:18].strip(),
                        "initial_chain_id": line[19].strip(),
                        "initial_residue_seq_number": int(line[21:25].strip()),
                        "initial_insertion_code": line[25].strip(),
                        "terminal_residue_name": line[27:30].strip(),
                        "terminal_chain_id": line[31].strip(),
                        "terminal_residue_seq_number": int(line[33:37].strip()),
                        "terminal_insertion_code": line[37].strip(),
                        "helix_type": int(line[38:40].strip()),
                        "comment": line[40:70].strip(),
                        "length": int(line[71:76].strip()),
                    }
                    pdb_data["helices"].append(helix_data)
                
                elif record_type == "SHEET":
                    sheet_data = {
                        "strand_number": int(line[7:10].strip()),
                        "sheet_identifier": line[11:14].strip(),
                        "num_strands": int(line[14:16].strip()),
                        "initial_residue_name": line[17:20].strip(),
                        "initial_chain_id": line[21].strip(),
                        "initial_residue_seq_number": int(line[22:26].strip()),
                        "initial_insertion_code": line[26].strip(),
                        "terminal_residue_name": line[28:31].strip(),
                        "terminal_chain_id": line[32].strip(),
                        "terminal_residue_seq_number": int(line[33:37].strip()),
                        "terminal_insertion_code": line[37].strip(),
                        "strand_sense": int(line[38:40].strip()),
                    }
                    pdb_data["sheets"].append(sheet_data)
                
                elif record_type == "SSBOND":
                    ssbond_data = {
                        "serial_number": int(line[7:10].strip()),
                        "residue_name": line[11:14].strip(),
                        "chain_id": line[15].strip(),
                        "residue_seq_number": int(line[17:21].strip()),
                        "insertion_code": line[21].strip(),
                        "symmetry_operator_for_first_residue": int(line[59:65].strip()),
                        "symmetry_operator_for_second_residue": int(line[66:72].strip()),
                        "length": float(line[73:78].strip()),
                    }
                    pdb_data["ssbonds"].append(ssbond_data)

        if save:

            for pdb_atom in pdb_data["atoms"]:
                self.add_atom = [ pdb_atom['x'], pdb_atom['y'], pdb_atom['z'] ]  

            for pdb_hetatms in pdb_data["hetatms"]:
                self.add_atom = [ pdb_atom['x'], pdb_atom['y'], pdb_atom['z'] ]  

        return pdb_data

    def export_as_PDB(self, file_location:str=None, bond_distance:float=None, save_to_file:str='w', bond_factor:float=None, verbose:bool=False) -> str:
        try:
            import numpy as np
        except ImportError as e:
            import sys
            sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
            del sys

        file_location  = file_location  if not file_location  is None else self.file_location+'config.pdb' if type(self.file_location) is str else self.file_location
        bond_factor = bond_factor if bond_factor is not None else 1.1    
        #self.wrap()
        self.atomPositions = self.atomPositions - np.min( self.atomPositions, axis=0 ) 
        if verbose: print(f' >> Export as PDB >> {file_location}')

        pdb_str = ''
        for A, position_A in enumerate(self.atomPositions):     #loop over different atoms
            pdb_str += "ATOM  %5d %2s   MOL     1  %8.3f%8.3f%8.3f  1.00  0.00\n" % (int(A+1), self.atomLabelsList[A], position_A[0], position_A[1], position_A[2])

        for A, B in self.connection_list:
            pdb_str += f'CONECT{int(A+1):>5}{int(B+1):>5}\n'
                   
        # Save the generated XYZ content to a file if file_location is specified and save_to_file is True
        if file_location and save_to_file:
            with open(file_location, save_to_file) as f:
                f.write(pdb_str)
            if verbose:
                print(f"XYZ content has been saved to {file_location}")

        return True
    